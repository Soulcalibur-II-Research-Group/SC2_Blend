import struct, math

def U8(f,o):  return f[o]
def S8(f,o):  return f[o]-256 if f[o]>=128 else f[o]
def U16(f,o): return struct.unpack_from("<H",f,o)[0]
def S16(f,o): return struct.unpack_from("<h",f,o)[0]
def U32(f,o): return struct.unpack_from("<I",f,o)[0]
def F32(f,o): return struct.unpack_from("<f",f,o)[0]


class Bone(object):
	def __init__(self):
		self.Name = ""
		self.Parent = -1
		self.X = 0.0; self.Y = 0.0; self.Z = 0.0

class Vertex(object):
	def __init__(self,x=0.0,y=0.0,z=0.0,nx=0.0,ny=1.0,nz=0.0,u=0.0,v=0.0,inf=None):
		self.X=x; self.Y=y; self.Z=z
		self.Nx=nx; self.Ny=ny; self.Nz=nz
		self.U=u; self.V=v
		self.Inf = inf if inf is not None else []

class Tri(object):
	def __init__(self,a=0,b=0,c=0,mat=0):
		self.A=a; self.B=b; self.C=c; self.Mat=mat

class Material(object):
	def __init__(self):
		self.Name=""; self.Rgba=None; self.W=0; self.H=0; self.Cutout=False


def m3_ident(): return [[1.0,0,0],[0,1.0,0],[0,0,1.0]]

# 4x4行優先行列。行ベクトルv*M。
def M4_ident():
	return [[1.0,0,0,0],[0,1.0,0,0],[0,0,1.0,0],[0,0,0,1.0]]
def M4_mul(A,B):
	return [[A[i][0]*B[0][j]+A[i][1]*B[1][j]+A[i][2]*B[2][j]+A[i][3]*B[3][j] for j in range(4)] for i in range(4)]
def M4_trans(x,y,z):
	M=M4_ident(); M[3][0]=x; M[3][1]=y; M[3][2]=z; return M
def M4_scale(s):
	M=M4_ident(); M[0][0]=s; M[1][1]=s; M[2][2]=s; return M
# YPR → クォータニオン
def quat_ypr(yaw,pitch,roll):
	hr=roll*.5; hp=pitch*.5; hy=yaw*.5
	sr=math.sin(hr); cr=math.cos(hr); sp=math.sin(hp); cp=math.cos(hp); sy=math.sin(hy); cy=math.cos(hy)
	return (cy*sp*cr+sy*cp*sr, sy*cp*cr-cy*sp*sr, cy*cp*sr-sy*sp*cr, cy*cp*cr+sy*sp*sr)
def M4_from_quat(q):
	x,y,z,w=q
	xx=x*x; yy=y*y; zz=z*z; xy=x*y; wz=z*w; xz=z*x; wy=y*w; yz=y*z; wx=x*w
	M=M4_ident()
	M[0][0]=1-2*(yy+zz); M[0][1]=2*(xy+wz);   M[0][2]=2*(xz-wy)
	M[1][0]=2*(xy-wz);   M[1][1]=1-2*(zz+xx); M[1][2]=2*(yz+wx)
	M[2][0]=2*(xz+wy);   M[2][1]=2*(yz-wx);   M[2][2]=1-2*(yy+xx)
	return M
def rad(turn): return turn*2.0*math.pi   # 回転数 → ラジアン


# VXT：DXT1/3/5、P8/ARGB8（Morton順）。
def _565(v):
	r=(v>>11)&0x1F; g=(v>>5)&0x3F; b=v&0x1F
	return ((r<<3)|(r>>2),(g<<2)|(g>>4),(b<<3)|(b>>2))

