from math import pi
import pygame
import sys
from time import perf_counter

W,H = 900, 760
CYAN = '#10a0ff'
ORANGE = '#ffa010'
RED = "#ff1020"
GREEN = '#00ff40'
SCALE = 100
w,h = W/(2*SCALE), H/(2*SCALE)
NOrig = (w,h)

Vec = pygame.Vector2

def NS(v, s, O):
	nv = Vec(v.x, -v.y)
	return (nv + O)*s

def SN(v, s, O):
	nv = Vec(v.x, v.y)
	nv = nv/s - O
	return Vec(nv.x, -nv.y)

def ray_gen(n, pos=Vec(), off=2):
	ray_arr = []
	gap = off/n
	i = -off/2 + pos.y
	while i <= off/2 + pos.y:
		ray_arr.append(Ray(Vec(pos.x, i)))
		i += gap
	return ray_arr


class Mirror:
	def __init__(self, pos=Vec(0,0), R=1, C=1, color='yellow', width=3):
		self.pos = pos
		self.r = R
		self.curve = C
		self.color = color
		self.w = width

	def show(self, surf):
		pos = NS(self.pos, SCALE, NOrig)
		self.rct = pygame.Rect(pos, (2*self.r*SCALE, 2*self.r*SCALE))
		self.rct.center = pos
		pygame.draw.circle(surf, RED, pos, 3)
		if self.curve == -1:
			pygame.draw.arc(surf, self.color, self.rct, pi/2,3/2*pi, self.w)
		else:
			pygame.draw.arc(surf, self.color, self.rct, -pi/2, pi/2, self.w)


class Ray:
	def __init__(self, pos=Vec(0, 0), slope=Vec(1, 0), color= CYAN, width=1 ,depth=0):
		self.pos = pos
		self.dirc = slope.normalize()
		self.length = w
		self.w = width
		self.color = color
		self.itr = 0
		self.depth = depth

	def show(self, surf):
		pos = NS(self.pos, SCALE, NOrig)
		if self.depth > 0:
			self.color = GREEN
		
		if self.itr:
			hit = NS(self.itr, SCALE, NOrig)
			pygame.draw.aaline(surf, self.color, pos, hit, 1)

		else:
			endpt = NS(self.pos + self.dirc*2*w, SCALE, NOrig)
			pygame.draw.aaline(surf, self.color, pos, endpt,1)


class System:
	def __init__(self, mir_pos = Vec(), mir_type=1, rays = 10, ray_pos = Vec(), offset = 2, max_depth=1):
		self.mirror = Mirror(mir_pos, C=mir_type)
		self.ray_no = rays
		self.ray_pos = ray_pos
		self.ray_offset = offset
		self.max_depth = max_depth
		self.rays = ray_gen(self.ray_no, self.ray_pos, self.ray_offset)

	def inter_reflect(self, ray_lst):
		for ray in ray_lst:
			ray.itr = 0
			if ray.depth < self.max_depth:
				R = ray.pos
				dirc = ray.dirc

				U = self.mirror.pos - R
				U1 = dirc * U.dot(dirc)
				U2 = U - U1

				d = U2.magnitude()
				if d <= self.mirror.r:
					m = (self.mirror.r**2 - d**2)**.5

					P = R+U1 + dirc*self.mirror.curve*m
					ray.itr = P
					n = (self.mirror.pos - P).normalize()
					d = ray.dirc
					r = d - n * 2*(d.dot(n))
					self.rays.append(Ray(P, r, ray.color, depth=ray.depth+1))


	def render(self, surf, motion):
		# LOGIC
		moveVec = SN(Vec(motion), SCALE, NOrig)
		if moveVec != self.mirror.pos:
			self.mirror.pos = moveVec
			self.rays = self.rays[:self.ray_no]
			self.inter_reflect(self.rays)
		
		# UI
			for ray in self.rays:
				ray.show(surf)
			
			self.mirror.show(surf)
			display.update()



pygame.init()
screen = pygame.display.set_mode((W,H))
display = pygame.display
clock = pygame.time.Clock()

# Setup
Sys = System(mir_type = 1, rays = 20, ray_pos = Vec(-w,0), offset = 1, max_depth=1)
Sys.mirror.r = 1

run = True
while run:
	t1 = perf_counter()
	clock.tick(60)
	screen.fill('black')

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	
	Sys.render(screen, pygame.mouse.get_pos())
	
	t2 = perf_counter()

	fps = f"{1/(t2-t1):.0f}"
	display.set_caption(fps)
