"""Ham Sandwich virtual offsets for Cry of Fear (Windows), from MSVC class layout reports.

hl_layout.txt / cof_layout.txt: cl /d1reportAllClassLayout output for the Half-Life SDK and for ReCoF's src/dlls.
Each key of AMX Mod X's valve offsets is mapped to the method at that slot of the HLSDK class (checked against the
published slot), then looked up in the Cry of Fear class. Overloads (same name twice) take their order from the
declarations: MSVC gives overloads their slots in reverse declaration order.
Writes gamedata/common.games/virtual.games/cryoffear/offsets-common.txt and report.txt in the layout folder.

Usage, from a Visual Studio x86 prompt in an empty folder (layout_*.cpp are next to this script):
  cl /nologo /c /EHsc /DWIN32 /DNDEBUG /D_WINDOWS /DQUIVER /DVOXEL /DQUAKE2 /DVALVE_DLL /I<ReCoF>\\src\\dlls
     /I<ReCoF>\\src\\engine /I<ReCoF>\\src\\common /I<ReCoF>\\src\\pm_shared /I<ReCoF>\\src\\game_shared
     /d1reportAllClassLayout layout_cof.cpp > cof_layout.txt
  cl (the same with the Half-Life SDK folders dlls, engine, common, pm_shared, game_shared, public) layout_hl.cpp
     > hl_layout.txt
  python gen_ham.py <this folder> <Half-Life SDK dlls folder> <ReCoF src\\dlls folder>"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LAYOUTS, HL_HEADERS, COF_HEADERS = sys.argv[1:4]
VALVE = os.path.join(ROOT, "gamedata", "common.games", "virtual.games", "valve", "offsets-common.txt")
CLASSES = ["CBaseEntity", "CBaseMonster", "CBasePlayerItem", "CBasePlayerWeapon", "CBasePlayer"]


def vftables(path):
    text = open(path, encoding="latin-1").read().splitlines()
    out = {}
    i = 0
    while i < len(text):
        m = re.match(r"^(\w+)::\$vftable@:$", text[i])
        if m and m.group(1) in CLASSES and m.group(1) not in out:
            slots = []
            i += 1
            while i < len(text) and text[i].strip():
                mm = re.match(r"^\s*(\d+)\s*\|\s*&(\w+)::(\w+)", text[i])
                if mm:
                    slots.append((int(mm.group(1)), mm.group(2), mm.group(3)))
                i += 1
            out[m.group(1)] = slots
        i += 1
    return out


def valve_keys(path):
    text = open(path, encoding="latin-1").read()
    # the "*" section is the classic Half-Life build (8684), which the Half-Life SDK matches; "#default" is the
    # 25th anniversary build, whose CBaseEntity has more virtuals
    body = text[text.index('"*" // Build 8684'):]
    keys = []
    for m in re.finditer(r'"(\w+)"\s*\{\s*"windows"\s*"([0-9a-fx]+)"', body):
        keys.append((m.group(1), int(m.group(2), 0)))
        if m.group(1) == "player_impulsecommands":
            pass
    seen = set()
    uniq = []
    for k, v in keys:
        if k not in seen:
            seen.add(k)
            uniq.append((k, v))
    return uniq


def decls(folder):
    """method name -> list of parameter strings of its virtual declarations, in file order (cbase.h first)."""
    order = ["cbase.h", "monsters.h", "basemonster.h", "weapons.h", "player.h"]
    files = [os.path.join(folder, f) for f in order if os.path.exists(os.path.join(folder, f))]
    res = {}
    for f in files:
        for line in open(f, encoding="latin-1"):
            m = re.search(r"virtual\s+[\w\s\*&:<>]+?\b(\w+)\s*\(([^)]*)\)", line)
            if m:
                res.setdefault(m.group(1), []).append(re.sub(r"\s+", " ", m.group(2).strip()))
    return res


def norm_params(p):
    p = re.sub(r"=\s*[^,]+", "", p)               # default values
    parts = [x.strip() for x in p.split(",") if x.strip() and x.strip() != "void"]
    types = []
    for x in parts:
        x = re.sub(r"(?<=[\s\*&])\w+$", "", x).strip()   # drop the parameter name
        types.append(re.sub(r"\s+", "", x))
    return types


hl = vftables(os.path.join(LAYOUTS, "hl_layout.txt"))
cof = vftables(os.path.join(LAYOUTS, "cof_layout.txt"))
hl_decl = decls(HL_HEADERS)
cof_decl = decls(COF_HEADERS)
keys = valve_keys(VALVE)

PREFIX = {"item_": "CBasePlayerItem", "weapon_": "CBasePlayerWeapon", "player_": "CBasePlayer"}
# keys whose name is not the method's lowercased
ALIAS = {"item_preframe": "ItemPreFrame", "item_postframe": "ItemPostFrame", "item_itemslot": "iItemSlot",
         "weapon_isusable": "IsUseable", "canplaysentence2": "CanPlaySentence"}
SPECIAL = {"fvecvisible": ("FVisible", "Vector"), "fvisible": ("FVisible", "CBaseEntity"),
           "fvecinviewcone": ("FInViewCone", "Vector"), "finviewcone": ("FInViewCone", "CBaseEntity")}


def slot_of(table, method, overload_hint, decl):
    """The slot of method in table; for overloads pick by parameter type with reverse declaration order."""
    slots = [s for s, c, n in table if n == method]
    if not slots:
        return None
    if len(slots) == 1 or overload_hint is None:
        return slots[0] if len(slots) == 1 else None
    params = decl.get(method, [])
    # declarations of this overload set in order; MSVC reverses them
    idx = [i for i, p in enumerate(params) if overload_hint in p]
    if len(params) != len(slots) or len(idx) != 1:
        return None
    return sorted(slots)[len(params) - 1 - idx[0]]


result = []
report = []
for key, vslot in keys:
    if key in ("pev", "base"):
        continue
    cls = None
    for p, c in PREFIX.items():
        if key.startswith(p):
            cls = c
    method_key = key
    for p in PREFIX:
        if method_key.startswith(p):
            method_key = method_key[len(p):]
    # find the HLSDK method at the published slot
    hl_method = None
    hint = None
    if key in SPECIAL:
        hl_method, hint = SPECIAL[key]
    candidates = [cls] if cls else ["CBaseEntity", "CBaseMonster"]
    for c in candidates:
        for s, owner, name in hl.get(c, []):
            if s == vslot and (name.lower() == method_key or (hl_method and name == hl_method)
                               or ALIAS.get(key) == name):
                hl_method = name
                cls = c
                break
        if cls and hl_method:
            break
    if not hl_method or not cls:
        report.append(f"skip  {key}: no HLSDK method at windows slot {vslot}")
        continue
    hl_slot = slot_of(hl[cls], hl_method, hint, hl_decl)
    if hl_slot != vslot:
        report.append(f"skip  {key}: HLSDK {cls}::{hl_method} is at {hl_slot}, valve says {vslot}")
        continue
    cof_slot = slot_of(cof.get(cls, []), hl_method, hint, cof_decl)
    if cof_slot is None:
        report.append(f"skip  {key}: no {cls}::{hl_method} in Cry of Fear")
        continue
    hp = hl_decl.get(hl_method, [])
    cp = cof_decl.get(hl_method, [])
    hs = [norm_params(x) for x in hp]
    cs = [norm_params(x) for x in cp]
    if set(map(tuple, hs)) != set(map(tuple, cs)):
        report.append(f"skip  {key}: {hl_method} differs: Half-Life {hp} / Cry of Fear {cp}")
        continue
    result.append((key, cof_slot))
    report.append(f"ok    {key}: {cls}::{hl_method} {vslot} -> {cof_slot}")

# Cry of Fear's own keys (modules/hamsandwich/hook_native.cpp), for its functions whose parameters differ from
# Half-Life's; their prototypes there must match these declarations
COF_KEYS = [("cof_giveammo", "CBaseEntity", "GiveAmmo"), ("cof_item_holster", "CBasePlayerItem", "Holster"),
            ("cof_stopfollowing", "CBaseMonster", "StopFollowing")]
for key, cls, method in COF_KEYS:
    slot = slot_of(cof.get(cls, []), method, None, cof_decl)
    if slot is None:
        report.append(f"skip  {key}: no single {cls}::{method} in Cry of Fear")
        continue
    result.append((key, slot))
    report.append(f"ok    {key}: {cls}::{method} -> {slot}  ({cof_decl.get(method)})")

OUT = os.path.join(ROOT, "gamedata", "common.games", "virtual.games", "cryoffear", "offsets-common.txt")
with open(OUT, "w", newline="\r\n") as f:
    f.write("/**\n * Cry of Fear: Ham Sandwich virtual offsets, Windows, for the classes of ReCoF's game DLL.\n")
    f.write(" * Written by support/cof/gen_ham.py; do not edit by hand.\n *\n")
    f.write(" * Generated from MSVC class layout reports of the Half-Life SDK and of ReCoF's src/dlls by matching each\n")
    f.write(" * Half-Life key's method; keys whose method Cry of Fear lacks or declares differently are left out.\n */\n\n")
    f.write('"Games"\n{\n    "#default"\n    {\n        "Offsets"\n        {\n')
    f.write('            "pev"\n            {\n                "windows"  "4"\n            }\n\n')
    f.write('            "base"\n            {\n                "windows"  "0x0"\n            }\n')
    for key, slot in result:
        f.write(f'\n            "{key}"\n            {{\n                "windows"  "{slot}"\n            }}\n')
    f.write("        }\n    }\n}\n")
open(os.path.join(LAYOUTS, "report.txt"), "w").write("\n".join(report) + "\n")
print(len(result), "keys written,", sum(1 for r in report if r.startswith("skip")), "skipped")
