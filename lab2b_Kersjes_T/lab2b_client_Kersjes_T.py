#! /usr/bin/python

## Netwerken en Systeembeveiliging Lab 2B - Chat Room (Client)
## NAME: Tijn Kersjes
## STUDENT ID: 11048018

import socket
import select
from gui import MainWindow

def loop(HOST, PORT, CERT):

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.connect((HOST, PORT))

	buffer = []
	disconnected = False

	# The following code explains how to use the GUI.
	w = MainWindow()
	# update() returns false when the user quits or presses escape.
	while w.update():

		if disconnected:
			continue

		try:
			rready, wready, xready = select.select([server], [server], [server])

			# ready to receive
			if server in rready:
				data = server.recv(1024)
				if not data:
					server.close()
					w.writeln("<server disconnected>")
					disconnected = True
					continue

				# print message
				w.writeln(data.rstrip())

			# ready to send
			if server in wready:
				if len(buffer) > 0:
					server.sendall(buffer.pop())

			# error
			if server in xready:
				server.close()
				sys.exit(1)

			# if the user entered a line getline() returns a string.
			line = w.getline()
			if line:
				buffer.append(line)
				w.writeln("> " + line)

		# close server on SIGINT
		except (KeyboardInterrupt, SystemExit):
			print "\nDisconnecting..."
			server.close()
			print "Cheers!"
			sys.exit(0)

## Command line parser.
if __name__ == '__main__':
	import sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--ip', help='ip to connect to', default="localhost")
	p.add_argument('--port', help='port to connect to', default=12345, type=int)
	p.add_argument('--cert', help='server public cert', default='')
	args = p.parse_args(sys.argv[1:])
	loop(args.ip, args.port, args.cert)
