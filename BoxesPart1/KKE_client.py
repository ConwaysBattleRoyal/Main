import sys, os, pygame, Image
from time import sleep
from sys import stdin, exit
from PodSixNet.Connection import connection, ConnectionListener
from thread import *
from pygame.locals import *

pygame.mixer.pre_init(22050,-16,2,4)
pygame.mixer.init()
pygame.init()

RED =   [(100, 0, 0),(200, 0, 0),(255, 0, 0)]
GREEN = [(0, 100, 0),(0, 200, 0),(0, 255, 0)]
BLUE =  [(0, 0, 100),(0, 0, 200),(0, 0, 255)]


class Client(ConnectionListener):
	def __init__(self, host, port):
		self.Connect((host, port))
		print "client started"
		self.move=[0,0]
		self.shooting=False
	
	def Loop(self):
		

		connection.Pump()
		self.Pump()

		for event in pygame.event.get():
			if event.type ==KEYDOWN and event.key == K_ESCAPE:
				pygame.quit()
			if event.type == KEYDOWN and event.key == K_a:
				self.move[0]-=1
			if event.type == KEYUP and event.key == K_a:
				self.move[0]+=1
			if event.type == KEYDOWN and event.key == K_d:
				self.move[0]+=1
			if event.type == KEYUP and event.key == K_d:
				self.move[0]-=1
			if event.type == KEYDOWN and event.key == K_w:
				self.move[1]-=1
			if event.type == KEYUP and event.key == K_w:
				self.move[1]+=1
			if event.type == KEYDOWN and event.key == K_s:
				self.move[1]+=1
			if event.type == KEYUP and event.key == K_s:
				self.move[1]-=1
			if event.type == MOUSEBUTTONDOWN:
				self.shooting=True
			if event.type == MOUSEBUTTONUP:
				self.shooting=False

		mousePos=pygame.mouse.get_pos()
		if self.shooting:
			shootDirection=mousePos
		else:
			shootDirection=()
		mb=25 #mouse border (how close to edge we let mouse get)
		ss=view.size
		pygame.mouse.set_pos(self.clamp(mousePos,mb,ss[0]-mb,mb,ss[1]-mb))
		
		connection.Send({'action':'playerState','move':self.move,'shoot':shootDirection})

	def clamp(self,(x,y),xmin,xmax,ymin,ymax):
	    return [max(min(xmax, x), xmin),max(min(ymax, y), ymin)]

	def Network_setup(self,data):
		print 'setup complete!'
		view.setup(data)
		
	def Network_update(self,data):
		view.frame(data['update'])

	def Network_connected(self, data):
		print "You are now connected to the server"
	
	def Network_error(self, data):
		print 'error:', data['error'][1]
		connection.Close()
	
	def Network_disconnected(self, data):
		print 'Server disconnected'
		exit()


