#!/bin/bash

# take template README
# put name of dir in CHANGEME
# cp file to dir
for d in `ls -d */`
do
	cp /home/matt/README.md .
	sed -i -e "s/CHANGEME/$d" README.md
	cp README.md $d/README.md
	rm README.md
done
