HOSTS=`< ../../inventory/hosts awk -f ../host-reconcile/inventory.awk | sort | uniq | sed /localhost/d | sed /ansible-dev/d`
SSH=ssh -o PasswordAuthentication=no

all: mreport.txt
	@cat $<

mreport.txt: memstats.dsv procstats.dsv hostgroups
	join -t: procstats.dsv memstats.dsv > stats.tmp
	join -t: stats.tmp hostgroups | awk -F: -f mreport.awk > $@

clean:
	rm -f memstats.dsv procstats.dsv
	rm -f *~

memstats.dsv:
	for host in ${HOSTS}; do \
		echo $$host 2>&1; \
		${SSH} $$host cat /proc/meminfo | \
		awk -v host=$$host -f memsum.awk >> $@; \
	done || true

procstats.dsv:
	for host in ${HOSTS}; do \
		echo $$host 2>&1; \
		${SSH} $$host ps auxw | sed '/^USER/d' | \
		awk -v host=$$host -f procsum.awk >> $@ || true; \
	done

hostgroups:
	< ../../inventory/hosts awk -f ../host-reconcile/hostgroup.awk | sort > $@
