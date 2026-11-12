# Writing plugins for Cry of Fear

This fork of AMX Mod X runs on the [ReCoF Server](https://github.com/caixax/ReCoF-Server), the dedicated server for Cry of Fear. Most of what you know from Half-Life plugins carries over; this page lists what is different and what this fork adds.

## Where things go

The server package has AMX Mod X in `cryoffear/addons/amxmodx`. Compiled plugins (`.amxx`) go in `plugins/` and are listed, one per line, in `configs/plugins.ini`; admins go in `configs/users.ini`, as in any AMX Mod X install.

To compile, use the compiler in `scripting/`: `amxxpc.exe yourplugin.sma` on Windows, `./amxxpc yourplugin.sma` on Linux. The includes in `scripting/include` are this fork's, `cof.inc` among them.

## What is different from Half-Life

- **Ham Sandwich**: Cry of Fear's game DLL has its own virtual functions, and the offsets in `data/gamedata/common.games/virtual.games/cryoffear` were generated from it for Windows and Linux. Three functions take other parameters than in Half-Life: hook `Ham_CoF_GiveAmmo`, `Ham_CoF_Item_Holster` and `Ham_CoF_StopFollowing` instead of `Ham_GiveAmmo`, `Ham_Item_Holster` and `Ham_StopFollowing`. `Ham_IsTriggered`, `Ham_Item_AddDuplicate` and `Ham_CanPlaySequence` do not exist in Cry of Fear.
- **Entity fields**: Cry of Fear added two fields to every entity. Fakemeta (`pev`, `set_pev`) and the engine module read every Half-Life field at the right place on this build; the two new ones are not offered as `pev_` fields yet.
- **Names**: weapons, ammo, items and monsters have Cry of Fear's own classnames (`weapon_glock`, `ammo_shells`, `monster_twitcher`...). `cof.inc` has them all.
- **Players**: co-op takes up to 4 players (`COF_MAX_COOP_PLAYERS`). A ReCoF Server only lets in players on ReCoF unless `server.cfg` sets `rc_require_recof 0`.
- **Modules**: fakemeta, engine, hamsandwich, fun, nvault, sqlite, regex, json, sockets and geoip are built for Cry of Fear. Modules made for one game, such as cstrike, csx or dodx, do not apply.
- **The game**: the game folder is `cryoffear` and its game DLL `cl_dlls/hl.dll` (`cl_dlls/hl.so` on Linux), not `dlls/`.

## cof.inc

`#include <cof>` gives you:

- `COF_WEAPONS`, `COF_AMMO`, `COF_ITEMS`, `COF_MONSTERS`: every classname of each kind in Cry of Fear's game DLL, to loop over or to hook.
- `cof_is_game()`: whether the server runs Cry of Fear, for plugins that also run elsewhere.
- `cof_get_recof_version(id, version[], len)`: the ReCoF version a player runs (for example `0.2.3`), from the private userinfo key the ReCoF client sends.
- `cof_is_weapon(classname[])`, `cof_is_monster(classname[])`.

## An example

[support/cof/examples/cof_killfeed.sma](../support/cof/examples/cof_killfeed.sma) greets each player with the ReCoF version they run and tells everyone who killed which monster. The part that is particular to Cry of Fear is the hook: Ham Sandwich hooks one class at a time, so the plugin registers `Ham_Killed` for every class in `COF_MONSTERS`:

```pawn
for (new i = 0; i < sizeof(COF_MONSTERS); i++)
	RegisterHam(Ham_Killed, COF_MONSTERS[i], "fw_monster_killed_post", 1);
```

It compiles with this fork's `amxxpc` and loads on the ReCoF Server with no errors, which also shows that every class in `COF_MONSTERS` exists in the game DLL.

## Checking a server

[plugins/testsuite/cof_selftest.sma](../plugins/testsuite/cof_selftest.sma) adds the server command `cof_selftest`: it puts a bot in the game, checks that fakemeta and the engine module read its fields at Cry of Fear's offsets and that the Spawn, TakeDamage and GiveAmmo hooks fire with the right values, and prints PASS or FAIL lines.
