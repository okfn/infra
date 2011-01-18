install:
	install -o root -m 444 munin.conf /etc/munin
	install -o root -m 444 munin-node.conf /etc/munin
	test -x /etc/init.d/munin-node && /etc/init.d/munin-node restart
