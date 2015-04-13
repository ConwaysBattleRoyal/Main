import sys
from time import sleep, localtime
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from weakref import WeakKeyDictionary
import random
import math

class ClientChannel(Channel):
	"""
	This is the server representation of a single connected client.
	"""
	def __init__(self, *args, **kwargs):
		self.pos=[0,0]
		self.move=[0,0]
		Channel.__init__(self, *args, **kwargs)
	
	def Close(self):
		self._server.DelPlayer(self)

	def Network_move(self,data):
		self.move=data['move']

class Serve(Server):
	channelClass = ClientChannel

	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		print 'Server launched'
	
	def Connected(self, channel, addr):
		channel.Send({'action':'setup',
			'screenSize':model.screenSize,
			'playerSize':model.playerSize,
			'zombieSize':model.zombieSize})
		model.AddPlayer(channel)
	
	def DelPlayer(self, player):
		model.DelPlayer(player)

	def SendToAll(self, data):
		[p.Send(data) for p in model.players]

	def Update(self):
		if model.players:
			model.Update()
		self.SendToAll({'action':'update',
			'update':[[p.pos for p in model.players],model.sendList]})
	
	def Launch(self):
		while True:
			self.Pump()
			self.Update()
			sleep(0.01)

class Zombie(object):
	def __init__(self,screenSize,zombieSize,playerSize):
		self.playerSize=playerSize
		self.zombieSize=zombieSize
		self.screenSize=screenSize
		if random.randint(0,1):
			self.pos=[random.randint(0,int(self.screenSize[0])-self.zombieSize),0]
		else:
			self.pos=[0,random.randint(0,int(self.screenSize[1])-self.zombieSize)]
		self.living=True
		self.speed=float(random.randint(3,10)/6.0)

	def dist(self,player):
		return math.sqrt((self.pos[0]-player[0])**2+(self.pos[1]-player[1])**2)
	def update(self,playerPositions):
		closestPlayer=playerPositions[0]
		closestDist=self.dist(playerPositions[0])
		for player in playerPositions:
			currentDist=self.dist(player)
			if currentDist<closestDist:
				closestPlayer=player
				closestDist=currentDist
		if closestDist!=0:
			xchase=(closestPlayer[0]-self.pos[0])/(2*closestDist)
			ychase=(closestPlayer[1]-self.pos[1])/(2*closestDist)
			self.pos[0]+=xchase*self.speed
			self.pos[1]+=ychase*self.speed
		d=(self.zombieSize+self.playerSize)/2
		if closestPlayer[0]-d<self.pos[0]<closestPlayer[0]+d and closestPlayer[1]-d<self.pos[1]<closestPlayer[1]+d:
			self.living=False

class Model(object):
	def __init__(self):
		self.screenSize=(700,500)
		self.playerSize=32
		self.zombieSize=16
		self.players=WeakKeyDictionary()
		self.zombieList=[]
		self.sendList=[]

	def AddPlayer(self,channel):
		self.players[channel] = True
		print 'person added!'

	def DelPlayer(self,player):
		del self.players[player]
		print 'person deleted!'

	def Update(self):
		playerPositions=[]
		#players
		for player in self.players:
			player.pos[0]+=player.move[0]
			player.pos[1]+=player.move[1]
			playerPositions+=[[player.pos[0],player.pos[1]]]
		#zombies
		if not self.sendList:
			self.AddZombies()
		for zombie in self.zombieList:
			if zombie.living==True:
				zombie.update(playerPositions)
		self.sendList=self.ZombieListifier(self.zombieList)

	def AddZombies(self):
		for z in range(30):
			self.zombieList+=[Zombie(self.screenSize,self.zombieSize,self.playerSize)]

	def ZombieListifier(self,zombieList):
		return [[zombie.pos[0],zombie.pos[1]] for zombie in zombieList if zombie.living==True]


# get command line argument of server, port
if len(sys.argv) != 2:
	print "Usage:", sys.argv[0], "host:port"
	print "e.g.", sys.argv[0], "localhost:31425"
else:
	host, port = sys.argv[1].split(":")
	s = Serve(localaddr=(host, int(port)))
	model=Model()
	s.Launch()
