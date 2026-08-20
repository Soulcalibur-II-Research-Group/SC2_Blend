import struct
import math

def U8(f,o):  return f[o]
def U16(f,o): return struct.unpack_from(">H",f,o)[0]
def S16(f,o): return struct.unpack_from(">h",f,o)[0]
def U32(f,o): return struct.unpack_from(">I",f,o)[0]
def F32(f,o): return struct.unpack_from(">f",f,o)[0]

# --- BuildBoneWorld：VMX／OlkViewer Vmx.cs互換のボーン再構築。
#     各レコードのstart@16、scale@28からワールド座標のボーン位置を再構築する。
#     rotation@32は回転数、parent@61、ボーン番号@62を使用。軸規約は
#     VMXと一致し、メッシュ重心ではなく関節ピボットを得る。---
def _m4i(): return [[1.0,0,0,0],[0,1.0,0,0],[0,0,1.0,0],[0,0,0,1.0]]
def _m4mul(A,B): return [[A[i][0]*B[0][j]+A[i][1]*B[1][j]+A[i][2]*B[2][j]+A[i][3]*B[3][j] for j in range(4)] for i in range(4)]
def _m4t(x,y,z):
    M=_m4i(); M[3][0]=x; M[3][1]=y; M[3][2]=z; return M
def _m4s(s):
    M=_m4i(); M[0][0]=s; M[1][1]=s; M[2][2]=s; return M
def _qypr(yaw,pitch,roll):
    hr=roll*.5; hp=pitch*.5; hy=yaw*.5
    sr=math.sin(hr); cr=math.cos(hr); sp=math.sin(hp); cp=math.cos(hp); sy=math.sin(hy); cy=math.cos(hy)
    return (cy*sp*cr+sy*cp*sr, sy*cp*cr-cy*sp*sr, cy*cp*sr-sy*sp*cr, cy*cp*cr+sy*sp*sr)
def _m4q(q):
    x,y,z,w=q; M=_m4i()
    xx=x*x; yy=y*y; zz=z*z; xy=x*y; wz=z*w; xz=z*x; wy=y*w; yz=y*z; wx=x*w
    M[0][0]=1-2*(yy+zz); M[0][1]=2*(xy+wz); M[0][2]=2*(xz-wy)
    M[1][0]=2*(xy-wz); M[1][1]=1-2*(zz+xx); M[1][2]=2*(yz+wx)
    M[2][0]=2*(xz+wy); M[2][1]=2*(yz-wx); M[2][2]=1-2*(yy+xx)
    return M
def _turns(t): return t*2.0*math.pi

# GCはすでにY-up。座標は変更しない。
def fix_axis(x,y,z):
	return (x, y, z)


class Bone(object):
	def __init__(self):
		self.Name = ""
		self.Parent = -1
		self.Group = 0
		self.X = 0.0
		self.Y = 0.0
		self.Z = 0.0

class Vertex(object):
	def __init__(self,x=0.0,y=0.0,z=0.0,nx=0.0,ny=1.0,nz=0.0,u=0.0,v=0.0,inf=None):
		self.X=x; self.Y=y; self.Z=z
		self.Nx=nx; self.Ny=ny; self.Nz=nz
		self.U=u; self.V=v
		self.Inf = inf if inf is not None else []

class Tri(object):
	def __init__(self,a=0,b=0,c=0,mat=0):
		self.A=a; self.B=b; self.C=c
		self.Mat=mat

class Material(object):
	def __init__(self):
		self.Name = ""
		self.Rgba = None
		self.W = 0
		self.H = 0
		self.Cutout = False


def _rgb565(c):
	r=(c>>11)&0x1F; g=(c>>5)&0x3F; b=c&0x1F
	return ((r<<3)|(r>>2),(g<<2)|(g>>4),(b<<3)|(b>>2))

