################################################################################################################
# Package Imports                                                                                              #
################################################################################################################
from pickle import dump,load
from pygame.locals import *
from math import *
import pygame
import sys
import os
import sys
from time import sleep, localtime
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from weakref import WeakKeyDictionary
import random
import math

################################################################################################################
# Global Variable Definitions                                                                                  #
################################################################################################################
clock = pygame.time.Clock()
pygame.font.init()
bulletList = []
enemyList = []
btnList = []
difficulty = 'easy'

# Number Initializations
MaxEnemies = 10
running = True
titleRunning = True

# font initialization
gameOverfont = pygame.font.SysFont('Ariel', 140, bold=True, italic=False)
scoreFont = pygame.font.SysFont('Ariel', 50, bold=True, italic=False)
titleFont = pygame.font.SysFont('Ariel', 40, bold=True, italic=False)
font = pygame.font.SysFont('Ariel', 80, bold=True, italic=False)


# Color Definitions
WHITE = (255, 255, 255)
LGREY = (200,200,200)
GREY = (119, 136, 153)
DGREY = (50,50,50)
ORANGE = (255, 102, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Screen Size
screenWidth = 700
screenHeight = 700
xCenter = screenWidth/2
yCenter = screenHeight/2

# # Define the Screen
# screen = pygame.display.set_mode((screenWidth, screenHeight))

################################################################################################################
# Class Definitions                                                                                            #
################################################################################################################

# client class initialization
class ClientChannel(Channel):
	"""
	This is the server representation of a single connected client.
	"""
	def __init__(self, *args, **kwargs):
		self.pos=[0,0]
		self.move=[0,0]

		# Health Bar Stuff
        self.hpWidth = width
        self.hpHeight = height/10
        self.hpImg = pygame.Surface([self.hpWidth, self.hpHeight])
        self.hpRect = self.hpImg.get_rect()
        self.hpImg.fill(GREEN)
        self.hpX = -self.width/2
        self.hpY = -self.pos[1]-self.hpHeight

		Channel.__init__(self, *args, **kwargs)
	
	def Close(self):
		self._server.DelPlayer(self)

	def Network_move(self,data):
		self.move=data['move']

# server class initialization
class Serve(Server):
	channelClass = ClientChannel

	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		print 'Server launched'
	
	def Connected(self, channel, addr):
		channel.Send({'action':'setup',
			'screenSize':world.screenSize,
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
			'update':[[p.pos for p in model.players],model.zombieList]})
	
	def Launch(self):
		while True:
			self.Pump()
			self.Update()
			sleep(0.01)

# World Class Initialization
class World():  # represents a bullet, not the game
    def __init__(self):
        """ The constructor of the class """
        self.screenSize=(screenWidth,screenHeight)
        self.backgroundList = []
        self.characterList = []
        self.bulletList = []
        self.enemyList = []
        self.blocksList = []
        self.score = 0
        self.wave = 1

    def gameClose(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit() # quit the screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit() # quit the screen


# Background Class Initialization
class Background():  # represents the player, not the game
    def __init__(self,color = BLACK,width = screenWidth,height = screenHeight):
        """ The constructor of the class """
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        # the background's position
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0

    def draw(self, surface):
        # blit yourself at your current position
        surface.blit(self.image, (self.x, self.y))


# Character Class Initialization
class Character():  # represents the player, not the game
    def __init__(self,color,x,y,width = 20,height = 20):
        """ The constructor of the class """
        # the character's position
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.width = width
        self.height = height
        self.xVel = 0
        self.yVel = 0
        self.xAcc = 0
        self.yAcc = 0

        self.health = 100

        
        
    def updateRect(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        """ Draw on surface """
        # blit yourself at your current position
        surface.blit(self.image, (self.x, self.y))
        # draw health bar
        surface.blit(self.hpImg, (self.hpX, self.hpY))

    def bulletDirection(self):
        mousePos = pygame.mouse.get_pos()
        mouseX = mousePos[0]
        mouseY = mousePos[1]

        xPart = float(abs(mouseX-self.x))/(abs(mouseX-self.x)+ abs(mouseY-self.y))
        yPart = float(abs(mouseY-self.y))/(abs(mouseX-self.x)+ abs(mouseY-self.y))

        if self.x < mouseX:
            # attraction must go right
            xDir = 'right'
        elif self.x > mouseX:
            # attraction must go left
            xDir = 'left'
        else:
            xDir = ''

        if self.y > mouseY:
            # attraction must go right
            yDir = 'up'
        elif self.y < mouseY:
            # attraction must go left
            yDir = 'down'
        else:
            yDir = ''
        return [xDir,yDir,xPart,yPart]

    def shoot(self,alist):
        partsDir = self.bulletDirection()
        xDir = partsDir[0]
        yDir = partsDir[1]
        xPart = partsDir[2]
        yPart = partsDir[3]
        initBulletVel = 20
        mousePress = pygame.mouse.get_pressed()
        if mousePress[0] == True:
            bullet = Bullet(GREY,0,0)
            bullet.x = self.x+self.width/2
            bullet.y = self.y+self.height/2

            if xDir == 'right':
                bullet.xVel += xPart*initBulletVel
            elif xDir == 'left':
                bullet.xVel -= xPart*initBulletVel
            else:
                bullet.xVel = 0

            if yDir == 'down':
                bullet.yVel += yPart*initBulletVel
            elif yDir == 'up':
                bullet.yVel -= yPart*initBulletVel
            else:
                bullet.yVel = 0
            alist.append(bullet)

    def gameControl(self,alist):
        self.shoot(alist)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit() # quit the screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit() # quit the screen
                elif event.key == pygame.K_a:
                    self.xVel -= 8
                elif event.key == pygame.K_d:
                    self.xVel += 8
                elif event.key == pygame.K_w:
                    self.yVel -= 8
                elif event.key == pygame.K_s:
                    self.yVel += 8

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    sys.exit() # quit the screen
                elif event.key == pygame.K_a:
                    self.xVel += 8
                elif event.key == pygame.K_d:
                    self.xVel -= 8
                elif event.key == pygame.K_w:
                    self.yVel += 8
                elif event.key == pygame.K_s:
                    self.yVel -= 8

    def moveChar(self):
        self.x += self.xVel
        self.y += self.yVel
        

    def checkX(self,other):
        if other.rect.x+other.width >= self.rect.x and other.rect.x+other.width <= self.rect.x+self.width:
            return True
        elif other.rect.x <= self.rect.x+self.width and other.rect.x >= self.rect.x:
            return True

    def checkY(self,other):
        if other.rect.y+other.height >= self.rect.y and other.rect.y+other.height <= self.rect.y+self.height:
            return True
        elif other.rect.y <= self.rect.y+self.height and other.rect.y >= self.rect.y:
            return True

    def checkCollideenemy(self,other):
        xCollide = self.checkX(other)
        yCollide = self.checkY(other)
        if xCollide == True and yCollide == True:
            return True

    def Update(self):
		playerPositions=[]
		#players
		for player in self.players:
			player.pos[0]+=player.move[0]
			player.pos[1]+=player.move[1]
			playerPositions+=[[player.pos[0],player.pos[1]]]
			player.hpWidth = self.width-((self.width/100)*(100-self.health))
	        self.hpHeight = self.height/10
	        self.hpX = self.x
	        self.hpY = self.y-self.hpHeight-2
	        self.hpImg = pygame.Surface([self.hpWidth, self.hpHeight])
	        self.hpRect = self.hpImg.get_rect()
	        self.hpImg.fill(GREEN)
	        self.updateRect()
            

class Model(object):
	def __init__(self):
		self.playerSize=32
		self.zombieSize=16
		self.zombieNum = 50
		self.players=WeakKeyDictionary()
		self.zombieList=[]

	def AddPlayer(self,channel):
		self.players[channel] = True
		print 'person added!'

	def DelPlayer(self,player):
		del self.players[player]
		print 'person deleted!'

	
		#zombies
		if not self.zombieList:
			self.AddZombies()
		for zombie in self.zombieList:
			closestPlayer=playerPositions[0]
			closestDist=self.dist(zombie,playerPositions[0])
			for player in playerPositions:
				currentDist=self.dist(zombie,player)
				if currentDist<closestDist:
					closestPlayer=player
					closestDist=currentDist
			if closestDist!=0:
				zombie[0]+=(closestPlayer[0]-zombie[0])/(2*closestDist)
				zombie[1]+=(closestPlayer[1]-zombie[1])/(2*closestDist)
	
	def dist(self,zombie,player):
		return math.sqrt((zombie[0]-player[0])**2+(zombie[1]-player[1])**2)

	def AddZombies(self):
		for z in range(self.zombieNum):
			self.zombieList+=[[
			random.randint(0,int(self.screenSize[0])-self.zombieSize),
			random.randint(0,int(self.screenSize[1])-self.zombieSize)]]

# get command line argument of server, port
if len(sys.argv) != 2:
	print "Usage:", sys.argv[0], "host:port"
	print "e.g.", sys.argv[0], "localhost:31425"
else:
	host, port = sys.argv[1].split(":")
	s = Serve(localaddr=(host, int(port)))
	model=Model()
	s.Launch()