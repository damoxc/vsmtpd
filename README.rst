vsmtpd
======

About
-----
After using qpsmtpd for some time and finding that its design was very
flexible and very well put together. This has spawned from the vmail project
which is mostly written in Python.

Wanting to experiment at how well TwistedMail could perform accepting
connections, as the majority of time spent during a SMTP conversation is
out of qpsmtpd (network i/o, spam scanning, virus checking), it seemed that
an async model rather than fork model would be preferable in terms of
memory consumption on inbound servers.

Installation
------------
The same as any python project:

	python setup.py build
	python setup.py install


Plugins
-------
Wanting to mimick how qpsmtpd is put together, the core of vsmtpd does very
little and denies mail from all senders, to all senders by default. The
functionality to accept messages, authenticate, starttls etc. will all come
from plugins that subscribe to hooks. See the docs/hooks.rst document for
details on what these hooks do.
