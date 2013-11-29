#!/bin/sh

./xvinabot.awk | uniq | while read host; do
	whois $host | ./whois2ban.awk -v host=$host
done