# CMPR=DXT1の2x2まとめ+バイト/ビット順入替。普通のDXT1に戻す
def _cmpr_to_dxt1(c,w,h):
	bw=max(1,w//4); bh=max(1,h//4)
	d=bytearray(bw*bh*8); o=0
	for my in range(0,bh,2):
		for mx in range(0,bw,2):
			for dy,dx in ((0,0),(0,1),(1,0),(1,1)):
				by=min(my+dy,bh-1); bx=min(mx+dx,bw-1)
				t=(by*bw+bx)*8
				if o+8>len(c): return bytes(d)
				d[t]=c[o+1]; d[t+1]=c[o]; d[t+2]=c[o+3]; d[t+3]=c[o+2]
				for k in range(4):
					v=c[o+4+k]
					d[t+4+k]=((v&3)<<6)|(((v>>2)&3)<<4)|(((v>>4)&3)<<2)|((v>>6)&3)
				o+=8
	return bytes(d)

def _dxt1_rgba(dxt,w,h):
	bw=w//4; bh=h//4
	out=bytearray(w*h*4)
	for by in range(bh):
		for bx in range(bw):
			s=(by*bw+bx)*8
			if s+8>len(dxt): continue
			c0=dxt[s]|dxt[s+1]<<8; c1=dxt[s+2]|dxt[s+3]<<8
			col=[_rgb565(c0),_rgb565(c1)]
			if c0>c1:
				col.append(tuple((2*col[0][i]+col[1][i])//3 for i in range(3)))
				col.append(tuple((col[0][i]+2*col[1][i])//3 for i in range(3)))
			else:
				col.append(tuple((col[0][i]+col[1][i])//2 for i in range(3)))
				col.append((0,0,0))
			idx=dxt[s+4]|dxt[s+5]<<8|dxt[s+6]<<16|dxt[s+7]<<24
			for i in range(16):
				px=bx*4+i%4; py=by*4+i//4
				t=(py*w+px)*4
				r,g,b=col[(idx>>(2*i))&3]
				out[t]=r; out[t+1]=g; out[t+2]=b; out[t+3]=255
	return bytes(out)


class VMG(object):

	def __init__(self):
		self.f = b''
		self.header = {}
		self.bones = []
		self.verts = []
		self.tris = []
		self.materials = []
		self.wr = []
		self.wt = []
		self.vgtBase = -1
		self.weights = None     # プール頂点インデックス -> [(ボーン、重み), ...]
		self.poolN = 0

	def read(self,f):
		if hasattr(f,'read'):
			f = f.read()
		self.f = f
		if f[:4]!=b'VMG.':
			print("Not a VMG file"); return
		self.read_header()
		self.read_bones()
		self.read_weights()
		self.find_vgt()
		self.read_materials()
		self.build_mesh()
		self.place_bones()

	def read_header(self):
		f=self.f
		# 0x18=VGT、0x1C=マテリアル表（1件80バイト）、0x24=行列表
		self.header = dict(
			contents = U8(f,0x09),
			matrices = U16(f,0x0A),
			obj0 = U16(f,0x0C), obj1 = U16(f,0x0E), obj2 = U16(f,0x10),
			bones = U16(f,0x12), mats = U16(f,0x14), mesh = U16(f,0x16),
			texOff = U32(f,0x18), materialOff = U32(f,0x1C),
			vertOff = U32(f,0x20), matrixOff = U32(f,0x24),
			obj0Off = U32(f,0x2C), obj1Off = U32(f,0x30), obj2Off = U32(f,0x34),
			weightOff = U32(f,0x38), boneOff = U32(f,0x40), nameOff = U32(f,0x44))

	def read_bones(self):
		f=self.f; h=self.header
		N=h['bones']; bo=h['boneOff']
		self.bones=[]
		for i in range(N):
			o=bo+i*64
			b=Bone()
			no=U32(f,o+44)
			if 0<no<len(f):
				e=no
				while e<len(f) and f[e]!=0: e+=1
				b.Name=f[no:e].decode('ascii','replace')
			if not b.Name: b.Name="bone%d"%i
			par=f[o+61]
			b.Parent = -1 if par==0xFF else par
			b.Group = f[o+63]
			self.bones.append(b)

	# 影響数1/2/3/4の頂点数。続いて@0x10にレコード本体。
	# rec16B：ボーン=U16(+14)&0xFF、重み=U16(+6)/8192。
	# 4本影響枠ではbyte14のstat==1によりレコード数が累積拡張される。
	def read_weights(self):
		f=self.f; h=self.header
		# mesh==0は静的武器。未使用のweight offsetは無視する。
		if h['mesh']==0:
			self.weights=None; self.poolN=0; return
		W=h['weightOff']
		if W==0 or W+0x14>len(f) or U32(f,W)==0:
			self.weights=None; self.poolN=0; return
		counts=[U32(f,W+k*4) for k in range(4)]
		n=sum(counts)
		if n==0 or n>500000:
			self.weights=None; self.poolN=0; return
		o=U32(f,W+0x10)
		if o==0 or o+n*16>len(f):
			self.weights=None; self.poolN=0; return
		per=[]
		for s in range(3):
			for _ in range(counts[s]):
				recs=[]
				for _ in range(s+1):
					recs.append((U16(f,o+14)&0xFF, U16(f,o+6)/8192.0)); o+=16
				per.append(recs)
		high=4
		for _ in range(counts[3]):
			cnt=high; recs=[]
			for _ in range(cnt):
				stat=f[o+14]
				recs.append((U16(f,o+14)&0xFF, U16(f,o+6)/8192.0)); o+=16
				if stat==1: high+=1
			per.append(recs)
		self.weights=per
		self.poolN=sum(counts)

	def find_vgt(self):
		self.vgtBase=self.f.find(b'VGT.')

	# 3レイヤに分かれた56バイトのオブジェクト。
	def objects(self):
		f=self.f; h=self.header
		out=[]
		for off,cnt,layer in ((h['obj0Off'],h['obj0'],0),
							   (h['obj1Off'],h['obj1'],1),
							   (h['obj2Off'],h['obj2'],2)):
			for i in range(cnt):
				b=off+i*56
				fmt=f[b:b+14]
				ob=dict(layer=layer, base=b, faceCount=U16(f,b+14),
						materialField=U32(f,b+20),
						pos=U32(f,b+24), nrm=U32(f,b+32),
						col=U32(f,b+40), uv=U32(f,b+44),
						face=U32(f,b+48), bnd=U32(f,b+52),
						uvFrac=fmt[9],
						wpos=1 if fmt[10]==2 else 2,
						wnrm=1 if fmt[11]==2 else 2,
						wcol=1 if fmt[12]==2 else 2,
						wuv =1 if fmt[13]==2 else 2)
				ob['skinned'] = (ob['bnd']==0)
				out.append(ob)
		return out

	def mat_index(self,ob):
		base=self.header['materialOff']
		if ob['materialField']<base: return 0
		return (ob['materialField']-base)//80

	# 0x98=ストリップ、0x90=リスト。頂点は位置・法線・カラー・UVの各インデックスを持つ。
	def decode_dl(self,ob):
		f=self.f
		p=ob['face']; end=min(ob['face']+ob['faceCount']*32, len(f))
		wpos,wnrm,wcol,wuv=ob['wpos'],ob['wnrm'],ob['wcol'],ob['wuv']
		stride=wpos+wnrm+wcol+wuv
		def rd(o,w): return (f[o]<<8|f[o+1]) if w==2 else f[o]
		tris=[]
		while p<end:
			op=f[p]
			if op==0: p+=1; continue
			if op not in (0x90,0x98): break
			n=U16(f,p+1); p+=3
			verts=[]
			for k in range(n):
				bo=p+k*stride
				verts.append((rd(bo,wpos), rd(bo+wpos,wnrm),
							  rd(bo+wpos+wnrm,wcol), rd(bo+wpos+wnrm+wcol,wuv)))
			p+=n*stride
			if op==0x98:
				for k in range(n-2):
					a,b,c=verts[k],verts[k+1],verts[k+2]
					if a[0]==b[0] or b[0]==c[0] or a[0]==c[0]: continue
					tris.append((a,c,b) if (k&1)==0 else (a,b,c))
			else:
				for k in range(0,n-2,3):
					tris.append((verts[k],verts[k+2],verts[k+1]))
		return tris

	# base+16は絶対行列構造体を指す。4x4行列は+16からの行優先配置。
	def get_matrix(self,ob):
		f=self.f
		mo=U32(f,ob['base']+16)
		M=[[F32(f,mo+16+(r*4+c)*4) for c in range(4)] for r in range(4)]
		return M

	# 構造体の+1バイトに親ボーン番号が入る。
	def matrix_parent(self,ob):
		f=self.f
		mo=U32(f,ob['base']+16)
		if mo+2>len(f): return -1
		return f[mo+1]

	def resolve_sk(self,ob,corner):
		f=self.f
		pI,nI,cI,uI=corner
		po=ob['pos']+pI*16; no=ob['nrm']+nI*16
		frac=float(1<<ob['uvFrac']) if ob['uvFrac'] else 2048.0
		uo=ob['uv']+uI*4
		pos=(F32(f,po),F32(f,po+4),F32(f,po+8))
		nrm=(F32(f,no),F32(f,no+4),F32(f,no+8))
		uv=(S16(f,uo)/frac, S16(f,uo+2)/frac)
		return pos,nrm,uv,pI

	def resolve_st(self,ob,corner):
		f=self.f
		pI,nI,cI,uI=corner
		po=ob['pos']+pI*12; no=ob['nrm']+nI*3
		def s8(x): return x-256 if x>=128 else x
		n=(s8(f[no]),s8(f[no+1]),s8(f[no+2]))
		ln=(n[0]**2+n[1]**2+n[2]**2)**0.5 or 1.0
		frac=float(1<<ob['uvFrac']) if ob['uvFrac'] else 2048.0
		uo=ob['uv']+uI*4
		pos=(F32(f,po),F32(f,po+4),F32(f,po+8))
		nrm=(n[0]/ln,n[1]/ln,n[2]/ln)
		uv=(S16(f,uo)/frac, S16(f,uo+2)/frac)
		return pos,nrm,uv

	def _bone_world_records(self):
		"""VMX互換レコードからワールド座標のボーン位置を構築する。
		ファイル順のレコード空間位置を返し、後でスキン空間へ較正する。"""
		f=self.f; h=self.header; bo=h['boneOff']; N=h['bones']
		st=[]; sc=[]; rt=[]; noff=[]; par=[]; bidx=[]
		for i in range(N):
			o=bo+i*64
			st.append((F32(f,o+16),F32(f,o+20),F32(f,o+24))); sc.append(F32(f,o+28))
			rt.append((F32(f,o+32),F32(f,o+36),F32(f,o+40)))
			noff.append(U32(f,o+44)); par.append(f[o+61]); bidx.append(f[o+62])
		rootM=_m4q(_qypr(_turns(180.0/360.0),0.0,_turns(90.0/360.0)))
		world={}
		def build(i,depth=0):
			sp=st[i]
			if noff[i]==0:
				local=_m4t(sp[0],sp[1],sp[2])
			else:
				q=_m4q(_qypr(_turns(rt[i][2]),_turns(rt[i][1]),_turns(rt[i][0])))
				local=_m4mul(_m4mul(_m4s(sc[i]),q),_m4t(sp[1],sp[2],sp[0]))  # Y,Z,Xの入れ替え
			p=par[i]
			pw = rootM if (p==0xFF or depth>256) else world.get(p,rootM)
			wm=_m4mul(local,pw)
			if noff[i]!=0: world[bidx[i]]=wm
			return wm
		wm=[build(i) for i in range(N)]
		return [(m[3][0],m[3][1],m[3][2]) for m in wm]   # ファイル順のボーンごとのワールド平行移動

	def _lstsq4(self, rows, ys):
		# (A^T A) M = A^T Y（A:Nx4 [x,y,z,1]、Y:Nx3）をガウス消去で解く。4x3を返す。
		if len(rows)<6: return None
		ATA=[[0.0]*4 for _ in range(4)]; ATY=[[0.0]*3 for _ in range(4)]
		for r,y in zip(rows,ys):
			for a in range(4):
				for b in range(4): ATA[a][b]+=r[a]*r[b]
				for k in range(3): ATY[a][k]+=r[a]*y[k]
		aug=[ATA[i][:]+ATY[i][:] for i in range(4)]
		for col in range(4):
			piv=max(range(col,4), key=lambda r:abs(aug[r][col]))
			if abs(aug[piv][col])<1e-12: return None
			aug[col],aug[piv]=aug[piv],aug[col]
			pv=aug[col][col]; aug[col]=[v/pv for v in aug[col]]
			for r in range(4):
				if r!=col:
					fac=aug[r][col]; aug[r]=[aug[r][j]-fac*aug[col][j] for j in range(7)]
		return [[aug[i][4+k] for k in range(3)] for i in range(4)]

	def build_mesh(self):
		self.verts=[]; self.tris=[]
		objs=self.objects()
		# 先にスキンを組んで背丈をとる
		skinned_ymax=1e-9
		for ob in objs:
			if not ob['skinned']: continue
			mat=self.mat_index(ob)
			tris=self.decode_dl(ob)
			vmap={}
			for tri in tris:
				idx=[]
				for corner in tri:
					vi=vmap.get(corner)
					if vi is None:
						pos,nrm,uv,pI=self.resolve_sk(ob,corner)
						x,y,z=fix_axis(*pos)
						nx,ny,nz=fix_axis(*nrm)
						if y>skinned_ymax: skinned_ymax=y
						inf=[]
						if self.weights and pI<len(self.weights):
							for (bi,w) in self.weights[pI]:
								if 0<=bi<len(self.bones) and w>0:
									inf.append([bi,w])
						if not inf: inf=[[0,1.0]]
						vi=len(self.verts)
						self.verts.append(Vertex(x,y,z,nx,ny,nz,uv[0],uv[1],inf))
						vmap[corner]=vi
					idx.append(vi)
				self.tris.append(Tri(idx[0],idx[1],idx[2],mat))

		# --- ボーンごとのスキン重心と関節境界（ボーン／親の重複領域）---
		N=len(self.bones); parent_of=[self.bones[i].Parent for i in range(N)]
		cacc=[[0.0,0.0,0.0] for _ in range(N)]; cn=[0]*N
		jacc=[[0.0,0.0,0.0] for _ in range(N)]; jn=[0]*N
		for v in self.verts:                        # この段階ではスキンのみ
			bis=set(int(bi) for (bi,w) in v.Inf if 0<=int(bi)<N)
			for bi in bis:
				cacc[bi][0]+=v.X; cacc[bi][1]+=v.Y; cacc[bi][2]+=v.Z; cn[bi]+=1
				p=parent_of[bi]
				if 0<=p<N and p in bis:
					jacc[bi][0]+=v.X; jacc[bi][1]+=v.Y; jacc[bi][2]+=v.Z; jn[bi]+=1
		cen=[None]*N; joint=[None]*N
		for i in range(N):
			if cn[i]>0: cen[i]=[cacc[i][k]/cn[i] for k in range(3)]
			if jn[i]>=3: joint[i]=[jacc[i][k]/jn[i] for k in range(3)]
		self._cen=cen; self._joint=joint

		# BuildBoneWorldレコードからスキン重心へのアフィンフィット。
		# スキンのないボーンも含め、全ボーンの関節ピボットをスキン空間で求める。
		try:
			bwr=self._bone_world_records()
		except Exception:
			bwr=None
		bwt=[None]*N
		if bwr and len(bwr)==N:
			# 完全線形フィット：skin=[bwr 1] @ M（Mは4x3）。ボーンワールド基底の回転を除去する。
			# 軸ごとのフィットではこの基底回転を除去できない。
			rows=[[bwr[i][0],bwr[i][1],bwr[i][2],1.0] for i in range(N) if cen[i] is not None]
			yy=[list(cen[i]) for i in range(N) if cen[i] is not None]
			Mx=self._lstsq4(rows,yy)
			if Mx is not None:
				for i in range(N):
					bx,by,bz=bwr[i]
					bwt[i]=[bx*Mx[0][k]+by*Mx[1][k]+bz*Mx[2][k]+Mx[3][k] for k in range(3)]
		self._bwt=bwt

		# オブジェクト行列からスキンへの較正（均一スケール＋オフセット／軸）。
		# 親がスキンを持つ剛体部品に合わせる。制約付き顔ボーン（Group==3：
		# 眼、顎／歯）はレコードEulerが不安定だが、オブジェクト行列には
		# 正しい位置が格納されている。
		mpairs=[]
		for ob in objs:
			if ob['skinned']: continue
			par=self.matrix_parent(ob)
			if 0<=par<N and cn[par]>=4 and cen[par] is not None:
				M=self.get_matrix(ob); mpairs.append(((M[0][3],M[1][3],M[2][3]),cen[par]))
		mscale=None; moff=[0.0,0.0,0.0]
		if len(mpairs)>=4:
			rr=[]
			for T,C in mpairs:
				bb=(C[0]**2+C[1]**2+C[2]**2)**0.5
				if bb>0.3: rr.append(((T[0]**2+T[1]**2+T[2]**2)**0.5)/bb)
			if rr:
				rr.sort(); Sm=rr[len(rr)//2]
				if Sm>1e-6:
					mscale=1.0/Sm
					for ax in range(3):
						mt=sum(T[ax] for T,_ in mpairs)/len(mpairs); mc=sum(C[ax] for _,C in mpairs)/len(mpairs)
						moff[ax]=mc-mscale*mt

		# S（最終フォールバック：レコードもスキンもないボーン）
		def _med(a):
			a=sorted(a); n=len(a)
			return (a[n//2] if (n%2) else 0.5*(a[n//2-1]+a[n//2])) if n else None
		ratios=[]
		for ob in objs:
			if ob['skinned']: continue
			par=self.matrix_parent(ob); ref=joint[par] if (0<=par<N and joint[par]) else None
			if ref:
				M=self.get_matrix(ob)
				rr=(M[0][3]**2+M[1][3]**2+M[2][3]**2)**0.5; rc=(ref[0]**2+ref[1]**2+ref[2]**2)**0.5
				if rc>0.25: ratios.append(rr/rc)
		Sf=_med(ratios)
		if Sf is None:
			sy=max([self.get_matrix(ob)[1][3] for ob in objs if not ob['skinned']] or [0.0])
			Sf=(sy/skinned_ymax) if (sy>0 and skinned_ymax>0) else 1.0
		S=Sf if Sf and Sf>0 else 1.0
		self.rigScale=S

		# 剛体メッシュ：較正済みboneWorld[parent]。関節、平行移動、スケールの順にフォールバック。
		for ob in objs:
			if ob['skinned']: continue
			mat=self.mat_index(ob); tris=self.decode_dl(ob)
			M=self.get_matrix(ob); R=[[M[r][c] for c in range(3)] for r in range(3)]
			par=self.matrix_parent(ob); boneid=par if 0<=par<N else 0
			grp=self.bones[par].Group if 0<=par<N else 0
			if 0<=par<N and bwt[par] is not None:
				at=bwt[par]                              # 基底回転を除去した3x3フィット変換
			elif 0<=par<N and joint[par]:
				at=joint[par]
			else:
				at=[M[0][3]/S, M[1][3]/S, M[2][3]/S]
			vmap={}
			for tri in tris:
				idx=[]
				for c in tri:
					vi=vmap.get(c)
					if vi is None:
						lp,ln,uv=self.resolve_st(ob,c)
						rx=R[0][0]*lp[0]+R[0][1]*lp[1]+R[0][2]*lp[2]
						ry=R[1][0]*lp[0]+R[1][1]*lp[1]+R[1][2]*lp[2]
						rz=R[2][0]*lp[0]+R[2][1]*lp[1]+R[2][2]*lp[2]
						nx=R[0][0]*ln[0]+R[0][1]*ln[1]+R[0][2]*ln[2]
						ny=R[1][0]*ln[0]+R[1][1]*ln[1]+R[1][2]*ln[2]
						nz=R[2][0]*ln[0]+R[2][1]*ln[1]+R[2][2]*ln[2]
						nl=(nx*nx+ny*ny+nz*nz)**0.5 or 1.0
						x,y,z=fix_axis(rx+at[0],ry+at[1],rz+at[2])
						nx,ny,nz=fix_axis(nx/nl,ny/nl,nz/nl)
						vi=len(self.verts); self.verts.append(Vertex(x,y,z,nx,ny,nz,uv[0],uv[1],[[boneid,1.0]]))
						vmap[c]=vi
					idx.append(vi)
				self.tris.append(Tri(idx[0],idx[1],idx[2],mat))


	# material+8はVGTエントリを指す。idx=(off-vgtBase-24)/68。
	def read_materials(self):
		f=self.f; h=self.header
		nmat=h['mats']
		self.materials=[]
		texcache={}
		for mi in range(nmat):
			m=Material(); m.Name="m%03d"%mi
			ti=self.material_texidx(mi)
			if ti is not None:
				if ti not in texcache:
					texcache[ti]=self.decode_texture(ti)
				tex=texcache[ti]
				if tex is not None:
					m.Rgba,m.W,m.H=tex
			self.materials.append(m)

	def material_texidx(self,mi):
		f=self.f; h=self.header
		vx=U32(f, h['materialOff']+mi*80+8)
		if vx==0 or self.vgtBase<0: return None
		return (vx-self.vgtBase-24)//68

	def decode_texture(self,ti):
		f=self.f; base=self.vgtBase
		if base<0: return None
		n=U32(f,base+8)
		if ti<0 or ti>=n: return None
		o=base+24+ti*68+4
		info=U32(f,o+8)
		w=1+(info&0x3FF); hgt=1+((info>>10)&0x3FF)
		imgtype=U32(f,o+20)
		doff=base+U32(f,o+12)
		size=w*hgt//2
		if imgtype!=14 or doff+size>len(f):     # 14 = CMPR だけ相手にする
			return None
		rgba=_dxt1_rgba(_cmpr_to_dxt1(f[doff:doff+size],w,hgt),w,hgt)
		return (rgba,w,hgt)

	# ボーン位置の優先順：較正済みboneWorldレコード、スキン重心、親からの継承。
	def place_bones(self):
		N=len(self.bones)
		self.wr=[[1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0] for _ in range(N)]
		self.wt=[[0.0,0.0,0.0] for _ in range(N)]
		bwt=getattr(self,'_bwt',None)
		cen=getattr(self,'_cen',[None]*N)
		placed=[False]*N
		for i in range(N):
			if bwt and i<len(bwt) and bwt[i] is not None:
				self.wt[i]=list(bwt[i]); placed[i]=True      # 正確なワールド位置
			elif cen[i] is not None:
				self.wt[i]=list(cen[i]); placed[i]=True
		for _ in range(8):
			for i in range(N):
				if not placed[i]:
					p=self.bones[i].Parent
					if 0<=p<N and placed[p]:
						self.wt[i]=list(self.wt[p]); placed[i]=True
		for i in range(N):
			self.bones[i].X=self.wt[i][0]
			self.bones[i].Y=self.wt[i][1]
			self.bones[i].Z=self.wt[i][2]


def load(path):
	v=VMG()
	with open(path,'rb') as f:
		v.read(f.read())
	return v
