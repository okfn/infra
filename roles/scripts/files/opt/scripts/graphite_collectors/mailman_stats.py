#!/usr/bin/python2.7
import re
import time
import os
from myutils import graphite_pickle
from myutils import reverse_tail
import configParser

config = ConfigParser.RawConfigParser()

config.read('/opt/scripts/config/config.ini')
graphite_host=config.get('graphite', 'host')

mailman_logs='/var/log/mailman/'
qpath='/var/lib/mailman/qfiles'

namespace='mail_metrics.mailman'


def get_post_stats():
	logfile = mailman_logs + 'post'
	stats={}
	stats['posts.total'] = 0
	time_now = int(time.time())
	five_mins_ago = time_now-300

	for line in reverse_tail.run(logfile):
		if not line:
			continue
		
		s = re.match(r"^(?P<ts>\w+ \d+ \d+:\d+:\d+ \d+) .*post to (?P<list_name>.*) from (?P<poster>.*@*.), size=(?P<msg_size>\d+), message-id.*, (?P<result>.*)$", line)
		ts = s.group('ts')
		list_name = s.group('list_name')
		poster = s.group('poster')
		msg_size = s.group('msg_size')
		result = s.group('result')

		ts = int(time.mktime(time.strptime(ts,'%b %d %H:%M:%S %Y')))	
		if ts < five_mins_ago:
			break
		else:
			#print line
			stats['posts.total'] += 1
			list_name = re.sub('\.', '-', list_name)
			
			# collect stats on posts - success/failures, posts per list
			if result == 'success':
				list_ns = list_name + '.posts' #set the graphite namespace to ${list-name}.posts
				if not list_ns in stats:
					stats[list_ns] = 0
				
				stats[list_ns] += 1

			else:
				list_ns = list_name + '.post_failures'
				if not list_ns in stats:
					stats[list_ns] = 0

				stats[list_ns] += int(result.split()[0])
			
	push_stats(stats)	

def get_outbound_stats(): #smtp
	logfile = mailman_logs + 'smtp'
	stats={}
	stats['outbound_mails.total'] = 0
	time_now = int(time.time())
	five_mins_ago = time_now-300

	for line in reverse_tail.run(logfile):
		if not line:
			continue
		
		s = re.match(r"^(?P<ts>\w+ \d+ \d+:\d+:\d+ \d+).* smtp to (?P<list_name>.*) for (?P<rcpt_count>\d+) recips", line)
		#print line
		ts = s.group('ts')
		list_name = s.group('list_name')
		rcpt_count = s.group('rcpt_count')

		ts = int(time.mktime(time.strptime(ts,'%b %d %H:%M:%S %Y')))	
		if ts < five_mins_ago:
			break
		else:
			stats['outbound_mails.total'] += int(rcpt_count)
			
			list_name = re.sub('\.', '-', list_name)
			
			# collect stats on outbound mails per list
			list_ns = 'outbound_mails.' + list_name + '.total' 
			
			if not list_ns in stats:
				stats[list_ns] = 0
				
			stats[list_ns] += int(rcpt_count)				
	push_stats(stats)	

	
def get_subscribe_stats():
	logfile = mailman_logs + 'subscribe'
	stats={}
		
	time_now = int(time.time())
	five_mins_ago = time_now-300

	for line in reverse_tail.run(logfile):
		if not line:
			continue
		
		s = re.match(r"^(?P<ts>\w+ \d+ \d+:\d+:\d+ \d+) \(.*\) (?P<list_name>.*?): (?:(?P<action>new|deleted|pending))", line)
		ts = s.group('ts')
		list_name = s.group('list_name')
		action = s.group('action')

		ts = int(time.mktime(time.strptime(ts,'%b %d %H:%M:%S %Y')))	
		if ts < five_mins_ago:
			break
		else:
			
			list_name = re.sub('\.', '-', list_name)
			
			if action == 'new':
				list_ns = 'subscribe.' + list_name + '.new' #setup graphite ns 
			if action == 'deleted':
				list_ns = 'subscribe.' + list_name + '.deleted' 
			if action == 'pending':
				list_ns = 'subscribe.' + list_name + '.pending'
		#		ip = re.match(r"^.*: pending .* (\d+\.\d+\.\d+\.\d+)", line)
			
			if not list_ns in stats:
				stats[list_ns]	= 0
			
			stats[list_ns] += 1
	push_stats(stats)
			
def get_qfiles_stats():
	stats={}
	queues='archive bad bounces commands in news out retry shunt virgin'
	queues=queues.split(' ')
	for q in queues:
		stats['queue.' + q] = len(os.listdir(qpath + '/' + q))
	
	push_stats(stats)		

def push_stats(stats): 
	#accepts dicts that should look like  metrics['datapoint']['value']
	metrics = []
	ts = int(time.time())
	for k, v in stats.items():
		datapoint = namespace + '.' + k
		metrics.append(((datapoint),(ts, v)))		
	
	#print metrics
	graphite_pickle.push(metrics, graphite_host)

get_post_stats()
get_outbound_stats()
get_subscribe_stats()
get_qfiles_stats()
