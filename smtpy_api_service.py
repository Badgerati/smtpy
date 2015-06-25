#!/usr/bin/env python3
"""
This is the main Windows service for the smtpy API.

Copyright (c) 2015, Matthew Kelly (Badgerati)
License: MIT (see LICENSE for details)
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import traceback
import smtpy_api
import smtpy_config as config


# Main Windows service
class SmtpApiService(win32serviceutil.ServiceFramework):
    _svc_name_ = config.settings['api']['svc_name']
    _svc_display_name_ = config.settings['api']['svc_display_name']
    _svc_description_ = config.settings['api']['svc_description']

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0 , None)
        socket.setdefaulttimeout(60)

        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        smtpy_api.__stop__()
        win32event.SetEvent(self.hWaitStop)


    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()


    def main(self):
        try:
            smtpy_api.__init__()
        except Exception as e:
            servicemanager.LogMsg(servicemanager.EVENTLOG_ERROR_TYPE,
                                  servicemanager.PYS_SERVICE_STARTED,
                                  (self._svc_name_, str(e) + '\n' + traceback.format_exc()))


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SmtpApiService)
