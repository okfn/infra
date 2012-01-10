This is the Open Knowledge Foundation (http://www.okfn.org/) sysadmin repository.

There is an associated trac instance for ticketing and wiki at:

  http://trac.okfn.org/

Jumping off point for sysadmin documentation is:

  http://trac.okfn.org/wiki/Sysadmin


Setting up for usage
====================

Some commands require the Python modules "fabric" (>=1.0.0) and "boto", e.g.

  $ cd aws
  $ ./manage.py -h


There are two ways the required modules:


(A) If you have a recent distribution, just installing them from your distro's
main repositories should suffice. E.g. in case you use Ubuntu:

  $ sudo apt-get install fabric python-boto


(B) If your distro doesn't have the required modules/versions, or you don't
won't them system-wide installed, you can install them into a contained
environment. You would need "virtualenv" and "pip":

  $ sudo apt-get install python-virtualenv python-pip
  $ virtualenv ../pyenv-sysadmin
  $ pip -E ../pyenv-sysadmin install -r pip-requirements.txt

You have to activate this virtualenv each time before you use it:

  $ .  ../pyenv-sysadmin/bin/activate


Backup
======

See doc/BACKUP.txt 

