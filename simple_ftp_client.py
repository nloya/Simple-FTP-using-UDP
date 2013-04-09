import sys
import threading

transmitted = -1
acked = -1

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
		host = sys.argv[1]
		port = sys.argv[2]
		filepath = sys.argv[3]
		window_size = sys.argv[4]
		mss = sys.argv[5]		
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect((host,port))
		t = myThread(s)
		t.start()
		try:
			f = open(filepath, 'r')
			msg = ""
			while True:
				c = rdt_send(f)
				if c != '':
					msg += c
				else:
					break
		except IOError as e:
			print("File Not Found or you didn't enter path in quotes or the ordering of arguments supplied is incorrect.")
	else:
		print "Provide correct number of arguments. There should be 5 arguments."

def rdt_send(f):
	return f.read(1)

main()