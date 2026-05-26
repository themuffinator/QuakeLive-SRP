from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QAGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "qagame.json"
CGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"
QAGAME_HLIL_PART02 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "qagamex86.dll"
	/ "qagamex86.dll.bndb_hlil_split"
	/ "qagamex86.dll.bndb_hlil_part02.txt"
)
CGAME_HLIL_PART01 = (
	REPO_ROOT
	/ "references"
	/ "hlil"
	/ "quakelive"
	/ "cgamex86.dll"
	/ "cgamex86.dll_hlil_split"
	/ "cgamex86.dll_hlil_part01.txt"
)


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_block(source: str, signature: str) -> str:
	start = source.index(signature)
	brace = source.index("{", start)
	depth = 1
	position = brace + 1
	while depth > 0:
		if source[position] == "{":
			depth += 1
		elif source[position] == "}":
			depth -= 1
		position += 1

	return source[start:position]


def _symbol_comment(path: Path, normalized_name: str) -> str:
	symbol_map = json.loads(path.read_text(encoding="utf-8"))
	for entry in symbol_map["functions"]:
		if entry["normalized_name"] == normalized_name:
			return entry["comment"]

	raise AssertionError(f"{normalized_name} missing from {path.name}")


def test_teleport_player_restores_retail_state_contract_and_hook_cleanup() -> None:
	g_misc = _read("src/code/game/g_misc.c")
	g_local = _read("src/code/game/g_local.h")
	qagame_hlil = QAGAME_HLIL_PART02.read_text(encoding="utf-8")
	teleport = _function_block(
		g_misc,
		"void TeleportPlayer( gentity_t *player, vec3_t origin, vec3_t angles )",
	)
	comment = _symbol_comment(QAGAME_SYMBOL_MAP, "TeleportPlayer")

	for expected in (
		"G_TempEntity( player->client->ps.origin, EV_PLAYER_TELEPORT_OUT );",
		"G_TempEntity( origin, EV_PLAYER_TELEPORT_IN );",
		"trap_UnlinkEntity (player);",
		"VectorCopy ( origin, player->client->ps.origin );",
		"player->client->ps.origin[2] += 1;",
		"AngleVectors( angles, player->client->ps.velocity, NULL, NULL );",
		"VectorScale( player->client->ps.velocity, 400, player->client->ps.velocity );",
		"player->client->ps.pm_time = 160;",
		"player->client->ps.pm_flags |= PMF_TIME_KNOCKBACK;",
		"player->client->ps.eFlags ^= EF_TELEPORT_BIT;",
		"if ( player->client->hook ) {",
		"Weapon_HookFree( player->client->hook );",
		"SetClientViewAngle( player, angles );",
		"G_KillBox (player);",
		"BG_PlayerStateToEntityState( &player->client->ps, &player->s, qtrue );",
		"G_ClearLagHaxHistory( player );",
		"trap_LinkEntity (player);",
	):
		assert expected in teleport

	assert teleport.index("player->client->ps.pm_time = 160;") < teleport.index(
		"player->client->ps.pm_flags |= PMF_TIME_KNOCKBACK;"
	)
	assert teleport.index("player->client->ps.eFlags ^= EF_TELEPORT_BIT;") < teleport.index(
		"Weapon_HookFree( player->client->hook );"
	)
	assert teleport.index("Weapon_HookFree( player->client->hook );") < teleport.index(
		"SetClientViewAngle( player, angles );"
	)
	assert teleport.index("SetClientViewAngle( player, angles );") < teleport.index("G_KillBox (player);")
	assert teleport.index("G_KillBox (player);") < teleport.index(
		"BG_PlayerStateToEntityState( &player->client->ps, &player->s, qtrue );"
	)
	assert "void Weapon_HookFree (gentity_t *ent);" in g_local

	for hlil_snippet in (
		"1005a587  *(arg3[0x8f] + 0x10) = 0xa0",
		"1005a594  *(eax_7 + 0xc) |= 0x40",
		"1005a59e  *(eax_8 + 0x68) ^= 4",
		"1005a5b3      sub_1006e330(eax_10)",
		"1006e330    void* sub_1006e330(void* arg1)",
	):
		assert hlil_snippet in qagame_hlil

	assert "pm_time = 160" in comment
	assert "PMF_TIME_KNOCKBACK" in comment
	assert "EF_TELEPORT_BIT" in comment
	assert "Weapon_HookFree" in comment


def test_server_teleport_producers_share_the_retail_teleport_helper() -> None:
	g_active = _read("src/code/game/g_active.c")
	g_client = _read("src/code/game/g_client.c")
	g_mover = _read("src/code/game/g_mover.c")
	g_target = _read("src/code/game/g_target.c")
	g_trigger = _read("src/code/game/g_trigger.c")
	qagame_hlil = QAGAME_HLIL_PART02.read_text(encoding="utf-8")

	client_events = _function_block(g_active, "void ClientEvents( gentity_t *ent, int oldEventSequence )")
	respawn = _function_block(g_client, "void respawn( gentity_t *ent )")
	target_use = _function_block(
		g_target,
		"void target_teleporter_use( gentity_t *self, gentity_t *other, gentity_t *activator )",
	)
	trigger_touch = _function_block(
		g_trigger,
		"static void trigger_teleporter_touch (gentity_t *self, gentity_t *other, trace_t *trace )",
	)
	trigger_spawn = _function_block(g_trigger, "void SP_trigger_teleport( gentity_t *self )")
	door_spectator = _function_block(
		g_mover,
		"static void Touch_DoorTriggerSpectator( gentity_t *ent, gentity_t *other, trace_t *trace )",
	)

	assert "case EV_USE_ITEM1:\t\t// teleporter" in client_events
	assert "SelectSpawnPoint( ent->client->ps.origin, origin, angles );" in client_events
	assert "TeleportPlayer( ent, origin, angles );" in client_events
	assert "G_TossFlag( ent, j, FLAG_DROP_CONTEXT_SCRIPTED, NULL, MOD_UNKNOWN, &dropped );" in client_events
	assert "ent->client->ps.generic1 = 0;" in client_events
	assert "G_TempEntity( ent->client->ps.origin, EV_PLAYER_TELEPORT_IN );" in respawn

	assert "if (!activator->client)" in target_use
	assert "dest = \tG_PickTarget( self->target );" in target_use
	assert "TeleportPlayer( activator, dest->s.origin, dest->s.angles );" in target_use
	assert "other->client->ps.pm_type == PM_DEAD" in trigger_touch
	assert "other->client->sess.sessionTeam != TEAM_SPECTATOR" in trigger_touch
	assert "TeleportPlayer( other, dest->s.origin, dest->s.angles );" in trigger_touch
	assert "self->s.eType = ET_TELEPORT_TRIGGER;" in trigger_spawn
	assert "self->touch = trigger_teleporter_touch;" in trigger_spawn
	assert "TeleportPlayer(other, origin, angles );" in door_spectator

	for name in (
		"target_teleporter_use",
		"SP_target_teleporter",
		"trigger_teleporter_touch",
		"SP_trigger_teleport",
		"Touch_DoorTriggerSpectator",
		"ClientEvents",
		"respawn",
	):
		assert _symbol_comment(QAGAME_SYMBOL_MAP, name)

	for hlil_snippet in (
		"100679d0    void sub_100679d0",
		"10067a0d      sub_1005a420",
		"1006b9a0    int32_t sub_1006b9a0",
		"1006b9f4              return sub_1005a420",
		"1005f1e0    void __fastcall sub_1005f1e0",
		"1005f2e3  sub_1005a420",
	):
		assert hlil_snippet in qagame_hlil


