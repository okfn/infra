install:
	squid3 -k parse -f squid.conf
	install  -o root -m 444 squid.conf /etc/squid3
	/etc/init.d/squid3 reload
