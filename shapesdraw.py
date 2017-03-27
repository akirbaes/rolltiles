from tkinter import *
from Point import Point
from time import sleep
from math import pi
root = Tk(className ="Shapes representation") #add a root window named Myfirst GUI
graph = Canvas(root, width=1000, height=800) # add a label to root window
graph.pack()

#Represent the faces of the 3D shape that can be rolled
#Each shape gives its neighbours
J1R = { #order is clockwise (but unimportant here)
	0: [1,2,3,4],
	1: [0,4,2],
	2: [1,3,0],
	3: [0,2,4],
	4: [0,3,1]
}

p = 5
#Represents the cases of the 2D net that tiles the space
#The neighbours outside of the net are represented by their ID + k*p (p being bigger than the number of polygons)
#A same outside shape has a same k. For example, for the pyramid, there are 4 different shapes
#A shape that is on one side and on the other is k*p on one side and -k*p on the other side (for easy symmetry)
#The representation is recursive, meaning the ID+k*p part can be further be explored as part of a full net as (ID + k*p-1)%p+1 = ID
#This is a simple representation, but all the tiles that I can see from the document follow this pattern
J1N = { #order is clockwise
	0: [1,0-p,3,0+p],
	1: [0,2+p,2],
	2: [1,4+2*p,1-p],
	3: [0,4-p,4],
	4: [3+p,3,2-2*p]
}

tetraR = {
	0: [1,2,3],
	1: [2,0,3],
	2: [0,1,3],
	3: [0,2,1]
}

p=4
tetraN = {
	0: [1,2,3],
	1: [3-p,2-2*p,0],
	2: [0,1+2*p,3-3*p],
	3: [0,2+3*p,1+p]
}

p=6

cubeR = {
	0: [1,2,4,3],
	1: [0,3,5,2],
	2: [0,1,5,4],
	3: [0,4,5,1],
	4: [0,2,5,3],
	5: [1,3,4,2]
}


cubeN = {
	0: [1,2,4,3],
	1: [0,2-p,5,5+2*p],
	2: [0,5+2*p,1+p,3+p],
	3: [0,4+p,4+2*p,2-p],
	4: [0,3-2*p,3-p,4],
	5: [5,2-2*p,1-2*p,1]
}
#Here, an exception, 5 goes to 5 symmetrically and 6 goes to 6 symmetrically

J1 = 0
tetra = 1
cube = 2

Rolls = [J1R, tetraR, cubeR]
Nets = [J1N, tetraN, cubeN]

current = cube #####

roll = Rolls[current]
net = Nets[current]
	
def pointAngle(a,b,c):
	#Course formula: [AB]x[BC] product
	return ((b.x-a.x)*(c.y-b.y) - (b.y-a.y)*(c.x-b.x));


def square(p1,p2):
	#creates a rectangle clockwise to p1,p2
	p1 = p1
	p2 = p2
	
	p34 = p1-p2
	p3 = p2 + Point(p34.y,-p34.x)
	p4 = p3+p34
	return p1,p2,p3,p4
	
def triangle(p1,p2):
	#creates a triangle clockwise to p1,p2
	p1 = p1
	p2 = p2
	p3 = p1 + (p2-p1).rotate(pi/3)
	"""pb = p1 + ((p2-p1)/2)
	ph = 
	dist = (p2-p1)"""
	return p1,p2,p3
	
def hexagon(p1,p2):
	#creates a triangle clockwise to p1,p2
	p1 = p1
	p2 = p2
	sol = [p1, p2]
	pa = p1
	pb = p2
	for i in range(4):
		pn = pb + (pa-pb).rotate(-2*pi/3)
		sol.append(pn)
		pa = pb
		pb = pn
	"""pb = p1 + ((p2-p1)/2)
	ph = 
	dist = (p2-p1)"""
	return sol
	
colors = ("black","red","yellow","cyan","magenta","blue","green")
def make(points,color=0):
	list = []
	w = 1+(color==0)*2
	#print(color)
	c = colors[color]
	for i,point in enumerate(points):
		next = points[(i+1)%len(points)]
		list.append(graph.create_line((point.x,point.y),(next.x,next.y),fill=c,width=w))
	return list

def makefill(points,color=0,full=False):
	if(full):
		s = ""
	else:
		s = "gray50"
	c = colors[color]
	return graph.create_polygon([(p.x,p.y) for p in points], fill=c, stipple=s) 
	
def number(id,point):
	graph.create_text((point.x,point.y),text=str(id))
def numcenter(id,points):
	number(id,sum(points,Point(0,0))/len(points))
def numbours(id,neighbours,points):
	m=sum(points,Point(0,0))/len(points)
	number(id,m)
	for i in range(len(neighbours)):
		p1 = points[i]
		p2 = points[(i+1)%len(points)]
		p = ((p1+p2)/2+m)/2
		number(neighbours[i]%len(order),p)

"""i = w.create_line(xy, fill="red")
w.coords(i, new_xy) # change coordinates
w.itemconfig(i, fill="blue") # change color

w.delete(i) # remove"""

p1 = Point(300,300)
p2 = Point(350,300)



		

shape = net
shapes = []
shapespoly = []
order = sorted(shape)

