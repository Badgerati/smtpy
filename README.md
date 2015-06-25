smtpy
=====

At my work we have a lot of hassle with QA, regression runs and dev PCs when it comes to sending out email from the core platform.
We have a SMTP server - but it's absolutely rubbish and fills up way too quickly and then dies miserably.

I created smtpy as a simple lightweight python Windows service which would run a mock SMTP server. This service would pick up all email that was sent to 127.0.0.1:25 and record it within a SQLite database. Further to that, after each insert to the database, the service would self-clean by deleting an emails that were older than 30 minutes.

Now I could run a regression without worrying about the server crumbling to pieces, and with the simple JSON REST API I could retrieve the emails from the SQLite database.


Usage
-----

To use smtpy is simple. First you need to have the following dependencies installed:

 * Python3
 * PyWin32

Ensure that python is setup in you PATH.

Next, you might need to edit the config file:

 * Open the smtpy_config.py file.
 * Edit the database path to point to where you want to database to be, and its name.
 * Edit the svc_name, svc_display_name and svc_description options in both the smtp and api sections.
 * Edit the host/port in the smtp section for where you want the smtp server to listen for incoming email.
 * Edit the host/port in the api section from where you want the JSON REST API to be accessible.

Now all you need is to run the install.bat file from a Command Prompt in administrator mode. All wallah! You will now have two services created under the svc_display_names (or svc_name) you stated above.

[Note: you will need to make sure all your SMTP configs for your programs send email to the host/port you entered above]

Start them both services and send some test email. Open the SQLite database in a program like DB SQLite Browser and you should see the emails flooding in! :)


Features
--------

 * Supports UTF-8
 * Self cleaning so it doesn't gobble up memory
 * Lightweight