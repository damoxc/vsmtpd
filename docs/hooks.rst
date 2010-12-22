Hooks
=====

Hooks are used within vsmtpd to extend its functionality, going as far as
even allowing Plugins to implement their own smtp commands.

pre_connection
--------------
:called:
	as soon as the connection is accepted.

:arguments:
	- connection

:exceptions:
	- DenyError / DenyDisconnectError: returns a 550 to the client and ends
	  the connection
	- DenySoftError / DenySoftDisconnectError: returns a 451 to the client
	  and ends the connection.

:return codes:
	ignored

connect
-------
:called:
	at the start of a connection, before the greeting is sent.

:arguments:
	- connection

post_connection
---------------
:called:
	directly before the connectino is finished, or if the client drops the
	connection.

:arguments:
	- connection

greeting
--------
:called:
	prior to sending the greeting to the client, allows plugins to modify
	what is sent to the client.

helo
----
:called:
	after the client sends HELO

ehlo
----
:called:
	after the client sends EHLO

reset_transaction
-----------------
:called:
	when a transaction is reset

mail
----
:called:
	after the client sends the MAIL FROM: command. The argument is parsed
	and then this hook is called.

rcpt
----
:called:
	after the client sends a RCPT TO: command. The argument is parsed and
	then this hook is called.

data
----
:called:
	after the client sends the DATA command, before any of the message data
	is sent.
