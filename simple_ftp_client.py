"""
Go-BACK-N
Simple_ftp_client server-host-name server-port# file-name N MSS 
"""

import sys
import threading
import datetime
import socket
import time

transmitted = -1
acked = -1
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
timeout = 0.3

# REFERENCE: http://codewiki.wikispaces.com/ip_checksum.py
def calculate_checksum(data):  # Form the standard IP-suite checksum
  pos = len(data)
  if (pos & 1):  # If odd...
    pos -= 1
    sum = ord(data[pos])  # Prime the sum with the odd end byte
  else:
    sum = 0
 
  #Main code: loop to calculate the checksum
  while pos > 0:
    pos -= 2
    sum += (ord(data[pos + 1]) << 8) + ord(data[pos])
 
  sum = (sum >> 16) + (sum & 0xffff)
  sum += (sum >> 16)
 
  result = (~ sum) & 0xffff #Keep lower 16 bits
  result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
  return result

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
		lock = threading.Lock()
		while True:
			data,addr = self.sock.recvfrom(64)
			lock.acquire()
			seq_no = int(data[0:32], 2)			
			hdr = data[32:48]
			ackpkt = data[48:64]	
			'''
			if ackpt != "1010101010101010":
				print("Error in the acknowledge packet")
			'''
			acked = seq_no # update the acked field
			lock.release()

class PktSentHandler():
	def __init__(self, datetimesent, seq_no, segment):
		threading.Thread.__init__(self)
		#self.sock = sock
		self.datetimesent = datetimesent
		self.seq_no = seq_no
		self.segment = segment
	"""
	def run(self):
		print("YOU CANT BE HERE")
		global host
		global port
		global timeout
		while True:
			''' 5 being the timeout value. Wait for timeout and resend'''
			while (time.time() - self.datetimesent) < timeout and acked < self.seq_no:
				pass # loop	till timeout occurs or packet is acknowledged		
			if acked < self.seq_no: # this means that the while loop was broken because timeout occured, resend packet
				print("Timeout1, sequence number = %s" %self.seq_no)
				self.sock.sendto(bytes(self.segment, 'UTF-8'), (host,port))
				self.datetimesent = time.time()
			else: # that means packet was acknowledged
				break
	"""
			
def main():
	
	global transmitted
	global acked
	global s
	global host
	global port
	global mss
	print("My IP: %s" %socket.gethostbyname(socket.gethostname()))
	s.connect((host,port))
	
	start_time = time.time()
	#t = myThread(s)
	#t.start()
	try:
		f = open(filepath, 'r')
		msg = ""
		rdt_send(f)	
		
		while threading.active_count() != 2:
			pass
		print("End of Program %s" %port)
		end_time = time.time()
		print("Delay: %s seconds" %(end_time-start_time))
	#s.close()
	except IOError as e:
		print("File Not Found or you didn't enter path in quotes or the ordering of arguments supplied is incorrect.")

def rdt_send(f):	
	global window_size
	global mss
	global timeout
	global s
	global host
	global port
	lock = threading.Lock() 
	msg = ""
	flag = True
	c = f.read(1)
	while c != '': # EOF
		msg += c
		if(len(msg)==mss):
			while transmitted - acked == window_size:
				#pass # loop till window_size is full
				#lock.acquire()
				if (time.time() - buffer[(acked+1)%window_size].datetimesent) > timeout:
					print("Timeout, sequence number = %s" %(buffer[(acked+1)%window_size].seq_no))					
					tmpacked = acked # So that even if the other thread changes no effect happens in this case
					for i in range(0,window_size):						
						s.sendto(bytes(buffer[(tmpacked+1+i)%window_size].segment,'UTF-8'), (host,port))
						buffer[(tmpacked+1+i)%window_size].datetimesent = time.time()				
				#lock.release()
			sendtoserver(msg)
			if flag:
				flag = False
				t = myThread(s)
				t.start()
			msg = ""
		c = f.read(1)
		
	if(len(msg)!=0): # if the file is read completely and the last chunk of msg is not sent as it is not 1024 then send that last chunk of msg
		while transmitted - acked == window_size:			
			if (time.time() - buffer[(acked+1)%window_size].datetimesent) > timeout:				
				print("Timeout, sequence number = %s" %buffer[(acked+1)%window_size].seq_no)
				tmpacked = acked # So that even if the other thread changes no effect happens in this case
				for i in range(0,window_size):					
					s.sendto(bytes(buffer[(tmpacked+1+i)%window_size].segment,'UTF-8'), (host,port))
					buffer[(tmpacked+1+i)%window_size].datetimesent = time.time()
		sendtoserver(msg)
	
	while acked != transmitted:
		if (time.time() - buffer[(acked+1)%window_size].datetimesent) > timeout:
			print("Timeout, sequence number = %s" %buffer[(acked+1)%window_size].seq_no)
			tmpacked = acked # So that even if the other thread changes no effect happens in this case
			for i in range(0,window_size):			
				s.sendto(bytes(buffer[(tmpacked+1+i)%window_size].segment,'UTF-8'), (host,port))
				buffer[(tmpacked+1+i)%window_size].datetimesent = time.time()

def sendtoserver(msg):
	global s
	global buffer
	global transmitted
	global host
	global port
	
	segment = ""
	transmitted += 1
	
	checksum = calculate_checksum(msg)
	
	segment += "{0:032b}".format(transmitted)
	segment += "{0:016b}".format(checksum)
	segment += '0101010101010101'
	segment += msg
	
	s.sendto(bytes(segment, 'UTF-8'), (host,port))
	
	p = PktSentHandler(time.time(), transmitted, segment) # transmitted here is the seq_no
	buffer[transmitted % window_size] = p
	
	#p.start()
	#p.join()
	#p.exit()

# THESE LINES WOULD BE EXECUTED FIRST	
if len(sys.argv) == 6:
	host = sys.argv[1]
	port = int(sys.argv[2])
	filepath = sys.argv[3]
	window_size = int(sys.argv[4])
	mss = int(sys.argv[5])
	buffer = window_size*[None] # initialize buffer with size as window_size
	if mss < 0 or window_size <= 0:
		print("One of mss, window_size is incorrect.")
	else:
		main()
else:
	print ("Provide correct number of arguments. There should be 5 arguments, you have given %s." %len(sys.argv))