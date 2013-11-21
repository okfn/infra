Countermeasures against vinabot
===============================

Zombies in Vietnam are attacking our listserv. The botnet seems to work
in two stages. First some hosts on the Internet, usually web servers with
the Wordpress software installed, are compromised and they host some PHP
code that does nasty things. Then people's computers are compromised and
caused to visit the compromised server which instructs their web browsers
to do things like ask for some poor sod to be subscribed to many mailing 
lists again and again. This generates a lot of email traffic causing the
listserv to be banned by some sites such as hotmail and aol and fills up
the poor sod's mailbox. 

The scripts here are designed to be run in a pipeline like so::

     tail -f /var/log/nginx/access.log | xvinabot.sh | tee -a xvinabot.log | sh

The shell script uses an awk script to parse out the offending IP addresses
and does a whois on them to find out the netblock they belong to. If the
netblock is in Vietnam it outputs a command to null route the entire 
netblock. If it isn't it outputs a command to null route the host.

The output looks like this::

    route add -host 185.17.26.247 reject # BM-PRIVAX-LIMITED-IP-9 (GB)
    route add -net 42.116.208.0/20 reject # FPT-STATICIP-NET (VN)

The log file can be run with::

    sh xvinabot.log

after a reboot to re-create the null routes.
