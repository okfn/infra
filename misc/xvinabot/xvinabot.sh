#!/bin/sh

awk -f xvinabot.awk | uniq | while read host; do
	whois $host | awk -f whois2ban.awk -v host=$host
done
