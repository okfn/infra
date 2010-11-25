This is the Open Knowledge Foundation (http://www.okfn.org/) sysadmin repository.

There is an associated trac instance for ticketing and wiki at:

  http://knowledgeforge.net/okfn/tasks

Jumping off point for sysadmin documentation is:

  http://knowledgeforge.net/okfn/tasks/wiki/Sysadmin


Setting up for usage
====================

If you want to run some commands (such as those requiring fabric or boto).

  # create a virtualenv so you do not pollute system with installed items
  $ virtualenv ../pyenv-sysadmin
  $ pip -E ../pyenv-sysadmin install -r pip-requirements.txt

To use this virtualenv:

  $ . pyenv-sysadmin/bin/activate

Then, for example to work with AWS:

  $ cd aws
  $ ./manage.py -h


Backup
======

See doc/BACKUP.txt 

