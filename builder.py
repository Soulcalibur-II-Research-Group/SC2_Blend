# -*- coding: utf-8 -*-
# builder.py — VMP/VMX/VMG共通のBlender側処理
#
# 3パーサ(model_fmt_{vmp,vmg,vmx})は同じインタフェースを返す:
#   model.bones[]      -> .Name, .Parent, .X/.Y/.Z
#   model.verts[]      -> .X/.Y/.Z, .Nx/.Ny/.Nz, .U/.V, .Inf=[[bone_i, weight], ...]
#   model.tris[]       -> .A, .B, .C, .Mat
#   model.materials[]  -> .Rgba, .W, .H, .Cutout
#   model.wr[] / model.wt[]  -> 骨ごとのワールド行列(回転flat9 / 平行移動)
#
# ここではフォーマットの中身は一切知らない。上のインタフェースを食って
# armature/mesh/materialをBlenderに組むだけ。3機種で同じコード。

import math
import bpy
from mathutils import Vector


# モデルはY-up、Blenderはz-up
def blender_co(p, scale):
    return (p[0] * scale, -p[2] * scale, p[1] * scale)


def build_armature(model, name, scale, center_y=0.0):
    # model.bones + model.wt からarmatureを組む
    # center_y: モデル空間(Y-up)でのY方向オフセット。骨と頂点の両方にかける。
    # VMP/VMXは足下が原点(center済み)、VMGは足が0にくるので center_y=1.15
    # (VMXのCENTER_Y、同じ生の空間)を渡して他2機種と高さを合わせる。
    bones = model.bones
    wt = getattr(model, "wt", None)
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    eb = {}
    for i, b in enumerate(bones):
        # bones[i].X/Y/Zは頂点と同じ空間(VMPはfix_axis適用済み、VMG/VMXはwtと一致)。
        # model.wtには絶対に落とさない。VMPのwtはfix_axis無しの生値で、
        # armatureがX<->Zで90度ズレて出る。
        bx = getattr(b, "X", None)
        if bx is not None:
            wp = (bx, getattr(b, "Y", 0.0) - center_y, getattr(b, "Z", 0.0))
        elif wt and i < len(wt) and wt[i] is not None:
            wp = (wt[i][0], wt[i][1] - center_y, wt[i][2])
        else:
            wp = (0.0, -center_y, 0.0)
        head = Vector(blender_co(wp, scale))
        e = arm.edit_bones.new(_safe_bone_name(b.Name if getattr(b, "Name", "") else "bone%d" % i))
        e.head = head
        e.tail = head + Vector((0, 0, 0.02))
        eb[i] = e

    for i, b in enumerate(bones):
        par = _parent_of(b, len(bones), i)
        if par is not None and par in eb:
            eb[i].parent = eb[par]
            ph = eb[par].head
            if (eb[i].head - ph).length > 0.005:
                eb[par].tail = eb[i].head  # 見やすさのため親の先端を子の方に向ける

    bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def _parent_of(b, n, self_i):
    par = getattr(b, "Parent", -1)
    if par is None or par < 0 or par == 0xFF or par >= n or par == self_i:
        return None
    return par


def _safe_bone_name(nm):
    # Blenderは骨名63バイト制限、念のため切る
    return nm[:63] if nm else nm


def make_image(name, W, H, rgba_bytes, use_alpha=False):
    # rgba_bytes = 上から下へのRGBA、長さW*H*4
    img = bpy.data.images.new(name, W, H, alpha=True)
    flat = [0.0] * (W * H * 4)
    o = 0
    for row in range(H - 1, -1, -1):          # Blenderは下から上
        rb = row * W * 4
        for col in range(W):
            p = rb + col * 4
            if p + 3 < len(rgba_bytes):
                flat[o] = rgba_bytes[p] / 255.0
                flat[o + 1] = rgba_bytes[p + 1] / 255.0
                flat[o + 2] = rgba_bytes[p + 2] / 255.0
                flat[o + 3] = (rgba_bytes[p + 3] / 255.0) if use_alpha else 1.0
            o += 4
    img.pixels[:] = flat
    img.pack()
    img.alpha_mode = 'STRAIGHT' if use_alpha else 'NONE'
    return img


