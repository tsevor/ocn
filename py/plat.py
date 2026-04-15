import math
import sys

import pygame

SCREEN_DIM = (1000, 700)

pygame.init()
SCREEN = pygame.display.set_mode(SCREEN_DIM)
pygame.display.set_caption("platformer test")
CLOCK = pygame.time.Clock()

OBJECTS = [
	pygame.Rect(50, 280, 300, 10),
	pygame.Rect(200, 150, 10, 110),
	pygame.Rect(75, 230, 100, 10),
	pygame.Rect(250, 150, 10, 110),
]


class Player(pygame.sprite.Sprite):
	GRAVITY = 0.2
	MAX_SPEED = 3
	JUMP = -5
	WALLJUMP_MAGNITUDE = 4
	WALLJUMP_ANGLE = 35
	WALLJUMP_X = -math.cos(math.radians(WALLJUMP_ANGLE)) * WALLJUMP_MAGNITUDE
	WALLJUMP_Y = -math.sin(math.radians(WALLJUMP_ANGLE)) * WALLJUMP_MAGNITUDE
	VAULTJUMP = -2
	SPEED = 0.3
	DRAG = 0.98
	GROUNDDRAG = 0.95
	WALLDRAG = 0.7

	def __init__(self):
		super().__init__()
		self.size = 8
		self.image = pygame.Surface((self.size, self.size))

		self.image.fill((255, 255, 255))

		# for x in range(self.size):

		self.grounded = 0  # 0 = air, 1 = ground
		self.on_wall = 0  # 1 = left, -1 = right, 0 = none

		self.xpos = 100
		self.ypos = 0
		self.xvel = 0
		self.yvel = 0

	def physics_step(self, movement=0, jumping=False, objects=[]):
		if abs(self.xvel) < Player.MAX_SPEED:
			if movement < 0:
				self.xvel = max(
					self.xvel - (Player.SPEED / 2 if self.grounded else Player.SPEED),
					-Player.MAX_SPEED,
				)
			elif movement > 0:
				self.xvel = min(
					self.xvel + (Player.SPEED / 2 if self.grounded else Player.SPEED),
					Player.MAX_SPEED,
				)

		if self.grounded and jumping:
			self.yvel = Player.JUMP
			self.grounded = 0

		if self.on_wall and jumping:
			self.xvel = Player.WALLJUMP_X * self.on_wall
			self.yvel = Player.WALLJUMP_Y
			self.on_wall = 0

		if self.grounded:
			self.xvel *= Player.GROUNDDRAG
			self.yvel = 0
		elif self.on_wall:
			self.xvel = 0
			self.yvel *= Player.WALLDRAG
		else:
			self.xvel *= Player.DRAG
			self.yvel *= Player.DRAG

		self.yvel += Player.GRAVITY

		self.xpos += self.xvel
		self.ypos += self.yvel

		self.grounded = 0
		self.on_wall = 0

		gnd = 0
		lwall = 0
		rwall = 0
		ceil = 0

		self.collider = pygame.Rect(self.xpos, self.ypos, self.size, self.size)

		for obj in OBJECTS:
			if self.collider.colliderect(obj):
				# bottom of player hits top of object
				if self.yvel > 0 and self.collider.top < obj.top:
					self.ypos = obj.top - self.size
					self.yvel = 0
					self.grounded = 1

				# top of player hits bottom of object
				if self.yvel < 0 and self.collider.bottom > obj.bottom:
					self.ypos = obj.bottom
					self.yvel = -0.8 * self.yvel

				# right of player hits left of object
				if self.xvel > 0 and self.collider.left < obj.left:
					self.xpos = obj.left - self.size + 1
					self.xvel = 0
					self.on_wall = 1

				# left of player hits right of object
				elif self.xvel < 0 and self.collider.right > obj.right:
					self.xpos = obj.right
					self.xvel = 0
					self.on_wall = -1

				# check for corner where player is both wall and ground
				if self.grounded and self.on_wall:
					print("corner")
					self.xvel = 0
					self.yvel = Player.VAULTJUMP
					self.on_wall = 0
					self.grounded = 0

	def draw(self, screen):
		mag = math.sqrt(self.xvel**2 + self.yvel**2)
		dir = math.atan2(self.yvel, self.xvel)

		if mag < 0.1:
			self.image

		screen.blit(self.image, (self.xpos, self.ypos))


def draw(player, objects=[]):
	SCREEN.fill((0, 0, 0))
	for obj in objects:
		pygame.draw.rect(SCREEN, (255, 255, 255), obj)
	player.draw(SCREEN)
	pygame.display.flip()


player = Player()


while True:
	CLOCK.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	keys = pygame.key.get_pressed()

	movement = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
	jumping = keys[pygame.K_UP]

	player.physics_step(movement, jumping, OBJECTS)
	draw(player, OBJECTS)
