#!/usr/bin/python

import ConfigParser
import os
from re import match 
import subprocess

a="/usr/lib/check_mk_agent/local/apt-security-check"
ansible_facts='/etc/ansible/facts.d'
apt_facts= ansible_facts + '/apt.fact'

facts = {}
facts['security_updates_available'] = False

devnull = open(os.devnull, 'w')


def security_updates(facts):
	c = subprocess.Popen([a,'--security-update-count'], stderr=devnull, stdout=subprocess.PIPE)
	streamdata = c.communicate()[0]
	out = streamdata.strip()
	if match("(\d+|\d)$", out):	
		out = int(out)
		if out > 0:
			facts['security_updates_available'] = True
			facts['security_updates'] = out
	return facts

if not os.path.exists(ansible_facts):   
	os.makedirs(ansible_facts)

facts = security_updates(facts)

if len(facts.keys()) > 0:
	config = ConfigParser.RawConfigParser()
	config.add_section('package_updates')
	for k, v in facts.items():
		config.set('package_updates', k, v)


with open(apt_facts, 'wb') as configfile:
	config.write(configfile)
