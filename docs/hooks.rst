Hooks
=====

Hooks are used within vsmtpd to extend its functionality, going as far as
even allowing Plugins to implement their own smtp commands.

pre_connection
--------------
This is fired as soon as the connection is accepted

connect
-------
This is fired at the start of a connection, before the greeting is sent.

post_connection
---------------
This is fired directly before the connection is finished, or if the client drops the connection.

greeting
--------
This allows plugins to modify the greeting that is sent to the client

logging
-------

config
------

helo
----
after the client sends HELO

ehlo
----
after the client sends EHLO
