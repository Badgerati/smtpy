#! /usr/bin/env python3
"""
This is the main SMTP stmpy service. This will set up a Windows service
which will listen on the specified host/port in the config file for incoming
emails.

By default, the SMTP server will be set up to allow UTF-8 emails, and to
automatically purge emails that become older than 30 minutes.

To disable UTF-8, set the 'use_utf8' setting in the smtp-config to False.
To disable the purging of emails, set the 'purge_email' setting to False.

This Windows service will also automatically create the SQLite database
if it doesn't yet exist, as well as the required table.

Copyright (c) 2015, Matthew Kelly (Badgerati)
License: MIT (see LICENSE for details)
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import smtpdutf8 as smtpd
import asyncore
import sqlite3
import re
import traceback
import smtpy_config as config

# This is the mock SMTP server that will be listening on the specified host/port.#
# It will insert any email into the SQLite database - purging older emails if enabled.
class MockSmtpServer(smtpd.SMTPServer):

    # Records a received email into the SQLite database
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        try:
            matches = re.search('^.*?\'(?P<ip>.*?)\'.*?(?P<port>\d+).*?$', str(peer))
            ip = matches.group('ip')
            port = matches.group('port')

            matches = re.search('Subject: (?P<subject>.+)', str(data))
            subject = matches.group('subject')

            try:
                # Store email in database
                conn = sqlite3.connect(config.settings['database'])
                sql = "INSERT INTO MailLog(IPAddress, PortNumber, Subject, Sender, Recipients, Body) VALUES (?, ?, ?, ?, ?, ?)"
                conn.execute(sql, (str(ip), str(port), str(subject), str(mailfrom), str(rcpttos), str(data)))
                conn.commit()

                # If enabled, purge emails older than 30 minutes
                if config.settings['smtp']['purge_email'] is True:
                    sql = "DELETE FROM MailLog WHERE TimeStamp < DATETIME('now', '-30 minute')"
                    conn.execute(sql)
                    conn.commit()
                    
                conn.close()
            except Exception as e:
                if conn is not None:
                    conn.close()
                servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, str(e) + '\n' + traceback.format_exc()))
        except Exception as e:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, str(e) + '\n' + traceback.format_exc()))
        return


# Main Windows service
class SmtpService(win32serviceutil.ServiceFramework):
    _svc_name_ = config.settings['smtp']['svc_name']
    _svc_display_name_ = config.settings['smtp']['svc_display_name']
    _svc_description_ = config.settings['smtp']['svc_description']

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0 , None)
        socket.setdefaulttimeout(60)

        try:
            # Attempt to create the database and table
            conn = sqlite3.connect(config.settings['database'])
            sql = """CREATE TABLE IF NOT EXISTS MailLog
                    (
                        MailLogId INTEGER PRIMARY KEY AUTOINCREMENT,
                        IPAddress TEXT,
                        PortNumber TEXT,
                        Subject TEXT,
                        Sender TEXT,
                        Recipients TEXT,
                        Body TEXT,
                        TimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )"""
            conn.execute(sql)
            conn.commit()
            conn.close()
        except Exception:
            if conn is not None:
                conn.close()
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, str(e) + '\n' + traceback.format_exc()))

        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        asyncore.close_all()
        raise asyncore.ExitNow('Service is quitting')            
        win32event.SetEvent(self.hWaitStop)


    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()


    def main(self):
        try:
            server = MockSmtpServer(
                (config.settings['smtp']['host'], config.settings['smtp']['port']),
                None,
                enable_SMTPUTF8 = config.settings['smtp']['use_utf8'],
                decode_data = (not config.settings['smtp']['use_utf8']))
            asyncore.loop()
        except Exception as e:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, str(e) + '\n' + traceback.format_exc()))


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SmtpService)