def make_material(name, image, use_alpha=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nd = nt.nodes
    lk = nt.links
    nd.clear()
    out = nd.new("ShaderNodeOutputMaterial"); out.location = (300, 0)
    bsdf = nd.new("ShaderNodeBsdfPrincipled"); bsdf.location = (0, 0)
    lk.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if "Roughness" in bsdf.inputs: bsdf.inputs["Roughness"].default_value = 0.85
    if "Metallic" in bsdf.inputs: bsdf.inputs["Metallic"].default_value = 0.0
    if image:
        tx = nd.new("ShaderNodeTexImage"); tx.image = image; tx.location = (-450, 0)
        lk.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
        if use_alpha:
            if "Alpha" in bsdf.inputs: lk.new(tx.outputs["Alpha"], bsdf.inputs["Alpha"])
            try: mat.blend_method = 'HASHED'
            except Exception: pass
        else:
            try: mat.blend_method = 'OPAQUE'
            except Exception: pass
    return mat


def build_materials(model, base, use_alpha=False):
    # モデルのmaterial1個につきBlenderのmaterialを1個(Rgbaがあれば画像も)
    mats = []
    src = getattr(model, "materials", []) or []
    for k, mm in enumerate(src):
        img = None
        rgba = getattr(mm, "Rgba", None)
        W = getattr(mm, "W", 0); H = getattr(mm, "H", 0)
        if rgba and W > 0 and H > 0:
            try:
                img = make_image("%s_tex_%03d" % (base, k), W, H, rgba, use_alpha)
            except Exception:
                img = None
        cutout = bool(getattr(mm, "Cutout", False)) or use_alpha
        mats.append(make_material("%s_m%03d" % (base, k), img, cutout))
    if not mats:
        mats = [make_material("%s_m0" % base, None, use_alpha)]
    return mats


def build_mesh(model, name, arm_obj, scale, materials,
               use_normals=True, flip_v=True, center_y=0.0):
    # verts/trisのフラットな配列から1個のmeshを組む
    # - 頂点: model.verts(ワールド/バインド空間済み)、Y-up -> Z-up
    # - 面: model.tris、.Matごとにグループ化(使われたMatだけスロットを作る)
    # - UV: 頂点単位 -> loop単位、flip_vでBlender側の向きに合わせる
    # - 法線: custom split + 実法線から面の向きを補正
    # - ウェイト: model.verts[i].Inf -> 骨名のvertex group
    verts = model.verts
    tris = model.tris
    if not verts or not tris:
        return None
    bones = getattr(model, "bones", [])
    nb = len(bones)

    # 座標(center_yでVMGをVMP/VMXに揃える)
    blv = []
    for v in verts:
        blv.append(blender_co((v.X, v.Y - center_y, v.Z), scale))
    nv = len(blv)

    # 面 + 面ごとのmaterialスロット
    local_mats = []      # 使われたmaterialの実インデックス、出現順
    faces = []
    face_slots = []
    for t in tris:
        a, b, c = t.A, t.B, t.C
        if a == b or b == c or a == c:
            continue
        if not (0 <= a < nv and 0 <= b < nv and 0 <= c < nv):
            continue
        mi = t.Mat if 0 <= t.Mat < len(materials) else 0
        if mi not in local_mats:
            local_mats.append(mi)
        faces.append((a, b, c))
        face_slots.append(local_mats.index(mi))

    if not faces:
        return None

    # 法線(Y-up -> Z-up、スケール無し)で面の向きを直してからcustom splitに使う
    have_norm = use_normals and any(
        (v.Nx or v.Ny or v.Nz) for v in verts)
    vnorm = None
    if have_norm:
        vnorm = [blender_co((v.Nx, v.Ny, v.Nz), 1.0) for v in verts]
        fixed = []
        for (a, b, c), slot in zip(faces, face_slots):
            na, nb, nc = vnorm[a], vnorm[b], vnorm[c]
            ax, ay, az = blv[a]; bx, by, bz = blv[b]; cx, cy, cz = blv[c]
            ux, uy, uz = bx - ax, by - ay, bz - az
            vx, vy, vz = cx - ax, cy - ay, cz - az
            gx, gy, gz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            sx = na[0] + nb[0] + nc[0]; sy = na[1] + nb[1] + nc[1]; sz = na[2] + nb[2] + nc[2]
            fixed.append((a, c, b) if (gx * sx + gy * sy + gz * sz) < 0 else (a, b, c))
        faces = fixed

    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.from_pydata(blv, [], faces)
    mesh.update()

    # UV(頂点単位 -> loop単位)
    ul = mesh.uv_layers.new(name="UVMap")
    for lp in mesh.loops:
        vi = lp.vertex_index
        if vi < nv:
            u = verts[vi].U
            vv = verts[vi].V
            ul.data[lp.index].uv = (u, (1.0 - vv) if flip_v else vv)

    # materialスロット
    for gmi in local_mats:
        m = materials[gmi] if 0 <= gmi < len(materials) else (materials[0] if materials else None)
        obj.data.materials.append(m)
    if len(obj.data.materials) > 1:
        for poly, slot in zip(mesh.polygons, face_slots):
            poly.material_index = slot

    # custom split normals
    if have_norm and vnorm is not None:
        try:
            if hasattr(mesh, "use_auto_smooth"):     # Blender 4.1未満
                mesh.use_auto_smooth = True
            mesh.normals_split_custom_set_from_vertices(vnorm)
        except Exception:
            import traceback; traceback.print_exc()

    # スキニング
    if arm_obj and nb:
        md = obj.modifiers.new("Armature", 'ARMATURE'); md.object = arm_obj
        obj.parent = arm_obj
        names = {i: _safe_bone_name(b.Name if getattr(b, "Name", "") else "bone%d" % i)
                 for i, b in enumerate(bones)}
        for vi, v in enumerate(verts):
            for pair in v.Inf:
                bi = int(pair[0]); w = float(pair[1])
                if w <= 0.0:
                    continue
                bn = names.get(bi)
                if not bn:
                    continue
                vg = obj.vertex_groups.get(bn) or obj.vertex_groups.new(name=bn)
                vg.add([vi], w, 'ADD')
    return obj
