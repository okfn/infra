import os

#read lines from a file from the bottom up, 
#to basically prevent polluting the system cache, when dealing with large log files
#spits out an iterable list of lines

#e.g
#for line in reverse_tail.run(logfile):
#	do stuff.

def __split_chunk(chunk, delimiter, is_lastchunk, str_half):
	lines = chunk.split(delimiter)
	lines.reverse()
	
	if not str_half:
		str_half = lines.pop()
	else:
		lines[0] = lines[0] + str_half
		str_half = lines.pop()
	if is_lastchunk:
		lines.append(str_half)
	
	return [lines, str_half]

def run(logfile, chunk_size=1000, delimiter='\n'):

	str_half=''
	fsize = os.path.getsize(logfile)
	f = open(logfile);
	lines =[]
	is_lastchunk = 0

	if fsize > chunk_size:
		seek_pos = fsize-chunk_size
	else:
		seek_pos = 0 #file is smaller than chunk size, hence lets just read the entire thing.
		chunk_size=fsize
		is_lastchunk = 1
	
	while 1:
		f.seek(seek_pos)
		if seek_pos < chunk_size:
			chunk_size = seek_pos+chunk_size
			seek_pos = 0
			f.seek(seek_pos)
			is_lastchunk = 1
		else:	
			seek_pos = seek_pos-chunk_size
		
		lines = f.read(chunk_size)
		(lines, str_half) = __split_chunk(lines, delimiter, is_lastchunk, str_half)
		for line in lines:
			yield line

		if seek_pos <= 0:
			break