# Text Class Initialization
class Text():
	def __init__(self,text,color,x,y,hueVal=1):
		""" The constructor of the text class """
		# Text Information
		# self.titleScreen = pygame.image.load('./KKE.png')
		self.x = x
		self.y = y
		self.text = text
		self.hueVal = hueVal
		self.clicked = False
		self.color = color
		self.font = pygame.font.SysFont('Ariel', 80, bold=True, italic=False)
		self.fontSmall = pygame.font.SysFont('Ariel', 40, bold=True, italic=False)
		self.scrollSound = pygame.mixer.Sound("scrollOver.wav")
		self.clickSound = pygame.mixer.Sound("click.wav")
		self.scrollSound.set_volume(.3)
		self.clickSound.set_volume(.3)

	def checkX(self,mousex,area):
		if mousex >= self.x and mousex <= self.x+area[0]:
			return True

	def checkY(self,mousey,area):
		if mousey >= self.y and mousey <= self.y+area[1]:
			return True

	def checkHover(self,area,sound):
		for event in pygame.event.get():
			pass
		mousePos = pygame.mouse.get_pos()
		mouseX = mousePos[0]
		mouseY = mousePos[1]
		boolX = self.checkX(mouseX,area)
		boolY = self.checkY(mouseY,area)
		if boolX == True and boolY == True:
			if self.hueVal != 2 and sound:
				# self.hoverSound.playMusic(0)
				self.scrollSound.play()
				self.hueVal = 2
			return True

	def checkClicked(self,area):
		mousePos = pygame.mouse.get_pos()
		mouseX = mousePos[0]
		mouseY = mousePos[1]
		mousePress = pygame.mouse.get_pressed()
		if mousePress[0] == True:
			boolX = self.checkX(mouseX,area)
			boolY = self.checkY(mouseY,area)
			if boolX == True and boolY == True:
				self.hueVal = 0
				return True

	def printText(self,view):
		# print stuff
		string = str(self.text)
		area = self.font.size(string)
		if not self.clicked:
			if self.checkClicked(area):
				label = self.font.render(string,True,self.color[self.hueVal])
				self.clickSound.play()
				self.clicked = True
			elif self.checkHover(area,True):
				label = self.font.render(string,True,self.color[self.hueVal])
			else:
				self.hueVal = 1
				label = self.font.render(string,True,self.color[self.hueVal])
		else:
			self.hueVal = 0
			label = self.font.render(string,True,self.color[self.hueVal])
		view.screen.blit(label,(self.x,self.y))

	def printTexttrans(self,view):
		# print stuff
		string = str(self.text)
		area = self.font.size(string)
		if not self.clicked:
			if self.checkHover(area,False):
				pass
			else:
				label = self.font.render(string,True,self.color)
				view.screen.blit(label,(self.x,self.y))

	def printTextnormal(self,view):
		# print stuff
		string = str(self.text)
		area = self.font.size(string)
		label = self.font.render(string,True,self.color[1])
		view.screen.blit(label,(self.x,self.y))

	def printTextnormalSmall(self,view):
		# print stuff
		string = str(self.text)
		area = self.fontSmall.size(string)
		label = self.fontSmall.render(string,True,self.color[1])
		view.screen.blit(label,(self.x,self.y))



