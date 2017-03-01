import optparse
import math, re
from collections import deque
import sys, numpy

# implement polyhedron as a dict, each face number maps to the ccw list of its neighbors

J7 = {
    1: [2,3,4],
    2: [3,1,4,5],
    3: [4,1,2,6],
    4: [2,1,3,7],
    5: [6,2,7],
    6: [7,3,5],
    7: [5,4,6]
    }

J8 ={
    1: [2,3,4,5],
    2: [1,5,6,3],
    3: [1,2,7,4],
    4: [1,3,8,5],
    5: [1,4,9,2],
    6: [2,9,7],
    7: [3,6,8],
    8: [4,7,9],
    9: [5,8,6]
    }

T1= {
    1: [2,3],
    2: [3,1],
    3: [2,1]
    }

def renumberpoly(poly):
    newpoly = {}
    keys = poly.keys()
    for i in range(len(keys)):
        newpoly[i] = [keys.index(j) for j in poly[keys[i]]]
    return newpoly
    
def laplacian(poly):
    n = len(poly)
    L = [[0]*n for i in range(n)]
    for node, neighbors in poly.iteritems():
        nodenum = poly.keys().index(node)
        L[nodenum][nodenum] = float(len(neighbors))
        for neighbor in neighbors:
            neighnum = poly.keys().index(neighbor)
            L[nodenum][neighnum] = -1.0
    return L

def matrixtree(L):
    return numpy.linalg.det([row[:len(row)-1] for row in L][:len(L)-1])

polyangles = {
    3: 2,
    4: 3,
    6: 4
    }

class SpanningTrees:
    def __init__(self, poly, root, valid=True):
        self.poly = renumberpoly(poly)
        self.L = laplacian(self.poly)
        self.count = 0
        self.parent = {root:None}
        self.fringe = [(root,i) for i in self.poly[root]]
        self.valid = valid
        #eulerian tour (ET) is a ccw list of edges around the unfolding
        # where each edge is represented by the 2 faces it joins,
        # and the interior angle of the next vertex, in multiples of 30
        # i.e. 2 for triangles, 3 for squares etc
        self.euler = [(root,i,polyangles[len(self.poly[root])]) for i in self.poly[root]]
    def __iter__(self):
        return self.next()
    def next(self):
        while self.fringe:
            node, other = self.fringe.pop()
            if other in self.parent.keys(): continue
            #try with this edge in
            oldfringe = self.fringe[:] #saving for backtracking
            oldeuler = self.euler[:]
            oldL = [row[:] for row in self.L]
            maxangle = 0
            pos = [(a,b) for (a,b,c) in self.euler].index((node,other)) #finding the edge in ET we glue the new face to
            backedge = self.poly[other].index(node)
            neighbors = self.poly[other][backedge+1:] #getting all new edges of the ET in the right order
            neighbors.extend(self.poly[other][:backedge])
            angle = polyangles[len(self.poly[other])]
            self.euler = oldeuler[:pos]
            for neighbor in neighbors:
                self.euler.append((other,neighbor,angle))
            a,b,c = self.euler[-1]
            self.euler[-1] = (a,b,oldeuler[pos][2]+angle)
            maxangle = max(maxangle,oldeuler[pos][2]+angle)
            self.euler.extend(oldeuler[pos+1:])
            a,b,c = self.euler[(pos-1)%len(self.euler)]
            self.euler[(pos-1)%len(self.euler)] = (a,b,c+angle)
            maxangle = max(maxangle,c+angle)
            for i in self.poly[other]:  #add new edges to the fringe
                if not i in self.parent.keys():
                    self.fringe.append((other,i))
            self.parent[other] = node
            if (not self.valid) or maxangle < 11:
                if len(self.parent) == len(self.poly):  #we have a spanning tree
                    self.count += 1
                    yield ([c for a,b,c in self.euler], self.count)
                else:   #we recurse
                    for v in self.next():
                        yield v
            else:
                if len(self.parent) == len(self.poly):  #we have a spanning tree
                    self.count += 1
                else:
                    subL = [[self.L[i][j] for j in range(len(self.L[i])) if not j in self.parent.keys()]
                            for i in range(len(self.L)) if not i in self.parent.keys()]
                    self.count += numpy.linalg.det(subL)
            del self.parent[other]  #restore original state for backtracking
            self.euler = oldeuler[:]
            self.fringe = oldfringe[:]
            self.L = oldL
            #try with this edge out (implicitely)
            self.L[node][other]=0
            self.L[other][node]=0
            self.L[other][other] -= 1
            self.L[node][node] -= 1

