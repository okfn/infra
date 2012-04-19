#!/bin/bash

ES_VERSION="0.18.7"
ES_HOME="/usr/local/elasticsearch"
ES_USER="elasticsearch"
USE_SUDO="y"

###

SUDO=$([[ "${USE_SUDO}" = "y" ]] && echo "sudo " || echo)

# Check to see if this version of ES is already installed, and abort if it is.
if [[ -d "${ES_HOME}/elasticsearch-${ES_VERSION}" ]]; then
  echo "${ES_HOME}/elasticsearch-${ES_VERSION} already exists, aborting!"
  exit 1
fi

echo "Installing JRE"
$SUDO apt-get install -y openjdk-6-jre-headless

# Does $ES_USER exist? If not create him...
echo "Checking for user ${ES_USER}"
id "${ES_USER}"
if [[ "${?}" -ne 0 ]]; then
  echo "Adding user ${ES_USER}"
  $SUDO useradd -s /bin/false -U -d "${ES_HOME}" "${ES_USER}"
fi

# Fetch ES sources...
echo "Downloading ElasticSearch version ${ES_VERSION}"
curl -OL "https://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-${ES_VERSION}.tar.gz"
tar -xf "elasticsearch-${ES_VERSION}.tar.gz"
rm "elasticsearch-${ES_VERSION}.tar.gz"

echo "Installing ElasticSearch in ${ES_HOME}"
$SUDO mkdir -p "${ES_HOME}"
$SUDO mv "elasticsearch-${ES_VERSION}" "${ES_HOME}"
$SUDO ln -snf "${ES_HOME}/elasticsearch-${ES_VERSION}" "${ES_HOME}/elasticsearch"

# Use existing config if already there, but move config if not
if [[ ! -d "${ES_HOME}/config" ]]; then
  echo "Using dist config"
  $SUDO mv "${ES_HOME}/elasticsearch/config" "${ES_HOME}"
else
  echo "Using existing config"
fi
$SUDO rm -rf "${ES_HOME}/elasticsearch/config"
$SUDO ln -s "${ES_HOME}/config" "${ES_HOME}/elasticsearch/config"

# Set up logs directory
echo "Setting ElasticSearch to log to /var/log/elasticsearch"
$SUDO mkdir -p /var/log/elasticsearch
$SUDO ln -snf /var/log/elasticsearch "${ES_HOME}/logs"
$SUDO ln -snf "${ES_HOME}/logs" "${ES_HOME}/elasticsearch/logs"

# Set up data directory
$SUDO mkdir -p "${ES_HOME}/data"
$SUDO ln -snf "${ES_HOME}/data" "${ES_HOME}/elasticsearch/data"

# Set up service wrapper
echo "Setting up service wrapper"
curl -L https://github.com/elasticsearch/elasticsearch-servicewrapper/tarball/master > service.tar.gz
tarball_prefix=$(tar -tf service.tar.gz | head -1)
tar --strip-components=1 -xf service.tar.gz "${tarball_prefix}service"
sed -i'.bak' -e "s/^#RUN_AS_USER=$/RUN_AS_USER=\"${ES_USER}\"/" service/elasticsearch
$SUDO mv service "${ES_HOME}/elasticsearch/bin/service"
$SUDO rm service.tar.gz
$SUDO ln -snf "${ES_HOME}/elasticsearch/bin/service/elasticsearch" /etc/init.d/elasticsearch

echo "Configuring ElasticSearch to start at boot"
$SUDO update-rc.d elasticsearch defaults

# Fix permissions
echo "Setting owner of ${ES_HOME} to ${ES_USER}"
$SUDO chown -R "${ES_USER}:${ES_USER}" "${ES_HOME}"
echo "Setting owner of /var/log/elasticsearch to ${ES_USER}"
$SUDO chown -R "${ES_USER}:${ES_USER}" /var/log/elasticsearch

echo "All done. Check the configuration of ElasticSearch in ${ES_HOME}/config and then"
echo "start it with 'sudo service start elasticsearch' or similar."
echo
echo "Don't forget you'll need to punch appropriate holes in the firewall..."
