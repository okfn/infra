#!/usr/bin/python2.7
import smtplib
import logging
import gspread
import pickle
import os
import shutil

from time import time
from subprocess import call
from email.mime.text import MIMEText
from lepl.apps.rfc3696 import Email
email_valid = Email()

# this script attempts to clump together mail aliases/forwards specified in multiple spreadsheets.
# The objective is to hand the ability to make mail forwards/alias changes to project owners/heads of units.
# it does a bunch of sanity checks on the email addresses and writes them out to the forwards_main_file.

import configparser

config = configparser.RawConfigParser()
config.read('/opt/scripts/config/config.ini')
g_doc_keys=config.get('google', 'mail_aliases_doc') # returns an unicode of doc keys
g_doc_keys=eval(g_doc_keys)
g_user=config.get('google', 'user')
g_password=config.get('google','pass')

logging.basicConfig(filename='/tmp/mail_forward.log',
					format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M', level=logging.INFO)

#forwards_file = '/etc/mailconfig/mail_domains.forward'
ts = str(int(time()))

logging.info('Script started: ' + ts)

forwards_main_file    = '/etc/mailconfig/mail_domains.forward'
forwards_backup_file  = '/home/okfn/mail_forwards_backup/mail_domains.forward.' + ts
forwards_temp_file    = '/var/tmp/mail_domains.forward.tmp.' + ts
forwards_fail_file    = '/home/okfn/mail_forwards_backup/mail_domains.forward.FAIL' + ts


min_size 	  = 100 # min size of the mail_forwards file, for sanity check 
current_aliases = {}
new_aliases     = {}
stats  = { 'added' : {}, 'deleted' : {} , 'invalid' : {} }
doc_key = { 'okfn_org': g_doc_keys[1], 
  	    'okfestival_org': g_doc_keys[2], 
	    'okfn_at': g_doc_keys[3], 
	    'okfn_be': g_doc_keys[4],
            'okfn_de': g_doc_keys[0]
	  } 

user=g_user
password=g_password
devnull = open(os.devnull, 'w')


def notify(subject, message):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = 'mail_forward_merge@s001.okserver.org'
	msg['To'] = 'sysadmin@okfn.org'
	
	s = smtplib.SMTP('localhost')
	s.sendmail(msg['From'], msg['To'], msg.as_string())

def compare(new, current):
	aliases_added = set(new.keys()) - set(current.keys())
	aliases_deleted = set(current.keys()) - set(new.keys())
	
#	print 'Added -> '
#	print aliases_added
#	print '=X='
#	
#	print 'Deleted -> '
#	print aliases_deleted
#	print '=X='


	#if its a new alias, add it to stats{} and update it with all the forwards

	if len(aliases_added):
		for alias in aliases_added:
			stats['added'][alias] = []
			for forward in new_aliases[alias]:
				stats['added'][alias].append(forward)
#		print 'Added -> '
#		print stats
#		print '=X='
	#if its a deleted alias, add it to stats{} and update stats with all the deleted forwards
	if len(aliases_deleted):
		for alias in aliases_deleted:
			stats['deleted'][alias] = []
			for forward in current_aliases[alias]:
				stats['deleted'][alias].append(forward)
#		print 'Deleted -> '
#		print stats
#		print '=X='
#	return stats
	
	#if its an existing alias, we compare and update forwards with additions	
	#print new.keys()
	for alias in new.keys():
		if alias in current.keys():
			forwards_deleted = set(current[alias]) - set(new[alias])
			forwards_added = set(new[alias]) - set(current[alias])

#			logging.info('Added -> ')
#			logging.info(str(forwards_added))
#			logging.info('=X=')
##	
#			logging.info('Deleted -> ')
#			logging.info(str(forwards_deleted))
#			logging.info('=X=')

			#check for forwards added
			if len(forwards_added):
				stats['added'][alias] = []
				for forward in forwards_added:
					stats['added'][alias].append(forward)
			
			#check for forwards deleted
			if len(forwards_deleted):
				stats['deleted'][alias] = []
				for forward in forwards_deleted:
					stats['deleted'][alias].append(forward)
	return stats				

def verify_clean(aliases):

	for alias in aliases:
		if type(alias) == str: # we dont care about anything else 
			forwards = aliases[alias].split(',')
			alias = alias.strip()
			alias = alias.lower()
	
			if len(forwards):
				idx =  len(forwards)-1
				while idx >= 0:
					forwards[idx] = forwards[idx].strip()
					forwards[idx] = forwards[idx].lower()
					if len(forwards[idx]):
						if not email_valid(forwards[idx]):
							stats['invalid'][alias] = []
							stats['invalid'][alias].append(forwards[idx])
							del(forwards[idx])
					else:#don't try to append an alias that maybe empty		
							del(forwards[idx])
					idx -= 1
				new_aliases[alias] = forwards
			else:
				msg = 'no forwards found for -> ' + alias + ' script exit.'
				logging.error(msg)
				notify('Script error.', msg)
				exit(1)
		else:
			continue
	return new_aliases


#read in the local mail_forwards file
try:
	f = open(forwards_main_file, "r+")
	for line in f:
		line = line.strip()
		(alias, forwards) =  line.split(':')
		alias = alias.strip()
		alias = alias.lower()
		email_addrs = forwards.split(',')
		idx = len(email_addrs)-1
		while idx >= 0:
			email_addrs[idx] = email_addrs[idx].strip()
			email_addrs[idx] = email_addrs[idx].lower()
			idx -= 1 

		current_aliases[alias] = email_addrs
except:
	msg = 'Failed to open ' + forwards_main_file
	logging.error(msg)
	notify('Script error.', msg)
	exit(1)


try:
	g = gspread.login(user, password)
except:
	msg = 'Authentication failure.'
	logging.error(msg)
	notify('Script error.', msg)
	exit(1)

#merge forwards data from each of the docs
for domain in doc_key: 
	try:
		doc   = g.open_by_key(doc_key[domain])
		sheet = doc.get_worksheet(0)
	except:
		msg = 'Failed to open: ' + doc_key[domain] + ' for ' + domain \
			   + ', forwards for ' + domain + ' may not be included, exited. '	
		logging.error(msg)
		notify('Script error.', msg)
		exit(1)
	#grab aliases from the spreadsheet
	aliases = dict(zip(sheet.col_values(1), sheet.col_values(2)))
	if len(aliases):
#	   	pickle.dump(aliases, open(doc_key[domain] + '_aliases.pickle', "wb"))
		aliases = verify_clean(aliases)
	else:
		msg = 'No aliases were found in ' + doc_key[domain] + ' for ' + domain \
			   + ', forwards for ' + domain + ' may not be included, exited.'
		logging.error(msg)
		notify('Script error.', msg)
		exit(1)
#for domain in doc_key:
#	aliases = pickle.load(open(doc_key[domain] + '_aliases.pickle', "r+"))
#	new_aliases = verify_clean(aliases)

#current_aliases = pickle.load(open('current_aliases.pickle', "r+"))
#new_aliases     = pickle.load(open('new_aliases.pickle', "r+"))

#pickle.dump(new_aliases, open('new_aliases.pickle', "wb"))
#pickle.dump(current_aliases, open('current_aliases.pickle', "wb"))


stats = compare(new_aliases, current_aliases)
if len(stats['added']) or len(stats['deleted']):
	
	logging.info('Changes present in spreadsheets, merging into forwards file.')
	logging.info(str(stats))

	try:
		f = open(forwards_temp_file, 'w+')
		for alias in new_aliases.keys():
			try:
				f.write(alias + ': ' + ", ".join([e for e in new_aliases[alias]]) + "\n" )
			except:
				msg = 'Could not write to file - ' + forwards_temp_file
				logging.error(msg)
				notify('Script error', msg)
				exit(1)
	except IOError:
		msg = 'Could not open ' +  forwards_temp_file + 'for writing, script exit.'
		logging.error(msg)
		notify('Script error', msg)
		exit(1)
	finally:
		f.flush()
		logging.info('Done writing to ' + forwards_temp_file + ' , closing file.' )
		f.close()
	
	
	if os.path.getsize(forwards_temp_file) > 100:
		#take a backup..
		shutil.copy(forwards_main_file, forwards_backup_file)
		t_size = int(os.path.getsize(forwards_temp_file))
				
		shutil.copy(forwards_temp_file, forwards_main_file)
		m_size = int(os.path.getsize(forwards_main_file))

		logging.info( forwards_temp_file + 'size in bytes: ' + str(t_size) )
		logging.info( forwards_main_file + 'size in bytes: ' + str(m_size) )

		if m_size != t_size:
			logging.error('file sizes differ, file not copied correctly!')
			shutil.copy(forwards_backup_file, forwards_main_file)
			logging.error('reverted to older config')
			exit(1)
		
		#sudo /usr/sbin/exim4 -d -bt tryggvi.bjorgvinsson@okfn.org &>/dev/null
#		test_addr = new_aliases.popitem()[0]
#		
#
#		cmd = ['sudo', '/usr/sbin/exim4', '-d', '-bt', test_addr]
#		logging.info('running command - ' + str(cmd))
#		e = call(cmd, stdout=devnull, stderr=devnull)				
#		
#		#e = 0
#		if e != 0:
#			#revert to previous config
#			shutil.copy(forwards_main_file, forwards_fail_file )
#			shutil.copy(forwards_backup_file, forwards_main_file)
#			msg = 'Alias test failed, reverting config, exit code: ' + str(e)
#			logging.error(msg)
#			notify('Script error.', msg)
#		else:
#			logging.info('Forwards file merged succesfully!')
#			notify('Changes to mail forwards applied.', str(stats))
#			exit(0)
else:
	logging.info('No changes to merge.')
	exit(0)
