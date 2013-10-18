all: hosts.ansible.diff hosts.trello.diff

hosts.%.diff: hosts.% hosts.combined
	diff -u hosts.combined $< > $@ || true

hosts.combined: hosts.ansible hosts.trello
	cat hosts.ansible hosts.trello | sort | uniq > $@

hosts.ansible: ../inventory/hosts inventory.awk
	< $< awk -f inventory.awk | sort | uniq | sed -e '/localhost/d' > $@

hosts.trello: hosts.trello.src
	< $< cut -d' ' -f1 | sed -e 's/_/./g' -e '/localhost/d'| sort | uniq > $@

clean:
	rm -f hosts.ansible hosts.trello hosts.combined hosts.*.diff
	rm -f *~
