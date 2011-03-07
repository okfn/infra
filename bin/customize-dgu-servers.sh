################################
# GENERAL OKFN STUFF, should actually go into our fabfile 
# Done on staging, uat, dev. Not done on live


# Install our tools
sudo apt-get update
sudo apt-get install vim bsd-mailx


# Enable color prompt (==> sysadmin Fabfile??)
# To be done: same for /root/.bashrc
sudo apt-get install patch
wget -O- https://bitbucket.org/okfn/sysadmin/raw/tip/etc/okfn/bashrc.colored-hostname.patch | patch .bashrc
# logout, login to make new prompt


# MANUAL: set new hostname (==>  sysadmin Fabfile??)
sudo vi /etc/hostname
sudo vi /etc/hosts
sudo hostname `cat /etc/hostname`
sudo /etc/init.d/syslog-ng restart


# Set mailname, root alias
if [ -f /etc/mailname ]; then
    ( cd /etc/; sudo rm mailname; sudo ln -s hostname mailname)
fi
egrep -q "^root:.*sysadmin@okfn.org" /etc/aliases || sudo sed -e 's/^\(root:.*\)$/\1,sysadmin@okfn.org/g' -i /etc/aliases
sudo newaliases
sudo cp -a /etc/postfix/main.cf /etc/postfix/main.cf.ORIG
sudo sed  -i /etc/postfix/main.cf \
    -e 's,^\( *myhostname *= *\).*$,#\1,g' \
    -e 's,^\( *myorigin *= *\).*$,\1$myhostname,g' \
    -e 's,^\( *mydestination *= *\).*$,\1$myhostname\, localhost,g' 
sudo /etc/init.d/postfix restart



################################
# GENERAL CKAN STUFF, should go into a ckan script of the ckan deb package
# Done on uat, dev. Not done on staging, live

# create CKAN user/group and directory layout
wget https://bitbucket.org/okfn/sysadmin/raw/tip/etc/okfn/ckan-package-postinstall.sh
./ckan-create-directories.sh
# login, logout to enjoy "okfn" being member of group "ckan"



################################
# HARDENING, should go into a ckan-dgu script
# Done on uat, dev. Not done on staging, live

# Remove shit
sudo /etc/init.d/mysql stop
sudo apt-get remove mysql-common php5-common
sudo apt-get autoremove
sudo /etc/init.d/apache2 restart

# bind postfix to localhost
sudo sed  -i /etc/postfix/main.cf -e 's,^\( *inet_interfaces *= *\).*$,\1localhost,g' 
sudo /etc/init.d/postfix restart

# disable sshd password/root login
sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.ORIG
sudo sed -i /etc/ssh/sshd_config -e 's,^[\t #]*PasswordAuthentication.*$,PasswordAuthentication no,g' -e 's,^[\t #]*PermitRootLogin.*$,PermitRootLogin no,g'
sudo /etc/init.d/ssh restart

