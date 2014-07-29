#!/usr/bin/env python

#Post Count by List
#Post Count by Sender
#weekly summary of postcount

import re
import os
import time
import tempfile
import smtplib
from email.mime.text import MIMEText


moderation_dir = '/var/lib/mailman/data'
spam_dir = '/var/lib/mailman/spam'
log_dir  = '/var/log/mailman/'

postlog  = 'post'
errorlog = 'error'
spamlog  = 'vette'

time_period = 7 #collect stats for last x days

time_now = int(time.time())

def mail(log):
	from_ = 'mailman_weekly_stats@lists.okfn.org'
	to = ['joel.rebello@okfn.org','neal.bastek@okfn.org']

	f = open(log, 'rb')
	msg = MIMEText(f.read())
	f.close
	
	msg['Subject'] =  "Mailman weekly stats for last 7 days"
	msg['from'] = from_
	msg['To'] = to[1]

	s = smtplib.SMTP('localhost')
	s.sendmail(from_, to, msg.as_string())
	s.quit()

def collect_postlog_stats():
 #unique posters count
 #top poster
 #total posts in the week
	
	print >>f, "List Post stats for last 7 days\n"
	print >>f, "===============================\n"

	stats={}
	days=[]
	l = open(log_dir + postlog)
	for line in l.readlines():
		if not line:
			continue
	
		s = re.match(r"^(?P<day>\w+ \d+) \d+:\d+:\d+ (?P<year>\d+) .*post to (?P<list_name>.*) from (?P<poster>.*@*.), size=(?P<msg_size>\d+), message-id.*, (?P<result>.*)$", line)
		
		day = s.group('day')
		day = re.sub(r'\s+', '_', day)
	
		year = s.group('year')
		list_name = s.group('list_name')
		poster = s.group('poster')
		msg_size = s.group('msg_size')
		result = s.group('result')
	
		if day not in stats:
			stats[day] = {}
			stats[day]['total_posts'] = 0
			days.append(day)
	
		if list_name not in stats[day]:	
			stats[day][list_name] = {}
			stats[day][list_name]['post_count'] = 0
			stats[day][list_name]['sender_stats'] = {}
			
		if poster not in stats[day][list_name]['sender_stats']:	
			stats[day][list_name]['sender_stats'][poster] = {}
			stats[day][list_name]['sender_stats'][poster]['post_count'] = 0
		
		stats[day]['total_posts'] += 1
		stats[day][list_name]['post_count'] += 1
		stats[day][list_name]['sender_stats'][poster]['post_count'] += 1
	
	
	for day in days[-7:]:
		d = re.sub(r'_', ' ', day)
		print >>f, "%s: %d total posts" % (d, stats[day]['total_posts']) 
		print >>f, '------------------'
	
		uniq_posters = []
		top_poster = ('',0)
		for list_n in stats[day]:
			if list_n == 'total_posts':
				continue
	
			print >>f, "%s  %d" % (list_n, stats[day][list_n]['post_count'])
	
			for poster in stats[day][list_n]['sender_stats']:
				if poster not in uniq_posters:
					uniq_posters.append(poster)
					
				if stats[day][list_n]['sender_stats'][poster]['post_count'] > top_poster[1]:
					top_poster = (poster, stats[day][list_n]['sender_stats'][poster]['post_count'])
	
		print >>f, "\nTop Poster: %s %d posts" % (top_poster[0], top_poster[1])		
		print >>f, '\nUnique posters: %d' % len(uniq_posters)
		print >>f, 'xxxxxxxxxxxxxxxxxxxx\n\n'


def collect_modq_stats(): 
	print >>f, "Moderation queue stats (only lists with greater than 5 posts in queue)"
	print >>f, "======================"
	
	stats = {}
	pcks = os.listdir(moderation_dir)
	for msg in pcks:
		msg = re.sub(r'(heldmsg-|-[0-9]*.pck)', '', msg)
		if msg not in stats:
			stats[msg] = {}
			stats[msg] = 0
	
		stats[msg] += 1
	
	lists = sorted(stats.items(), key=lambda x: x[1], reverse=True)
	for t in lists:
		if t[1] >= 5:
			print >>f, t[0] + ' - ' + str(t[1])



tmp = tempfile.mkstemp()
f = open(tmp[1], 'w+')

collect_postlog_stats()
collect_modq_stats()

f.write('\n\n\n\nStats collected: ' + time.strftime('%d %b %X',time.localtime()))

f.close()
mail(tmp[1])
os.remove(tmp[1])
