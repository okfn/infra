#!/usr/bin/python2.7

import subprocess
import re
import time
from myutils import graphite_pickle
import configparser

config = configparser.RawConfigParser()

config.read('/opt/scripts/config/config.ini')
graphite_host=config.get('graphite', 'host')

NAME='exim_stats'
EXIM='/usr/sbin/exim'
VERBOSE_LOGGING='False'
LIST_ADDR='@lists.okfn.org'
namespace='mail_metrics.exim'




def get_stats():
	stats = {}
	stats['total_queued_mail'] = 0
	stats['to_gmail'] = 0
	stats['to_yahoo'] = 0
	stats['from_okfn_lists'] =0 
	
	cmd_queue_size = [ EXIM, '-bpc']
	try:
		p = subprocess.Popen(cmd_queue_size, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	except:
		return None

	out = p.stdout.readline()
	stats['total_queued_mail'] = out.strip()
	

	cmd_queue = [ EXIM, '-bp']
	try:
		p = subprocess.Popen(cmd_queue, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	except:
		return None

	for line in p.stdout.readlines():
		if re.match('.*' + LIST_ADDR, line):
			stats['from_okfn_lists'] += 1
		if re.match('.*@gmail', line):
			stats['to_gmail'] += 1
		elif re.match('.*@yahoo', line):
			stats['to_yahoo'] += 1
	return stats

metrics = []
stats = get_stats()
ts = int(time.time())
for k, v in stats.items():
	datapoint = namespace + '.' + k
	metrics.append(((datapoint),(ts, v)))		

#print metrics

graphite_pickle.push(metrics, graphite_host)