class View(object):
	def __init__(self):	
		pygame.init()
		self.size=(0,0)	
		self.font = pygame.font.Font(None, 24)
		self.BLACK    = (   0,   0,   0)
		self.WHITE    = ( 255, 255, 255)
		self.GREEN    = (   25, 255,   25)
		self.RED      = ( 255,   0,   0)
		self.zombieImg = pygame.image.load('./zombieArt.png')
		self.titleMusic = pygame.mixer.Sound("DeepTorvus.ogg")
		self.gameMusic = pygame.mixer.Sound("KraidsLair.wav")
		self.titleMusic.set_volume(1)
		self.gameMusic.set_volume(1)
		# self.wordList = []

	def titleRunning(self):
		self.titleBackground = pygame.image.load('./KKE.png')
		self.optionsBackground = pygame.image.load('./KKEoptions.png')
		play = Text('Play',RED,100,450)
		options = Text('Options',RED,100,520)
		story = Text('Story',RED,250,450)
		quit = Text('Quit',RED,100,590)
		self.titleMusic.play(-1,0)
		while True:
			self.titleBackground = pygame.transform.scale(self.titleBackground, (self.size[0], self.size[1]))
			self.screen.blit(self.titleBackground, (0, 0))
			play.printText(self)
			options.printText(self)
			quit.printText(self)
			story.printText(self)
			pygame.display.flip()
			if quit.clicked:
				self.quitGame()
			if story.clicked:
				self.storyRunning()
				story.clicked = False
			if options.clicked:
				self.optionsRunning()
				options.clicked = False
			if play.clicked:
				# introMusic.fadeMusic(1000)
				# sleep(1)
				break

	def optionsRunning(self):
		self.optionsBackground = pygame.transform.scale(self.optionsBackground, (self.size[0], self.size[1]))
		difficulty = Text('Select Difficulty:',RED,50,50)
		easy = Text('Easy',RED,100,110)
		medium = Text('Medium',RED,250,110)
		hard = Text('Hard',RED,500,110)
		back = Text('Back',RED,50,350)
		easy.clicked = True

		screenOpt = Text('Screen Options:',RED,50,200)
		fullscreen = Text('Fullscreen',RED,100,260)
		normal = Text('Normal',RED,400,260)
		normal.clicked = True

		while True:
			self.screen.blit(self.optionsBackground, (0, 0))
			difficulty.printTextnormal(self)
			easy.printText(self)
			medium.printText(self)
			hard.printText(self)
			back.printText(self)

			screenOpt.printTextnormal(self)
			fullscreen.printText(self)
			normal.printText(self)

			if fullscreen.clicked:
				self.screen = pygame.display.set_mode([0,0],NOFRAME|FULLSCREEN|HWSURFACE|DOUBLEBUF)
				normal.clicked = False
				if normal.clicked:
					self.screen = pygame.display.set_mode(self.size)
					fullscreen.clicked = False

			pygame.display.flip()
			sleep(0.1)
			if back.clicked:
				back.clicked = False
				break

	def quitGame(self):
		sys.exit()

	def storyRunning(self):
		self.optionsBackground = pygame.transform.scale(self.optionsBackground, (self.size[0], self.size[1]))
		storyLineone = Text('It was half past 12:20 and all through the diner',RED,50,50)
		storyLinetwo = Text('Not an employee was stirring, not even the fryer',RED,50,100)
		storyLinethree = Text("Yet deep in the freezer's oldest recesses,",RED,50,150)
		storyLinefour = Text('Plot sick, twisted meat cubes. The oldest confesses,',RED,50,200)
		storyLinefive = Text('"'+"I've lived here too long, in this cold, dark, dank prison.",RED,50,250)
		storyLinesix = Text("It's time for some payback, our army is risen!"+'"',RED,50,300)
		storyLineseven = Text('These meat cubes rose up, gross, rotten, mutated,',RED,50,350)
		storyLineeight = Text('Struck back at the cooks, refused to be plated.',RED,50,400)
		storyLinenine = Text('They conquered the diner, took over this b*tch,',RED,50,450)
		storyLineten = Text('But they never considered that shifts would be switched.',RED,50,500)
		storyLineeleven = Text("It's time for your shift. Prepare for battle.",RED,50,600)

		back = Text('Back',RED,650,585)
		while True:
			self.screen.blit(self.optionsBackground, (0, 0))
			storyLineone.printTextnormalSmall(self)
			storyLinetwo.printTextnormalSmall(self)
			storyLinethree.printTextnormalSmall(self)
			storyLinefour.printTextnormalSmall(self)
			storyLinefive.printTextnormalSmall(self)
			storyLinesix.printTextnormalSmall(self)
			storyLineseven.printTextnormalSmall(self)
			storyLineeight.printTextnormalSmall(self)
			storyLinenine.printTextnormalSmall(self)
			storyLineten.printTextnormalSmall(self)
			storyLineeleven.printTextnormalSmall(self)

			back.printText(self)

			pygame.display.flip()
			sleep(0.1)
			if back.clicked:
				back.clicked = False
				break

	def setup(self,data):
		self.size	   = data['screenSize']
		self.playerSize= data['playerSize']
		self.zombieSize= data['zombieSize']
		self.bulletSize= data['bulletSize']
		os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
		self.screen   = pygame.display.set_mode(self.size)
		pygame.display.set_caption("KILL KILL Evolution")
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))
		self.screen.blit(self.background, (0, 0))
		self.titleRunning()
		self.titleMusic.stop()
		self.gameMusic.play(-1)

	def frame(self,data):
		score = Text('10',self.BLACK,10,10)
		self.screen.fill(self.WHITE)
		for player in data['players']:
			pygame.draw.rect(self.screen, self.RED,[
				player[0]-self.playerSize/2, 
				player[1]-self.playerSize/2, 
				self.playerSize,self.playerSize])
		for zombie in data['zombies']:
			self.screen.blit(self.zombieImg, [zombie[0], zombie[1]])
		for bullet in data['bullets']:
			pygame.draw.rect(self.screen, self.BLACK,[
				bullet[0]-self.bulletSize/2,
				bullet[1]-self.bulletSize/2,
				self.bulletSize,self.bulletSize])
		for (i,player) in enumerate(data['players']):
			health = self.font.render(str(data['health'][i]), 1, (10, 10, 10))
			self.screen.blit(health, (player[0]-self.playerSize/4, player[1]-self.playerSize/2))
		# score.printTexttrans(self)
		pygame.display.flip()

if len(sys.argv) != 2:
	print "Usage:", sys.argv[0], "host:port"
	print "e.g.", sys.argv[0], "localhost:31425"
else:
	host, port = sys.argv[1].split(":")
	c = Client(host, int(port))
	view=View()
	while 1:
		c.Loop()
		sleep(0.0001)