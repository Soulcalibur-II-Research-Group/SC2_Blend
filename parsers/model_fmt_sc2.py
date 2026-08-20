import struct
from enum import Flag, auto, Enum

def rotateMtx(matrix):

    newmtx = [[],[],[],[]]
    for y in range(4):
        for idx,x in enumerate(matrix):
            newmtx[y].append(x[y])
    return newmtx

class D3DFORMAT(Enum):
    D3DFMT_L8 = 0x00
    D3DFMT_AL8 = 0x01
    D3DFMT_A1R5G5B5 = 0x02
    D3DFMT_X1R5G5B5 = 0x03
    D3DFMT_A4R4G4B4 = 0x04
    D3DFMT_R5G6B5 = 0x05
    D3DFMT_A8R8G8B8 = 0x06
    D3DFMT_X8R8G8B8 = 0x07
    D3DFMT_X8L8V8U8 = 0x07 # 別名

    D3DFMT_P8 = 0x0b # 8ビットパレット形式

    D3DFMT_A8 = 0x19
    D3DFMT_A8L8 = 0x1a
    D3DFMT_R6G5B5 = 0x27
    D3DFMT_L6V5U5 = 0x27 # 別名

    D3DFMT_G8B8 = 0x28
    D3DFMT_V8U8 = 0x28 # 別名

    D3DFMT_R8B8 = 0x29
    D3DFMT_D24S8 = 0x2a
    D3DFMT_F24S8 = 0x2b
    D3DFMT_D16 = 0x2c
    D3DFMT_D16_LOCKABLE = 0x2c # 別名

    D3DFMT_F16 = 0x2d
    D3DFMT_L16 = 0x32
    D3DFMT_V16U16 = 0x33
    D3DFMT_R5G5B5A1 = 0x38
    D3DFMT_R4G4B4A4 = 0x39
    D3DFMT_A8B8G8R8 = 0x3A
    D3DFMT_Q8W8V8U8 = 0x3A # 別名

    D3DFMT_B8G8R8A8 = 0x3B
    D3DFMT_R8G8B8A8 = 0x3C

    # YUV形式

    D3DFMT_YUY2 = 0x24
    D3DFMT_UYVY = 0x25

    # 圧縮形式

    D3DFMT_DXT1 = 0x0C # 不透明／1ビットアルファ
    D3DFMT_DXT2 = 0x0E # D3DFMT_DXT3の別名
    D3DFMT_DXT3 = 0x0E # リニアアルファ
    D3DFMT_DXT4 = 0x0F # D3DFMT_DXT5の別名
    D3DFMT_DXT5 = 0x0F # 補間アルファ

    # リニア形式

    D3DFMT_LIN_A1R5G5B5 = 0x10
    D3DFMT_LIN_R5G6B5 = 0x11
    D3DFMT_LIN_A8R8G8B8 = 0x12
    D3DFMT_LIN_L8 = 0x13
    D3DFMT_LIN_R8B8 = 0x16
    D3DFMT_LIN_G8B8 = 0x17
    D3DFMT_LIN_V8U8 = 0x17 # 別名

    D3DFMT_LIN_AL8 = 0x1b
    D3DFMT_LIN_X1R5G5B5 = 0x1c
    D3DFMT_LIN_A4R4G4B4 = 0x1d
    D3DFMT_LIN_X8R8G8B8 = 0x1e
    D3DFMT_LIN_X8L8V8U8 = 0x1e # 別名

    D3DFMT_LIN_A8 = 0x1f
    D3DFMT_LIN_A8L8 = 0x20
    D3DFMT_LIN_D24S8 = 0x2E
    D3DFMT_LIN_F24S8 = 0x2f
    D3DFMT_LIN_D16 = 0x30
    D3DFMT_LIN_F16 = 0x31
    D3DFMT_LIN_L16 = 0x35
    D3DFMT_LIN_V16U16 = 0x36
    D3DFMT_LIN_R6G5B5 = 0x37
    D3DFMT_LIN_L6V5U5 = 0x37 # 別名

    D3DFMT_LIN_R5G5B5A1 = 0x3D
    D3DFMT_LIN_R4G4B4A4 = 0x3e
    D3DFMT_LIN_A8B8G8R8 = 0x3f
    D3DFMT_LIN_B8G8R8A8 = 0x40
    D3DFMT_LIN_R8G8B8A8 = 0x41
class FmtTXVFlag(Flag):
    BIT01 = auto()
    CLAMP = auto()
    BIT03 = auto()
    BIT04 = auto()
    TWOSIDED = auto()
    BIT06 = auto()
    BIT07 = auto()
    BIT08 = auto()
    SPEC  = auto()
    BIT10 = auto()
    BIT11 = auto()
    BIT12 = auto()
    BIT13 = auto()
    BIT14 = auto()
    BIT15 = auto()
    BIT16 = auto()
class FRead(object): # 汎用ファイルリーダー
    def __init__(self,f,big_endian=False):
        self.endian='<'
        if(big_endian):
            self.endian ='>'
        self.file = f
    def swapEndian(self):
        if(self.endian == '>'):
            self.endian = '<'
        else:
            self.endian = '>'
    def u32(self):
        return struct.unpack(self.endian+'I', self.file.read(4))[0]
    def u16(self):
        return struct.unpack(self.endian+'H', self.file.read(2))[0]
    def u8(self):
        return struct.unpack(self.endian+'B', self.file.read(1))[0]
    def u8_4(self):
        return struct.unpack(self.endian+'BBBB', self.file.read(4))[0:4]
    def s32(self):
        return struct.unpack(self.endian+'i', self.file.read(4))[0]
    def s16(self):
        return struct.unpack(self.endian+'h', self.file.read(2))[0]
    def s8(self):
        return struct.unpack(self.endian+'b', self.file.read(1))[0]
    def f16(self):
        return struct.unpack(self.endian+'e', self.file.read(2))[0]
    def g16(self):
        val = struct.unpack(self.endian+'h', self.file.read(2))[0]
        val = val/8192
        return val
    def g16_2(self):
        val = [self.g16(),self.g16()]
        return val
    def g16_3(self):
        val = [self.g16(),self.g16(),self.g16()]
        return val
    def f32(self):
        return struct.unpack(self.endian+'f', self.file.read(4))[0]
    def f32_4(self):
        return struct.unpack(self.endian+'ffff', self.file.read(16))[0:4]
    def f32_3(self):
        return struct.unpack(self.endian+'fff', self.file.read(12))[0:3]
    def f32_2(self):
        return struct.unpack(self.endian+'ff', self.file.read(8))[0:2]
    def seek(self,offset,whence=0):
        self.file.seek(offset,whence)
    def tell(self):
        return self.file.tell()
    def read(self,x):
        return self.file.read(x)
    def getString(self,offset = 0):
        if(offset):
            ret = self.file.tell()
            self.seek(offset)
        result = ""
        tmpChar = self.file.read(1)
        while ord(tmpChar) != 0:
            result += tmpChar.decode("utf-8")
            tmpChar = self.file.read(1)
        if(offset):
            self.seek(ret)
        return result
    def getStringSpecal(self,offset = 0):
        if(offset):
            ret = self.file.tell()
            self.seek(offset)
        result = ""
        tmpChar = chr(self.u8()-0x40)
        while ord(tmpChar) != 0:
            result += tmpChar
            tmpChar = chr(self.u8()-0x40)
        if(offset):
            self.seek(ret)
        return result
