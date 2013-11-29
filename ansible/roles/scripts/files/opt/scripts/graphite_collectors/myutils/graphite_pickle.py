import commands
import pickle
import socket
import struct
import time

#metrics should look like an array of tuples = [('namespace.metric',(ts, 'datapoint')), ('namespace.metric',(ts, 'datapoint'))]
#
def push(metrics, hostname, timestamp=int(time.time()), port=2004):

	if metrics:	
		carbon_host = hostname
		carbon_port = port
		
		sock = socket.socket()
		try:
			sock.connect((carbon_host, carbon_port))
		except socket.error:	
			raise SystemExit("Couldn't connect to carbon host " +  hostname)
	
	#	metrics.append(('system_metrics.s001-okserver-org.foo', (timestamp, '13241')))
	
		payload = pickle.dumps(metrics, 1)
		size = struct.pack("!L", len(payload))
		message = size + payload
		
		sock.sendall(message)
		sock.close()
