#!/usr/bin/env python3
"""
Confiuration file for setting up the smtpy service and API. This will be
for settings like the location of the SQLite database, service names/descriptions,
and the host/port for the SMTP/Web API to listen on.

Copyright (c) 2015, Matthew Kelly (Badgerati)
Company: Cadaeic Studios
License: MIT (see LICENSE for details)
"""

settings = dict(
    # Location of the SQLite database (will be auto-created)
    database = 'path/to/your/smtpy.db',

    # SMTP settings for host/port and service information
    smtp = dict(
        svc_name = 'Smtpy Service',
        svc_display_name = 'Smtpy Service',
        svc_description = 'This is the service which runs the mock SMTP service',
        purge_email = True,
        use_utf8 = True,
        host = '127.0.0.1',
        port = 25
    ),

    # API settings for host/port and service information
    api = dict(
        svc_name = 'Smtpy API Srvice',
        svc_display_name = 'Smtpy API Service',
        svc_description = 'This is the service which runs the smtpy API service',
        host = '127.0.0.1',
        port = 8081
    )
)
