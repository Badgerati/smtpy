#! /usr/bin/env python3
"""
Simple JSON REST API for the smtpy service using the bottle framework.
Ony contains two retrievals currently:

    - /email?email=<email>
        This will retrieve the first entry in the database (if any) for
        the supplied email address.

    - /emails?email=<email>[&amount=<value>]
        This will retrieve an amount of entries from the database for the
        supplied email. If the amount parameter is omitted, it is defaulted
        to 1.

Copyright (c) 2015, Matthew Kelly (Badgerati)
License: MIT (see LICENSE for details)
"""

import json
import sqlite3
import smtpy_config as config
from bottle import route, run, request, ServerAdapter


# Formats the datarows into a nice dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Select the top email from the database for the sender email supplied
@route('/email', method='GET')
def select_email():
    email = request.query.email

    try:
        conn = sqlite3.connect(config.settings['database'])
        conn.row_factory = dict_factory
        curs = conn.cursor()
        sql = "SELECT MailLogId, IPAddress, PortNumber, Subject, Sender, Recipients, Body FROM MailLog WHERE Sender = ? ORDER BY MailLogId DESC LIMIT 1"
        curs.execute(sql, (email,))
        value = curs.fetchone()
        curs.close()
        conn.close()
        return json.JSONEncoder().encode(value)
    except Exception as e:
        if conn is not None:
            curs.close()
            conn.close()
        return str(e)


# Select the top x emails from the database for the sender email supplied
@route('/emails', method='GET')
def select_emails():
    email = request.query.email
    amount = request.query.amount

    if amount is None or amount == "" or int(amount) < 1:
        amount = 1

    try:
        conn = sqlite3.connect(config.settings['database'])
        conn.row_factory = dict_factory
        curs = conn.cursor()
        sql = "SELECT MailLogId, IPAddress, PortNumber, Subject, Sender, Recipients, Body FROM MailLog WHERE Sender = ? ORDER BY MailLogId DESC LIMIT ?"
        curs.execute(sql, (email, amount,))
        values = curs.fetchall()
        curs.close()
        conn.close()
        return json.JSONEncoder().encode(values)
    except Exception as e:
        if conn is not None:
            curs.close()
            conn.close()
        return str(e)


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

