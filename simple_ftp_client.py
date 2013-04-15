"""
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
timeout = 2
pktlist = []
lock = threading.Lock()
start_time = ""
end_time = ""
close_conn = False

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
		global lock
		global close_conn
		global port
		#h = socket.gethostbyname(socket.gethostname())
		#s.bind((h, 50001))
		while True:
			data,addr = self.sock.recvfrom(64)
			data = data.decode('UTF-8')
			if data[0:3] == "END":
				self.sock.close()
				close_conn = True
				break
			else:
				seq_no = int(data[0:32], 2)			
				hdr = data[32:48]
				ackpkt = data[48:64]
				lock.acquire()
				if seq_no in pktlist:
					#print("Seq_No: %s" %seq_no)
					pktlist.remove(seq_no)
				lock.release()
				'''
				if ackpt != "1010101010101010":
					print("Error in the acknowledge packet")
				'''
				#acked = seq_no # update the acked field

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
		global timeout
		global pktlist
		global lock
		while True:		
			while (datetime.datetime.now() - self.datetimesent).seconds < timeout and self.seq_no in pktlist:
				pass # loop	till timeout occurs or packet is acknowledged		
			if self.seq_no in pktlist: # this means that the while loop was broken because timeout occured, resend packet
				print("Timeout, sequence number = %s" %self.seq_no)
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
	global start_time
	global end_time
	global close_conn
	
	start_time = datetime.datetime.now()
	print("My IP: %s" %socket.gethostbyname(socket.gethostname()))
	s.connect((host,port))
	#t = myThread(s)
	#t.start()
	try:
		f = open(filepath, 'r')
		msg = ""
		rdt_send(f)
	
		while threading.active_count() != 2:
			pass
		s.sendto(bytes("END","UTF-8"), (host,port))
		while close_conn != True:
			pass
		end_time = datetime.datetime.now()
		print("End of Program %s" %port)
		print("Time for data transfer: %s seconds" %(end_time-start_time).seconds)
	except IOError as e:
		print("File Not Found or you didn't enter path in quotes or the ordering of arguments supplied is incorrect.")
	#s.close()

def rdt_send(f):	
	global window_size
	global mss
	global timeout
	global s
	global host
	global port
	
	msg = ""
	flag = True
	
	c = f.read(1)
	while c != '': # EOF
		msg += c
		if(len(msg)==mss):
			while len(pktlist) == window_size:
				pass # loop till window_size is full					
			lock.acquire()
			sendtoserver(msg)
			lock.release()
			if flag:
				flag = False
				t = myThread(s)
				t.start()
			msg = ""
		c = f.read(1)
		
	if(len(msg)!=0): # if the file is read completely and the last chunk of msg is not sent as it is not 1024 then send that last chunk of msg
		while len(pktlist) == window_size:
			pass # loop till window_size is full					
		lock.acquire()
		sendtoserver(msg)
		lock.release()		
	
	# TO check whether after sending last packet, are there any more packets which have not been acknowledged yet
	while len(pktlist) != 0:
		pass

def sendtoserver(msg):
	global s
	global buffer
	global transmitted
	global host
	global port
	global pktdict
	global lock
	
	segment = ""
	transmitted += 1
	
	checksum = calculate_checksum(msg)
	
	segment += "{0:032b}".format(transmitted)
	segment += "{0:016b}".format(checksum)
	segment += '0101010101010101'
	segment += msg
	
	s.sendto(bytes(segment, 'UTF-8'), (host,port))
	#lock.acquire()
	pktlist.append(transmitted) # transmitted here is the seq_no
	#lock.release()
	p = PktSentHandler(s, datetime.datetime.now(), transmitted, segment) # transmitted here is the seq_no
	p.start()
	#buffer[transmitted % window_size] = p
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
	if mss < 0 or window_size <= 0 or port != 7735:
		print("One of mss, window_size or port value is incorrect.")
	else:
		main()
else:
	print ("Provide correct number of arguments. There should be 5 arguments, you have given %s." %len(sys.argv))