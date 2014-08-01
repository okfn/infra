#!/usr/bin/python2.7
import re
import time
import os
from myutils import graphite_pickle
from myutils import reverse_tail
import configparser

config = configparser.RawConfigParser()
config.read('/opt/scripts/config/config.ini')
graphite_host=config.get('graphite', 'host')

postfix_log='/var/log/mail.log'

namespace='mail_metrics.postfix'


def get_spam_stats():
	logfile = postfix_log 
	stats={}
#	stats['total'] = 0
#	stats['inbound'] = 0
#	stats['outbound'] = 0
#	stats['queue_size'] = 0
	stats['spamhaus_blocks'] = 0
	stats['spamasassin_rejects'] = 0
	stats['greylist_rejects'] = 0
	stats['greylist_allow'] = 0

	time_now = int(time.time())
	five_mins_ago = time_now-300
	year = time.strftime('%Y', time.localtime())

	for line in reverse_tail.run(logfile):
		if not line:
			continue

		m = re.match(r"(?P<ts>\w+\s+\d+ \d+:\d+:\d+).*$", line)
		if m:  
		        ts = m.group('ts')
		        ts = ts + ' ' + year
		        ts = int(time.mktime(time.strptime(ts, '%b %d %H:%M:%S %Y')))
		        if ts < five_mins_ago:
		                break
	
		m = re.match(r"^\w+\s+\d+ \d+:\d+:\d+.*: (?:554.*(?P<spamhaus>blocked)|(?P<spamd>spamd): result: Y)", line)
		if m:  
		        if m.group('spamhaus'):
		                stats['spamhaus_blocks'] += 1
		
		        if m.group('spamd'):
		                stats['spamasassin_rejects'] += 1
		
		m = re.match(r"\w+\s+\d+ \d+:\d+:\d+.* postgrey\[\d+\]: action=(:?(?P<greylist>greylist)|(?P<pass>pass)),.*", line)
		if m:  
		        if m.group('greylist'):
		                stats['greylist_rejects'] += 1
		        if m.group('pass'):
		                stats['greylist_allow'] += 1
			
	push_stats(stats)	

def push_stats(stats): 
	#accepts dicts that should look like  metrics['datapoint']['value']
	metrics = []
	ts = int(time.time())
	for k, v in stats.items():
		datapoint = namespace + '.' + k
		metrics.append(((datapoint),(ts, v)))		
	
#	print metrics
	graphite_pickle.push(metrics, graphite_host)

get_spam_stats()
