import sys
import threading
import datetime
import socket

def main():
	global filename
	global received
	skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	host = socket.gethostbyname(socket.gethostname())
	port = 7735
	print("Host: %s" %host)
	skt.bind((host, port))
	#skt.listen(5)
	#client,addr = skt.accept()
	try:
		f = open(filename, 'wb')		
	except IOError as e:
		print("File Not Found or you didn't enter correct path.")	
		
	while True:		
		data, address = skt.recvfrom(1088)		
		seq_no = int(data[0:32], 2)
		checksum = data[32:48]
		hdr = data[48:64]
		segment = data[64:]
		if seq_no - received == 1:
			f = open(filename, 'ab')
			print(segment)
			print("Here")
			print(str(segment))
			received += 1
			f.write(segment)
			'''this would work as this is the value that is being sent anyways. it should be received field value. data[0:32]'''
			segment = data[0:32] 
			segment += bytes("{0:016b}".format(0),'UTF-8')
			segment += bytes("1010101010101010", 'UTF-8')
			#print segment
			skt.sendto(segment, address)
			f.close()
		

if len(sys.argv) == 4:
	received = -1
	port = sys.argv[1]
	filename = sys.argv[2]
	p = sys.argv[3]
	main()
	print ("End of Program")
else:
	print("There should be 3 command-line arguments only.")
