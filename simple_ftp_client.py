import sys
import threading

transmitted = -1
acked = -1
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class myThread(threading.thread):
	def __init__(self, sock):
		threading.Thread.__init__(self)
		self.sock = sock
	
	def run(self):
		global transmitted
		global acked
		while True:
			self.sock.recv(1024)
			
def main():
	if len(sys.argv) == 6:
		global transmitted
		global acked
		global s
		global host
		global port
		global mss
		s.connect((host,port))
		t = myThread(s)
		t.start()
		try:
			f = open(filepath, 'r')
			msg = ""
			while True:
				rdt_send(f)
				#c = rdt_send(f)
				if c != '':
					msg += c
					if(len(msg) == mss):
						prepare segment
						s.send(msg)
						msg = ""
				else:
					break
		except IOError as e:
			print("File Not Found or you didn't enter path in quotes or the ordering of arguments supplied is incorrect.")
	else:
		print "Provide correct number of arguments. There should be 5 arguments."

def rdt_send(f):	
	global window_size
	global mss
	msg = ""
	c = f.read(1)
	while c != '':
		msg += c
		if(len(msg)==mss):
			while transmitted - acked == window_size:
				# loop till window_size is full
			
			sendtoserver(msg)
			msg = ""
		c = f.read(1)
		
	if(len(msg)!=0): # if the file is read completely and the last chunk of msg is not sent as it is not 1024 then send that last chunk of msg
		sendtoserver(msg)

def sendtoserver(msg):
	global s
	global buffer
	global transmitted
	
	segment = ""
	transmitted += 1
	buffer[transmitted % window_size] = msg
	checksum = ""
	segment += "{0:032b}".format(transmitted)
	segment += "{0:016b}".format(checksum)
	segment += '0101010101010101'
	s.send(segment)
	
		
host = sys.argv[1]
port = sys.argv[2]
filepath = sys.argv[3]
window_size = sys.argv[4]
mss = sys.argv[5]
buffer = window_size*[None] # initialize buffer with size as window_size
main()