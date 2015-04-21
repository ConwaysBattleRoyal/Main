# screen.blit(titleScreen,(0,0))
# play.printText()
# if play.clicked:
# 	break

# # Color Definitions
# RED =   [(100, 0, 0),(200, 0, 0),(255, 0, 0)]
# GREEN = [(0, 100, 0),(0, 200, 0),(0, 255, 0)]
# BLUE =  [(0, 0, 100),(0, 0, 200),(0, 0, 255)]

# titleScreen = pygame.image.load('./KKE.jpg')
# 		play = Text(Play,RED,300,300)

# Text Class Initialization
class Text():
    def __init__(self,text,color,x,y,hueVal=1):
        """ The constructor of the class """
        # Text Information
        self.x = x
        self.y = y
        self.text = text
        self.hueval = hueVal
        self.clicked = False
        self.color = color
        self.font = pygame.font.SysFont('Ariel', 80, bold=True, italic=False)

    def checkX(self,mousex,area):
        if mousex >= self.x and mousex <= self.x+area[0]:
            return True

    def checkY(self,mousey,area):
        if mousey >= self.y and mousey <= self.y+area[1]:
            return True

    def checkHover(self,area):
        mousePos = pygame.mouse.get_pos()
        mouseX = mousePos[0]
        mouseY = mousePos[1]
        mousePress = pygame.mouse.get_pressed()
        boolX = self.checkX(mouseX,area)
        boolY = self.checkY(mouseY,area)
        if boolX == True and boolY == True:
        	self.hueVal+=1
        	return True

	def checkClick(self,area):
		mousePos = pygame.mouse.get_pos()
        mouseX = mousePos[0]
        mouseY = mousePos[1]
        mousePress = pygame.mouse.get_pressed()
        if mousePress[0] == True:
            boolX = self.checkX(mouseX,area)
            boolY = self.checkY(mouseY,area)
            if boolX == True and boolY == True:
            	self.hueVal = 0
            	self.clicked = True
                return True

	def printText(self):
	    # print stuff
	    string = str(self.text)
	    label = self.font.render(string,True,self.color[self.hueVal])
	    area = self.font.size(string)

	    if self.clicked:
	    	pass
	    elif self.checkClick(area):
	    	label = self.font.render(string,True,self.color[self.hueVal])
	    else:
		    if self.checkHover(area):
		    	label = self.font.render(string,True,self.color[self.hueVal])

	    labelRect = label.get_rect()
	    labelRect.pos = (self.x,self.y)
	    screen.blit(label,(labelRect.pos))

    def clickText(self):
        if self.checkClick():
            return True