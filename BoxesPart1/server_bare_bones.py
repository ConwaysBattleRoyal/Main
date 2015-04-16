import sys, random,math,copy,time
from time import sleep, localtime
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from weakref import WeakKeyDictionary


screenSize=(700,500)
zombieSize=16
playerSize=32
bulletSize=4

class ClientChannel(Channel):
	"""
	This is the server representation of a single connected client.
	"""
	def __init__(self, *args, **kwargs):
		self.pos=[0,0]
		self.move=[0,0]
		self.shootDirection=()
		Channel.__init__(self, *args, **kwargs)
	
	def Close(self):
		self._server.DelPlayer(self)

	def Network_playerState(self,data):
		self.move=data['move']
		self.shootDirection=data['shoot']

class Serve(Server):
	channelClass = ClientChannel

	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		print 'Server launched'
	
	def Connected(self, channel, addr):
		channel.Send({'action':'setup',
			'screenSize':screenSize,
			'playerSize':playerSize,
			'zombieSize':zombieSize,
			'bulletSize':bulletSize})
		model.AddPlayer(channel)
	
	def DelPlayer(self, player):
		model.DelPlayer(player)

	def SendToAll(self, data):
		[p.Send(data) for p in model.players]

	def Update(self):
		if model.players:
			model.Update()
		self.SendToAll({'action':'update',
			'update':model.sendDict})
	
	def Launch(self):
		while True:
			self.Pump()
			self.Update()
			sleep(.01)
class Zombie(object):
	def __init__(self):
		#positioning randomly around border of game
		if random.randint(0,1):
			if random.randint(0,1):
				self.pos=[random.randint(0,int(screenSize[0])-zombieSize),0]
			else:
				self.pos=[random.randint(0,int(screenSize[0])-zombieSize),screenSize[1]]
		else:
			if random.randint(0,1):
				self.pos=[0,random.randint(0,int(screenSize[1])-zombieSize)]
			else:
				self.pos=[screenSize[0],random.randint(0,int(screenSize[1])-zombieSize)]


		self.living=True
		self.speed=float(random.randint(3,10)/6.0)

	def dist(self,player): #returns distances between zombie and player
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
		#d represents the distance between centerpoints of the zombie and the player	
		d=(zombieSize+playerSize)/2
		if closestPlayer[0]-d<self.pos[0]<closestPlayer[0]+d and closestPlayer[1]-d<self.pos[1]<closestPlayer[1]+d:
			self.living=False
		#h is the distance between centerpoints of the bullets and the zombies
		h=(zombieSize+bulletSize)/2
		for bullet in model.bulletList:
			if self.pos[0]-h<bullet.pos[0]<self.pos[0]+h and self.pos[1]-h<bullet.pos[1]<self.pos[1]+h:
				self.living=False
				bullet.living=False
class Bullet(object):
	def __init__(self,target,position):
		#figure out where the bullet starts and in what direction it should go
		self.speed=5
		self.living=True
		self.pos=position
		dist=math.sqrt((self.pos[0]-target[0])**2+(self.pos[1]-target[1])**2)
		self.direction=[(target[0]-self.pos[0])/dist,
						(target[1]-self.pos[1])/dist]
	def update(self):
		self.pos[0]+=self.direction[0]*self.speed
		self.pos[1]+=self.direction[1]*self.speed
		if not 0<self.pos[0]<screenSize[0] or not 0<self.pos[1]<screenSize[1]:
			self.living=False
class Model(object):
	def __init__(self):
		self.players=WeakKeyDictionary()
		self.zombieList=[]
		self.bulletList=[]
		self.sendDict={}
		self.bulletTimer=time.time()
		
	def AddPlayer(self,channel):
		self.players[channel] = True
		print 'person added!'

	def DelPlayer(self,player):
		del self.players[player]
		print 'person deleted!'

	def Update(self):
		#players
		self.playerPositions=[]
		for player in self.players:
			player.pos[0]+=player.move[0]
			player.pos[1]+=player.move[1]
			self.playerPositions+=[[player.pos[0],player.pos[1]]]
			if player.shootDirection and time.time()-self.bulletTimer>.3:
				self.bulletTimer=time.time()
				self.bulletList+=[Bullet(player.shootDirection,
					copy.copy(player.pos))]
		#zombies
		zombiesLeft=False
		for zombie in self.zombieList:
			if zombie.living==True:
				zombie.update(self.playerPositions)
				zombiesLeft=True
		if not zombiesLeft:
			self.AddZombies()
		#bullets
		self.bulletList=[bullet for bullet in self.bulletList if bullet.living==True]
		for bullet in self.bulletList:
			if bullet.living==True:
				bullet.update()

		self.sendDict={'players':self.playerPositions,
			'zombies':self.Listifier(self.zombieList),
			'bullets':self.Listifier(self.bulletList)}

	def AddZombies(self):
		for z in range(30):
			self.zombieList+=[Zombie()]

	def Listifier(self,listy):
		return [[item.pos[0],item.pos[1]] for item in listy if item.living==True]

# get command line argument of server, port
if len(sys.argv) != 2:
	print "Usage:", sys.argv[0], "host:port"
	print "e.g.", sys.argv[0], "localhost:31425"
else:
	host, port = sys.argv[1].split(":")
	s = Serve(localaddr=(host, int(port)))
	model=Model()
	s.Launch()
