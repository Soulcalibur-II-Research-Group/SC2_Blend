import io
import math
import struct
from model_fmt_sc2 import FRead

# キャラクター／武器モデル用の軸入れ替え。ステージでは不要。
def fix_axis(x,y,z):
	return (z,y,-x)

class MTX(object):
	def ident(self):
		return [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]
	def eulerZYX(self,x,y,z):
		a = math.cos(x); bb = math.sin(x)
		c = math.cos(y); d = math.sin(y)
		e = math.cos(z); f = math.sin(z)
		ae = a*e; af = a*f; be = bb*e; bf = bb*f
		return [c*e, be*d-af, ae*d+bf,
				c*f, bf*d+ae, af*d-be,
				-d,  bb*c,    a*c]
	def mul(self,A,B):
		return [
			A[0]*B[0]+A[1]*B[3]+A[2]*B[6], A[0]*B[1]+A[1]*B[4]+A[2]*B[7], A[0]*B[2]+A[1]*B[5]+A[2]*B[8],
			A[3]*B[0]+A[4]*B[3]+A[5]*B[6], A[3]*B[1]+A[4]*B[4]+A[5]*B[7], A[3]*B[2]+A[4]*B[5]+A[5]*B[8],
			A[6]*B[0]+A[7]*B[3]+A[8]*B[6], A[6]*B[1]+A[7]*B[4]+A[8]*B[7], A[6]*B[2]+A[7]*B[5]+A[8]*B[8],
		]
	def apply(self,m,x,y,z):
		return (m[0]*x+m[1]*y+m[2]*z, m[3]*x+m[4]*y+m[5]*z, m[6]*x+m[7]*y+m[8]*z)
	def transpose(self,m):
		return [m[0],m[3],m[6], m[1],m[4],m[7], m[2],m[5],m[8]]

class BRead(object):
	def __init__(self,b):
		self.b = b
	def u8(self,o):
		return self.b[o]
	def u16(self,o):
		return struct.unpack_from('<H',self.b,o)[0]
	def u32(self,o):
		return struct.unpack_from('<I',self.b,o)[0]
	def u64(self,o):
		return struct.unpack_from('<Q',self.b,o)[0]
	def f32(self,o):
		return struct.unpack_from('<f',self.b,o)[0]

