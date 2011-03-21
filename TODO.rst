TODO
====

* Convert SMTP errors to Python exceptions, remove the sending of
  codes from the command handlers to the command dispatcher so its
  easier to make sure that the client isn't left hanging.
* Complete the handling of the DATA command.
* Implement the queue parts of the mail server.
* Implement the dispatch hooks method
* Decide upon a plugin format
* The ability to fork childen and have a master process with a couple of
  workers that die after a certain number of handled requests.
