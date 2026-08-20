# -*- coding: utf-8 -*-
bl_info = {
    "name": "SC2 Model (VMP / VMX / VMG)",
    "author": "Hino , smb123w64gb, Diogenes",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "File > Import > SoulCalibur II model (.vmp/.vmx/.vmg)",
    "description": "",
    "category": "Import",
}

import os
import importlib
import bpy
from bpy.props import (StringProperty, BoolProperty, FloatProperty,
                       CollectionProperty)
from bpy.types import Operator, OperatorFileListElement
try:
    from bpy_extras.io_utils import ImportHelper
except Exception:
    ImportHelper = object

from . import builder
from . import loader

# 開発中のホットリロード
importlib.reload(builder)
importlib.reload(loader)


class SC2IO_OT_import(Operator, ImportHelper):
    """読み込み（PS2 .vmp／Xbox .vmx／GameCube .vmg）"""
    bl_idname = "import_scene.sc2_model"
    bl_label = "SC2モデルを読み込む"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".vmp"
    filter_glob: StringProperty(default="*.vmp;*.vmx;*.vmg", options={'HIDDEN'})

    # 複数ファイル：複数キャラクターを一度に選択
    files: CollectionProperty(name="ファイル", type=OperatorFileListElement)
    directory: StringProperty(subtype='DIR_PATH')

    import_skeleton: BoolProperty(
        name="スケルトン", default=True,
        description="アーマチュアを作成し、メッシュを結合する（頂点グループでスキニング）")
    import_textures: BoolProperty(
        name="テクスチャ", default=True,
        description="テクスチャをデコードして適用する（VXT／VGT／VPT）")
    import_normals: BoolProperty(
        name="法線", default=True,
        description="頂点ごとの実法線（カスタム分割）を読み、法線に合わせて面の向きを補正する")
    use_alpha: BoolProperty(
        name="アルファ（透明度）", default=False,
        description="テクスチャのアルファを透明度として使う（無効時は不透明、推奨）")
    flip_v: BoolProperty(
        name="Vを反転（UV）", default=True,
        description="BlenderのUV規約（下から上）。特定形式でテクスチャが上下反転する場合は解除")
    global_scale: FloatProperty(name="スケール", default=1.0, min=0.001, max=1000.0)

    def execute(self, context):
        paths = []
        if self.files and self.directory:
            for fe in self.files:
                if fe.name:
                    paths.append(os.path.join(self.directory, fe.name))
        if not paths and self.filepath:
            paths = [self.filepath]
        if not paths:
            self.report({'ERROR'}, "ファイルが選択されていません。")
            return {'CANCELLED'}

        ok = 0
        reports = []
        for p in paths:
            res = loader.import_model(
                p,
                import_skeleton=self.import_skeleton,
                import_textures=self.import_textures,
                global_scale=self.global_scale,
                use_alpha=self.use_alpha,
                import_normals=self.import_normals,
                flip_v=self.flip_v,
            )
            if res.get("ok"):
                ok += 1
                reports.append(res.get("report", os.path.basename(p)))
            else:
                reports.append("%s : %s" % (os.path.basename(p), res.get("error", "?")))

        level = {'INFO'} if ok == len(paths) else ({'WARNING'} if ok else {'ERROR'})
        self.report(level, "%d/%d件を読み込みました。%s" % (ok, len(paths), " || ".join(reports)))
        return {'FINISHED'} if ok else {'CANCELLED'}

    def draw(self, context):
        l = self.layout
        l.prop(self, "import_skeleton")
        l.prop(self, "import_textures")
        l.prop(self, "import_normals")
        l.prop(self, "use_alpha")
        l.prop(self, "flip_v")
        l.prop(self, "global_scale")


def menu_func_import(self, context):
    self.layout.operator(SC2IO_OT_import.bl_idname,
                         text="SoulCalibur II model (.vmp/.vmx/.vmg)")


def register():
    bpy.utils.register_class(SC2IO_OT_import)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(SC2IO_OT_import)


if __name__ == "__main__":
    register()