def stitch (p1,i1,p2,i2): #glues edge i1 from p1 to edge i2 from p2, removes all edges that disappear.
    pp1 = p1*2
    pp2 = p2*2
    j1 = (i1-1) + len(p1)
    j2 = i2
    while pp1[j1]+pp2[j2] == 12:
        j1 = j1 - 1
        j2 = j2 + 1
    k1 = i1
    k2 = (i2-1) + len(p2)
    while pp1[k1]+pp2[k2] == 12:
        k1 = k1 + 1
        k2 = k2 - 1
    if pp1[j1]+pp2[j2] > 12 or pp1[j1]+pp2[j2] == 11 or pp1[k1]+pp2[k2] > 12 or pp1[k1]+pp2[k2] == 11:
        return False
    else:
        pp = pp1[k1+1:j1+1]
        pp[-1] += pp2[j2]
        pp.extend(pp2[j2+1:k2+1])
        pp[-1] += pp1[k1]
        return pp

def zero_adversary():
    def adv(carpet):
        return 0
    return adv

def one_adversary():
    def adv(carpet):
        return 1
    return adv

def last_adversary():
    def adv(carpet):
        return len(carpet)-1
    return adv

def maxofwidth_adversary(width=2):
    def adv(carpet):
        cc = carpet[:]
        for i in range(1,width):
            cc = [cc[j]+(carpet*2)[j+i] for j in range(len(cc))]
        return cc.index(max(cc)) 
    return adv

def longestpurse_adversary(turn=1, width=10):
    def adv(carpet):
        cc = [carpet[0]-6]
        for i in range(1,len(carpet)*2):
            cc.append(cc[-1]+(carpet*2)[i]-6)
        w = min(len(carpet),width)
        maxx = [max([cc[j+i]-cc[j] for j in range(len(carpet))]) for i in range(w)]
        goodidx = [i for i in range(w) if maxx[i] >= turn]
        maxwidth = max(goodidx)
        return (maxofwidth_adversary(maxwidth)(carpet) + maxwidth/2)%len(carpet)
#        return greedyedge(carpet,maxofwidth_adversary(maxwidth)(carpet),maxwidth)
    return adv

def greedyedge(carpet, pos, width):
    cc = carpet*2
    while width > 1:
        if cc[pos] < cc[pos+width-1]:
            pos += 1
        width -= 1
    return pos % len(carpet)
    
def tiletry(carpet,tile,depth=3, adversary = maxofwidth_adversary(2)): #tries to glue tile on carpet 'depth' times at positions determined by the adversary
    if depth == 0:
        return carpet
    cc = carpet[:]
#    for i in range(1,width):
#        cc = [cc[j]+(carpet*2)[j+i] for j in range(len(cc))]
#    maxpos = cc.index(max(cc)) #the adversary: glue on the 1st edge of the max sequence of length 'width'
    maxpos = adversary(carpet)
    for i in range(len(tile)):
        s = stitch(carpet,maxpos,tile,i)
        if s:
            ccc = tiletry(s,tile,depth-1, adversary)
            if ccc:
                return ccc
    return False

def tryallunfolds(poly,depth=3,root=1,width=2,candidates=None): #tries to glue each unfolding onto itself 'depth' times. if it returns false, poly is not TP!
    count = 0
    numtrees = matrixtree(laplacian(poly))
    if candidates:
        trees = candidates
        numcand = len(candidates)
    else:
        trees = SpanningTrees(poly,root)
        numcand = numtrees
    for (t,num) in trees:
        count += 1
        for w in range(1,width+1):
            carp = tiletry(t,t,depth,maxofwidth_adversary(w))
            if not carp:
                break
        if carp:
            carp = tiletry(t,t,depth,longestpurse_adversary())
        if carp:
            carp = tiletry(t,t,depth,zero_adversary())
        if carp:
            carp = tiletry(t,t,depth,one_adversary())
        if carp:
            carp = tiletry(t,t,depth,last_adversary())
        if carp:
            yield carp,t,num
        sys.stdout.write("%d / %.0f (est.), %.4f%% complete (est.), %.0f / %.0f cand: %d   \n\x1b[1A"%(count, count*numtrees/num, 100.0*num/numtrees, num, numtrees, numcand))
        sys.stdout.flush()
    print "%d / %.0f (est.), %.4f%% complete (est.), %.0f / %.0f cand: %d   "%(count, count, 100.0, numtrees, numtrees, numcand)

def strrots(s):
    for i in range(len(s)):
        yield s[i:]+s[:i]

def minrot(s):
    return min(strrots(s))

def tilestr(tile):
    return minrot(''.join([hex(t)[2] for t in tile]))

def makepath(tile): #compute coordinates (careful: roundoff errors)
    path = [(0,0),(1,0)]
    angle = 0
    for a in tile:
        angle += a - 6
        x,y = path[-1]
        path.append((x+math.cos(angle*math.pi/6.0), y+math.sin(angle*math.pi/6.0)))
    return path[:-1]

