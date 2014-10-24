from	ubuntu:12.04

#user	etherpad-lite
run	echo 'deb http://us.archive.ubuntu.com/ubuntu/ precise universe' >> /etc/apt/sources.list
run	apt-get -y update

# Install supervisord
run	apt-get -y install supervisor
run	apt-get -y install python-software-properties mysql-client-5.5

# Install required packages
run	add-apt-repository ppa:chris-lea/node.js
run	apt-get -y update
run	apt-get -y install nodejs git-core curl python libssl-dev pkg-config build-essential

# Install etherpad-lite
run	mkdir /src
run	git clone https://github.com/ether/etherpad-lite.git /src/etherpad-lite
run	/src/etherpad-lite/bin/installDeps.sh

env	ETHERPAD_USER etherpad_lite
env	ETHERPAD_PASS change_password
env	ETHERPAD_DB   etherpad_lite
env	ADMIN_PASS change_password

add	./etherpad-lite.conf /etc/supervisor/conf.d/etherpad-lite.conf
add	./run-supervisord /usr/sbin/run-supervisord
add	./settings.json /src/etherpad-lite/settings.json

expose	:9001

cmd	["/usr/sbin/run-supervisord"]
# vim:ts=8:noet:
