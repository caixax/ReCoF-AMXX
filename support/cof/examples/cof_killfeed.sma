// Example plugin for a Cry of Fear server (ReCoF Server): tells everyone who killed which monster, and greets
// players with the ReCoF version they run. See docs/cryoffear.md.

#include <amxmodx>
#include <fakemeta>
#include <hamsandwich>
#include <cof>

new g_kills[MAX_PLAYERS + 1];

public plugin_init()
{
	register_plugin("Cry of Fear kill feed", "1.0", "ReCoF");

	if (!cof_is_game())
	{
		set_fail_state("This plugin is for Cry of Fear");
		return;
	}

	// One hook per monster class: Ham Sandwich hooks a class, not every entity
	for (new i = 0; i < sizeof(COF_MONSTERS); i++)
		RegisterHam(Ham_Killed, COF_MONSTERS[i], "fw_monster_killed_post", 1);

	register_clcmd("say /kills", "cmd_kills");
}

public client_putinserver(id)
{
	g_kills[id] = 0;
	set_task(5.0, "task_greet", id);
}

public task_greet(id)
{
	if (!is_user_connected(id))
		return;

	new version[16];
	if (cof_get_recof_version(id, version, charsmax(version)))
		client_print(id, print_chat, "Welcome %n, you run ReCoF %s. Say /kills to see your kills.", id, version);
}

public fw_monster_killed_post(monster, attacker, shouldgib)
{
	if (!is_user_connected(attacker))
		return HAM_IGNORED;

	g_kills[attacker]++;

	new classname[32];
	pev(monster, pev_classname, classname, charsmax(classname));
	// "monster_twitcher3" is shown as "twitcher3"
	client_print(0, print_chat, "%n killed a %s (%d so far)", attacker, classname[8], g_kills[attacker]);
	return HAM_IGNORED;
}

public cmd_kills(id)
{
	client_print(id, print_chat, "You killed %d monsters on this map.", g_kills[id]);
	return PLUGIN_HANDLED;
}
