Try to figure out the canonical list of hosts.

Start with the list in the ansible inventory, and the list in the
trello ticket. Clean them up, sort them and run diff.

       make clean all

will produce hosts.ansible.diff and hosts.trello.diff which represent
the difference between those individual host lists and the combined
one.
