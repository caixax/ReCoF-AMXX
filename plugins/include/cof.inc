// Cry of Fear for AMX Mod X: names and helpers for plugins on a Cry of Fear server (ReCoF Server).
//
// Cry of Fear's game DLL is not Half-Life's. Things to know when porting a plugin:
//  - Ham Sandwich: GiveAmmo, Item_Holster and StopFollowing take other parameters in Cry of Fear; hook
//    Ham_CoF_GiveAmmo, Ham_CoF_Item_Holster and Ham_CoF_StopFollowing instead (ham_const.inc). Ham_IsTriggered,
//    Ham_Item_AddDuplicate and Ham_CanPlaySequence are not available.
//  - Entities have two more fields than Half-Life's (fakemeta and engine already read every other field at the
//    right place); the game's donator level is one of them and is not offered as a pev_ field yet.
//  - Co-op takes up to 4 players, and only ReCoF players unless the server sets rc_require_recof 0.
//  - The game DLL is cl_dlls/hl.dll, the game folder cryoffear.

#if defined _cof_included
	#endinput
#endif
#define _cof_included

#include <amxmodx>

#define COF_GAME_DIR		"cryoffear"
#define COF_MAX_COOP_PLAYERS	4

/**
 * Weapons of Cry of Fear, by classname.
 */
stock const COF_WEAPONS[][] =
{
	"weapon_action", "weapon_axe", "weapon_beretta", "weapon_booklaser", "weapon_branch",
	"weapon_browning_wheelchair", "weapon_camera", "weapon_dualweapon", "weapon_famas", "weapon_flare",
	"weapon_flashlight", "weapon_g43", "weapon_glock", "weapon_hammer", "weapon_knife", "weapon_lantern",
	"weapon_m16", "weapon_mobile", "weapon_mp5", "weapon_mp5k", "weapon_nightstick", "weapon_p345", "weapon_radio",
	"weapon_revolver", "weapon_rifle", "weapon_shotgun", "weapon_sledgehammer", "weapon_switchblade",
	"weapon_syringe", "weapon_tmp", "weapon_uzi", "weapon_vp70"
};

/**
 * Ammo entities of Cry of Fear, by classname.
 */
stock const COF_AMMO[][] =
{
	"ammo_flashlightbattery", "ammo_g43", "ammo_glock", "ammo_m16", "ammo_mp5", "ammo_p345", "ammo_revolver",
	"ammo_rifle", "ammo_shells", "ammo_tmp", "ammo_vp70"
};

/**
 * Items of Cry of Fear, by classname.
 */
stock const COF_ITEMS[][] =
{
	"item_antidote", "item_armour", "item_battery", "item_glocktaclight", "item_key", "item_longjump",
	"item_nightvision", "item_padlock", "item_phonebattery", "item_security", "item_sodacan", "item_suit"
};

/**
 * Monsters of Cry of Fear, by classname (Half-Life leftovers such as monster_cine_* included).
 */
stock const COF_MONSTERS[][] =
{
	"monster_baby", "monster_booksimon", "monster_booksimonsledgehammer", "monster_bosschainsaw", "monster_child",
	"monster_crab", "monster_crazybitch", "monster_custom", "monster_doctorboss", "monster_faceless",
	"monster_facelessv", "monster_faster", "monster_krypande", "monster_rcrazy", "monster_roofboss",
	"monster_sawcrazy", "monster_sawrunner", "monster_sewerboss", "monster_sewmo", "monster_slower",
	"monster_slower3", "monster_slowerstuck", "monster_spitter", "monster_stranger", "monster_suicider",
	"monster_taller", "monster_twitcher", "monster_twitcher2", "monster_twitcher3", "monster_twitcher4",
	"monster_watro", "monster_zombie", "monster_ruben", "monster_furniture", "monster_generic",
	"monster_generic_dead", "monster_target", "monster_mortar", "monster_nerd", "monster_hevsuit_dead",
	"monster_cine_barney", "monster_cine_panther", "monster_cine_scientist", "monster_cine2_hvyweapons",
	"monster_cine2_scientist", "monster_cine2_slave", "monster_cine3_barney", "monster_cine3_scientist"
};

/**
 * Whether this server runs Cry of Fear.
 */
stock bool:cof_is_game()
{
	new dir[32];
	get_modname(dir, charsmax(dir));
	return bool:equali(dir, COF_GAME_DIR);
}

/**
 * The ReCoF version a player runs, from the private userinfo key _recof that ReCoF's client sends.
 *
 * @param id		Player index
 * @param version	Buffer for the version, for example "0.2.3"; empty when the player does not run ReCoF
 * @param len		Buffer size
 * @return		true when the player runs ReCoF
 */
stock bool:cof_get_recof_version(id, version[], len)
{
	get_user_info(id, "_recof", version, len);
	return version[0] != EOS;
}

/**
 * Whether the classname is one of Cry of Fear's weapons.
 */
stock bool:cof_is_weapon(const classname[])
{
	for (new i = 0; i < sizeof COF_WEAPONS; i++)
	{
		if (equal(classname, COF_WEAPONS[i]))
			return true;
	}
	return false;
}

/**
 * Whether the classname is one of Cry of Fear's monsters.
 */
stock bool:cof_is_monster(const classname[])
{
	for (new i = 0; i < sizeof COF_MONSTERS; i++)
	{
		if (equal(classname, COF_MONSTERS[i]))
			return true;
	}
	return false;
}
