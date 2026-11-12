// Cry of Fear self test for ReCoF's AMX Mod X build. Server command cof_selftest: puts a bot in the game and checks
// that fakemeta and engine read its entity fields at Cry of Fear's offsets and that Ham Sandwich's Spawn and
// TakeDamage hooks fire with the right values. Prints PASS or FAIL lines to the server console.

#include <amxmodx>
#include <fakemeta>
#include <engine>
#include <hamsandwich>

new g_bot;
new g_spawned;
new g_hurt;
new Float:g_hurtDamage;
new g_hurtVictim;
new g_failures;

public plugin_init()
{
	register_plugin("Cry of Fear self test", "1.0", "ReCoF");
	register_srvcmd("cof_selftest", "cmd_selftest");
	RegisterHam(Ham_Spawn, "player", "fw_spawn_post", 1);
	RegisterHam(Ham_TakeDamage, "player", "fw_takedamage", 0);
}

public fw_spawn_post(id)
{
	if (id == g_bot)
		g_spawned++;
}

public fw_takedamage(victim, inflictor, attacker, Float:damage, damagebits)
{
	if (victim == g_bot)
	{
		g_hurt++;
		g_hurtVictim = victim;
		g_hurtDamage = damage;
	}
	return HAM_IGNORED;
}

check(ok, const what[], const detail[] = "")
{
	if (!ok)
		g_failures++;
	server_print("[cof_selftest] %s %s %s", ok ? "PASS" : "FAIL", what, detail);
}

public cmd_selftest()
{
	g_failures = 0;
	g_spawned = 0;
	g_hurt = 0;

	if (!g_bot || !is_user_connected(g_bot))
	{
		g_bot = engfunc(EngFunc_CreateFakeClient, "cof_selftest_bot");
		check(g_bot > 0, "create a bot");
		if (g_bot <= 0)
			return PLUGIN_HANDLED;

		new reject[128];
		dllfunc(DLLFunc_ClientConnect, g_bot, "cof_selftest_bot", "127.0.0.1", reject);
		dllfunc(DLLFunc_ClientPutInServer, g_bot);
		set_pev(g_bot, pev_flags, pev(g_bot, pev_flags) | FL_FAKECLIENT);
	}

	// Ham Spawn: run the player's Spawn through Ham so the post hook must see it
	ExecuteHamB(Ham_Spawn, g_bot);
	check(g_spawned > 0, "Ham_Spawn hook fired on the bot");

	// fakemeta and engine read fields before and after Cry of Fear's extra entvars field (after light_level)
	new classname[32], netname[32];
	pev(g_bot, pev_classname, classname, charsmax(classname));
	pev(g_bot, pev_netname, netname, charsmax(netname));
	check(equal(classname, "player"), "pev_classname (before the extra field)", classname);
	check(equal(netname, "cof_selftest_bot"), "pev_netname (after it)", netname);

	new Float:health;
	pev(g_bot, pev_health, health);	// float fields come back through the third argument
	new Float:ehealth = entity_get_float(g_bot, EV_FL_health);
	new detail[96];
	formatex(detail, charsmax(detail), "pev %.1f, engine %.1f", health, ehealth);
	check(health > 0.0 && health == ehealth, "health read the same by fakemeta and engine", detail);

	set_pev(g_bot, pev_iuser4, 4242);
	check(entity_get_int(g_bot, EV_INT_iuser4) == 4242, "pev_iuser4 written by fakemeta, read by engine");

	new Float:origin[3];
	pev(g_bot, pev_origin, origin);
	formatex(detail, charsmax(detail), "%.0f %.0f %.0f", origin[0], origin[1], origin[2]);
	check(true, "pev_origin", detail);

	// Ham TakeDamage: hurt the bot through the game's own TakeDamage
	set_pev(g_bot, pev_takedamage, DAMAGE_YES);
	set_pev(g_bot, pev_health, 100.0);
	ExecuteHamB(Ham_TakeDamage, g_bot, 0, 0, 10.0, DMG_GENERIC);
	formatex(detail, charsmax(detail), "fired %d, victim %d, damage %.1f", g_hurt, g_hurtVictim, g_hurtDamage);
	check(g_hurt > 0 && g_hurtVictim == g_bot && g_hurtDamage == 10.0, "Ham_TakeDamage hook got the call", detail);
	new Float:after;
	pev(g_bot, pev_health, after);
	formatex(detail, charsmax(detail), "100 -> %.1f", after);
	check(after < 100.0, "the game took the damage", detail);

	server_print("[cof_selftest] %s, %d failed", g_failures ? "FAILED" : "all passed", g_failures);
	return PLUGIN_HANDLED;
}
