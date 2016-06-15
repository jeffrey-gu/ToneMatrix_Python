import pygame
from pygame.locals import *

#not sure if we need this yet for 2D version
from OpenGL.GL import *
from OpenGL.GLU import *

import threading	#for multithreading
import os	#for specifying file paths

#tile dimensions
width = 20
height = 20
defaultColor = (0,0,0)
flashColor = (255, 255, 255)

#other constants
numTiles = 4
numCols = 2
padding = 10

LEFT = 1
gray = (128,128,128)

class Tile(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, color, width, height, position, soundFile, tileI, tileJ):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)

       # Create an image of the block, and fill it with a color.
       # This could also be an image loaded from the disk.
       self.image = pygame.Surface([width, height])
       self.image.fill(defaultColor)

       #attach audio file
       self.sound = pygame.mixer.Sound(soundFile)
       self.isActive = False

       # Fetch the rectangle object that has the dimensions of the image
       # Update the position of this object by setting the values of rect.x and rect.y
       self.rect = self.image.get_rect()
       self.rect.x = position[0]
       self.rect.y = position[1]
       # self.rect = pygame.Rect(position[0], position[1], width, height)

       #assign sprite position
       self.i = tileI
       self.j = tileJ

    #have each tile individually play and update?
    def update(self, screen, soundCol, tileList):

    	# print "we are updating a tile"

    	if self.isActive:
    		# self.sound.play()
    		soundCol.append(self.sound)	#add sound to a list
    		tileList.append((self.image, self.rect))	#add column position to a list

    		# self.image.fill(flashColor)
    		# screen.blit(self.image, self.rect)
    		# pygame.display.update(self.rect)

    		# pygame.time.wait(300)

    		# self.image.fill(defaultColor)
    		# screen.blit(self.image, self.rect)
    		# pygame.display.update(self.rect)

def setMatrix():
	groupCount = numTiles/numCols
	groupList = []

	for i in range(numCols):

		group = pygame.sprite.Group()
		groupList.append(group)

		for j in range(groupCount):
			clipName = os.path.join(os.path.dirname(__file__), 'test' + str(i+j+1) + '.wav')	#this can be very important
			tile = Tile(defaultColor, width, height, (i*(width+padding), j*(height+padding)), clipName, i, j)	#tileID must be unique
			groupList[i].add(tile)

			print "we made a tile at position (%d, %d), with width %d and length %d)" %(tile.rect.x, tile.rect.y, tile.rect.width, tile.rect.height)

	return groupList

#call on each group's tile update functions in succession
def activateMatrix(groupList, screen):
	for group in groupList:

		soundCol = []
		tileList = []
		group.update(screen, soundCol, tileList)	#calling update on group -> calls update on each indv sprite
		# for tile in group:
		# 	tile.update(screen)

		threadList = []

		for i in range(0,len(tileList)):	#activate all tiles in column at once
			t = threading.Thread(target=lightEmUp, args = (soundCol[i],tileList[i], screen))
			threadList.append(t)

		for thread in threadList:
			thread.start()

		for thread in threadList:	#wait for all threads to finish?
			thread.join()

		pygame.time.delay(400)	#delay in between each group update

def lightEmUp(sound, square, screen):
	def playSound():
		sound.play()

	def blip():
		#retrieve tile
		image = square[0]
		rect = square[1]

		image.fill(flashColor)
		screen.blit(image, rect)
		pygame.display.update(rect)

		pygame.time.wait(200)

		image.fill(defaultColor)
		screen.blit(image, rect)
		pygame.display.update(rect)

	chime = threading.Thread(target = playSound, args=())
	flash = threading.Thread(target = blip, args=())

	chime.start()
	flash.start()

	chime.join()
	flash.join()


def main():
	#standard init stuff
	pygame.init()
	display = (800, 600)
	screen = pygame.display.set_mode(display)
	screen.fill(gray)	#default background = gray

	pygame.display.set_caption('Tone Matrix')
	clock = pygame.time.Clock()	#helps to keep track of fps

	#instantiate matrix
	groupList = setMatrix()

	#######################
	#pygame event loop
	while True:
		for event in pygame.event.get():	#gets every event that is queued up (per frame per second)
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:

				print "you clicked at ", event.pos

				#check if user clicked on any of the tiles
				for group in groupList:
					for t in group:
						# print "tile rect is at: (%d, %d) with %d width and height" %(t.rect.x, t.rect.y, t.rect.width)
						if (t.rect.collidepoint(event.pos)) == 1:
							print "you clicked a tile!"
							t.isActive = not t.isActive

						# print "is the tile active: %r" %t.isActive
						# print "did you click in its region? %r" %(t.rect.collidepoint(event.pos))


		for group in groupList:
			group.draw(screen)

		activateMatrix(groupList, screen)
		# screen.blit()

		pygame.display.flip()
		# screen.fill((0,0,0))	#do we need to redraw?

		clock.tick(30)	#frames per second (Desired)

main()
pygame.quit()
quit()