class Poly:
	def __init__(self,id,points):
		self.n = []
		self.id = id
		self.points = points
		realid = id%len(order)
		self.pid = make(points,int((id-realid)/len(order)))
		#print(points)
		number(realid,sum(points,Point(0,0))/len(points))
		
	def order(self,neighbor):
		index = self.n.index(neighbor)
		return self.n[neighbor:]+self.n[:neighbor]
	def fill(self,neighbours):
		self.n = list(neighbours)
	def __eq__(self,other):
		return self.id == other
	def remplis(self):
		graph.create_polygon([(p.x,p.y) for p in self.points], fill="red",stipple="gray50") 

def extend(p1,p2,newshape,oldshape=None):
	print(end="Draw the")
	realshape = newshape%len(order)
	if(len(shape[realshape]))==3:
		points = triangle(p1,p2)
		print(" triangle ",newshape)
	elif(len(shape[realshape]))==4:
		points = square(p1,p2)
		print(" square ",newshape)
	else:
		points = hexagon(p1,p2)
		print(" hexagon ",newshape)
		
	shapespoly.append(Poly(newshape,points))
	current = shape[realshape]
	if(oldshape!=None and newshape==realshape):
		#print(oldshape,"in",current,newshape,realshape)
		index = current.index(oldshape)
		current =  current[index:]+current[:index]
		print("Previous:",oldshape,"Next:",current)
	shapespoly[-1].fill(current)
	shapes.append(newshape)
	
	root.update()
	sleep(0.5)
	#print("I have",len(points),"points")
	if(newshape==realshape):
		for index,p in enumerate(current):
			#print(index)
			p1 = points[index%len(points)]
			p2 = points[(index+1)%len(points)]
			if not p in shapes or p==newshape and not (newshape != p and p==oldshape):
				###[TODO] ici pose problème de retourner à même shape
				#print(p,shapes)
				#print("Work",newshape)
				if(p==newshape):
					p+=len(order)
				extend(p2,p1,p,newshape)
		
				
extend(p1,p2,order[0])

root.update()
sleep(3)

"""
Two things:
the face, and the orientation
The orientation = current face (its shape) and order

For example, we went 2-3 on the net, and 4-1 on the shape

So on face 3, if face 3 is 2,4,6, we note, 4,X,X (the important part is the 4 at the beginning of the 1 face, matching the order in face 3)
We re-order them from the smallest face, so that it always matches

Same orientation as beginning: fill the normal set
Then go into a new set: until meet an orientation that we already met before, then stop


Algo:
If orientation is not in face
	Add orientation in face (and draw it)
	Try out possible rolls (same shape, adjacent)
else:
	found (draw it differently)
"""
print("#"*30)

orientations = dict()
for face in roll:
	orientations[face] = []
start = 1
#case = part of J1 net on which we are rolling
#face = part of J1R polyhedron which is looking at the floor
def explore(p1,p2,case,face,previouscase=None,previousface=None):
	print("Exploring",previouscase,"-",case,"with face",previousface,"-",face)
	
	#else same shape
	if(len(roll[face])==3):
		points = triangle(p1,p2)
	elif(len(roll[face])==4):
		points = square(p1,p2)
	else:
		points = hexagon(p1,p2)
		
	if(len(net[case]) != len(roll[face])):
		make(points,-2)
		#different shapes: incompatible
		return
		
	currentCaseNeighbours = net[case]
	currentFaceNeighbours = roll[face]
	if(previouscase!=None):
		#décalage : previouscase n'est pas le bas, le bas réel l'est: on fait l'inverse de la rotation pour qu'elle y soit
		print(currentCaseNeighbours)
		caseOrientation = currentCaseNeighbours.index(previouscase) #décalage actuel par rapport à la normale
		points = points[-caseOrientation:]+points[:-caseOrientation]
		#currentCaseNeighbours = currentCaseNeighbours[caseOrientation:] + currentCaseNeighbours[:caseOrientation]
		
		#décalage : previousface doit être le bas: on fait une rotation pour qu'elle y soit
		faceOrientation = currentFaceNeighbours.index(previousface)
		#décalage: la face du bas doit être la même que celle de l'orientation que la case
		faceOrientation = (faceOrientation - caseOrientation)%len(order)
		currentFaceNeighbours = currentFaceNeighbours[faceOrientation:] + currentFaceNeighbours[:faceOrientation]
	orientation = currentFaceNeighbours
	print("My orientation is",orientation)
	if(orientation in orientations[case]):
		#already visited like this
		makefill(points,-1,True)
		make(points,2)
		numbours(case,currentCaseNeighbours,points)
		return
	else:
		make(points)
		makefill(points,1)
		numbours(case,currentCaseNeighbours,points)
		orientations[case].append(orientation)
		for i in range(len(currentFaceNeighbours)):
			print(i)
			nextcasereal = currentCaseNeighbours[i]
			nextface = currentFaceNeighbours[i]
			p1 = points[i%len(points)]
			p2 = points[(i+1)%len(points)]
			nextcase = nextcasereal%len(order)
			difference = nextcasereal-nextcase
			if(nextface!=previousface):
				root.update()
				sleep(0.05)
				explore(p2,p1,nextcase,nextface,case-difference,face)
			

explore(p1,p2,0,0)
print("Finished!")
for face in sorted(orientations):
	print("orientations found for face",face,":", len(orientations[face]))
	print(orientations[face])
root.mainloop()