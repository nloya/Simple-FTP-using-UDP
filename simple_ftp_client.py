import sys
import threading
import datetime
import socket

transmitted = -1
acked = -1
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class myThread(threading.Thread):
	def __init__(self, sock):
		threading.Thread.__init__(self)
		self.sock = sock
	
	def run(self):
		global transmitted
		global acked
		global s
		#h = socket.gethostbyname(socket.gethostname())
		#s.bind((h, 50001))
		while True:
			data,addr = self.sock.recvfrom(64)
			seq_no = int(data[0:32], 2)			
			hdr = data[32:48]
			ackpkt = data[48:64]			
			acked = seq_no

class PktSentHandler(threading.Thread):
	def __init__(self, sock, datetimesent, seq_no, segment):
		threading.Thread.__init__(self)
		self.sock = sock
		self.datetimesent = datetimesent
		self.seq_no = seq_no
		self.segment = segment
	
	def run(self):
		global host
		global port
		while True:
			''' 5 being the timeout value. Wait for timeout and resend'''
			while (datetime.datetime.now() - self.datetimesent).seconds < 5 and acked < self.seq_no:
				pass # infinite loop			
			if acked < self.seq_no: # this means that the while loop was broken because timeout occured, resend packet
				self.sock.sendto(bytes(self.segment, 'UTF-8'), (host,port))
				self.datetimesent = datetime.datetime.now()
			else: # that means packet was acknowledged
				break

			
def main():
	
	global transmitted
	global acked
	global s
	global host
	global port
	global mss
	print("Host: %s" %host)
	s.connect((host,port))
	#t = myThread(s)
	#t.start()
	try:
		f = open(filepath, 'r')
		msg = ""
		rdt_send(f)
		'''
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
		'''
	except IOError as e:
		print("File Not Found or you didn't enter path in quotes or the ordering of arguments supplied is incorrect.")
	print("End of Program")

def rdt_send(f):	
	global window_size
	global mss
	msg = ""
	flag = True
	c = f.read(1)
	while c != '': # EOF
		msg += c
		if(len(msg)==mss):
			while transmitted - acked == window_size:
				pass # loop till window_size is full
			sendtoserver(msg)
			if flag:
				flag = False
				t = myThread(s)
				t.start()
			msg = ""
		c = f.read(1)
		
	if(len(msg)!=0): # if the file is read completely and the last chunk of msg is not sent as it is not 1024 then send that last chunk of msg
		sendtoserver(msg)

def sendtoserver(msg):
	global s
	global buffer
	global transmitted
	global host
	global port
	
	segment = ""
	transmitted += 1
	buffer[transmitted % window_size] = msg
	checksum = 0
	segment += "{0:032b}".format(transmitted)
	segment += "{0:016b}".format(checksum)
	segment += '0101010101010101'
	segment += msg
	print (segment)
	s.sendto(bytes(segment, 'UTF-8'), (host,port))
	p = PktSentHandler(s, datetime.datetime.now(), transmitted, segment)
	p.start()

# THESE LINES WOULD BE EXECUTED FIRST	
if len(sys.argv) == 6:
	host = sys.argv[1]
	port = int(sys.argv[2])
	filepath = sys.argv[3]
	window_size = int(sys.argv[4])
	mss = int(sys.argv[5])
	buffer = window_size*[None] # initialize buffer with size as window_size
	main()
else:
	print ("Provide correct number of arguments. There should be 5 arguments, you have given %s." %len(sys.argv))	
