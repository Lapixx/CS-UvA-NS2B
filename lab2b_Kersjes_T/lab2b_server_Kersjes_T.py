#! /usr/bin/python

## Netwerken en Systeembeveiliging Lab 2B - Chat Room (Server)
## NAME: Tijn Kersjes
## STUDENT ID: 11048018

import socket
import select

class Client:

	def __init__(self, sock):
		self.sock = sock
		self.nickname = "Anon"
		self.buffer = []

	def receive(self, num=1024):
		 return self.sock.recv(num)

	def close(self):
		return self.sock.close()

	def send(self, data):
		self.buffer.append(data)

	def flush(self):
		if len(self.buffer) > 0:
			self.sock.sendall(self.buffer.pop() + "\n")

class ClientList:
	def __init__(self):
		self.clients = {}

	def add(self, client):
		self.clients[client.sock] = client

	def remove(self, client):
		del self.clients[client.sock]

	def has(self, client):
		return client.sock in self.clients

	def hasSocket(self, sock):
		return sock in self.clients

	def get(self, sock):
		return self.clients[sock]

	def getSockets(self):
		client_sockets = []
		for sock in self.clients:
			client_sockets.append(sock)
		return client_sockets

	def getOthers(self, me):
		others = []
		for sock in self.clients:
			if self.clients[sock] != me:
				others.append(self.clients[sock])
		return others

	def closeAll(self):
		for sock in self.clients:
			sock.close()

def handleMessage(client, all, message):
	parts = message.split(" ")
	cmd = parts[0]

	# normal message
	if cmd[0] != "/":
		others = all.getOthers(client)
		for c in others:
			c.send("<" + client.nickname + "> " + message)

	elif cmd == "/nick":
		client.nickname = " ".join(parts[1:])

def serve(IP, PORT):

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((IP, PORT))
	server.listen(10)

	print "Listening at " + (IP or "localhost") + ":" + str(PORT) + "..."

	clients = ClientList()

	while True:
		try:

			disconnect = []

			# get the sockets from all clients
			client_sockets = clients.getSockets()

			# wait for updates
			rready, wready, xready = select.select([server] + client_sockets, client_sockets, [server] + client_sockets)

			# exception occurred - close connection
			for sock in xready:
				disconnect.append(sock)

			# receive new data
			for sock in rready:

				# accept new clients
				if sock == server:
					sock, (cip, cport) = server.accept()
					print " >> connected: "+ str(cip) + ":" + str(cport)
					clients.add(Client(sock))
					continue

				client = clients.get(sock)
				data = client.receive(1024)

				# disconnected
				if not data:
					disconnect.append(sock)
					continue

				# received data
				handleMessage(client, clients, data.rstrip())

			# ready to send
			for sock in wready:
				client = clients.get(sock)
				client.flush()

			# remove disconnected clients
			for sock in disconnect:
				if clients.hasSocket(sock):
					c = clients.get(sock)
					others = clients.getOthers(c)
					for o in others:
						o.send("<disconnected: " + c.nickname + ">")
					clients.remove(c)
					c.close()
				else:
					sock.close()

		# close server on SIGINT
		except (KeyboardInterrupt, SystemExit):
			print "\nClosing server..."
			server.close()
			print "\nDisconnecting..."
			clients.closeAll()
			print "Cheers!"
			sys.exit(0)

## Command line parser.
if __name__ == '__main__':
	import sys, argparse
	p = argparse.ArgumentParser()
	p.add_argument('--ip', help='ip to connect to', default="localhost")
	p.add_argument('--port', help='port to listen on', default=12345, type=int)
	args = p.parse_args(sys.argv[1:])
	serve(args.ip, args.port)
