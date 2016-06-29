import pygame
from pygame.locals import *

from multiprocessing import Process, Pool
import threading
import os

#some touchscreen calibration environment vars
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"

#tile properties
width = 40
height = 40
defaultColor = (0,0,0)
flashColor = (255, 255, 255)
gray = (128, 128, 128)

#board properties
numTiles = 14
numCols = 7
padding = 20

#for the mouse event check
LEFT = 1

class Tile(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block and its x and y position
    def __init__(self, color, width, height, position, soundFile, tileI, tileJ):
       # Call the parent class (Sprite) constructor
       pygame.sprite.Sprite.__init__(self)

       # Create an image of the block, and fill it with a color.
       # This could also be an image loaded from the disk.
       self.image = pygame.Surface([width, height])
       self.image.fill(defaultColor)

       # attach audio file
       self.sound = pygame.mixer.Sound(soundFile)
       self.soundFile = soundFile
       self.isActive = False

       # Fetch the rectangle object that has the dimensions of the image
       # Update the position of this object by setting the values of rect.x and rect.y
       self.rect = self.image.get_rect()
       self.rect.x = position[0]
       self.rect.y = position[1]
       # self.rect = pygame.Rect(position[0], position[1], width, height)

       #assign sprite position (for passing into update later)
       self.i = tileI
       self.j = tileJ

    def update(self):

    	def toggleSound():
    		self.sound.play()

    	def blip():
    		#color change
    		self.image.fill(defaultColor)
    		screen.blit(self.image, self.rect)
    		pygame.display.update(self.rect)

    		pygame.time.wait(100)

    		self.image.fill(flashColor)
    		screen.blit(self.image, self.rect)
    		pygame.display.update(self.rect)

    	blip()
    	toggleSound()

# this function creates a board of tile sprites, and appends them to a list
def setMatrix():
	groupCount = numTiles/numCols
	groupList = []

	for i in range(numCols):

		group = pygame.sprite.Group()
		groupList.append(group)

		for j in range(groupCount):
			clipName = os.path.join(os.path.dirname(__file__), 'pluck' + str(i+j+1) + '.wav')	#indexed starting from 1
			tile = Tile(defaultColor, width, height, (i*(width+padding), j*(height+padding)), clipName, i, j)	#tileID must be unique
			groupList[i].add(tile)

	return groupList

#call on each group's tile update functions in succession
def activateMatrix(groupList):

	# def light(sound, image, rect):

	# 	def toggleSound(sound):
	#     	sound.play()

	#     def blip(image, rect):
	#     	#color change
	#     	image.fill(defaultColor)
	#    		screen.blit(image, rect)
	#     	pygame.display.update(rect)

	#     	pygame.time.wait(100)

	#     	image.fill(flashColor)
	#     	screen.blit(image, rect)
	#    		pygame.display.update(rect)

	#    	blip()
	#    	toggleSound()

	for group in groupList:

		updateList = []

		for tile in group:
			if tile.isActive:
				# updateList.append(threading.Thread(target=tile.update()))
				# updateList.append(Process(target=tile.update()))
				updateList.append(tile)

		numActive = len(updateList)

		if numActive > 0:	# must have at least 1 process to instan. pool

			pool = Pool(processes=len(updateList))
			for tile in updateList:
				# pool.apply_async(light, (tile.sound, tile.image, tile.rect))
				pool.apply_async(tile.update())

			pool.close()
			pool.join()

		# for thread in updateList:
		# 	thread.start()
		# 	thread.join()

		# for thread in updateList:
		# 	thread.join()

		pygame.time.delay(50)	#delay in between each column
	pygame.time.delay(1500)	#delay before next iteration

# def lightEmUp(sound, rect, image):
# 	def toggleSound():
# 		sound.play()

# 	def blip():
# 		#color change
# 		image.fill(defaultColor)
# 		screen.blit(image, rect)
# 		pygame.display.update(rect)

# 		pygame.time.wait(100)

# 		image.fill(flashColor)
# 		screen.blit(image, rect)
# 		pygame.display.update(rect)

# 	# chime = threading.Thread(target = playSound)
# 	# flash = threading.Thread(target = blip)

# 	# chime.start()
# 	# flash.start()

# 	# chime.join()
# 	# flash.join()

# 	blip()
# 	toggleSound()

def main():
	global screen

	display = (800, 600)
	screen = pygame.display.set_mode(display)
	screen.fill(gray)	#default background
	clock = pygame.time.Clock()

	pygame.display.set_caption('Tone Matrix')

	#instantiate matrix
	groupList = setMatrix()

	for group in groupList:	#draw tiles on screen
		group.draw(screen)

	#######################
	#pygame event loop
	while True:
		events = pygame.event.get()
		for event in events:
			if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
				pygame.quit()
				quit()

			elif event.type == pygame.MOUSEBUTTONUP:	#ISSUE: event position is carried over to the next click?

				print event.pos

				#check if user clicked on any of the tiles
				for group in groupList:
					for t in group:
						# print "tile rect is at: (%d, %d) with %d width and height" %(t.rect.x, t.rect.y, t.rect.width)
						if (t.rect.collidepoint(event.pos)) == 1:
							t.isActive = not t.isActive
							if t.isActive:
								t.image.fill(flashColor)

							else:
								t.image.fill(defaultColor)

							pygame.display.update(t.rect)

					# group.draw(screen)
				# pygame.display.flip()	#update tiles to include any activated ones

		activateMatrix(groupList)
		pygame.display.flip()

###############################

if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()