def chir(a,b,c):
    return a[0]*b[1]-b[0]*a[1]-(a[0]*c[1]-a[1]*c[0])+b[0]*c[1]-b[1]*c[0]

def dist(a,b):
    return math.sqrt((b[0]-a[0])**2+(b[1]-a[1])**2)

def inedges(p):
    lst = []
    for i in range(len(p)-1):
        for j in range(len(p)-1):
            if abs((i-j+1)%(len(p)-1))-1>1 and abs(dist(p[i],p[j])-1)<0.1 and chir(p[i-1],p[j],p[i+1])>0:
                lst.append([p[i],p[j]])
    return lst

def normpath(path):
    totx = 0.0
    toty = 0.0
    for (x,y) in path:
        totx += x
        toty += y
    return [(x-(totx/len(path)),y-(toty/len(path))) for (x,y) in path]

def pathtops(path, orig = (300,300), scale = 10, show=True): #generates postscript for a path
    ox,oy = orig
    s= "%f %f newpath moveto\n"%(path[0][0]*scale+ox,path[0][1]*scale+oy)
    for x,y in path:
        s += "%f %f lineto\n"%(ox+x*scale,oy+y*scale)
    s += "stroke\n"
    if show:
        s += "showpage\n"
    return s

def wrl2poly(filename):
    f = open(filename, 'r')
    s = f.read()
    f.close()
    m = re.findall("coordIndex *\[([^\]]+)\]",s)
    if not len(m) == 1:
        print "Can't read file"
        return False
    faces = re.split('-1,',m[0])
    faces = [[int(v.strip('\r\n ')) for v in re.split(',',a.strip('\r\n ,')) if v.strip('\r\n\t ')]
             for a in faces if a.strip('\r\n\t ')]
    print faces
    for face in faces:
        if not len(face) in [3,4,6]:
            print "Faces must be triangles, squares or hexagons!"
            return False
    poly = {}
    touched = set([0])
    fringe = [0]
    while fringe:
        facenum = fringe.pop()
#        print "face %d"%facenum
        face = faces[facenum]
#        print faces
#        print poly
        neighbors = []
        for edge in range(len(face)):
            i = face[edge]
            j = (face*2)[edge+1]
            others = [other for other in range(len(faces))
                      if j in faces[other] and (faces[other]*2)[faces[other].index(j)+1] == i ]
            if not len(others) == 1:
                others = [other for other in range(len(faces))
                          if other != facenum and i in faces[other] and (faces[other]*2)[faces[other].index(i)+1] == j ]                
                if len(others) == 1:
                    if others[0] in touched:
                        others = []
                    else:
#                        print "reverse %d"%others[0]
                        faces[others[0]].reverse()
            if not len(others) == 1:
                print "Can't find an edge (%d,%d) from face %d"%(i,j,facenum)
                return False
#            print "found %d"%others[0]
            if not others[0] in touched:
                touched.add(others[0])
                fringe.append(others[0])
            neighbors.append(others[0])
        poly[facenum] = neighbors
    return poly
    
optparser = optparse.OptionParser (
  usage = '%prog [options] poly.wrl')
optparser.add_option('-d', type="int", dest="depth", default = 3)
optparser.add_option('-w', type="int", dest="width", default = 1)
optparser.add_option('-p', action="store_true", dest="printnets", default=False)

def main ():
  options, args = optparser.parse_args ()
  if not args:
    optparser.error ('Please specify a poly.wrl to use.')
  poly =  wrl2poly(args[0])
  cand = None
  newcand = [] 
  if options.printnets:
    outfile = open("%s-tiles-p.ps"%(args[0]), 'w')
    outfile.write("%!PS\n\n")
    tilescount = 0
    for tile in SpanningTrees(poly,1):
        outfile.write(pathtops(normpath(makepath(tile[0])),orig=(50+30*(tilescount%18),700-32*(tilescount/18)),scale=5,show=False))
        tilescount += 1
    outfile.close()
    return
  mindepth = min(options.depth,5)
  for dd in range(mindepth,options.depth+1):
    outfile = open("%s-tiles-d%d.ps"%(args[0],dd), 'w')
    outfile.write("%!PS\n\n")
    tileseen = set()
    for tile in tryallunfolds(poly,depth=dd,root=0,width=options.width,candidates=cand):
        ts = tilestr(tile[1])
        if ts in tileseen:
            print "seen %s \n"%ts
        else:
            print "new %s \n"%ts
            newcand.append((tile[1],tile[2]))
            tileseen.add(ts)
            outfile.write(pathtops(makepath(tile[1])))
            outfile.write(pathtops(makepath(tile[0])))
        print tile
        print "found: %d"%len(newcand)
        print
    cand = newcand
    newcand = []
    print "DEPTH: %d, #tiles: %d\n"%(dd,len(cand)) 
    outfile.close()

if __name__ == '__main__': main ()