def test_client_teleport_prediction_snapshot_and_view_wiring_stays_pinned() -> None:
	cg_event = _read("src/code/cgame/cg_event.c")
	cg_predict = _read("src/code/cgame/cg_predict.c")
	cg_snapshot = _read("src/code/cgame/cg_snapshot.c")
	cg_view = _read("src/code/cgame/cg_view.c")
	cgame_hlil = CGAME_HLIL_PART01.read_text(encoding="utf-8")
	trigger_prediction = _function_block(cg_predict, "static void CG_TouchTriggerPrediction( void )")
	next_snap = _function_block(cg_snapshot, "static void CG_SetNextSnap( snapshot_t *snap )")
	transition_snapshot = _function_block(cg_snapshot, "static void CG_TransitionSnapshot( void )")
	calc_view = _function_block(cg_view, "static int CG_CalcViewValues( void )")
	draw_frame = _function_block(
		cg_view,
		"void CG_DrawActiveFrame( int serverTime, stereoFrame_t stereoView, qboolean demoPlayback )",
	)

	assert "case EV_PLAYER_TELEPORT_IN:" in cg_event
	assert "CG_SpawnEffect( position);" in cg_event
	assert "case EV_PLAYER_TELEPORT_OUT:" in cg_event
	assert trigger_prediction.index("if ( ent->eType == ET_TELEPORT_TRIGGER ) {") < trigger_prediction.index(
		"cg.hyperspace = qtrue;"
	)
	assert "trap_CM_BoxTrace( &trace, cg.predictedPlayerState.origin, cg.predictedPlayerState.origin," in trigger_prediction
	assert "CG_Trace(" not in trigger_prediction

	assert "( ( cent->currentState.eFlags ^ es->eFlags ) & EF_TELEPORT_BIT )" in next_snap
	assert "( ( snap->ps.eFlags ^ cg.snap->ps.eFlags ) & EF_TELEPORT_BIT )" in next_snap
	assert "cg.nextFrameTeleport = qtrue;" in next_snap
	assert "( ps->eFlags ^ ops->eFlags ) & EF_TELEPORT_BIT" in transition_snapshot
	assert "cg.thisFrameTeleport = qtrue;" in transition_snapshot
	assert "cg.refdef.rdflags |= RDF_NOWORLDMODEL | RDF_HYPERSPACE;" in calc_view
	assert "if ( !cg.hyperspace ) {" in draw_frame
	assert "CG_AddPacketEntities();" in draw_frame

	for name in (
		"CG_SpawnEffect",
		"CG_TouchTriggerPrediction",
		"CG_SetNextSnap",
		"CG_Respawn",
		"CG_TransitionPlayerState",
		"CG_CalcViewValues",
	):
		assert _symbol_comment(CGAME_SYMBOL_MAP, name)

	for hlil_snippet in (
		"1001a919                      result_1 = \"EV_PLAYER_TELEPORT_IN\\n\"",
		"1001a959                      result_1 = \"EV_PLAYER_TELEPORT_OUT\\n\"",
		"100445ab                                  data_10a9c20c = 1",
		"100449af                              sub_10020a90(\"PredictionTeleport\\n\")",
	):
		assert hlil_snippet in cgame_hlil


def test_bot_and_dropped_powerup_teleport_wiring_uses_the_shared_state_contract() -> None:
	ai_dmq3 = _read("src/code/game/ai_dmq3.c")
	g_items = _read("src/code/game/g_items.c")
	qagame_hlil = QAGAME_HLIL_PART02.read_text(encoding="utf-8")
	bot_setup = _function_block(ai_dmq3, "void BotSetupForMovement(bot_state_t *bs)")
	dropped_powerup = _function_block(g_items, "static void G_DroppedPowerupRunFrame( gentity_t *ent, float thinktime )")

	assert "if ((bs->cur_ps.pm_flags & PMF_TIME_KNOCKBACK) && (bs->cur_ps.pm_time > 0)) {" in bot_setup
	assert "initmove.or_moveflags |= MFL_TELEPORTED;" in bot_setup
	assert "if ((bs->cur_ps.pm_flags & PMF_TIME_WATERJUMP) && (bs->cur_ps.pm_time > 0)) {" in bot_setup
	assert bot_setup.index("PMF_TIME_KNOCKBACK") < bot_setup.index("PMF_TIME_WATERJUMP")

	assert 'if ( !Q_stricmp( trigger->classname, "trigger_teleport" ) ) {' in dropped_powerup
	assert 'G_Printf( "Couldn\'t find teleporter destination\\n" );' in dropped_powerup
	assert 'te->s.eventParm = G_SoundIndex( "sound/world/teleout.ogg" );' in dropped_powerup
	assert "VectorCopy( dest->s.origin, ent->r.currentOrigin );" in dropped_powerup
	assert "VectorScale( forward, 400, ent->s.pos.trDelta );" in dropped_powerup
	assert "ent->s.pos.trDelta[2] += 96;" in dropped_powerup
	assert "SnapVector( ent->s.pos.trDelta );" in dropped_powerup
	assert 'te->s.eventParm = G_SoundIndex( "sound/world/telein.ogg" );' in dropped_powerup

	assert "PMF_TIME_KNOCKBACK" in _symbol_comment(QAGAME_SYMBOL_MAP, "BotSetupForMovement")
	assert "MFL_TELEPORTED" in _symbol_comment(QAGAME_SYMBOL_MAP, "BotSetupForMovement")
	assert "trigger_teleport" in _symbol_comment(QAGAME_SYMBOL_MAP, "G_DroppedPowerupRunFrame")

	for hlil_snippet in (
		"10050f80    void* sub_10050f80(float arg1)",
		"10051110              char const* const ecx_2 = \"trigger_teleport\"",
		"1005117d                      sub_1006be90(\"sound/world/teleout.ogg\")",
		"10051273                  long double x87_r6_5 = fconvert.t(400.0)",
		"100512bd                  var_8 = fconvert.s(fconvert.t(var_8) + fconvert.t(96.0))",
		"10051315                      sub_1006be90(\"sound/world/telein.ogg\")",
	):
		assert hlil_snippet in qagame_hlil
