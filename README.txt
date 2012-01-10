This is the Open Knowledge Foundation (http://www.okfn.org/) sysadmin repository.

There is an associated trac instance for ticketing and wiki at:

    http://trac.okfn.org/

Jumping off point for sysadmin documentation is:

    http://trac.okfn.org/wiki/Sysadmin


Setting up for usage
====================

Some commands require the Python modules "fabric" and "boto", e.g.

    $ cd aws
    $ ./manage.py -h


IMPORTANT: fabric has changed the order of parameters for "append()" with
version 1.0.0. It is vital that you use fabric 1.0.0 or later.


There are two ways to install the required modules:


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

Test it:

    (pyenv-sysadmin)$ fab -V
    Fabric 1.0.1

If you instead receive an error like this:

    pkg_resources.DistributionNotFound: pycrypto>=2.1,!=2.4

there you have a conflict with your system-wide PyChrypto library.
In this case you have to force it's installation into your virtualenv:

    $ sudo apt-get install build-essential python-dev
    $ pip -E ../pyenv-sysadmin install --upgrade PyCrypto

[See http://trac.okfn.org/ticket/1095]



Backup
======

See doc/BACKUP.txt 