class VMP(object):
	PSMCT32 = 0
	PSMT8 = 19
	PSMT4 = 20
	BLOCK32 = [
		[0,1,4,5,16,17,20,21],[2,3,6,7,18,19,22,23],
		[8,9,12,13,24,25,28,29],[10,11,14,15,26,27,30,31]]
	COL32 = [
		[0,1,4,5,8,9,12,13],[2,3,6,7,10,11,14,15],
		[16,17,20,21,24,25,28,29],[18,19,22,23,26,27,30,31],
		[32,33,36,37,40,41,44,45],[34,35,38,39,42,43,46,47],
		[48,49,52,53,56,57,60,61],[50,51,54,55,58,59,62,63]]
	BLOCK4 = [
		[0,2,8,10],[1,3,9,11],[4,6,12,14],[5,7,13,15],
		[16,18,24,26],[17,19,25,27],[20,22,28,30],[21,23,29,31]]
	COL4 = [
		[0,8,32,40,64,72,96,104,2,10,34,42,66,74,98,106,4,12,36,44,68,76,100,108,6,14,38,46,70,78,102,110],
		[16,24,48,56,80,88,112,120,18,26,50,58,82,90,114,122,20,28,52,60,84,92,116,124,22,30,54,62,86,94,118,126],
		[65,73,97,105,1,9,33,41,67,75,99,107,3,11,35,43,69,77,101,109,5,13,37,45,71,79,103,111,7,15,39,47],
		[81,89,113,121,17,25,49,57,83,91,115,123,19,27,51,59,85,93,117,125,21,29,53,61,87,95,119,127,23,31,55,63],
		[192,200,224,232,128,136,160,168,194,202,226,234,130,138,162,170,196,204,228,236,132,140,164,172,198,206,230,238,134,142,166,174],
		[208,216,240,248,144,152,176,184,210,218,242,250,146,154,178,186,212,220,244,252,148,156,180,188,214,222,246,254,150,158,182,190],
		[129,137,161,169,193,201,225,233,131,139,163,171,195,203,227,235,133,141,165,173,197,205,229,237,135,143,167,175,199,207,231,239],
		[145,153,177,185,209,217,241,249,147,155,179,187,211,219,243,251,149,157,181,189,213,221,245,253,151,159,183,191,215,223,247,255],
		[256,264,288,296,320,328,352,360,258,266,290,298,322,330,354,362,260,268,292,300,324,332,356,364,262,270,294,302,326,334,358,366],
		[272,280,304,312,336,344,368,376,274,282,306,314,338,346,370,378,276,284,308,316,340,348,372,380,278,286,310,318,342,350,374,382],
		[321,329,353,361,257,265,289,297,323,331,355,363,259,267,291,299,325,333,357,365,261,269,293,301,327,335,359,367,263,271,295,303],
		[337,345,369,377,273,281,305,313,339,347,371,379,275,283,307,315,341,349,373,381,277,285,309,317,343,351,375,383,279,287,311,319],
		[448,456,480,488,384,392,416,424,450,458,482,490,386,394,418,426,452,460,484,492,388,396,420,428,454,462,486,494,390,398,422,430],
		[464,472,496,504,400,408,432,440,466,474,498,506,402,410,434,442,468,476,500,508,404,412,436,444,470,478,502,510,406,414,438,446],
		[385,393,417,425,449,457,481,489,387,395,419,427,451,459,483,491,389,397,421,429,453,461,485,493,391,399,423,431,455,463,487,495],
		[401,409,433,441,465,473,497,505,403,411,435,443,467,475,499,507,405,413,437,445,469,477,501,509,407,415,439,447,471,479,503,511]]

	class Header(object):
		def __init__(self):
			self.State = 0
			self.RelocSelector = 0
			self.RelocCount = 0
			self.Version = 0
			self.unk0 = 0
			self.unk1 = 0
			self.Contents = 0
			self.ObjectCount = 0
			self.BoneCount = 0
			self.BoneTableOffset = 0
			self.TextureSectionOffset = 0
			self.unk2 = 0
			self.CalcStreamOffset = 0
			self.DrawStreamOffset = 0
			self.unk3 = 0
			self.ObjectPointers = []
		def read(self,f):
			self.State = f.u8()
			self.RelocSelector = f.u8()
			self.RelocCount = f.u8()
			f.u8()
			self.Version = f.u8()
			self.unk0 = f.u8()
			self.unk1 = f.u8()
			self.Contents = f.u8()
			self.ObjectCount = f.u16()
			self.BoneCount = f.u16()
			f.u16()
			f.u16()
			self.BoneTableOffset = f.u32()
			self.TextureSectionOffset = f.u32()
			self.unk2 = f.u32()
			self.CalcStreamOffset = f.u32()
			self.DrawStreamOffset = f.u32()
			self.unk3 = f.u32()
			self.ObjectPointers = []
			for x in range(self.ObjectCount):
				self.ObjectPointers.append(f.u32())
		def __str__(self):
			rt = ""
			rt += str("Contents: %i\n" % self.Contents)
			rt += str("ObjectCount: %i\n" % self.ObjectCount)
			rt += str("BoneCount: %i @ %s\n" % (self.BoneCount,hex(self.BoneTableOffset)))
			rt += str("TextureSectionOffset: %s\n" % hex(self.TextureSectionOffset))
			rt += str("CalcStreamOffset: %s\n" % hex(self.CalcStreamOffset))
			rt += str("DrawStreamOffset: %s\n" % hex(self.DrawStreamOffset))
			return rt

	# 1件64バイト。回転は回転数のEulerで、ZYX順に適用。
	class BoneInfo(object):
		def __init__(self):
			self.EndPositionXYZScale = [0.0,0.0,0.0,0.0]
			self.StartPositionXYZScale = [0.0,0.0,0.0,0.0]
			self.Rotation = [0.0,0.0,0.0]
			self.BoneNameOffset = 0
			self.unk0 = [0.0,0.0,0.0]
			self.unk1 = 0
			self.BoneParentIdx = 0xFF
			self.BoneIdx = 0
			self.boneType = 0
			self.Name = ""
			self.X = 0.0
			self.Y = 0.0
			self.Z = 0.0
			self.Parent = -1
		def to_dict(self):
			return {'Name':self.Name,
					'EndPositionXYZScale':self.EndPositionXYZScale,
					'StartPositionXYZScale':self.StartPositionXYZScale,
					'Rotation':self.Rotation,
					'Unk0':self.unk0,'unk1':self.unk1,
					'BoneParentIdx':self.BoneParentIdx,
					'BoneIdx':self.BoneIdx,'boneType':self.boneType,
					'X':self.X,'Y':self.Y,'Z':self.Z,'Parent':self.Parent}
		def read(self,f,b=None):
			self.EndPositionXYZScale = list(f.f32_4())
			self.StartPositionXYZScale = list(f.f32_4())
			self.Rotation = list(f.f32_3())
			self.BoneNameOffset = f.u32()
			self.unk0 = list(f.f32_3())
			self.unk1 = f.u8()
			self.BoneParentIdx = f.u8()
			self.BoneIdx = f.u8()
			self.boneType = f.u8()
			if(self.BoneNameOffset and b is not None):
				p = self.BoneNameOffset
				if(p < len(b)):
					e = p
					while e < len(b) and e < p+64 and b[e] != 0:
						e += 1
					self.Name = b[p:e].decode('ascii','replace')

	class Node(object):
		def __init__(self):
			self.Type = 0
			self.RefCount = 0
			self.Offset = 0
			self.ShapeRefs = []
		def read(self,f,b):
			self.Offset = f.tell()
			if(self.Offset+8 > len(b)):
				return
			self.Type = b[self.Offset]
			self.RefCount = b[self.Offset+1]
			sa = 0
			if(self.Type == 0):
				sa = self.Offset+0x08
			elif(self.Type == 1):
				sa = self.Offset+0x28
			self.ShapeRefs = []
			if(sa == 0):
				return
			br = BRead(b)
			for x in range(self.RefCount):
				if(sa+(x+1)*4 > len(b)):
					break
				sref = br.u32(sa+x*4)
				if(sref == 0 or sref+8 > len(b)):
					continue
				layer = b[sref]
				block = br.u32(sref+4)
				self.ShapeRefs.append((layer,block))

	class Shape(object):
		def __init__(self):
			self.Name = ""
			self.Layer = 0
			self.Skinned = False
			self.Material = -1
			self.VertStart = 0
			self.VertCount = 0
			self.TriStart = 0
			self.TriCount = 0
		def __str__(self):
			rt = ""
			if(self.Skinned):
				rt += "SKINNED\n"
			else:
				rt += "STATIC\n"
			rt += str("Layer: %i\n" % self.Layer)
			rt += str("Material: %i\n" % self.Material)
			rt += str("VertCount: %i @ %i\n" % (self.VertCount,self.VertStart))
			rt += str("TriCount: %i @ %i\n" % (self.TriCount,self.TriStart))
			return rt

	class Material(object):
		def __init__(self):
			self.Name = ""
			self.Rgba = None
			self.W = 0
			self.H = 0
			self.Cutout = False

	class TextureUpload(object):
		def __init__(self):
			self.DBP = 0
			self.DPSM = 0
			self.RRW = 0
			self.RRH = 0
			self.DBW = 0
			self.Data = b''

	class TexEntry(object):
		def __init__(self):
			self.Psm = 0
			self.Tbw = 0
			self.W = 0
			self.H = 0

	# ワールド空間、事前スキン済み。各影響はInf=[bone,weight,lx,ly,lz,lnx,lny,lnz]。
	class Vertex(object):
		def __init__(self,x=0.0,y=0.0,z=0.0,nx=0.0,ny=1.0,nz=0.0,u=0.0,v=0.0,inf=None):
			self.X = x; self.Y = y; self.Z = z
			self.Nx = nx; self.Ny = ny; self.Nz = nz
			self.U = u; self.V = v
			self.Inf = inf if inf is not None else []

	class Tri(object):
		def __init__(self,a=0,b=0,c=0,mat=0):
			self.A = a; self.B = b; self.C = c
			self.Mat = mat

	class DrawRef(object):
		def __init__(self):
			self.Payload = 0
			self.Tex = 0
			self.Qwc = 0
			self.Op = 0

	class PacketVert(object):
		def __init__(self,x=0,y=0,z=0,nx=0,ny=1,nz=0,u=0,v=0,valid=False,face=0,inf=None):
			self.X = x; self.Y = y; self.Z = z
			self.Nx = nx; self.Ny = ny; self.Nz = nz
			self.U = u; self.V = v
			self.Valid = valid
			self.Face = face
			self.Inf = inf if inf is not None else []

	class VifBatch(object):
		def __init__(self):
			self.Pos = []
			self.Nrm = []
			self.Uv = []
			self.Ctrl = []

	def __init__(self):
		self.header = self.Header()
		self.bones = []
		self.boneInfo = self.bones
		self.shapes = []
		self.materials = []
		self.textures = []
		self.verts = []
		self.tris = []
		self.nodes = []
		self.b = b''
		self.br = BRead(b'')
		self.mtx = MTX()
		self.stage = False
		self.boneCount = 0
		self.boneTab = 0
		self.locR = []
		self.locT = []
		self.par = []
		self.btype = []
		self.bflags = []
		self.wr = []
		self.wt = []
		self.done = []
		self.active = []
		self.uploads = []
		self.uploadAt = {}
		self.uploadsAt = {}
		self.texInfo = {}
		self.matCache = {}
		self.blankMat = -1
		self.blockInfo = {}
		self.calcBones = {}
		self.palette = []
		self.shapeIdx = 0
		self.localBone = -1
		self.seen = set()

	# CSM1。32件ごとに8-15と16-23のエントリを入れ替える。
	def clut_reorder(self,x):
		return (x & 0xE7) | ((x & 0x08) << 1) | ((x & 0x10) >> 1)

	def unswizzle8(self,buf,w,h):
		outb = bytearray(w*h)
		blen = len(buf)
		for y in range(h):
			for x in range(w):
				blockLoc = (y & ~0xf)*w + (x & ~0xf)*2
				swapSel = (((y+2)>>2) & 0x1)*4
				ypos = (((y & ~3)>>1) + (y & 1)) & 0x7
				colLoc = ypos*w*2 + ((x+swapSel) & 0x7)*4
				byteSel = ((y>>1) & 1) + ((x>>2) & 2)
				s = blockLoc + colLoc + byteSel
				outb[y*w+x] = buf[s] if s < blen else 0
		return outb

	def pixel_offset(self,psm,x,y,bufferWidth):
		if(psm == self.PSMCT32):
			pw,ph,bw,bh,cw,ch = 64,32,8,4,8,8
			bt,ct = self.BLOCK32,self.COL32
		else:
			pw,ph,bw,bh,cw,ch = 128,128,4,8,32,16
			bt,ct = self.BLOCK4,self.COL4
		blockSize = cw*ch
		pageSize = blockSize*bw*bh
		pageX = x // pw; pageY = y // ph
		subX = x % pw; subY = y % ph
		pagesWide = max(1,(bufferWidth+pw-1)//pw) if bufferWidth > 0 else 1
		blockId = bt[(subY//ch) % bh][(subX//cw) % bw]
		column = ct[subY % ch][subX % cw]
		return (pageY*pagesWide + pageX)*pageSize + blockId*blockSize + column

	def buffer_width(self,width,psm,tbw):
		if(tbw > 0):
			return tbw if psm == self.PSMCT32 else (tbw << 1)
		return width

	def max_offset(self,psm,w,h,bufferWidth,nibble):
		mx = 0
		for y in range(h):
			for x in range(w):
				off = self.pixel_offset(psm,x,y,bufferWidth)
				if(not nibble):
					off *= 4
				if(off > mx):
					mx = off
		return mx

	def decode_psmt4(self,data,width,height,clut,tbw,uploadW,uploadH,uploadDbw):
		if(clut is None or width <= 0 or height <= 0 or uploadW <= 0 or uploadH <= 0):
			return None
		pal = bytearray(16*4)
		for x in range(16):
			if(x*4+4 > len(clut)):
				break
			pal[x*4] = clut[x*4]
			pal[x*4+1] = clut[x*4+1]
			pal[x*4+2] = clut[x*4+2]
			pal[x*4+3] = min(255,clut[x*4+3]*2)
		bufW = self.buffer_width(width,self.PSMT4,tbw)
		upBufW = self.buffer_width(uploadW,self.PSMCT32,uploadDbw)
		gsLen = max(len(data),
			max(self.max_offset(self.PSMCT32,uploadW,uploadH,upBufW,False)+4,
				self.max_offset(self.PSMT4,width,height,bufW,True)+1))
		if(gsLen > 64*1024*1024):
			print("tex buffer too big %i" % gsLen)
			return None
		gs = bytearray(gsLen)
		for y in range(uploadH):
			for x in range(uploadW):
				src = (y*uploadW + x)*4
				if(src+4 > len(data)):
					continue
				dst = self.pixel_offset(self.PSMCT32,x,y,upBufW)*4
				if(dst+4 > len(gs)):
					continue
				gs[dst:dst+4] = data[src:src+4]
		rgba = bytearray(width*height*4)
		for y in range(height):
			for x in range(width):
				nib = self.pixel_offset(self.PSMT4,x,y,bufW)
				at = nib >> 1
				if(at >= len(gs)):
					continue
				idx = (gs[at] >> ((nib & 1) << 2)) & 0xF
				p = idx*4
				t = (y*width + x)*4
				rgba[t] = pal[p]; rgba[t+1] = pal[p+1]
				rgba[t+2] = pal[p+2]; rgba[t+3] = pal[p+3]
		return bytes(rgba)

	def read(self,f):
		if(hasattr(f,'read')):
			pos = f.tell()
			f.seek(0,2)
			sz = f.tell()
			f.seek(0)
			self.b = f.read(sz)
			f.seek(pos)
		else:
			self.b = f
		b = self.b
		self.br = BRead(b)
		if(len(b) < 0x40):
			print("bad header size %i" % len(b))
			return
		fr = FRead(io.BytesIO(b))
		self.header.read(fr)
		self.stage = (self.header.Contents == 0)
		self.boneCount = self.header.BoneCount
		self.boneTab = self.header.BoneTableOffset

		self.read_bones()
		self.read_textures()
		self.read_nodes()
		self.read_draw_stream()
		self.fix_winding()
		self.read_bone_names()

	def read_bones(self):
		n = self.boneCount
		b = self.b
		br = self.br
		mtx = self.mtx
		self.locR = [None]*n
		self.locT = [None]*n
		self.par = [0]*n
		self.btype = [0]*n
		self.bflags = [0]*n
		fixedUp = [False]*n
		# type 3ボーンにはこの事前回転が必要。理由は未解明だが、形式に従う。
		corr = mtx.mul(mtx.eulerZYX(0,math.pi/2,0),mtx.eulerZYX(0,0,math.pi/2))
		boneTab = self.boneTab
		for x in range(n):
			o = boneTab + x*0x40
			if(o+0x40 > len(b)):
				self.locR[x] = mtx.ident()
				self.locT[x] = [0.0,0.0,0.0]
				self.par[x] = -1
				continue
			r = mtx.eulerZYX(br.f32(o+0x20)*math.pi*2,
							 br.f32(o+0x24)*math.pi*2,
							 br.f32(o+0x28)*math.pi*2)
			self.btype[x] = b[o+0x3F]
			self.bflags[x] = b[o+0x3C]
			p = b[o+0x3D]
			if(p == 0xFF or p >= n):
				p = -1
			self.par[x] = p
			inherited = (p >= 0 and p < x and fixedUp[p])
			if(self.btype[x] == 3 and not inherited):
				r = mtx.mul(corr,r)
				fixedUp[x] = True
			else:
				fixedUp[x] = inherited
			self.locR[x] = r
			self.locT[x] = [br.f32(o+0x10),br.f32(o+0x14),br.f32(o+0x18)]
		self.wr = [None]*n
		self.wt = [None]*n
		self.done = [False]*n
		self.active = [False]*n
		for x in range(n):
			self.compose_world(x)

	def compose_world(self,i):
		mtx = self.mtx
		if(self.done[i]):
			return (self.wr[i],self.wt[i])
		if(self.active[i]):
			print("Cyclic bone binding at %i" % i)
			return (mtx.ident(),list(self.locT[i]))
		self.active[i] = True
		p = self.par[i]
		if(p < 0):
			pr = mtx.ident()
			t = list(self.locT[i])
		else:
			ppr,ppt = self.compose_world(p)
			pr = ppr
			vx,vy,vz = mtx.apply(ppr,self.locT[i][0],self.locT[i][1],self.locT[i][2])
			t = [ppt[0]+vx,ppt[1]+vy,ppt[2]+vz]
		localR = self.locR[i]
		if(self.btype[i] == 7):
			tgt = self.bflags[i]
			if(tgt >= 0 and tgt < self.boneCount and not self.active[tgt]):
				tp = self.compose_world(tgt)[1]
				ax = tp[0]-t[0]; ay = tp[1]-t[1]; az = tp[2]-t[2]
				al = math.sqrt(ax*ax+ay*ay+az*az)
				if(al > 1e-6):
					ax /= al; ay /= al; az /= al
					yx = 0.0; yy = az; yz = -ay
					yl = math.sqrt(yy*yy+yz*yz)
					if(yl > 1e-6):
						yy /= yl; yz /= yl
						zx = ay*yz - az*yy
						zy = az*yx - ax*yz
						zz = ax*yy - ay*yx
						zl = math.sqrt(zx*zx+zy*zy+zz*zz)
						if(zl > 1e-6):
							zx /= zl; zy /= zl; zz /= zl
							want = [ax,yx,zx, ay,yy,zy, az,yz,zz]
							localR = mtx.mul(mtx.transpose(pr),want)
		self.wr[i] = mtx.mul(pr,localR)
		self.wt[i] = t
		self.done[i] = True
		self.active[i] = False
		return (self.wr[i],self.wt[i])

	def read_bone_names(self):
		n = self.boneCount
		boneTab = self.boneTab
		b = self.b
		self.bones = []
		self.boneInfo = self.bones
		if(n == 0 or boneTab + n*0x40 > len(b)):
			return
		fr = FRead(io.BytesIO(b))
		for x in range(n):
			o = boneTab + x*0x40
			fr.seek(o)
			bi = self.BoneInfo()
			bi.read(fr,b)
			p = b[o+0x3D]
			name = bi.Name
			xx,yy,zz = fix_axis(self.wt[x][0],self.wt[x][1],self.wt[x][2])
			bi.Name = name if len(name) > 0 else ("bone%i" % x)
			bi.Parent = -1 if (p == 0xFF or p >= n) else p
			bi.BoneParentIdx = p
			bi.boneType = b[o+0x3F]
			bi.X = float(xx); bi.Y = float(yy); bi.Z = float(zz)
			self.bones.append(bi)

	def read_textures(self):
		b = self.b
		br = self.br
		ts = br.u32(0x14)
		end = len(b)
		ups = []
		if(ts != 0 and ts < end):
			dbp = 0; dpsm = 0; dbw = 1; rrw = 0; rrh = 0
			have = False
			o = ts
			while o+16 <= end and o < ts+0x9000:
				data = br.u64(o)
				reg = br.u64(o+8) & 0xFF
				d0 = br.u32(o); d1 = br.u32(o+4)
				if(reg == 0x50):
					dbp = (data >> 32) & 0x3FFF
					dbw = (data >> 48) & 0x3F
					dpsm = (data >> 56) & 0x3F
					have = False
				elif(reg == 0x52):
					rrw = data & 0xFFF
					rrh = (data >> 32) & 0xFFF
					have = True
				elif((d0 & 0x70000000) == 0x30000000 and have):
					n = (d0 & 0xFFFF)*16
					ptr = ts + d1
					if(n > 0 and n <= 0x100000 and ptr+n <= end and dpsm == 0
					   and rrw >= 1 and rrw <= 256 and rrh >= 1 and rrh <= 256):
						u = self.TextureUpload()
						u.DBP = int(dbp); u.DPSM = int(dpsm)
						u.RRW = int(rrw); u.RRH = int(rrh); u.DBW = int(dbw)
						u.Data = bytes(b[ptr:ptr+n])
						ups.append(u)
					have = False
				o += 16
		self.uploads = ups
		self.textures = self.uploads
		self.uploadAt = {}
		self.uploadsAt = {}
		for u in self.uploads:
			self.uploadAt[u.DBP] = u
			self.uploadsAt.setdefault(u.DBP,[]).append(u)
		m = {}
		off = br.u32(0x14)
		if(off != 0 and off+0x20 <= len(b)):
			sec = off
			v0 = b[sec]
			if(v0 == 8 or v0 == 9):
				fld = 0x24 if v0 == 9 else 0x14
				t = br.u32(sec+fld)
				if(t > 0 and sec+t+0x20 <= len(b)):
					sec += t
					ver = b[sec]
					if(ver == 2 or ver == 3):
						count = b[sec+5]
						table = br.u32(sec+0x0C)
						for x in range(count):
							refOff = sec + table + x*4
							if(refOff < 0 or refOff+4 > len(b)):
								break
							raw = br.u32(refOff)
							info = sec + (raw & ~0xF)
							if(info < 0 or info+0x28 > len(b)):
								continue
							lo = br.u32(info+0x20)
							te = self.TexEntry()
							te.W = br.u16(info+0x0C)
							te.H = br.u16(info+0x0E)
							te.Psm = (lo >> 20) & 0x3F
							te.Tbw = (lo >> 14) & 0x3F
							m[int(lo & 0x3FFF)] = te if (int(lo & 0x3FFF) not in m or te.W * te.H >= m[int(lo & 0x3FFF)].W * m[int(lo & 0x3FFF)].H) else m[int(lo & 0x3FFF)]
			else:
				ver = b[sec]
				if(ver == 2 or ver == 3):
					count = b[sec+5]
					table = br.u32(sec+0x0C)
					for x in range(count):
						refOff = sec + table + x*4
						if(refOff < 0 or refOff+4 > len(b)):
							break
						raw = br.u32(refOff)
						info = sec + (raw & ~0xF)
						if(info < 0 or info+0x28 > len(b)):
							continue
						lo = br.u32(info+0x20)
						te = self.TexEntry()
						te.W = br.u16(info+0x0C)
						te.H = br.u16(info+0x0E)
						te.Psm = (lo >> 20) & 0x3F
						te.Tbw = (lo >> 14) & 0x3F
						m[int(lo & 0x3FFF)] = te if (int(lo & 0x3FFF) not in m or te.W * te.H >= m[int(lo & 0x3FFF)].W * m[int(lo & 0x3FFF)].H) else m[int(lo & 0x3FFF)]
		self.texInfo = m

	def find_clut(self,cbp,need):
		direct = self.uploadAt.get(cbp)
		if(direct is not None and direct.DPSM == 0 and len(direct.Data) >= need):
			return direct
		best = None
		for u in self.uploads:
			if(u.DPSM == 0 and len(u.Data) >= need):
				if(best is None or len(u.Data) < len(best.Data)):
					best = u
		return best

	def blank_material(self):
		if(self.blankMat < 0):
			self.blankMat = len(self.materials)
			m = self.Material()
			m.Name = "untex"
			self.materials.append(m)
		return self.blankMat

	def resolve_material(self,tbp0,cbp,tcc,layer):
		key = (tbp0,cbp,layer)
		if(key in self.matCache):
			return self.matCache[key]
		img = self.uploadAt.get(tbp0)
		if(img is None):
			self.matCache[key] = self.blank_material()
			return self.matCache[key]
		te = self.texInfo.get(tbp0)
		is4bit = (te is not None and te.Psm == self.PSMT4 and te.W > 0 and te.H > 0)
		clut = self.find_clut(cbp, 64 if is4bit else 1024)
		if(clut is None):
			self.matCache[key] = self.blank_material()
			return self.matCache[key]
		if(is4bit):
			t4 = self.texInfo[tbp0]
			w = t4.W; h = t4.H
			dec = self.decode_psmt4(img.Data,w,h,clut.Data,t4.Tbw,img.RRW,img.RRH,img.DBW)
			if(dec is None):
				self.matCache[key] = self.blank_material()
				return self.matCache[key]
			rgba = dec
		else:
			if(te is not None and te.W > 0 and te.H > 0):
				w = te.W; h = te.H
			else:
				w = img.RRW*2; h = img.RRH*2
			if(w <= 0 or h <= 0):
				self.matCache[key] = self.blank_material()
				return self.matCache[key]
			if(len(img.Data) < w*h and tbp0 in self.uploadsAt):
				pick = None
				for u in self.uploadsAt[tbp0]:
					if(len(u.Data) >= w*h and (pick is None or len(u.Data) < len(pick.Data))):
						pick = u
				if(pick is not None):
					img = pick
			if(len(img.Data) < w*h):
				self.matCache[key] = self.blank_material()
				return self.matCache[key]
			pal = bytearray(256*4)
			cb = clut.Data
			for x in range(256):
				if(x*4+3 >= len(cb)):
					break
				d = self.clut_reorder(x)*4
				pal[d] = cb[x*4]
				pal[d+1] = cb[x*4+1]
				pal[d+2] = cb[x*4+2]
				pal[d+3] = min(255,cb[x*4+3]*2)
			px = bytearray(img.Data[:w*h])
			idx = self.unswizzle8(px,w,h)
			rgba_ba = bytearray(w*h*4)
			for x in range(w*h):
				ci = idx[x]*4
				rgba_ba[x*4] = pal[ci]
				rgba_ba[x*4+1] = pal[ci+1]
				rgba_ba[x*4+2] = pal[ci+2]
				rgba_ba[x*4+3] = pal[ci+3]
			rgba = bytes(rgba_ba)
		hasAlpha = False
		for x in range(w*h):
			if(rgba[x*4+3] == 0):
				hasAlpha = True
				break
		cutout = (tcc != 0 and hasAlpha and layer >= 1)
		mi = len(self.materials)
		mat = self.Material()
		mat.Name = "t%i" % tbp0
		mat.Rgba = rgba; mat.W = w; mat.H = h; mat.Cutout = cutout
		self.materials.append(mat)
		self.matCache[key] = mi
		return mi

	def material_from_setup(self,setup,layer):
		b = self.b
		br = self.br
		if(setup == 0 or setup >= len(b)):
			return self.blank_material()
		j = 0
		while j+16 <= 0x90 and setup+j+16 <= len(b):
			if((br.u64(setup+j+8) & 0xFF) == 0x06):
				v = br.u64(setup+j)
				return self.resolve_material(int(v & 0x3FFF),int((v >> 37) & 0x3FFF),
											  int((v >> 34) & 1),layer)
			j += 16
		return self.blank_material()

	def material_for_block(self,block,layer):
		b = self.b
		br = self.br
		r = 0
		while r+8 <= 0x80 and block+r+8 <= len(b):
			if(br.u32(block+r) == 0x06011403):
				setup = br.u32(block+r+4)
				j = 0
				while j+16 <= 0x90 and setup+j+16 <= len(b):
					if((br.u64(setup+j+8) & 0xFF) == 0x06):
						v = br.u64(setup+j)
						return self.resolve_material(int(v & 0x3FFF),int((v >> 37) & 0x3FFF),
													  int((v >> 34) & 1),layer)
					j += 16
				break
			r += 4
		return self.blank_material()

	def read_nodes(self):
		b = self.b
		br = self.br
		count = br.u16(0x08)
		self.nodes = []
		self.blockInfo = {}
		fr = FRead(io.BytesIO(b))
		for x in range(count):
			node = br.u32(0x28 + x*4)
			if(node == 0 or node+8 > len(b)):
				continue
			n = self.Node()
			fr.seek(node)
			n.read(fr,b)
			self.nodes.append(n)
			for layer,block in n.ShapeRefs:
				self.blockInfo[block] = (layer,n.Type)

	def read_calc_stream(self,at):
		m = {}
		b = self.b
		br = self.br
		if(at == 0 or at >= len(b)):
			return m
		pp = at
		cur = -1
		for x in range(65536):
			if(pp+1 >= len(b)):
				break
			op = b[pp]
			if(op == 0):
				break
			if(op == 4):
				cur = b[pp+1]
				pp += 4
				continue
			if(op == 3):
				cur = -1
			elif(op == 6 and pp+8 <= len(b)):
				m[br.u32(pp+4)] = cur
			pp += 0xC if op == 11 else 8
		return m

	def read_draw_stream(self):
		b = self.b
		br = self.br
		self.calcBones = self.read_calc_stream(br.u32(0x1C))
		pp = br.u32(0x20)
		lastPalette = ""
		self.palette = []
		self.shapeIdx = 0
		self.localBone = -1
		self.seen = set()
		for x in range(500000):
			if(pp >= len(b)):
				break
			cmd = b[pp]
			if(cmd == 0):
				break
			if(cmd == 6):
				key = br.u32(pp+4)
				self.localBone = self.calcBones.get(key,-1)
				pp += 8
			elif(cmd == 7):
				n = b[pp+1]
				np = []
				for y in range(n):
					if(pp+4+y >= len(b)):
						break
					np.append(b[pp+4+y])
				key = ",".join(str(z) for z in np)
				if(key != lastPalette):
					self.shapeIdx = 0
					lastPalette = key
				self.palette = np
				pp += 0x24
			elif(cmd == 0xB):
				self.read_shape(br.u32(pp+4))
				pp += 8
				self.shapeIdx += 1
			elif(cmd == 2):
				pp += 0xC
			elif(cmd == 5 or cmd == 0xC or cmd == 0xD or cmd == 0xE):
				pp += 4
			else:
				pp += 8

	def walk_list(self,cursor,refs,visited):
		b = self.b
		br = self.br
		if(cursor >= len(b) or cursor in visited):
			return
		visited.add(cursor)
		tex = 0; branch = 0
		for x in range(256):
			if(cursor+2 > len(b)):
				break
			op = b[cursor]; size = b[cursor+1]
			if(op == 0 or size == 0):
				break
			if(op == 3 and size >= 8):
				p = br.u32(cursor+4)
				if(p > 0 and p < len(b)):
					tex = p
			elif((op == 2 or op == 5) and size >= 8):
				p = br.u32(cursor+4)
				if(p > 0 and p < len(b)):
					r = self.DrawRef()
					r.Payload = p; r.Tex = tex
					r.Qwc = br.u16(cursor+2) if op == 2 else 0
					r.Op = op
					refs.append(r)
			elif(op == 1 and size >= 8):
				np = br.u32(cursor+4)
				if(np > 0 and np < len(b)):
					self.walk_list(np,refs,visited)
			elif(op == 4 and size >= 8):
				branch = br.u32(cursor+4)
			elif(op == 6 and branch != 0):
				self.walk_list(branch,refs,visited)
			cursor += size

	def read_shape(self,block):
		br = self.br
		if(block == 0 or block >= len(self.b)):
			return
		if(self.localBone >= 0 and self.localBone < self.boneCount):
			rigidBone = self.localBone
		elif(len(self.palette) > 0):
			rigidBone = self.palette[min(self.shapeIdx,len(self.palette)-1)]
		else:
			rigidBone = 0
		ni = self.blockInfo.get(block,(0,0))
		startV = len(self.verts)
		startT = len(self.tris)
		refs = []
		visited = set()
		self.walk_list(block,refs,visited)
		for r in refs:
			if(r.Tex != 0):
				mat = self.material_from_setup(r.Tex,ni[0])
			else:
				mat = self.material_for_block(block,ni[0])
			if(self.stage):
				if(r.Op == 2 and r.Qwc >= 4 and r.Payload not in self.seen):
					self.seen.add(r.Payload)
					self.add_stage_mesh(r.Payload,r.Qwc,mat)
				continue
			dg = r.Payload + 0x10
			if(dg+0x10 <= len(self.b)
			   and br.u32(dg+4) == 0x303E4000
			   and (br.u32(dg+8) & 0xFFF) == 0x412):
				if(r.Payload not in self.seen):
					self.seen.add(r.Payload)
					self.add_skinned_mesh(self.read_skinned_packet(r.Payload),mat)
				continue
			o = r.Payload
			for x in range(1000):
				if(o+16 > len(self.b)):
					break
				idb = self.b[o+3]
				addr = br.u32(o+4)
				if(idb == 0x30):
					if(addr in self.seen):
						o += 16
						continue
					self.seen.add(addr)
					gt = addr + 0x10
					if(gt+0x10 <= len(self.b)
					   and br.u32(gt+4) == 0x303E4000
					   and (br.u32(gt+8) & 0xFFF) == 0x412):
						self.add_skinned_mesh(self.read_skinned_packet(addr),mat)
					else:
						self.add_rigid_mesh(addr,rigidBone,mat)
					o += 16
				elif(idb == 0x60):
					break
				else:
					o += 16
		shape = self.Shape()
		shape.Name = "shape%i" % len(self.shapes)
		shape.Layer = ni[0]
		shape.Skinned = (not self.stage) and ni[1] == 1
		if(len(self.tris) > startT):
			shape.Material = self.tris[startT].Mat
		else:
			shape.Material = -1
		shape.VertStart = startV
		shape.VertCount = len(self.verts) - startV
		shape.TriStart = startT
		shape.TriCount = len(self.tris) - startT
		self.shapes.append(shape)

	# 影響ブロックの後にUVブロック。すべて重みを事前乗算済み。
	def read_skinned_packet(self,addr):
		b = self.b
		br = self.br
		mtx = self.mtx
		verts = []
		end = len(b)
		nloop = br.u32(addr+0x10) & 0x7FFF
		cur = addr + 0x20
		while cur+0x20 <= end and len(verts) < nloop:
			posX = posY = posZ = 0.0
			nx = ny = nz = 0.0
			wsum = 0.0
			u = v = 0.0
			gotUv = False
			face = 0
			infl = []
			for x in range(64):
				if(cur+0x20 > end):
					break
				# 一部パケットではカラーqwordがゼロになるため、両方の条件を確認する。
				isUv = False
				if(cur+0x20 <= len(b)):
					if(br.u32(cur+28) == 0x43000000):
						isUv = True
					elif(br.u32(cur+8) == 0x3F800000 and br.u32(cur+12) <= 1):
						isUv = True
				if(isUv):
					u = br.f32(cur); v = br.f32(cur+4); face = br.u32(cur+12)
					cur += 0x20; gotUv = True
					break
				w = br.f32(cur+12); x0 = br.f32(cur)
				if(w > 0 and w <= 1 and abs(x0) <= 2):
					lx = br.f32(cur)/w; ly = br.f32(cur+4)/w; lz = br.f32(cur+8)/w
					lnx = br.f32(cur+16)/w; lny = br.f32(cur+20)/w; lnz = br.f32(cur+24)/w
					slot = b[cur+28] >> 2
					bone = self.palette[slot] if slot < len(self.palette) else -1
					if(bone >= 0 and bone < self.boneCount):
						infl.append([bone,w,lx,ly,lz,lnx,lny,lnz])
						px,py,pz = mtx.apply(self.wr[bone],lx,ly,lz)
						posX += (px + self.wt[bone][0])*w
						posY += (py + self.wt[bone][1])*w
						posZ += (pz + self.wt[bone][2])*w
						rnx,rny,rnz = mtx.apply(self.wr[bone],lnx,lny,lnz)
						nx += rnx*w; ny += rny*w; nz += rnz*w
					wsum += w
				ctrl = b[cur+29]
				cur += 0x20
				if(ctrl == 0x00):
					continue
				if(ctrl == 0x80):
					for y in range(12):
						if(cur+0x20 > end):
							break
						isUv2 = False
						if(cur+0x20 <= len(b)):
							if(br.u32(cur+28) == 0x43000000):
								isUv2 = True
							elif(br.u32(cur+8) == 0x3F800000 and br.u32(cur+12) <= 1):
								isUv2 = True
						if(isUv2):
							break
						if(br.u32(cur) != 0 or br.u32(cur+12) != 0):
							break
						cur += 0x20
					isUv3 = False
					if(cur+0x20 <= len(b)):
						if(br.u32(cur+28) == 0x43000000):
							isUv3 = True
						elif(br.u32(cur+8) == 0x3F800000 and br.u32(cur+12) <= 1):
							isUv3 = True
					if(isUv3):
						u = br.f32(cur); v = br.f32(cur+4); face = br.u32(cur+12)
						cur += 0x20; gotUv = True
					break
			if(not gotUv):
				if(wsum < 0.001):
					verts.append(self.PacketVert(0,0,0,0,1,0,0,0,False,1))
					continue
				break
			if(wsum > 0.01):
				nl = math.sqrt(nx*nx+ny*ny+nz*nz)
				if(nl < 1e-8):
					nl = 1.0
				verts.append(self.PacketVert(posX,posY,posZ,nx/nl,ny/nl,nz/nl,u,v,True,face,infl))
			else:
				verts.append(self.PacketVert(0,0,0,0,1,0,0,0,False,face))
		return verts

	def add_skinned_mesh(self,pv,mat):
		start = len(self.verts)
		for p in pv:
			x,y,z = fix_axis(p.X,p.Y,p.Z)
			nx,ny,nz = fix_axis(p.Nx,p.Ny,p.Nz)
			self.verts.append(self.Vertex(float(x),float(y),float(z),
										  float(nx),float(ny),float(nz),p.U,p.V,p.Inf))
		flip = False; prev = False
		for x in range(2,len(pv)):
			if(pv[x].Face == 0):
				prev = flip
				if(pv[x].Valid and pv[x-1].Valid and pv[x-2].Valid):
					a = start+x-2; c = start+x-1; d = start+x
					if(flip):
						self.tris.append(self.Tri(c,a,d,mat))
					else:
						self.tris.append(self.Tri(a,c,d,mat))
				flip = not flip
			else:
				flip = prev

	def read_vif_batch(self,addr):
		batch = self.VifBatch()
		b = self.b
		br = self.br
		o = addr; end = len(b)
		for x in range(8000):
			if(o+4 > end):
				break
			word = br.u32(o)
			cmd = (word >> 24) & 0x7F
			num = (word >> 16) & 0xFF
			if(num == 0):
				num = 256
			imm = word & 0xFFFF
			if((cmd & 0x60) == 0x60):
				dest = (imm & 0x3FF) & 0xF
				comps = ((cmd >> 2) & 3) + 1
				data = o + 4
				if(dest == 3 and comps == 4):
					for y in range(num):
						p = data + y*0x10
						if(p+0x10 > end):
							break
						batch.Pos.append([br.f32(p),br.f32(p+4),br.f32(p+8)])
						batch.Ctrl.append(br.u32(p+0xC))
				elif(dest == 4 and comps == 3):
					for y in range(num):
						p = data + y*0xC
						if(p+0xC > end):
							break
						batch.Nrm.append([br.f32(p),br.f32(p+4),br.f32(p+8)])
				elif(dest == 1 and comps == 2):
					for y in range(num):
						p = data + y*8
						if(p+8 > end):
							break
						batch.Uv.append([br.f32(p),br.f32(p+4)])
				o = data + num*comps*4
			elif(cmd <= 0x07 or cmd == 0x10 or cmd == 0x11 or cmd == 0x13):
				o += 4
			else:
				break
		return batch

	# posのwのbit15はADC。2回連続すると再開および三角形破棄を示す。
	def add_rigid_mesh(self,addr,bone,mat):
		batch = self.read_vif_batch(addr)
		n = len(batch.Pos)
		if(n < 3 or bone < 0 or bone >= self.boneCount):
			return
		mtx = self.mtx
		r = self.wr[bone]; t = self.wt[bone]
		start = len(self.verts)
		for x in range(n):
			px,py,pz = mtx.apply(r,batch.Pos[x][0],batch.Pos[x][1],batch.Pos[x][2])
			xx,yy,zz = fix_axis(px+t[0],py+t[1],pz+t[2])
			lnx = batch.Nrm[x][0] if x < len(batch.Nrm) else 0.0
			lny = batch.Nrm[x][1] if x < len(batch.Nrm) else 1.0
			lnz = batch.Nrm[x][2] if x < len(batch.Nrm) else 0.0
			rnx,rny,rnz = mtx.apply(r,lnx,lny,lnz)
			nx,ny,nz = fix_axis(rnx,rny,rnz)
			uu = batch.Uv[x][0] if x < len(batch.Uv) else 0.0
			vv = batch.Uv[x][1] if x < len(batch.Uv) else 0.0
			self.verts.append(self.Vertex(float(xx),float(yy),float(zz),
										  float(nx),float(ny),float(nz),uu,vv,
										  [[bone,1.0,batch.Pos[x][0],batch.Pos[x][1],batch.Pos[x][2],
											lnx,lny,lnz]]))
		bad = [False]*n
		restart = [False]*n
		for x in range(n):
			px = batch.Pos[x][0]; py = batch.Pos[x][1]; pz = batch.Pos[x][2]
			if(math.isnan(px) or math.isinf(px) or abs(px) > 1e10
			   or abs(py) > 1e10 or abs(pz) > 1e10):
				bad[x] = True
				continue
			c = batch.Ctrl[x] if x < len(batch.Ctrl) else 0
			adc = (c & 0x8000) != 0
			prevAdc = (x > 0 and x-1 < len(batch.Ctrl) and (batch.Ctrl[x-1] & 0x8000) != 0)
			nextAdc = (x+1 < len(batch.Ctrl) and (batch.Ctrl[x+1] & 0x8000) != 0)
			restart[x] = adc and (prevAdc or nextAdc)
		for x in range(n-2):
			if(bad[x] or bad[x+1] or bad[x+2] or restart[x+2]):
				continue
			a = start+x; c = start+x+1; d = start+x+2
			if((x & 1) == 0):
				self.tris.append(self.Tri(a,d,c,mat))
			else:
				self.tris.append(self.Tri(a,c,d,mat))

	def add_stage_mesh(self,payload,qwc,mat):
		b = self.b
		br = self.br
		vertStart = payload + 16
		payloadEnd = vertStart + (qwc-1)*16
		posSec = -1; nrmSec = -1; uvSec = -1
		posCount = 0
		scan = vertStart
		while scan+4 <= payloadEnd and scan+4 <= len(b):
			cmd = b[scan+3]
			if(cmd < 0x60 or cmd > 0x7F):
				scan += 4
				continue
			num = b[scan+2]
			if(num < 3 or num > 250):
				scan += 4
				continue
			dest = br.u16(scan) & 0x7FFF
			if(cmd == 0x6C and dest == 0x0003 and posSec < 0):
				posSec = scan+4; posCount = num
			elif(cmd == 0x68 and dest == 0x0004 and nrmSec < 0):
				nrmSec = scan+4
			elif(cmd == 0x64 and dest == 0x0001 and uvSec < 0):
				uvSec = scan+4
			if(posSec >= 0 and nrmSec >= 0 and uvSec >= 0):
				break
			scan += 4
		if(posSec < 0 or posCount < 3):
			return
		start = len(self.verts)
		bad = [False]*posCount
		restart = [False]*posCount
		for x in range(posCount):
			p = posSec + x*16
			if(p+16 > len(b)):
				bad[x] = True
				self.verts.append(self.Vertex(0,0,0,0,1,0,0,0))
				continue
			xx = br.f32(p); yy = br.f32(p+4); zz = br.f32(p+8)
			w = br.u32(p+12)
			nx = 0.0; ny = 1.0; nz = 0.0
			if(nrmSec >= 0):
				np = nrmSec + x*12
				if(np+12 <= len(b)):
					nx = br.f32(np); ny = br.f32(np+4); nz = br.f32(np+8)
			uu = 0.0; vv = 0.0
			if(uvSec >= 0):
				up = uvSec + x*8
				if(up+8 <= len(b)):
					uu = br.f32(up); vv = br.f32(up+4)
			self.verts.append(self.Vertex(xx,yy,zz,nx,ny,nz,uu,vv))
			restart[x] = (w & 0x8000) != 0
			bad[x] = (not restart[x]) and (math.isnan(xx) or math.isinf(xx))
		for x in range(posCount-2):
			if(bad[x] or bad[x+1] or bad[x+2] or restart[x+2]):
				continue
			a = start+x; c = start+x+1; d = start+x+2
			if((x & 1) == 0):
				self.tris.append(self.Tri(a,d,c,mat))
			else:
				self.tris.append(self.Tri(a,c,d,mat))

	def fix_winding(self):
		verts = self.verts
		tris = self.tris
		for x in range(len(tris)):
			tr = tris[x]
			pa = verts[tr.A]; pb = verts[tr.B]; pc = verts[tr.C]
			ux = pb.X-pa.X; uy = pb.Y-pa.Y; uz = pb.Z-pa.Z
			vx = pc.X-pa.X; vy = pc.Y-pa.Y; vz = pc.Z-pa.Z
			fx = uy*vz - uz*vy; fy = uz*vx - ux*vz; fz = ux*vy - uy*vx
			dn = (fx*(pa.Nx+pb.Nx+pc.Nx)
				  + fy*(pa.Ny+pb.Ny+pc.Ny)
				  + fz*(pa.Nz+pb.Nz+pc.Nz))
			if(dn < 0):
				tris[x] = self.Tri(tr.A,tr.C,tr.B,tr.Mat)

def load(path):
	v = VMP()
	with open(path,'rb') as f:
		v.read(f)
	return v