class FWrite(object): # 汎用ファイルライター
    def __init__(self,f,big_endian=False):
        self.endian='<'
        if(big_endian):
            self.endian ='>'
        self.file = f
    def swapEndian(self):
        if(self.endian == '>'):
            self.endian = '<'
        else:
            self.endian = '>'
    def u32(self,val):
        self.file.write(struct.pack(self.endian+'I', val))
    def u16(self,val):
        self.file.write(struct.pack(self.endian+'H', val))
    def u8(self,val):
        self.file.write(struct.pack(self.endian+'B', val))
    def u8_4(self,val):
        self.file.write(struct.pack(self.endian+'BBBB', val[0],val[1],val[2],val[3]))
    def s32(self,val):
        self.file.write(struct.pack(self.endian+'i', val))
    def s16(self,val):
        self.file.write(struct.pack(self.endian+'h', val))
    def s8(self,val):
        self.file.write(struct.pack(self.endian+'b', val))
    def f16(self,val):
        self.file.write(struct.pack(self.endian+'e', val))
    def f32(self,val):
        self.file.write(struct.pack('f', val))
    def f32_4(self,val):
        self.file.write(struct.pack('ffff',val[0],val[1],val[2],val[3]))
    def f32_3(self,val):
        self.file.write(struct.pack('fff',val[0],val[1],val[2]))
    def f32_2(self,val):
        self.file.write(struct.pack('ff',val[0],val[1]))
    def seek(self,offset,whence=0):
        self.file.seek(offset,whence)
    def tell(self):
        return self.file.tell()
    def write(self,x):
        return self.file.write(x)
    def getString(self,offset = 0):
        if(offset):
            ret = self.file.tell()
            self.seek(offset)
        result = ""
        tmpChar = self.file.read(1)
        while ord(tmpChar) != 0:
            result += tmpChar.decode("utf-8")
            tmpChar = self.file.read(1)
        if(offset):
            self.seek(ret)
        return result
class MTX(object):
    def __init__(self):
        self.matrix = [[0.0,0.0,0.0,0.0]*4]
    def read(self,f):
        tmp = []
        for x in range(4):
            tmp.append(f.f32_4())
        self.matrix = tmp
    def write(self,f):
        for x in self.matrix:
            f.f32_4(x)
textureOffset = 0
materixOffset = 0
materialOffset = 0
isCube = False