def _decode_dxt(data,w,h,mode):
	# 1=DXT1、3=DXT3、5=DXT5。並べ替えなしのリニア配置。
	bs = 8 if mode==1 else 16
	bw=max(1,(w+3)//4); bh=max(1,(h+3)//4)
	out=bytearray(w*h*4)
	pos=0
	for by in range(bh):
		for bx in range(bw):
			if pos+bs>len(data): break
			alpha=[255]*16
			if mode==5:
				a0=data[pos]; a1=data[pos+1]
				bits=0
				for k in range(6): bits|=data[pos+2+k]<<(k*8)
				for k in range(16):
					code=(bits>>(k*3))&7
					if a0>a1:
						alpha[k]=[a0,a1,(6*a0+a1)//7,(5*a0+2*a1)//7,(4*a0+3*a1)//7,(3*a0+4*a1)//7,(2*a0+5*a1)//7,(a0+6*a1)//7][code]
					else:
						alpha[k]=[a0,a1,(4*a0+a1)//5,(3*a0+2*a1)//5,(2*a0+3*a1)//5,(a0+4*a1)//5,0,255][code]
				pos+=8
			elif mode==3:
				for k in range(8):
					bb=data[pos+k]; alpha[k*2]=(bb&0xF)*17; alpha[k*2+1]=(bb>>4)*17
				pos+=8
			c0=data[pos]|data[pos+1]<<8; c1=data[pos+2]|data[pos+3]<<8
			rows=data[pos+4]|data[pos+5]<<8|data[pos+6]<<16|data[pos+7]<<24
			pos+=8
			col=[_565(c0),_565(c1)]
			if mode==1 and c0<=c1:
				col.append(tuple((col[0][i]+col[1][i])//2 for i in range(3))); col.append((0,0,0))
			else:
				col.append(tuple((2*col[0][i]+col[1][i])//3 for i in range(3)))
				col.append(tuple((col[0][i]+2*col[1][i])//3 for i in range(3)))
			for py in range(4):
				for px in range(4):
					ix=bx*4+px; iy=by*4+py
					if ix>=w or iy>=h: continue
					pi=py*4+px
					code=(rows>>(pi*2))&3
					r,g,b=col[code]
					a=alpha[pi] if mode!=1 else (255 if not(mode==1 and c0<=c1 and code==3) else 0)
					t=(iy*w+ix)*4
					out[t]=r; out[t+1]=g; out[t+2]=b; out[t+3]=a
	return bytes(out)

def _morton(x,y):
	r=0
	for bit in range(16):
		r|=((x>>bit)&1)<<(2*bit)
		r|=((y>>bit)&1)<<(2*bit+1)
	return r

def _decode_p8(d,dataOff,w,h,pal):
	out=bytearray(w*h*4)
	for y in range(h):
		for x in range(w):
			s=dataOff+_morton(x,y)
			idx=d[s] if s<len(d) else 0
			p=idx*4
			t=(y*w+x)*4
			if p+3<len(pal):
				out[t]=pal[p+2]; out[t+1]=pal[p+1]; out[t+2]=pal[p]; out[t+3]=pal[p+3]
			else:
				out[t+3]=255
	return bytes(out)

def _decode_argb8(d,dataOff,w,h):
	out=bytearray(w*h*4)
	for y in range(h):
		for x in range(w):
			s=dataOff+_morton(x,y)*4
			t=(y*w+x)*4
			if s+3<len(d):
				out[t]=d[s+2]; out[t+1]=d[s+1]; out[t+2]=d[s]; out[t+3]=d[s+3]
			else:
				out[t+3]=255
	return bytes(out)


class VMX(object):

	def __init__(self):
		self.f=b''; self.header={}
		self.bones=[]; self.verts=[]; self.tris=[]; self.materials=[]
		self.wr=[]; self.wt=[]
		self.counts=[0,0,0,0]; self.vrec=[]; self.poolPos=[]; self.poolNrm=[]

	def read(self,f):
		if hasattr(f,'read'): f=f.read()
		self.f=f
		if f[:3]!=b'VMX':
			print("Not a VMX file"); return
		self.read_header()
		self.read_bones()
		self.build_bone_world()
		self.read_weights()
		self.read_textures()
		self.build_mesh()

	def read_header(self):
		f=self.f
		self.header=dict(
			contents=U8(f,0x09),
			nMtx=U16(f,0x0A), n1=U16(f,0x0C), n2=U16(f,0x0E), n3=U16(f,0x10),
			nBone=U16(f,0x12), nMat=U16(f,0x14), nMesh=U16(f,0x16),
			texOff=U32(f,0x18), matAddr=U32(f,0x1C), texMapOff=U32(f,0x20),
			mtxAddr=U32(f,0x24), unk1Off=U32(f,0x28),
			objOff=[U32(f,0x2C),U32(f,0x30),U32(f,0x34)],
			weightOff=U32(f,0x38), boneOff=U32(f,0x40), nameOff=U32(f,0x44))

	def read_bones(self):
		f=self.f; h=self.header
		N=h['nBone']; bo=h['boneOff']
		self.bones=[]
		# 生データを保持。startとscaleは別管理し、階層はboneIdx@62で接続する。
		self._start=[]; self._scale=[]; self._rot=[]; self._parent=[]; self._nameOff=[]; self._bidx=[]
		for i in range(N):
			o=bo+i*64
			self._start.append([F32(f,o+16), F32(f,o+20), F32(f,o+24)])
			self._scale.append(F32(f,o+28))
			self._rot.append([F32(f,o+32), F32(f,o+36), F32(f,o+40)])   # turns
			self._nameOff.append(U32(f,o+44))
			par=f[o+61]
			self._parent.append(par)
			self._bidx.append(f[o+62])
			b=Bone()
			b.Parent = -1 if par==0xFF else par
			self.bones.append(b)
		# ヌル終端の名前表。ボーンごとに1件。
		no=h['nameOff']
		if no:
			p=no
			for i in range(N):
				e=p
				while e<len(f) and f[e]!=0: e+=1
				self.bones[i].Name=f[p:e].decode('ascii','replace')
				p=e+1
		for i in range(N):
			if not self.bones[i].Name: self.bones[i].Name="bone%d"%i

	# root=YPR(180/360,0,90/360)。local=Scale*Quat(YPR(rotZ,rotY,rotX))*Trans(startY,startZ,startX)。world=local*parent。
	def build_bone_world(self):
		N=len(self.bones)
		rootM=M4_from_quat(quat_ypr(rad(180.0/360.0), 0.0, rad(90.0/360.0)))
		world={}          # boneIdx → 4x4
		self.bwT={}       # boneIdx → 平行移動（関節の根元）
		self.bwR={}       # boneIdx → 3x3回転（flat9）
		for i in range(N):
			sp=self._start[i]; sc=self._scale[i]; rt=self._rot[i]
			nameOff=self._nameOff[i]; parent=self._parent[i]; bidx=self._bidx[i]
			if nameOff==0:
				local=M4_trans(sp[0],sp[1],sp[2])
			else:
				q=M4_from_quat(quat_ypr(rad(rt[2]),rad(rt[1]),rad(rt[0])))
				local=M4_mul(M4_mul(M4_scale(sc),q), M4_trans(sp[1],sp[2],sp[0]))
			par = rootM if parent==255 else world.get(parent, rootM)
			wm=M4_mul(local,par)
			if nameOff!=0:
				world[bidx]=wm
			self.bwT[bidx]=(wm[3][0],wm[3][1],wm[3][2])
			self.bwR[bidx]=[wm[0][0],wm[0][1],wm[0][2],wm[1][0],wm[1][1],wm[1][2],wm[2][0],wm[2][1],wm[2][2]]
		# 表示側インタフェース（wr/wt）はファイル順。存在しないボーンは原点を使う。
		self.wr=[]; self.wt=[]
		for i in range(N):
			bidx=self._bidx[i]
			t=self.bwT.get(bidx,(0.0,0.0,0.0))
			r=self.bwR.get(bidx,[1,0,0,0,1,0,0,0,1])
			self.wt.append([t[0],t[1],t[2]]); self.wr.append(r)
			self.bones[i].X=t[0]; self.bones[i].Y=t[1]; self.bones[i].Z=t[2]

	# 影響数1/2/3/4の頂点数。@16にレコード、@20にvertices1、@24にvertices2。
	def read_weights(self):
		f=self.f; h=self.header
		wa=h['weightOff']
		self.hasW=False
		# nMesh==0は静的武器。未使用のweight offsetは無視する。
		if h['nMesh']==0: return
		if not wa or wa+28>len(f): return
		self.counts=[U32(f,wa+k*4) for k in range(4)]
		n=sum(self.counts)
		if n==0 or n>500000: return
		self.weightBuf=U32(f,wa+16); self.verts1=U32(f,wa+20)
		if (not self.weightBuf or not self.verts1 or
			self.weightBuf>=len(f) or self.verts1+n*32>len(f)): return
		self.hasW=True
		# rec32B：pos3f（重み込み）、重み、nrm3f、bidx@28、stat@29。
		# 4本影響枠ではstat==1によりレコード数が累積拡張される。
		o=self.weightBuf
		self.vrec=[]           # 頂点インデックス → [(位置、重み、法線、ボーン番号), ...]
		def rdrec():
			nonlocal o
			pos=(F32(f,o),F32(f,o+4),F32(f,o+8)); w=F32(f,o+12)
			nrm=(F32(f,o+16),F32(f,o+20),F32(f,o+24))
			bi=U8(f,o+28); stat=U8(f,o+29)
			o+=32
			return (pos,w,nrm,bi),stat
		for g in range(3):
			for _ in range(self.counts[g]):
				recs=[]
				for _ in range(g+1):
					rec,stat=rdrec(); recs.append(rec)
				self.vrec.append(recs)
		high=4
		for _ in range(self.counts[3]):
			cnt=high; recs=[]
			for _ in range(cnt):
				rec,stat=rdrec(); recs.append(rec)
				if stat==1: high+=1
			self.vrec.append(recs)
		# vertices1: 32B、pos3f+scale, 法線3f+scale。バインド姿勢
		self.poolPos=[]; self.poolNrm=[]
		v1=self.verts1
		for i in range(n):
			p=v1+i*32
			sc=F32(f,p+12); nsc=F32(f,p+28)
			self.poolPos.append((F32(f,p)*sc, F32(f,p+4)*sc, F32(f,p+8)*sc))
			self.poolNrm.append((F32(f,p+16)*nsc, F32(f,p+20)*nsc, F32(f,p+24)*nsc))

	# 40バイトのオブジェクトレコード
	def objects(self):
		f=self.f; h=self.header
		out=[]
		for layer,(base,cnt) in enumerate(zip(h['objOff'],(h['n1'],h['n2'],h['n3']))):
			for i in range(cnt):
				o=base+i*40
				out.append(dict(layer=layer, base=o,
						skinned=U16(f,o)==4, prim=U16(f,o+2),
						idxCount=U32(f,o+4), mtx=U32(f,o+8), material=U32(f,o+12),
						faces=U32(f,o+16), buf1=U32(f,o+20), cr=U32(f,o+36)))
		return out

	def mat_index(self,ob):
		base=self.header['matAddr']
		if ob['material']<base: return 0
		return (ob['material']-base)//80

	def matrix_parent(self,ob):
		# 400バイトの行列表。構造体の+1バイトに親ボーン番号が入る。
		mo=ob['mtx']
		if mo+2>len(self.f): return -1
		return self.f[mo+1]

	# ストリップ（0xFFFFで再開）またはリスト
	def read_faces(self,ob):
		f=self.f; p=ob['faces']; n=ob['idxCount']
		faces=[]
		if ob['prim']==1:                       # トライアングルリスト
			for v in range(n//3):
				a=U16(f,p); b=U16(f,p+2); c=U16(f,p+4); p+=6
				faces.append((a,b,c))
			return faces
		if n<3: return faces
		end=p+n*2
		fa=U16(f,p); fb=U16(f,p+2); p+=4
		d=-1
		while p+2<=end and p+2<=len(f):
			fc=U16(f,p); p+=2
			if fc==0xFFFF:
				if p+4>end or p+4>len(f): break
				fa=U16(f,p); fb=U16(f,p+2); p+=4; d=-1
			else:
				d=-d
				if fa!=fb and fb!=fc and fc!=fa:
					faces.append((fa,fb,fc) if d>0 else (fa,fc,fb))
				fa=fb; fb=fc
		return faces

	# 表内+16の3x3行列。剛体の向きに使用。
	def obj_rot(self,ob):
		f=self.f; mo=ob['mtx']
		if mo+16+48>len(f): return m3_ident()
		return [[F32(f,mo+16+(r*4+c)*4) for c in range(3)] for r in range(3)]

	# スキンはvertices1プールを直接使用し、Yを1.15ずらす。
	CENTER_Y = 1.15
	def build_mesh(self):
		f=self.f
		self.verts=[]; self.tris=[]
		# スキン（共有プール。UV／カラーは各オブジェクトのbuffer1から取得）
		for ob in self.objects():
			if not ob['skinned']: continue
			mat=self.mat_index(ob)
			faces=self.read_faces(ob)
			vmap={}
			for (a,b,c) in faces:
				idx=[]
				for pI in (a,b,c):
					vi=vmap.get(pI)
					if vi is None:
						if not self.hasW or pI>=len(self.poolPos):
							vi=len(self.verts); self.verts.append(Vertex()); vmap[pI]=vi; idx.append(vi); continue
						p=self.poolPos[pI]; nr=self.poolNrm[pI]
						nl=(nr[0]**2+nr[1]**2+nr[2]**2)**0.5 or 1.0
						infs=[[bi,w] for pos,w,nrm,bi in self.vrec[pI] if bi<len(self.bones) and w>0]
						if not infs: infs=[[0,1.0]]
						uo=ob['buf1']+pI*12
						uu=F32(f,uo+4) if uo+12<=len(f) else 0.0
						vv=F32(f,uo+8) if uo+12<=len(f) else 0.0
						vi=len(self.verts)
						self.verts.append(Vertex(p[0],p[1]-self.CENTER_Y,p[2],
												 nr[0]/nl,nr[1]/nl,nr[2]/nl,uu,vv,infs))
						vmap[pI]=vi
					idx.append(vi)
				self.tris.append(Tri(idx[0],idx[1],idx[2],mat))
		# 剛体：40バイト頂点=(CenterRadius-buffer1)/40。pos3f、normal3f、color4、u、v、pad。
		for ob in self.objects():
			if ob['skinned']: continue
			mat=self.mat_index(ob)
			par=self.matrix_parent(ob)
			R=self.obj_rot(ob)
			bt=self.bwT.get(par,(0.0,0.0,0.0)); boneid=None
			for k in range(len(self.bones)):
				if self._bidx[k]==par: boneid=k; break
			if boneid is None: boneid=0
			cnt=(ob['cr']-ob['buf1'])//40 if ob['cr']>ob['buf1'] else 0
			if cnt<0 or cnt>1000000: cnt=0
			faces=self.read_faces(ob)
			start=len(self.verts)
			for x in range(cnt):
				o=ob['buf1']+x*40
				if o+40>len(f):
					self.verts.append(Vertex()); continue
				lx,ly,lz=F32(f,o),F32(f,o+4),F32(f,o+8)
				lnx,lny,lnz=F32(f,o+12),F32(f,o+16),F32(f,o+20)
				uu=F32(f,o+28); vv=F32(f,o+32)
				# v*R＋ボーンのワールド平行移動
				wx=lx*R[0][0]+ly*R[1][0]+lz*R[2][0]+bt[0]
				wy=lx*R[0][1]+ly*R[1][1]+lz*R[2][1]+bt[1]
				wz=lx*R[0][2]+ly*R[1][2]+lz*R[2][2]+bt[2]
				nx=lnx*R[0][0]+lny*R[1][0]+lnz*R[2][0]
				ny=lnx*R[0][1]+lny*R[1][1]+lnz*R[2][1]
				nz=lnx*R[0][2]+lny*R[1][2]+lnz*R[2][2]
				nl=(nx*nx+ny*ny+nz*nz)**0.5 or 1.0
				self.verts.append(Vertex(wx,wy,wz,nx/nl,ny/nl,nz/nl,uu,vv,[[boneid,1.0]]))
			for (a,b,c) in faces:
				self.tris.append(Tri(start+a,start+b,start+c,mat))

	# VXTブロック
	def read_textures(self):
		f=self.f; h=self.header
		self.materials=[Material() for _ in range(h['nMat'])]
		for i,m in enumerate(self.materials): m.Name="m%03d"%i
		base=h['texOff']
		if not base or f[base:base+3]!=b'VXT': return
		rowType=f[base+4]
		count=U32(f,base+8)
		hdr=20
		# rowType2=36B（dataOff@16）、rowType1=32B（dataOff@12）。
		entrySize=36 if rowType==2 else 32
		do=16 if rowType==2 else 12
		texs=[]
		for i in range(count):
			e=base+hdr+i*entrySize
			txph=U32(f,e)
			dataOff=U32(f,e+do); ddstype=U32(f,e+do+4)
			w=U16(f,e+do+8); hh=U16(f,e+do+10)
			texs.append(dict(txph=txph,dataOff=base+dataOff,ddstype=ddstype,w=w,h=hh))
		# material+8はVXTエントリ（先頭のdiffuseテクスチャ）を指す。
		self.texEntrySize=entrySize; self.texBase=base; self.texHdr=hdr
		decoded={}
		for mi,m in enumerate(self.materials):
			vx=U32(f, h['matAddr']+mi*80+8)
			if vx==0: continue
			ti=(vx-(base+hdr))//entrySize
			if ti<0 or ti>=len(texs): continue
			if ti not in decoded:
				decoded[ti]=self.decode_tex(base,texs[ti])
			t=decoded[ti]
			if t is not None: m.Rgba,m.W,m.H=t

	def decode_tex(self,base,t):
		f=self.f; w=t['w']; hh=t['h']
		if w==0 or hh==0: return None
		dt=t['ddstype']
		if dt==0x0C: return (_decode_dxt(f[t['dataOff']:],w,hh,1),w,hh)
		if dt==0x0E: return (_decode_dxt(f[t['dataOff']:],w,hh,3),w,hh)
		if dt==0x0F: return (_decode_dxt(f[t['dataOff']:],w,hh,5),w,hh)
		if dt==0x06: return (_decode_argb8(f,t['dataOff'],w,hh),w,hh)
		if dt==0x0B:
			# P8：TxPHオフセット → パレット行（オフセット、件数）。オフセットはブロック相対。
			if t['txph']==0: return None
			pr=base+t['txph']
			palOff=base+U32(f,pr); ncol=U32(f,pr+4)
			pal=f[palOff:palOff+max(0,min(ncol,256))*4]
			return (_decode_p8(f,t['dataOff'],w,hh,pal),w,hh)
		return None


def load(path):
	v=VMX()
	with open(path,'rb') as fp:
		v.read(fp.read())
	return v
