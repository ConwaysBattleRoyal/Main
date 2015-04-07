from weakref import WeakKeyDictionary
class Turtle(object):
	def __init__(self):
		self.name='bobby'

players=WeakKeyDictionary

turtle=Turtle()

players[turtle]=True

