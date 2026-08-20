# -*- coding: utf-8 -*-
"""形式判定 → パーサ → 共通Blender処理（builder.py）。

マジック値で判定し、失敗時は拡張子を使う：
    'VMX...'         → Xbox      (model_fmt_vmx)
    'VMG...'         → GameCube  (model_fmt_vmg)
    byte0 0x08/0x09  → PS2 VMP   (model_fmt_vmp)   [0x08=SC2、0x09=SC3]
"""

import os
import sys
import importlib

from . import builder

_PARSERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsers")


def _ensure_path():
    if _PARSERS_DIR not in sys.path:
        sys.path.insert(0, _PARSERS_DIR)


def detect_format(filepath):
    """'vmp'、'vmx'、'vmg'、またはNoneを返す。まずマジック値、次に拡張子で判定。"""
    try:
        with open(filepath, "rb") as f:
            head = f.read(8)
    except Exception:
        head = b""
    if head[:3] == b"VMX":
        return "vmx"
    if head[:3] == b"VMG":
        return "vmg"
    if head and (head[0] & 0xFF) in (0x08, 0x09):
        return "vmp"
    ext = os.path.splitext(filepath)[1].lower()
    return {".vmp": "vmp", ".vmx": "vmx", ".vmg": "vmg"}.get(ext)


def _load_model(fmt, filepath):
    """対応する同梱パーサを読み込み、モデルインスタンスを返す。"""
    _ensure_path()
    modname = {"vmp": "model_fmt_vmp", "vmx": "model_fmt_vmx", "vmg": "model_fmt_vmg"}[fmt]
    # 開発中や再インポート時のクリーンな再読み込み
    for k in list(sys.modules):
        if k == modname or k.startswith(modname + "."):
            del sys.modules[k]
    mod = importlib.import_module(modname)
    return mod.load(filepath)


def import_model(filepath, import_skeleton=True, import_textures=True,
                 global_scale=1.0, use_alpha=False, import_normals=True,
                 flip_v=True):
    """単一エントリポイント。.vmp／.vmx／.vmgをBlenderへ読み込む。"""
    import bpy
    fmt = detect_format(filepath)
    if fmt is None:
        return {"ok": False, "error": "未認識の形式（VMX／VMG／VMPではありません）。"}

    try:
        model = _load_model(fmt, filepath)
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"ok": False, "error": "解析失敗（%s）：%s" % (fmt.upper(), e)}
    if model is None:
        return {"ok": False, "error": "%sパーサが結果を返しませんでした。" % fmt.upper()}

    base = os.path.splitext(os.path.basename(filepath))[0]
    scale = float(global_scale)
    # VMGは足元が0、VMP／VMXは中央基準で出力される。VMXのCENTER_Yと同じ生空間で
    # VMGを1.15下げ、3形式の高さを揃える。
    center_y = 1.15 if fmt == "vmg" else 0.0
    nb = len(getattr(model, "bones", []) or [])
    nv = len(getattr(model, "verts", []) or [])
    nt = len(getattr(model, "tris", []) or [])
    log = ["%s: bones=%d verts=%d tris=%d mats=%d"
           % (fmt.upper(), nb, nv, nt, len(getattr(model, "materials", []) or []))]

    # アーマチュア
    arm_obj = None
    if import_skeleton and nb:
        try:
            arm_obj = builder.build_armature(model, "%s_Armature" % base, scale, center_y)
        except Exception as e:
            import traceback; traceback.print_exc(); log.append("arm_err=%s" % e)

    # マテリアル
    try:
        materials = builder.build_materials(model, base, use_alpha) if import_textures \
            else builder.build_materials(_NoMats(), base, use_alpha)
    except Exception as e:
        import traceback; traceback.print_exc(); log.append("tex_err=%s" % e)
        materials = builder.build_materials(_NoMats(), base, use_alpha)

    # メッシュ
    try:
        obj = builder.build_mesh(model, "%s_mesh" % base, arm_obj, scale, materials,
                                 use_normals=import_normals, flip_v=flip_v, center_y=center_y)
        log.append("mesh=%s" % ("ok" if obj else "empty"))
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"ok": False, "error": "メッシュ構築失敗：%s" % e}

    bpy.context.view_layer.update()
    return {"ok": True, "report": " | ".join(log)}


class _NoMats(object):
    """テクスチャなしのダミーモデル（import_textures無効時）。"""
    materials = []
