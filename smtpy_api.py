#! /usr/bin/env python3
"""
Simple JSON REST API for the smtpy service using the bottle framework.

Copyright (c) 2015, Matthew Kelly (Badgerati)
Company: Cadaeic Studios
License: MIT (see LICENSE for details)
"""

import json
import sqlite3
import strex
import smtpy_config as config
from bottle import route, run, request, ServerAdapter


# Formats the datarows into a nice dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def close_conn(curs, conn):
    try:
        if conn is not None:
            conn.close()
        if curs is not None:
            curs.close()
    except Exception:
        return


# Retrieve an email from the database for the mailLogId supplied.
#
# Examples:
#       /retrieve/email?mailLogId=1337
@route('/retrieve/email', method='GET')
def retrieve_email():
    try:
        mailLogId = strex.safeguard(request.query.mailLogId, 0)

        if int(mailLogId) <= 0:
            return {'error':'no mailLogId supplied'}

        try:
            conn = None
            curs = None
            
            conn = sqlite3.connect(config.settings['database'])
            conn.row_factory = dict_factory
            curs = conn.cursor()
            
            sql = 'SELECT MailLogId, IPAddress, PortNumber, Subject, Sender, Recipients, Body, TimeStamp FROM MailLog WHERE MailLogId = ? ORDER BY MailLogId DESC LIMIT 1'
            curs.execute(sql, (mailLogId,))
            value = curs.fetchone()
            
            curs.close()
            conn.close()

            if value is None:
                return '{}'
            return json.JSONEncoder().encode(value)
        except Exception as e:
            close_conn(curs, conn)
            return {'error':str(e)}
    except Exception as e:
        return {'error':str(e)}


# Retrieve the top x emails from the database for the sender email supplied.
# If the amount is not passed it is defaulted to 1.
# 
# Example:
#       /retrieve/emails?email=from@domain.com&amount=2
@route('/retrieve/emails', method='GET')
def retrieve_emails():
    try:
        email = request.query.email
        amount = strex.safeguard(request.query.amount, 1)
        
        if strex.is_none_or_empty(email):
            return {'error':'no email supplied'}

        if int(amount) < 1:
            amount = 1

        try:
            conn = None
            curs = None
            
            conn = sqlite3.connect(config.settings['database'])
            conn.row_factory = dict_factory
            curs = conn.cursor()

            sql = 'SELECT MailLogId, IPAddress, PortNumber, Subject, Sender, Recipients, Body, TimeStamp FROM MailLog WHERE Sender = ? ORDER BY MailLogId DESC LIMIT ?'
            curs.execute(sql, (email, amount,))
            values = curs.fetchall()
            
            curs.close()
            conn.close()

            if values is None:
                return '{}'
            return json.JSONEncoder().encode(values)
        except Exception as e:
            close_conn(curs, conn)
            return {'error':str(e)}
    except Exception as e:
        return {'error':str(e)}


# Create an email within the database
# The sender and recipients parameters are mandatory.
# Ip and port are optional, and will be defaulted to 127.0.0.1 and 1234 respectively.
# Subject and body are also optional parameters.
#
# Examples
#       /create/email?ip=127.0.0.1&port=1234&subject=This%20is%20a%20test&sender=from@domain.com&recipients=to@domain.com&body=This%20is%20a%20test
@route('/create/email', method='GET')
def create_email():
    try:
        ip = strex.safeguard(request.query.ip, '127.0.0.1')    
        port = strex.safeguard(request.query.port, '1234')
        subject = strex.safeguard(request.query.subject)
        body = strex.safeguard(request.query.body)
        
        sender = request.query.sender
        if strex.is_none_or_empty(sender):
            return {'error':'no sender supplied'}
        
        recipients = request.query.recipients
        if strex.is_none_or_empty(recipients):
            return {'error':'no recipients supplied'}

        try:
            conn = None
            curs = None
            
            conn = sqlite3.connect(config.settings['database'])
            conn.row_factory = dict_factory
            curs = conn.cursor()

            sql = 'INSERT INTO MailLog(IPAddress, PortNumber, Subject, Sender, Recipients, Body) VALUES (?, ?, ?, ?, ?, ?)'
            curs.execute(sql, (str(ip), str(port), str(subject), str(sender), str(recipients), str(body)))
            _id = curs.lastrowid

            sql = 'SELECT MailLogId, IPAddress, PortNumber, Subject, Sender, Recipients, Body, TimeStamp FROM MailLog WHERE MailLogId = ? ORDER BY MailLogId DESC LIMIT 1'
            curs.execute(sql, (_id,))
            value = curs.fetchone()
            
            conn.commit()
            curs.close()
            conn.close()
            return json.JSONEncoder().encode(value)
        except Exception as e:
            close_conn(curs, conn)
            return {'error':str(e)}
    except Exception as e:
        return {'error':str(e)}


# Deletes an email from the database for the mailLogId supplied.
#
# Examples:
#       /delete/email?mailLogId=1337
@route('/delete/email', method='GET')
def delete_email():
    try:
        mailLogId = strex.safeguard(request.query.mailLogId, 0)

        if int(mailLogId) <= 0:
            return {'error':'no mailLogId supplied'}

        try:
            conn = None
            curs = None
            
            conn = sqlite3.connect(config.settings['database'])
            curs = conn.cursor()
            
            sql = 'DELETE FROM MailLog WHERE MailLogId = ?'
            curs.execute(sql, (mailLogId,))

            conn.commit()
            curs.close()
            conn.close()
            return '{}'
        except Exception as e:
            close_conn(curs, conn)
            return {'error':str(e)}
    except Exception as e:
        return {'error':str(e)}


# Delete all emails from the database for the sender email supplied.
# 
# Example:
#       /delete/emails?email=from@domain.com
@route('/delete/emails', method='GET')
def delete_emails():
    try:
        email = request.query.email
        
        if strex.is_none_or_empty(email):
            return {'error':'no email supplied'}

        try:
            conn = None
            curs = None
            
            conn = sqlite3.connect(config.settings['database'])
            curs = conn.cursor()
            
            sql = 'DELETE FROM MailLog WHERE Sender = ?'
            curs.execute(sql, (email,))
            
            conn.commit()
            curs.close()
            conn.close()
            return '{}'
        except Exception as e:
            close_conn(curs, conn)
            return {'error':str(e)}
    except Exception as e:
        return {'error':str(e)}



__server__ = None

# Start the bottle server
def __init__():
    global __server__
    __server__ = MyWSGIRefServer(host=config.settings['api']['host'], port=config.settings['api']['port'])
    run(server=__server__, quiet=True)


# Stop the bottle server
def __stop__():
    global __server__
    __server__.stop()


# Custom server to run bottle
class MyWSGIRefServer(ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

