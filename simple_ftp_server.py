"""
Simple_ftp_server port# file-name p
"""
import sys
import threading
import datetime
import socket
import random

pktdict = {}

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

def copydatatofile():
	global filename
	global pktdict
	try:
		f = open(filename, 'w')		
		for i in sorted(pktdict):
			f.write(pktdict[i])
		f.close()
	except IOError as e:
		print("File Not Found or you didn't enter correct path.")

def main():
	global filename
	global received
	global p
	global port
	global pktdict
	skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	host = socket.gethostbyname(socket.gethostname())
	
	print("Host: %s" %host)
	skt.bind((host, port))
	#skt.listen(5)
	#client,addr = skt.accept()
	#try:
	#	f = open(filename, 'w')		
	#except IOError as e:
	#	print("File Not Found or you didn't enter correct path.")	
		
	while True:		
		data, address = skt.recvfrom(1088)		
		data = data.decode('UTF-8')
		if data[0:3] == "END":
			skt.sendto(bytes("END", "UTF-8"), address)
			skt.close()
			copydatatofile()
			break
		else:
			seq_no = int(data[0:32], 2)
			checksum_incoming_pkt = int(data[32:48],2)
			hdr = data[48:64]
			segment = data[64:]		
			checksum_value = calculate_checksum(segment)
			#print("Checksum for %s is: %s (%s)" %(str(seq_no), str(checksum_value), data[64:]))					
			
			r = random.random()
			# if the packets arrive out of order no need to do anything
			if seq_no not in pktdict:
				if (r > p) and (checksum_incoming_pkt == checksum_value) and (hdr == '0101010101010101'):
					pktdict[seq_no] = segment
					print("Packet received, sequence number = %s" %str(seq_no))
					#f = open(filename, 'a')				
					received += 1
					#f.write(segment)		
					'''this would work as this is the value that is being sent anyways. it should be received field value. data[0:32]'''
					segment = data[0:32]
					segment += "{0:016b}".format(0)
					segment += "1010101010101010"				
					skt.sendto(bytes(segment, "UTF-8"), address)
					#f.close()
				elif r<=p:
					print("Packet loss, sequence number = %s" %str(seq_no))
				elif checksum_incoming_pkt != checksum_value:
					print("Checksum for sequence number: %s is incorrect" %str(seq_no))
				else:
					print("Value should be: 0101010101010101 but found something else")
		

if len(sys.argv) == 4:
	received = -1
	port = int(sys.argv[1])
	filename = sys.argv[2]
	p = float(sys.argv[3])
	if p>0 and p<1 and port==7735:
		main()
	elif port!=7735:
		print("Value of port should be 7735")
	else:
		print("Value of p should be between 0 and 1, excluding 0 and 1.")
	print ("End of Program %s" %port)
else:
	print("There should be 3 command-line arguments only.")

