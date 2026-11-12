# ReCoF AMX Mod X

AMX Mod X for the [ReCoF Server](https://github.com/caixax/ReCoF-Server), the Cry of Fear dedicated server, built against [ReCoF-HLSDK](https://github.com/caixax/ReCoF-HLSDK) (Cry of Fear's entity layout):

- Ham Sandwich offsets for Cry of Fear (`gamedata/common.games/virtual.games/cryoffear`), generated from the class layouts of the Half-Life SDK and of ReCoF's game DLL by `support/cof/gen_ham.py`; `Ham_CoF_GiveAmmo`, `Ham_CoF_Item_Holster` and `Ham_CoF_StopFollowing` for the functions whose parameters differ from Half-Life's.
- `cof.inc`: Cry of Fear's weapon, ammo, item and monster names and a few helpers, with notes for porting plugins.
- The engine module's `set_view` camera no longer needs Half-Life's `models/rpgrocket.mdl`.
- `plugins/testsuite/cof_selftest.sma` checks all of it on a server with a bot.

Build (Windows): `python configure.py --enable-optimize --no-mysql --hlsdk=<ReCoF-HLSDK> --metamod=<metamod-hl1>` in a build folder, then `ambuild`. Everything else is upstream AMX Mod X, under its license; the original README follows.

---


<p align="center">
 <img src="https://github.com/alliedmodders/amxmodx/blob/master/editor/studio/AMXXLarge.bmp"/>
</p>

**AMX Mod X** is a [Metamod](https://github.com/jkivilin/metamod-p) plugin for [Half-Life 1](https://github.com/ValveSoftware/halflife). It provides comprehensive scripting for the game engine and its mods. Scripts can intercept network messages, log events, commands, client commands, set cvars, modify entities, and more. AMX Mod X also has a system for extending native scripting through modules, leading to outside support for things like MySQL and Sockets.

General
-------
- [AMXX website](https://amxmodx.org/)
- [Forum](https://forums.alliedmods.net/forumdisplay.php?f=3): Discussion forum including plugin/extension development
- [General documentation](https://wiki.alliedmods.net/Category:Documentation_%28AMX_Mod_X%29): Miscellaneous information about AMXX
- [Latest release](https://amxmodx.org/downloads.php): The latest stable AMXX release
- [Build snapshots](https://www.amxmodx.org/downloads-new.php): Builds of recent development versions
 
Development
-----------
- [Issue tracker](https://github.com/alliedmodders/amxmodx/issues): Issues that require back and forth communication
- [Issue archive](https://bugs.alliedmods.net/describecomponents.cgi?product=AMX%20Mod%20X): Old issue tracker (read-only)
- [Building AMXX](https://wiki.alliedmods.net/Building_AMX_Mod_X): Instructions on how to build AMXX itself using [AMBuild](https://github.com/alliedmodders/ambuild)
- [AMX Mod X API](https://amxmodx.org/api/): AMX Mod X API reference generated from include files
- [AMXX scripting](https://wiki.alliedmods.net/Category:Scripting_(AMX_Mod_X)): Pawn examples and introduction to the language

Tools
-----
- `tools/crc32`: Standalone helper that prints the CRC32 used by AMXX/Sourcemod-style gamedata. Build it with `tools/crc32/build.sh` and run `./tools/crc32/crc32 <path-to-binary>` to generate the 8-digit hex CRC for your gamedata `CRC` sections.
