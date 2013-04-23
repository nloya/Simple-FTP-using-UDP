"""
Selective Repeat
Simple_ftp_client server-host-name server-port# file-name N MSS 
simple_ftp_client.py 152.14.245.180 7737 test_input.txt 1 500
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
pktlist = []
segmentdict = {}
lock = threading.Lock()

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
		#h = socket.gethostbyname(socket.gethostname())
		#s.bind((h, 50001))
		#lock = threading.Lock()
		while True:
			data,addr = self.sock.recvfrom(64)
			data = data.decode('UTF-8')
			if data[0:3] == "END":
				self.sock.close()		
				break
			else:
				seq_no = int(data[0:32], 2)			
				hdr = data[32:48]
				ackpkt = data[48:64]	
				'''
				if ackpt != "1010101010101010":
					print("Error in the acknowledge packet")
				'''
				lock.acquire()
				acked = seq_no # update the acked field
				
				for i in range(0, len(pktlist)):
					if pktlist[i].seq_no == seq_no:
						pktlist.remove(pktlist[i])
						break
				
				lock.release()

class PktSentHandler():
	def __init__(self, time, seq_no, segment):
		threading.Thread.__init__(self)
		#self.sock = sock
		self.time = time
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
		s.sendto(bytes("END", 'UTF-8'), (host,port))
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
			while len(pktlist) == window_size:
				checkfortimeout()				
				#lock.release()
			sendtoserver(msg)
			if flag:
				flag = False
				t = myThread(s)
				t.start()
			msg = ""
		c = f.read(1)
	#print("LAST SEGMENT STARTS")	
	if(len(msg)!=0): # if the file is read completely and the last chunk of msg is not sent as it is not 1024 then send that last chunk of msg
		while len(pktlist) == window_size:			
			checkfortimeout()
		sendtoserver(msg)
	
	while acked != transmitted:
		checkfortimeout()

def checkfortimeout():
	global pktlist
	global timeout
	global acked
	global window_size
	global s, host, port
	global lock
	#print("pktlist: %s" %len(pktlist))
	lock.acquire()
	if len(pktlist)!= 0 and ((time.time() - pktlist[0].time) > timeout):
		
		#print("Timeout, sequence number = %s" %(pktlist[0].seq_no))
		print("Timeout, sequence number = %s" %(pktlist[0].seq_no))
		s.sendto(bytes(pktlist[0].segment,'UTF-8'), (host,port))
		pktlist[0].time = time.time()
		lock.release()
		lock.acquire()
		#print("Pktlist: %s %s" %(len(pktlist), pktlist))
		for i in range(1,len(pktlist)):
			#print("Starts I: %s" %i)
			if pktlist[i].time < timeout:
				pass #break
			else:
				print("Timeout, sequence number = %s" %(pktlist[i].seq_no))
				s.sendto(bytes(pktlist[i].segment,'UTF-8'), (host,port))
				pktlist[i].time = time.time()
			#print("Ends I: %s" %i)
		lock.release()
	if lock.locked():
		lock.release()

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
	pktlist.append(p)
	#print("Packet added. Length of pktlist = %s" %len(pktlist))
	#segmentdict[transmitted] = segment
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