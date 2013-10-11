#!/usr/bin/python2.7
import re
import time
from myutils import graphite_pickle
from myutils import reverse_tail

logpath='/var/log/nginx/'
namespace='application_metrics.nginx'
graphite_host='ansible-dev.okserver.org'
domains = ['openspending.org', 'openspending.org-ssl']



def get_accesslog_stats(domain):
	logfile = logpath + domain + '-access.log'
	stats={}
	stats['requests.total'] = 0
	stats['bytes_sent'] = 0
	stats['requests.api'] = 0
	stats['api_bytes_sent'] = 0
	time_now = int(time.time())
	five_mins_ago = time_now-300

	for line in reverse_tail.run(logfile):
		if not line:
			continue
		s = re.match(r"^(?P<ip>\d+\.\d+\.\d+\.\d+|^.*).*\[(?P<ts>.*) .*\] \"(?P<request>.*)\" (?P<http_status>\d+) (?P<bytes>\d+)", line)
		ip = s.group('ip')
		ts = s.group('ts')
		request = s.group('request') # get + uri 
		http_status = s.group('http_status')
		content_size = s.group('bytes')
		#11/Oct/2013:02:26:37
		ts = int(time.mktime(time.strptime(ts,'%d/%b/%Y:%H:%M:%S')))	
		if ts < five_mins_ago:
#			print line
			break
		else:
#			print line
			stats['requests.total'] += 1
			stats['bytes_sent'] += int(content_size)
			
			if request == '-': #request is empty
				continue
			else:
				uri = request.split(' ')[1]

			if re.match(r"\/api\/", uri):
				stats['requests.api'] += 1
				stats['api_bytes_sent'] += int(content_size)

	push_stats(stats, domain)	

def get_errorlog_stats(domain):
	logfile = logpath + domain + '-error.log'
	stats={}
	stats['errors']	= 0
	stats['warnings'] = 0
	time_now = int(time.time())
	five_mins_ago = time_now-300
	
	for line in reverse_tail.run(logfile):
		if not line:
			continue
		#2013/10/11 06:03:28	
		s = re.match(r"^(?P<date>.*) (?P<time>\d+:\d+:\d+)", line)
		ts = s.group('date') + s.group('time')
		ts = int(time.mktime(time.strptime(ts, '%Y/%m/%d%H:%M:%S')))
		if ts < five_mins_ago:
			break
		else:
			if '[warn]' in line:
				stats['warnings'] += 1
			if '[error]' in line:
				stats['errors'] += 1
	
	push_stats(stats, domain)


def push_stats(stats, domain): 
	#accepts dicts that should look like  metrics['datapoint']['value']
	domain = re.sub('\.', '-', domain)
	metrics = []
	ts = int(time.time())
	for k, v in stats.items():
		datapoint = namespace + '.' +  domain + '.' + k 
		metrics.append(((datapoint),(ts, v)))		
	
	#print metrics
	graphite_pickle.push(metrics, graphite_host)

for domain in domains:
	get_accesslog_stats(domain)
	get_errorlog_stats(domain)
