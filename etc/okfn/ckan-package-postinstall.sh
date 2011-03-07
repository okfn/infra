#!/bin/bash


sample_ckan_config='WHERE??'
instances="dgu"
daemonuser="www-data"


if ! id ckan >/dev/null 2>&1 ; then
  sudo groupadd --system ckan
  sudo useradd  --system  --gid ckan  --home /var/lib/ckan -M  --shell /usr/sbin/nologin  ckan 
  sudo usermod -a -G ckan ${daemonuser}
  sudo usermod -a -G ckan okfn
fi 

# remove old CKAN data directories
sudo rm -fR  /var/{lib,backup,log}/ckan/


sudo mkdir -p 0755  /etc/ckan

sudo mkdir -p /var/backup
sudo mkdir -m 2750  /var/{lib,backup,log}/ckan/
sudo chgrp -R ckan /var/{lib,backup,log}/ckan/

for instance in ${instances}; do 
  sudo mkdir -p 0755  /etc/ckan/${instance}
  sudo cp ${sample_ckan_config} /etc/ckan/${instance}/${instance}.ini
  ( 
    cd /etc/ckan/${instance}
    sudo ln -s /usr/lib/pymodules/python2.6/ckanext/dgu/bin/wsgi.py ${instance}.py
  )

  sudo mkdir -m 2750 /var/lib/ckan/${instance}{,/static}
  sudo mkdir -m 2770 /var/{backup,log}/ckan/${instance} /var/lib/ckan/${instance}/{data,sstore,static/dump}
done

sudo find /var/{lib,backup,log}/ckan/ -ls