class VM(object): # 頂点モデル。Xbox=X、GC=G（VMX、VMGなど）
    class Header(object):
        def __init__(self):
            tmpOnC = {"offset":0,"count":0} # オフセットと件数をまとめた管理用ペア
            self.MAGIC = b'VMX.'
            self.Version = 4
            self.Endian = False # False=LITTLE、True=BIG
            # Version==3の場合：GC/PPCはビッグエンディアン、PS2/MipsとXbox/x86はリトルエンディアン
            self.textureOffsetPoint = 0x10
            self.textureCount = 0x13
            self.isLoaded = 0
            self.unk0 = 0
            self.ModelContent = 0
            self.MatricesInfo = tmpOnC.copy()
            self.Layer0Info = tmpOnC.copy()
            self.Layer1Info = tmpOnC.copy()
            self.Layer2Info = tmpOnC.copy()
            self.BoneInfo = tmpOnC.copy()
            self.MaterialsInfo = tmpOnC.copy()
            self.WeightTableCount = 0
            self.TextureTableOffset = 0
            self.TextureMapOffset = 0
            self.ukn_MatrixTableOffset = 0
            self.WeightTableOffset = 0
            self.ukn01_offset = 0
            self.BoneNameOffset = 0
            self.BoneHeaderOffset = 0
        def read(self,f):
            self.MAGIC = f.read(4)
            if(self.MAGIC == b'VMG.'):
                f.swapEndian()
                isCube = True
                self.Endian = True
            self.Version = f.u8()
            self.textureOffsetPoint = f.u8()
            self.textureCount = f.u8()
            self.isLoaded = f.u8()
            self.unk0 = f.u8()
            self.modelContent = f.u8()
            self.MatricesInfo['count'] = f.u16()
            self.Layer0Info['count'] = f.u16()
            self.Layer1Info['count'] = f.u16()
            self.Layer2Info['count'] = f.u16()
            self.BoneInfo['count'] = f.u16()
            self.MaterialsInfo['count'] = f.u16()
            self.WeightTableCount = f.u16()
            self.TextureTableOffset = f.u32()
            self.MaterialsInfo['offset'] = f.u32()
            self.TextureMapOffset = f.u32()
            self.MatricesInfo['offset'] = f.u32()
            self.ukn_MatrixTableOffset = f.u32()
            self.Layer0Info['offset'] = f.u32()
            self.Layer1Info['offset'] = f.u32()
            self.Layer2Info['offset'] = f.u32()
            self.WeightTableOffset = f.u32()
            self.ukn01_offset = f.u32()
            self.BoneInfo['offset'] = f.u32()
            self.BoneNameOffset = f.u32()
            self.BoneHeaderOffset = f.u32()
        def write(self,f):
            f.write(self.MAGIC)
            f.u8(self.Version)
            f.u8(self.textureOffsetPoint)
            f.u8(self.textureCount)
            f.u8(self.isLoaded)
            f.u8(self.unk0)
            f.u8(self.modelContent)
            f.u16(self.MatricesInfo['count'])
            f.u16(self.Layer0Info['count'])
            f.u16(self.Layer1Info['count'])
            f.u16(self.Layer2Info['count'])
            f.u16(self.BoneInfo['count'])
            f.u16(self.MaterialsInfo['count'])
            f.u16(self.WeightTableCount)
            f.u32(self.TextureTableOffset)
            f.u32(self.MaterialsInfo['offset'])
            f.u32(self.TextureMapOffset)
            f.u32(self.MatricesInfo['offset'])
            f.u32(self.ukn_MatrixTableOffset)
            f.u32(self.Layer0Info['offset'])
            f.u32(self.Layer1Info['offset'])
            f.u32(self.Layer2Info['offset'])
            f.u32(self.WeightTableOffset)
            f.u32(self.ukn01_offset)
            f.u32(self.BoneInfo['offset'])
            f.u32(self.BoneNameOffset)
            f.u32(self.BoneHeaderOffset)
        def __str__(self):
            rt = ""
            rt += str("Magic: %s\n" % self.MAGIC)
            rt += str("Ver: %i\n" % self.Version)
            rt += str("ModelContent: %i\n"%self.ModelContent)
            rt += str("Matrix count %i @ %s\n"%(self.MatricesInfo['count'],hex(self.MatricesInfo['offset'])))
            rt += str("Layer0Info count %i @ %s\n"%(self.Layer0Info['count'],hex(self.Layer0Info['offset'])))
            rt += str("Layer1Info count %i @ %s\n"%(self.Layer1Info['count'],hex(self.Layer1Info['offset'])))
            rt += str("Layer2Info count %i @ %s\n"%(self.Layer2Info['count'],hex(self.Layer2Info['offset'])))
            rt += str("BoneInfo count %i @ %s\n"%(self.BoneInfo['count'],hex(self.BoneInfo['offset'])))
            rt += str("MaterialsInfo count %i @ %s\n"%(self.MaterialsInfo['count'],hex(self.MaterialsInfo['offset'])))
            return rt
    class Credit(object):
        def __init__(self):
            self.day = 0
            self.month = 0
            self.year = 0
            self.sec = 0
            self.min = 0
            self.hour = 0
            self.name = ''
        def read(self,f):
            self.day = f.u8()
            self.month = f.u8()
            self.year = f.u16()

            self.sec = f.u8()
            self.min = f.u8()
            self.hour = f.u8()
            f.u8()
            precrd = f.read(0x20)
            self.name = precrd.decode('shift_jis')
    class Material(object):
        class MaterialMap(object):
            def __init__(self):
                self.offset = 0
                
                self.type = 1
                self.size = 36
                self.value = [0.0]*8
            def read(self,f):
                self.offset = f.tell()
                self.type = f.u16()
                self.size = f.u16()
                self.value = []
                for x in range(int((self.size - 4)/4)):
                    self.value.append(f.f32())
            def write(self,f):
                f.u16(self.type)
                f.u16(self.size)
                for x in self.value:
                    f.f32(x)
        def __init__(self):
            self.textureOffset = 0

            self.Type = 0
            self.unk1 = 0
            self.unk2 = 0
            self.CullMode = 0
            self.OpacitySrc = 0
            self.TextureIdx0 = 0
            self.TextureIdx1 = None
            self.TextureIdx2 = None
            self.TextureMap0 = None
            self.TextureMap1 = None
            self.TextureMap2 = None
            self.AmbientRGBA = [0.0]*4
            self.DiffuseRGBA = [1.0]*4
            self.SpecularRGBA = [0.2,0.2,0.2,20.0]
        def calc_texture_index(self,offset):
            idx = None
            if(offset>self.textureOffset):# 0はインデックスなしを示す
                rel = offset - (self.textureOffset + 0x14)# VXT本体とヘッダ位置まで進める
                div = 0x24
                if(isCube):
                    rel-=4
                    div = 0x44
                idx = int(rel/div)
            return idx
        def write_texture_offset(self,indx):
            if(indx is None):
                return 0
            else:
                muit = 0x24
                if(isCube):
                    muit = 0x44
                return (self.textureOffset + (indx * muit))
        
        def read(self,f):
            value = f.u32()
            self.Type = value & 0xFF
            self.unk1 = (value>>8) & 0xFF
            self.unk2 = (value>>16) & 0xFF
            self.CullMode = (value>>24) & 0xFF
            self.OpacitySrc = f.u32()
            self.TextureIdx0 = self.calc_texture_index(f.u32())
            self.TextureIdx1 = self.calc_texture_index(f.u32())
            self.TextureIdx2 = self.calc_texture_index(f.u32())
            map0 = f.u32()
            if(map0>0):
                self.TextureMap0 = self.MaterialMap()
                ret = f.tell()
                f.seek(map0)
                self.TextureMap0.read(f)
                f.seek(ret)
            map1 = f.u32()
            if(map1>0):
                self.TextureMap1 = self.MaterialMap()
                ret = f.tell()
                f.seek(map1)
                self.TextureMap1.read(f)
                f.seek(ret)
            map2 = f.u32()
            if(map2>0):
                self.TextureMap2 = self.MaterialMap()
                ret = f.tell()
                f.seek(map2)
                self.TextureMap2.read(f)
                f.seek(ret)
            self.AmbientRGBA = f.f32_4()
            self.DiffuseRGBA = f.f32_4()
            self.SpecularRGBA = f.f32_4()
        def write(self,f):
            value = self.Type | (self.unk1 << 8) | (self.unk2 << 16) | (self.CullMode<<24)
            f.u32(value)
            f.u32(self.OpacitySrc)
            f.u32(self.write_texture_offset(self.TextureIdx0))
            f.u32(self.write_texture_offset(self.TextureIdx1))
            f.u32(self.write_texture_offset(self.TextureIdx2))
            if self.TextureMap0 is  None:
                f.u32(0)
            else:
                f.u32(self.TextureMap0.offset)

            if self.TextureMap1 is  None:
                f.u32(0)
            else:
                f.u32(self.TextureMap1.offset)
            
            if self.TextureMap2 is  None:
                f.u32(0)
            else:
                f.u32(self.TextureMap2.offset)
            f.f32_4(self.AmbientRGBA)
            f.f32_4(self.DiffuseRGBA)
            f.f32_4(self.SpecularRGBA)
    class MatrixUnk(object):
        def __init__(self):
            self.unk = 0
            self.Count = 0
            self.Offset = 0
        def read(self,f):
            self.unk = f.u16()
            self.Count = f.u16()
            self.Offset = f.u32()
        def write(self,f):
            f.u16(self.unk)
            f.u16(self.Count)
            f.u32(self.Offset)
    class MatrixTable(object):
        def __init__(self):
            self.Type = 0
            self.ParentBoneIdx = 0
            self.unk1 = 0
            self.unk2 = 0 # ステージファイル用の領域
            self.unk3 = 0
            self.unk4 = 0
            self.Matrix = MTX()
        def read(self,f):
            self.Type = f.u8()
            self.ParentBoneIdx = f.u8()
            self.unk1 = f.u16()
            self.unk2 = f.u32()
            self.unk3 = f.u32()
            self.unk4 = f.u32()
            self.Matrix.read(f)
        def write(self,f):
            f.u8(self.Type)
            f.u8(self.ParentBoneIdx)
            f.u16(self.unk1)
            f.u32(self.unk2)
            f.u32(self.unk3)
            f.u32(self.unk4)
            self.Matrix.write(f)
    class BoneInfo(object):
        def __init__(self):
            self.EndPositionXYZScale = []
            self.swing_backup = bytearray()
            self.StartPositionXYZScale = []
            self.Rotation = []
            self.BoneNameOffset = 0
            self.unk0 = []
            self.rotfix = []
            self.rotfix2 = bytearray()
            self.unk1 = 0
            self.BoneParentIdx = -1
            self.BoneIdx = 0
            self.boneType = 1
            self.Name = ""
        def to_dict(self):
            return {'Name' : self.Name,'EndPositionXYZScale' : self.EndPositionXYZScale,
                    'StartPositionXYZScale' : self.StartPositionXYZScale,
                    'Rotation' : self.Rotation,
                    'Unk0':self.unk0, 'unk1' : self.unk1,'BoneParentIdx':self.BoneParentIdx,
                    'BoneIdx':self.BoneIdx,'boneType':self.boneType}
        def read(self,f,isSC3=False):
            start = f.tell()
            self.EndPositionXYZScale = f.f32_4()
            self.StartPositionXYZScale = f.f32_4()
            self.Rotation = f.f32_3()
            self.BoneNameOffset = f.u32()
            rotstart = f.tell()
            self.unk0 = f.f32_3()
            self.unk1 = f.u8()
            self.BoneParentIdx = f.u8()
            self.BoneIdx = f.u8()
            self.boneType = f.u8()
            end = f.tell()
            if(self.boneType == 11):# GC固有処理（エンディアン変換なし）
                f.seek(start+4)
                self.swing_backup = f.read(12)
                f.seek(rotstart)
                for x in range(2):
                    self.rotfix.append(f.u16())
                self.rotfix2 = f.read(8)
                f.seek(end)
            if(self.BoneNameOffset):
                if(isSC3):
                    self.Name = f.getStringSpecal(self.BoneNameOffset)
                else:
                    self.Name = f.getString(self.BoneNameOffset)
        def write(self,f):
            if(self.boneType == 11):
                f.f32(self.EndPositionXYZScale[0])
                f.write(self.swing_backup)
            else:
                f.f32_4(self.EndPositionXYZScale)
            f.f32_4(self.StartPositionXYZScale)
            f.f32_3(self.Rotation)
            f.u32(self.BoneNameOffset)
            if(self.boneType == 11):
                for x in self.rotfix:
                    f.u16(x)
                f.write(self.rotfix2)
            else:
                f.f32_3(self.unk0)
            f.u8(self.unk1)
            f.u8(self.BoneParentIdx)
            f.u8(self.BoneIdx)
            f.u8(self.boneType)
    class WeightTable(object):
        class BufferColorUV(object):
            def __init__(self):
                self.RGBA = [255]*4
                self.UV = [0.0]*2
            def read(self,f):
                self.RGBA = f.u8_4()
                self.UV = f.f32_2()
            def write(self,f):
                f.u8_4(self.RGBA)
                f.f32_2(self.UV)
        class BufferScaleVertex(object):
            def __init__(self):
                self.Position = [0.0] * 3
                self.PositionScale = 1.0
                self.Normal = [0.0] * 3
                self.NormalScale = 1.0
            def read(self,f):
                self.Position = f.f32_3()
                self.PositionScale = f.f32()
                self.Normal = f.f32_3()
                self.NormalScale = f.f32()
            def gc_read_pos(self,f):
                self.Position = f.f32_3()
                self.PositionScale = f.f32()
            def gc_read_nor(self,f):
                self.Normal = f.f32_3()
            def write(self,f):
                f.f32_3(self.Position)
                f.f32(self.PositionScale)
                f.f32_3(self.Normal)
                f.f32(self.NormalScale)
        class WeightDef(object):
            def __init__(self):
                self.Pos = [0.0]*3
                self.bWgt = 1.0
                self.Nor = [0.0]*3
                self.bIdx = 0
                self.stat = 0
            def read(self,f):
                self.Pos = f.f32_3()
                self.bWgt = f.f32()
                self.Nor = f.f32_3()
                self.bIdx = f.u8()
                self.stat = f.u8()
                f.seek(2,1)
            def read_gc(self,f):
                self.Pos = f.g16_3()
                self.bWgt = f.g16()
                self.Nor = f.g16_3()
                self.stat = f.u8()
                self.bIdx = f.u8()
            def as_bytes(self):
                return struct.pack('fffffffBBH',self.Pos[0],self.Pos[1],self.Pos[2],self.bWgt,self.Nor[0],self.Nor[1],self.Nor[2],self.bIdx,self.stat,0)
            def write(self,f):
                f.f32_3(self.Pos)
                f.f32(self.bWgt)
                f.f32_3(self.Nor)
                f.u8(self.bIdx)
                f.u8(self.stat)
                f.u16(0)
        def __init__(self):
            self.VertCounts = [0]*4
            self.WeightBufferOffset = 0
            self.VertBuffer1Offset = 0
            self.VertBuffer2Offset = 0
            self.VertBuffer0Offset = 0 # 元のレイアウトにはないが、外部互換性のため保持する
            self.WeightBuffer = [] # 影響数が可変のフラットバッファ
            self.VertexBuff0 = [] # カラーとUV
            self.VertexBuff1 = [] # 未解析
            self.VertexBuff2 = [] # 同上
        def dynaSize(self):
                totalSize = 0
                for x in self.WeightBuffer:
                    for y in x:
                        totalSize+=0x20
                return totalSize
        def read_gc(self,f):
            totalVertCount = 0
            for x in range(4):
                self.VertCounts[x] = f.u32()
                totalVertCount += self.VertCounts[x]
            WeightBufferOffset = f.u32()
            VertPosBuffer1Offset = f.u32()
            VertPosBuffer2Offset = f.u32()
            VertNorBuffer1Offset = f.u32()
            VertNorBuffer2Offset = f.u32()
            f.seek(WeightBufferOffset)
            high = 1
            for x in range(self.VertCounts[0]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 2
            for x in range(self.VertCounts[1]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 3
            for x in range(self.VertCounts[2]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    arr.append(a)

                self.WeightBuffer.append(arr)
            high = 4
            for x in range(self.VertCounts[3]):
                arr = []
                total_unbinded = 0
                where_zero = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read_gc(f)
                    if(a.bWgt<=0.0):
                        total_unbinded += 1
                        where_zero.append(y)
                    arr.append(a)
                    if(a.stat == 1):
                        high +=1
                for y in where_zero:
                    sharedWgt = 0.0
                    for z in range(len(arr[y:])):
                        valy = arr[y+z]
                        if(valy.bWgt>0):
                            arr[y+z].bWgt *= 0.5
                            arr[y].bWgt = arr[y+z].bWgt
                            break
                        print(valy.bWgt)


                    print("Zero-weight binding at %i" % y)

                self.WeightBuffer.append(arr)
            posStride = 0
            norStride = 0
            for x in range(totalVertCount):
                f.seek(VertPosBuffer1Offset+posStride)
                a = self.BufferScaleVertex()
                a.gc_read_pos(f)
                posStride+= 0x10
                f.seek(VertNorBuffer1Offset+posStride)
                a.gc_read_nor(f)
                norStride+= 0x10
                self.VertexBuff1.append(a)
            posStride = 0
            norStride = 0
            for x in range(totalVertCount):
                f.seek(VertPosBuffer2Offset+posStride)
                a = self.BufferScaleVertex()
                a.gc_read_pos(f)
                posStride+= 0x10
                f.seek(VertNorBuffer2Offset+norStride)
                a.gc_read_nor(f)
                norStride+= 0x10
                self.VertexBuff2.append(a)
        def read(self,f):
            totalVertCount = 0
            for x in range(4):
                self.VertCounts[x] = f.u32()
                totalVertCount += self.VertCounts[x] 
            self.WeightBufferOffset = f.u32()
            self.VertBuffer1Offset = f.u32()
            self.VertBuffer2Offset = f.u32()
            sizeOfColor = (totalVertCount * 0xC) +(0x10 - ((totalVertCount * 0xC) % 0x10))
            #self.VertBuffer0Offset = self.VertBuffer1Offset - sizeOfColor
            f.seek(self.WeightBufferOffset)
            high = 1
            for x in range(self.VertCounts[0]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 2
            for x in range(self.VertCounts[1]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)
                self.WeightBuffer.append(arr)
            high = 3
            for x in range(self.VertCounts[2]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)

                self.WeightBuffer.append(arr)
            high = 4
            for x in range(self.VertCounts[3]):
                arr = []
                for y in range(high):
                    a = self.WeightDef()
                    a.read(f)
                    arr.append(a)
                    if(a.stat == 1):
                        high +=1
                self.WeightBuffer.append(arr)
            f.seek(self.VertBuffer1Offset)
            for x in range(totalVertCount):
                a = self.BufferScaleVertex()
                a.read(f)
                self.VertexBuff1.append(a)
                
            f.seek(self.VertBuffer2Offset)
            for x in range(totalVertCount):
                a = self.BufferScaleVertex()
                a.read(f)
                self.VertexBuff2.append(a)
            if(self.VertBuffer0Offset):
                f.seek(self.VertBuffer0Offset)
                for x in range(totalVertCount):
                    a = self.BufferColorUV()
                    a.read(f)
                    self.VertexBuff0.append(a)
        def write(self,f):
            for x in self.VertCounts:
                f.u32(x)
            f.u32(self.WeightBufferOffset )
            f.u32(self.VertBuffer1Offset)
            f.u32(self.VertBuffer2Offset)
    class LayerObjectEntryXbox(object):
        class BufferStaticVertex(object):
            def __init__(self):
                self.Position = [0.0] * 3
                self.Normal = [0.0] * 3
                self.RGBA = [255]*4
                self.UV = [0.0]*2
                self.pad = 0
            def read(self,f):
                self.Position = f.f32_3()
                self.Normal = f.f32_3()
                self.RGBA = f.u8_4()
                self.UV = f.f32_2()
                self.pad = f.u32()
            def write(self,f):
                f.f32_3(self.Position)
                f.f32_3(self.Normal)
                f.u8_4(self.RGBA)
                f.f32_2(self.UV)
                f.u32(self.pad)
        def __init__(self):
            self.materialOffset = 0
            self.materixOffset = 0
            self.ObjectType = 0
            self.PrimitiveType = 0
            self.FaceCount = 0
            self.MatrixIndex = 0
            self.MaterialIndex = 0
            self.FaceOffset = 0
            self.Buffer1Offset = 0
            self.Buffer2Offset = 0
            self.Buffer3Offset = 0
            self.Buffer4Offset = 0
            self.CenterRadiusOffset = 0
            self.Mesh = []
            self.StaticVerts = [] 
            self.CenterRadius = [0.0]*4
        def calc_material_index(self,offset):
            rel = offset - self.materialOffset
            idx = int(rel/0x50)
            return idx
        def calc_materix_index(self,offset):
            rel = offset - self.materixOffset
            idx = int(rel/400)
            return idx
        def findmaxVerts(self):
            maxi = 0
            for x in self.Mesh:
                if(x == 0xFFFF):
                    pass
                elif(maxi < x):
                    maxi = x
            return maxi + 1
        def read(self,f):
                self.ObjectType = f.u16()
                self.PrimitiveType = f.u16()
                self.FaceCount = f.u32()
                MatrixOffset = f.u32()
                self.MatrixIndex = self.calc_materix_index(MatrixOffset)
                MaterialOffset = f.u32()
                self.MaterialIndex = self.calc_material_index(MaterialOffset)
                self.FaceOffset = f.u32()
                self.Buffer1Offset = f.u32()
                self.Buffer2Offset = f.u32()
                self.Buffer3Offset = f.u32()
                self.Buffer4Offset = f.u32()
                self.CenterRadiusOffset = f.u32()
                fret = f.tell()
                f.seek(self.FaceOffset)
                for x in range(self.FaceCount):
                    self.Mesh.append(f.u16())
                vertCount = self.findmaxVerts()
                if(self.ObjectType == 4):
                    pass # Dynaメッシュはすべて同じバッファを共有
                else:
                    f.seek(self.Buffer1Offset)
                    for x in range(vertCount):
                        vert = self.BufferStaticVertex()
                        vert.read(f)
                        self.StaticVerts.append(vert)
                    f.seek(self.CenterRadiusOffset)
                    self.CenterRadius = f.f32_4()
                f.seek(fret)
        def write(self,f):
            f.u16(self.ObjectType)
            f.u16(self.PrimitiveType)
            f.u32(self.FaceCount)
            f.u32(self.materixOffset + (self.MatrixIndex*400))
            f.u32(self.materialOffset + (self.MaterialIndex*0x50))
            f.u32(self.FaceOffset)
            f.u32(self.Buffer1Offset)
            f.u32(self.Buffer2Offset)
            f.u32(self.Buffer3Offset)
            f.u32(self.Buffer4Offset)
            f.u32(self.CenterRadiusOffset)
        def __str__(self):
            rt = ""

            if(self.ObjectType == 0):
                rt += "STATIC\n"
            elif(self.ObjectType == 4):
                rt += "SKINNED\n"
            else:
                rt += str("UNK %i\n" % self.ObjectType)

            if(self.PrimitiveType == 0):
                rt += "TRIANGLESTRIP\n"
            elif(self.PrimitiveType == 1):
                rt += "TRIANGLELIST\n"
            else:
                rt += str("UNK %i\n" % self.PrimitiveType)
            rt += str("Face Count: %i @ %s\n" % (self.FaceCount,hex(self.FaceOffset)))
            return rt
    class VertexStorageGC(object):
        def __init__(self,stride,format,fraction):
            self.stride = stride
            self.format = format # Ubyte、Byte、UShort、Short、Float
            self.fraction = fraction
            self.values = []

        def read(self,f):
            numVal = 0
            reader = f.u8
            devisor = 1
            
            match(self.format):
                case 0:
                    numVal = self.stride
                    reader = f.u8
                    devisor = (1<<self.fraction)
                case 1:
                    numVal = self.stride
                    reader = f.s8
                    devisor = (1<<self.fraction)
                case 2:
                    numVal = int(self.stride / 2)
                    reader = f.u16
                    devisor = (1<<self.fraction)
                case 3:
                    numVal = int(self.stride / 2)
                    reader = f.s16
                    devisor = (1<<self.fraction)
                case _:
                    numVal = int(self.stride / 4)
                    reader = f.f32
            valz = []

            for x in range(numVal):
                valbefore = reader()
                valz.append(float(float(valbefore)/devisor))
            self.values.append(valz)        
    class LayerObjectEntryGC(object):
        class PolyHead(object):
            def __init__(self,StrideArr,type):
                self.Type = 0x90
                self.StrideArr = StrideArr
                self.FaceType = type
                self.IdxArr = []
                self.large = [0,0,0,0]
            def read(self,f):
                sizeValue = 1
                if(self.FaceType == 2):
                    f.u8()
                    sizeValue+=1
                self.Type = f.u8()
                if(self.Type > 0):
                    sizeValue += 2
                    idxSize = f.u16()
                    
                    for x in range(idxSize):
                        idx = []
                        for y in range(4):
                            if(self.StrideArr[y] == 2):
                                sizeValue +=1
                                idx.append(f.u8())
                            elif(self.StrideArr[y] == 3):
                                sizeValue += 2
                                idx.append(f.u16())
                            if(self.large[y] < idx[y]+1):
                                self.large[y] = idx[y]+1
                        self.IdxArr.append(idx)
                return sizeValue
        def __init__(self):
            self.MeshType = 0
            self.PositionStorage = VM.VertexStorageGC(12,4,0) # 静的形式として設定
            self.NormalStorage = VM.VertexStorageGC(12,4,0) # 静的形式として設定
            self.UVStorage = VM.VertexStorageGC(8,4,0)

            self.idxType = [2,2,2,2] # Index8=2／Index16=3
            self.FaceCount = 0
            self.MatrixOffset = 0
            self.MatrixIndex = 0
            self.MaterialOffset = 0
            self.MaterialIndex = 0
            self.Position1Offset = 0
            self.Position2Offset = 0
            self.Normal1Offset = 0
            self.Normal2Offset = 0
            self.ColorOffset = 0
            self.TexCoordOffset = 0
            self.FaceOffset = 0
            self.BoundingOffset = 0
            self.Mesh = []
            self.topV = 0
            self.Possition = []
            self.Normal = []
            self.Color = []
            self.TexCords = []
            self.CenterRadius = [0.0]*4
        def calc_material_index(self,offset):
            rel = offset - self.materialOffset
            idx = int(rel/0x50)
            return idx
        def calc_materix_index(self,offset):
            rel = offset - self.materixOffset
            idx = int(rel/336)
            return idx
        def read(self,f):
            self.MeshType = f.u8()

            pStride = f.u8()
            pFormat = f.u8()
            pScale = f.u8()
            self.PositionStorage = VM.VertexStorageGC(pStride,pFormat,pScale)

            nStride = f.u8()
            nFormat = f.u8()
            nScale = f.u8()
            self.NormalStorage = VM.VertexStorageGC(nStride,nFormat,nScale)

            uStride = f.u8()
            uFormat = f.u8()
            uScale = f.u8()
            self.UVStorage = VM.VertexStorageGC(uStride,uFormat,uScale)


            self.idxType = [f.u8(),f.u8(),f.u8(),f.u8()] # Index8=2／Index16=3
            self.FaceCount = f.u16()
            MatrixOffset = f.u32()
            self.MatrixIndex = self.calc_materix_index(MatrixOffset)
            MaterialOffset = f.u32()
            self.MaterialIndex = self.calc_material_index(MaterialOffset)
            self.Position1Offset = f.u32()
            self.Position2Offset = f.u32()
            self.Normal1Offset = f.u32()
            self.Normal2Offset = f.u32()
            self.ColorOffset = f.u32()
            self.TexCoordOffset = f.u32()
            self.FaceOffset = f.u32()
            self.BoundingOffset = f.u32()
            ret = f.tell()
            f.seek(self.FaceOffset)
            toContinue = self.FaceCount * 32
            self.topV = 0
            topN = 0 
            topC = 0
            topT = 0
            
            while(toContinue>0):
                head = self.PolyHead(self.idxType,self.MeshType)
                size = head.read(f)
                if(size>1):
                    toContinue -= size
                    if(self.topV < head.large[0]):
                        self.topV = head.large[0]
                    if(topN < head.large[1]):
                        topN = head.large[1]
                    if(topC < head.large[2]):
                        topC = head.large[2]
                    if(topT < head.large[3]):
                        topT = head.large[3]
                    self.Mesh.append(head)
                else:
                    toContinue = 0
            f.seek(self.Position1Offset)
            for x in range(self.topV):
                self.PositionStorage.read(f)
            f.seek(self.Normal1Offset)
            for x in range(topN):
                self.NormalStorage.read(f)
            f.seek(self.ColorOffset)
            for x in range(topC):
                self.Color.append(f.u8_4())
            f.seek(self.TexCoordOffset)
            for x in range(topT):
                self.UVStorage.read(f)
            f.seek(self.BoundingOffset)
            self.CenterRadius = f.f32_4()
            f.seek(ret)
    def __init__(self):
        self.f = None
        self.header = self.Header()
        self.unkMtx = self.MatrixUnk()
        self.wgtTbl = self.WeightTable()
        self.matrix_table = []
        self.materials = []
        self.boneInfo = []
        self.Object_0 = []
        self.Object_1 = []
        self.Object_2 = []
        self.texture = b''
        self.unkArray = b'\x00'*40
        self.credits = self.Credit()
        self.textureOffset = 0
        self.materixOffset = 0
        self.materialOffset = 0
    def read(self,f):
        self.f = FRead(f)
        self.header.read(self.f)
        self.textureOffset = self.header.TextureTableOffset
        textureSize = self.header.BoneHeaderOffset - self.textureOffset
        self.f.seek(self.textureOffset)
        self.texture = self.f.read(textureSize)
        self.f.seek(self.header.BoneHeaderOffset)
        aeu = f.tell()
        self.unkArray = f.read(40)
        f.seek(aeu)
        self.credits.read(self.f)
        self.f.seek(self.header.ukn_MatrixTableOffset)
        self.unkMtx.read(self.f)

        self.materixOffset = self.header.MatricesInfo['offset']
        self.f.seek(self.header.MatricesInfo['offset'])
        skipAmount = 320
        if(self.header.Endian):
            skipAmount = 256
        for x in range(self.header.MatricesInfo['count']):
            a = self.MatrixTable()
            a.read(self.f)
            self.matrix_table.append(a)
            self.f.seek(skipAmount,1)
        self.materialOffset = self.header.MaterialsInfo['offset']
        self.f.seek(self.header.MaterialsInfo['offset'])
        for x in range(self.header.MaterialsInfo['count']):
            a = self.Material()
            a.textureOffset = self.textureOffset
            a.read(self.f)
            self.materials.append(a)
        self.f.seek(self.header.BoneInfo['offset'])
        for x in range(self.header.BoneInfo['count']):
            a = self.BoneInfo()
            a.read(self.f)
            self.boneInfo.append(a)
        
        
        
        layerType = self.LayerObjectEntryXbox
        if(self.header.Endian):
            layerType = self.LayerObjectEntryGC
        self.f.seek(self.header.Layer0Info['offset'])
        
        for x in range(self.header.Layer0Info['count']):
            Layer = layerType()
            Layer.materialOffset = self.materialOffset
            Layer.materixOffset = self.materixOffset
            Layer.read(self.f)
            self.Object_0.append(Layer)
        self.f.seek(self.header.Layer1Info['offset'])
        for x in range(self.header.Layer1Info['count']):
            Layer = layerType()
            Layer.materialOffset = self.materialOffset
            Layer.materixOffset = self.materixOffset
            Layer.read(self.f)
            self.Object_1.append(Layer)
        self.f.seek(self.header.Layer2Info['offset'])
        for x in range(self.header.Layer2Info['count']):
            Layer = layerType()
            Layer.materialOffset = self.materialOffset
            Layer.materixOffset = self.materixOffset
            Layer.read(self.f)
            self.Object_2.append(Layer)
        if(not self.header.Endian):
            for x in self.Object_0:
                if(x.ObjectType == 4):
                    self.wgtTbl.VertBuffer0Offset = x.Buffer1Offset
            if(self.header.WeightTableCount):
                self.f.seek(self.header.WeightTableOffset)
                self.wgtTbl.read(self.f)
        else:
            if(self.header.WeightTableCount):
                self.f.seek(self.header.WeightTableOffset)
                self.wgtTbl.read_gc(self.f)
    def calcObj(self,x,head):
        x.materixOffset = self.materixOffset
        x.materialOffset = self.materialOffset
        if(x.ObjectType == 4):
            x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
            x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
            x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
            if(head % 0x10):
                head += 0x10 - (head % 0x10)
            x.FaceOffset = head
            x.FaceCount = len(x.Mesh)
            head += len(x.Mesh)*2
        if(x.ObjectType == 0):
            x.Buffer1Offset = head
            head += len(x.StaticVerts) * 40
            if(head % 0x10):
                head += 0x10 - (head % 0x10)
            x.CenterRadiusOffset = head
            head += 0x10
    def recalc(self):
        head = 0x4C # ヘッダ直後。多くのデータはここから始まる
        self.header.Layer0Info['offset'] = head
        self.header.Layer0Info['count'] = len(self.Object_0)
        head += len(self.Object_0)*40

        self.header.Layer1Info['offset'] = head
        self.header.Layer1Info['count'] = len(self.Object_1)
        head += len(self.Object_1)*40

        self.header.Layer2Info['offset'] = head
        self.header.Layer2Info['count'] = len(self.Object_2)
        head += len(self.Object_2)*40
        self.header.TextureMapOffset = head
        
        for x in self.materials:
            if x.TextureMap0 is not None:
                x.TextureMap0.size = 4*len(x.TextureMap0.value)+4
                x.TextureMap0.offset = head
                head += x.TextureMap0.size
            if x.TextureMap1 is not None:
                 x.TextureMap1.size = 4*len(x.TextureMap1.value)+4
                 x.TextureMap1.offset = head
                 head += x.TextureMap1.size
            if x.TextureMap2 is not None:
                 x.TextureMap2.size = len(x.TextureMap2.value)+4
                 x.TextureMap2.offset = head
                 head += x.TextureMap2.size
        
        head += 4#That part where 0xFFFFFFFF comes in... still dont know yet but we respect it
        self.header.WeightTableOffset = head
        if(self.header.WeightTableCount):
            head += 28

        self.header.ukn_MatrixTableOffset = head
        head += 8
        if(head % 0x10):
            head += 0x10 - (head % 0x10)

        self.header.MatricesInfo['offset'] = head
        self.materixOffset = head
        self.header.MatricesInfo['count'] = len(self.matrix_table)
        head += len(self.matrix_table) * 400

        self.unkMtx.Offset = head
        self.materialOffset = head
        self.header.MaterialsInfo['offset'] = head
        self.header.MaterialsInfo['count'] = len(self.materials)
        head += len(self.materials) * 80
        if(self.header.WeightTableCount):
            self.wgtTbl.VertBuffer0Offset = head
            head += len(self.wgtTbl.VertexBuff0)*12
            if(head % 0x10):
                head += 0x10 - (head % 0x10)
            self.wgtTbl.VertBuffer1Offset = head
            head += len(self.wgtTbl.VertexBuff1)*0x20
            head += 0x400 # 予約アライメント領域。確認した配置をそのまま保持する
            self.wgtTbl.VertBuffer2Offset = head
            head += len(self.wgtTbl.VertexBuff2)*0x20
            head += 0x400 # ここも同様
            self.wgtTbl.WeightBufferOffset = head
            head += self.wgtTbl.dynaSize()
            head += 0x10 # 0xF境界の調整
            for x in self.Object_0:
                if(x.ObjectType == 4):
                    x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
                    x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
                    x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
                    if(head % 0x10):
                        head += 0x10 - (head % 0x10)
                    x.FaceOffset = head
                    x.FaceCount = len(x.Mesh)
                    head += len(x.Mesh)*2
            for x in self.Object_1:
                if(x.ObjectType == 4):
                    x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
                    x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
                    x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
                    if(head % 0x10):
                        head += 0x10 - (head % 0x10)
                    x.FaceOffset = head
                    x.FaceCount = len(x.Mesh)
                    head += len(x.Mesh)*2
            for x in self.Object_2:
                if(x.ObjectType == 4):
                    x.Buffer1Offset = self.wgtTbl.VertBuffer0Offset
                    x.Buffer2Offset = self.wgtTbl.VertBuffer1Offset
                    x.Buffer3Offset = self.wgtTbl.VertBuffer2Offset
                    if(head % 0x10):
                        head += 0x10 - (head % 0x10)
                    x.FaceOffset = head
                    x.FaceCount = len(x.Mesh)
                    head += len(x.Mesh)*2
        if(head % 0x10):
            head += 0x10 - (head % 0x10)
        for x in self.Object_0:
            x.materixOffset = self.materixOffset
            x.materialOffset = self.materialOffset
            if(x.ObjectType == 0):
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.Buffer1Offset = head
                x.Buffer4Offset = head
                head += len(x.StaticVerts) * 40
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
               
                x.CenterRadiusOffset = head
                head += 0x10
                x.FaceOffset = head
                x.FaceCount = len(x.Mesh)
                head += len(x.Mesh)*2
        for x in self.Object_1:
            x.materixOffset = self.materixOffset
            x.materialOffset = self.materialOffset
            if(x.ObjectType == 0):
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.Buffer1Offset = head
                x.Buffer4Offset = head
                head += len(x.StaticVerts) * 40
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.CenterRadiusOffset = head
                head += 0x10
                x.FaceOffset = head
                x.FaceCount = len(x.Mesh)
                head += len(x.Mesh)*2
        for x in self.Object_2:
            x.materixOffset = self.materixOffset
            x.materialOffset = self.materialOffset
            if(x.ObjectType == 0):
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.Buffer1Offset = head
                x.Buffer4Offset = head
                head += len(x.StaticVerts) * 40
                if(head % 0x10):
                    head += 0x10 - (head % 0x10)
                x.CenterRadiusOffset = head
                head += 0x10
                x.FaceOffset = head
                x.FaceCount = len(x.Mesh)
                head += len(x.Mesh)*2

        self.header.BoneInfo['offset'] = head
        self.header.BoneInfo['count'] = len(self.boneInfo)
        head += len(self.boneInfo)*0x40
        if(head % 0x80):
            head += 0x80 - (head % 0x80)
            
        self.header.TextureTableOffset = head
        self.textureOffset = head+0x14
        for x in self.materials:
            x.textureOffset = head+0x14
        head += len(self.texture)
        if(head % 0x10):
            head += 0x10 - (head % 0x10)
        self.header.BoneHeaderOffset = head
        head += 40
        self.header.BoneNameOffset = head
        for x in self.boneInfo:
            if(len(x.Name)>0):
                x.BoneNameOffset = head
                head += len(x.Name)+1
            else:
                x.BoneNameOffset = 0
            

    def write(self,ff):
        f = FWrite(ff)
        self.recalc()
        self.header.write(f)
        for x in self.Object_0:
            x.write(f)
        for x in self.Object_1:
            x.write(f)
        for x in self.Object_2:
            x.write(f)
        for x in self.materials:
            if x.TextureMap0 is not None:
                x.TextureMap0.write(f)
            if x.TextureMap1 is not None:
                 x.TextureMap1.write(f)
            if x.TextureMap2 is not None:
                 x.TextureMap2.write(f)
        f.write(b'\xFF\xFF\xFF\xFF')
        if(self.header.WeightTableCount > 0):
            self.wgtTbl.write(f)
        self.unkMtx.write(f)
        alighnment = f.tell() % 0x10
        if(alighnment):
            for y in range(0x10-alighnment):
                f.u8(0)
        for x in self.matrix_table:
            x.write(f)
            f.write(b'\x00'*320)
        for x in self.materials:
            x.write(f)
        if(self.header.WeightTableCount > 0):
            for x in self.wgtTbl.VertexBuff0:
                x.write(f)
            alighnment = f.tell() % 0x10
            if(alighnment):
                for y in range(0x10-alighnment):
                    f.u8(0)
            for x in self.wgtTbl.VertexBuff1:
                x.write(f)
            f.write(b'\x00'*0x400)
            for x in self.wgtTbl.VertexBuff2:
                x.write(f)
            f.write(b'\x00'*0x400)
            for x in self.wgtTbl.WeightBuffer:
                for y in x:
                    y.write(f)
            f.write(b'\xFF'*0x10)
            for x in self.Object_0:
                if x.ObjectType == 0x4:
                    alighnment = f.tell() % 0x10
                    if(alighnment):
                        for y in range(0x10-alighnment):
                            f.u8(0)
                    for y in x.Mesh:
                        f.u16(y)
            for x in self.Object_1:
                if x.ObjectType == 0x4:
                    alighnment = f.tell() % 0x10
                    if(alighnment):
                        for y in range(0x10-alighnment):
                            f.u8(0)
                    for y in x.Mesh:
                        f.u16(y)
            for x in self.Object_2:
                if x.ObjectType == 0x4:
                    alighnment = f.tell() % 0x10
                    if(alighnment):
                        for y in range(0x10-alighnment):
                            f.u8(0)
                    for y in x.Mesh:
                        f.u16(y)
            alighnment = f.tell() % 0x10
            if(alighnment):
                for y in range(0x10-alighnment):
                    f.u8(0)
        for x in self.Object_0:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.StaticVerts:
                    y.write(f)
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                f.f32_4(x.CenterRadius)
                for y in x.Mesh:
                    f.u16(y)
        for x in self.Object_1:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.StaticVerts:
                    y.write(f)
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                f.f32_4(x.CenterRadius)
                for y in x.Mesh:
                    f.u16(y)
        for x in self.Object_2:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.StaticVerts:
                    y.write(f)
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                f.f32_4(x.CenterRadius)
                for y in x.Mesh:
                    f.u16(y)
        
        
        for x in self.Object_2:
            if x.ObjectType == 0:
                alighnment = f.tell() % 0x10
                if(alighnment):
                    for y in range(0x10-alighnment):
                        f.u8(0)
                for y in x.Mesh:
                    f.u16(y)
        for x in self.boneInfo:
            x.write(f)
        alighnment = f.tell() % 0x80
        if(alighnment):
            for y in range(0x80-alighnment):
                f.u8(0)
        f.write(self.texture)
        alighnment = f.tell() % 0x10
        if(alighnment):
            for y in range(0x10-alighnment):
                f.u8(0)
        f.write(self.unkArray)
        for x in self.boneInfo:
            if(len(x.Name)>0):
                f.write(x.Name.encode())
                f.u8(0)
        alighnment = f.tell() % 0x80
        if(alighnment):
            for y in range(0x80-alighnment):
                f.u8(0)
    def toXbox(self):
        if(self.header.Endian):
            isCube = False
            largest = 0
            newObj_0 = []
            for x in self.Object_0:
                obj = self.LayerObjectEntryXbox()
                isStatic = x.Position2Offset == 0
                obj.ObjectType = 0 if isStatic else 4
                
                isTristrip = x.Mesh[0].Type == 0x98
                obj.PrimitiveType = 0 if isTristrip else 1
                
                big = 0
                for y in x.Mesh:
                    if(big < max(y.large)):
                        big = max(y.large)
                
                newMesh = []
                if(isStatic):
                    newVert = [VM.LayerObjectEntryXbox.BufferStaticVertex()] * big
                else:
                    newVert = [VM.WeightTable.BufferColorUV()] * big
                
                isStart = True
                prev = 0
                for y in x.Mesh:
                    if(not isStart):
                        if(isTristrip):
                            newMesh.append(prev)
                            newMesh.append(y.IdxArr[0][0])
                    for z in y.IdxArr:
                        if(isStatic):
                            nVert = VM.LayerObjectEntryXbox.BufferStaticVertex()
                            nVert.Position = x.PositionStorage.values[z[0]]
                            nVert.Normal = x.NormalStorage.values[z[1]]
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        else:
                            nVert = VM.WeightTable.BufferColorUV()
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        newMesh.append(z[0])
                        prev = z[0]
                    isStart = False
                obj.Mesh = newMesh
                if(isStatic):
                    obj.StaticVerts = newVert
                    obj.CenterRadius = x.CenterRadius
                else:
                    if(largest < big):
                        self.wgtTbl.VertexBuff0 = newVert
                obj.MatrixIndex = x.MatrixIndex
                obj.MaterialIndex = x.MaterialIndex
                newObj_0.append(obj)

            newObj_1 = []
            for x in self.Object_1:
                obj = self.LayerObjectEntryXbox()
                isStatic = x.Position2Offset == 0
                obj.ObjectType = 0 if isStatic else 4
                
                isTristrip = x.Mesh[0].Type == 0x98
                obj.PrimitiveType = 0 if isTristrip else 1
                
                big = 0
                for y in x.Mesh:
                    if(big < max(y.large)):
                        big = max(y.large)
                
                newMesh = []
                if(isStatic):
                    newVert = [VM.LayerObjectEntryXbox.BufferStaticVertex()] * big
                else:
                    newVert = [VM.WeightTable.BufferColorUV()] * big
                
                isStart = True
                prev = 0
                for y in x.Mesh:
                    if(not isStart):
                        if(isTristrip):
                            newMesh.append(prev)
                            newMesh.append(y.IdxArr[0][0])
                    for z in y.IdxArr:
                        if(isStatic):
                            nVert = VM.LayerObjectEntryXbox.BufferStaticVertex()
                            nVert.Position = x.PositionStorage.values[z[0]]
                            nVert.Normal = x.NormalStorage.values[z[1]]
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        else:
                            nVert = VM.WeightTable.BufferColorUV()
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        newMesh.append(z[0])
                        prev = z[0]
                    isStart = False
                obj.Mesh = newMesh
                if(isStatic):
                    obj.StaticVerts = newVert
                    obj.CenterRadius = x.CenterRadius
                else:
                    if(largest < big):
                        self.wgtTbl.VertexBuff0 = newVert
                obj.MatrixIndex = x.MatrixIndex
                obj.MaterialIndex = x.MaterialIndex
                newObj_1.append(obj)
            newObj_2 = []
            for x in self.Object_2:
                obj = self.LayerObjectEntryXbox()
                isStatic = x.Position2Offset == 0
                obj.ObjectType = 0 if isStatic else 4
                
                isTristrip = x.Mesh[0].Type == 0x98
                obj.PrimitiveType = 0 if isTristrip else 1
                
                big = 0
                for y in x.Mesh:
                    if(big < max(y.large)):
                        big = max(y.large)
                
                newMesh = []
                if(isStatic):
                    newVert = [VM.LayerObjectEntryXbox.BufferStaticVertex()] * big
                else:
                    newVert = [VM.WeightTable.BufferColorUV()] * big
                
                isStart = True
                prev = 0
                for y in x.Mesh:
                    if(not isStart):
                        if(isTristrip):
                            newMesh.append(prev)
                            newMesh.append(y.IdxArr[0][0])
                    for z in y.IdxArr:
                        if(isStatic):
                            nVert = VM.LayerObjectEntryXbox.BufferStaticVertex()
                            nVert.Position = x.PositionStorage.values[z[0]]
                            nVert.Normal = x.NormalStorage.values[z[1]]
                            
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        else:
                            nVert = VM.WeightTable.BufferColorUV()
                            nVert.RGBA = x.Color[z[2]]
                            nVert.UV = x.UVStorage.values[z[3]]
                            newVert[z[0]] = nVert
                        newMesh.append(z[0])
                        prev = z[0]
                    isStart = False
                obj.Mesh = newMesh
                if(isStatic):
                    obj.StaticVerts = newVert
                    obj.CenterRadius = x.CenterRadius
                else:
                    if(largest < big):
                        self.wgtTbl.VertexBuff0 = newVert
                obj.MatrixIndex = x.MatrixIndex
                obj.MaterialIndex = x.MaterialIndex
                newObj_2.append(obj)
            self.Object_0 = newObj_0
            self.Object_1 = newObj_1
            self.Object_2 = newObj_2
            # 行列の並びを変更
            for x in self.matrix_table:
                x.Matrix.matrix = rotateMtx(x.Matrix.matrix)
            # 最後にエンディアンを変更
            self.header.Endian = False
            self.header.MAGIC = b'VMX.'
            self.header.Version = 4
            self.f.swapEndian()
        else:
            print("Xbox format detected")