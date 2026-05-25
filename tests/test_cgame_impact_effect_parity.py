from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_EVENT = REPO_ROOT / "src" / "code" / "cgame" / "cg_event.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_PARTICLES = REPO_ROOT / "src" / "code" / "cgame" / "cg_particles.c"
CG_PLAYERS = REPO_ROOT / "src" / "code" / "cgame" / "cg_players.c"
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
CG_WEAPONS = REPO_ROOT / "src" / "code" / "cgame" / "cg_weapons.c"
CG_LOCAL = REPO_ROOT / "src" / "code" / "cgame" / "cg_local.h"
CGAME_SYMBOL_MAP = REPO_ROOT / "references" / "symbol-maps" / "cgame.json"
CGAME_GHIDRA = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "decompile_top_functions.c"
)
CGAME_FUNCTIONS = (
	REPO_ROOT
	/ "references"
	/ "reverse-engineering"
	/ "ghidra"
	/ "cgamex86"
	/ "functions.csv"
)


def _read(path: Path) -> str:
	return path.read_text(encoding="utf-8")


def _block_from_marker(source: str, marker: str) -> str:
	start = source.index(marker)
	brace_start = source.index("{", start)
	depth = 0

	for index in range(brace_start, len(source)):
		char = source[index]
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start:index + 1]

	raise AssertionError(f"Unbalanced block for marker: {marker}")


def _case_block(source: str, marker: str) -> str:
	start = source.index(marker)
	next_markers = [
		position
		for position in (
			source.find("\n\tcase ", start + len(marker)),
			source.find("\n\tdefault:", start + len(marker)),
		)
		if position != -1
	]
	end = min(next_markers) if next_markers else len(source)
	return source[start:end]


def test_cgame_impact_effects_are_backed_by_committed_retail_evidence() -> None:
	symbol_map = json.loads(_read(CGAME_SYMBOL_MAP))
	entries = {
		entry["normalized_name"]: entry
		for entry in symbol_map["functions"]
		if "normalized_name" in entry
	}

	for name in (
		"CG_BubbleTrail",
		"CG_SmokePuff",
		"CG_ImpactMark",
		"CG_MissileHitWall",
		"CG_MissileHitPlayer",
		"CG_MissileHitWallDmgThrough",
		"CG_ShotgunPellet",
		"CG_ShotgunPattern",
		"CG_ShotgunFire",
		"CG_Tracer",
		"CG_Bullet",
		"CG_NailgunEjectBrass",
		"CG_NailTrail",
		"CG_Missile",
		"CG_PlasmaTrail",
		"CG_SpawnRailRing",
		"CG_RailTrail",
		"CG_SpawnRailTrail",
		"CG_FireWeapon",
		"CG_UpdatePredictedRailFire",
	):
		assert entries[name]["status"] == "matched"

	ghidra = _read(CGAME_GHIDRA)
	for expected in (
		'DAT_10a5f74c = (**(code **)(DAT_1074cccc + 0xd0))("surfacePuff");',
		"/* FUN_10054db0 @ 10054db0 size 1657 */",
		"FUN_10012f30(local_1770,DAT_1007417c,DAT_10073f74,DAT_10073f74,DAT_1006723c,0x3f800000,",
		"FUN_10053ef0(param_3,0,param_1);",
		"/* FUN_10053ef0 @ 10053ef0 size 3471 */",
	):
		assert expected in ghidra

	functions = _read(CGAME_FUNCTIONS)
	assert "FUN_100561f0,100561f0,506,0,unknown" in functions


def test_cgame_smoke_shadow_debug_and_model_scale_cvars_match_retail_table_and_wiring() -> None:
	main_source = _read(CG_MAIN)
	local_source = _read(CG_LOCAL)
	players_source = _read(CG_PLAYERS)
	predict_source = _read(CG_PREDICT)
	weapons_source = _read(CG_WEAPONS)
	retail_flags = "CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD"

	for expected in (
		'{ &cg_scalePlayerModelsToBB, "cg_scalePlayerModelsToBB", "1", CVAR_CHEAT },',
		'{ &cg_shadows, "cg_shadows", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_showmiss, "cg_showmiss", "0", 0 },',
		'{ &cg_smoke_SG, "cg_smoke_SG", "1", ' + retail_flags + ', "0", "1" },',
		'{ &cg_smokeRadius_dust, "cg_smokeRadius_dust", "24", ' + retail_flags + ', "0", "32" },',
		'{ &cg_smokeRadius_flight, "cg_smokeRadius_flight", "8", ' + retail_flags + ', "0", "16" },',
		'{ &cg_smokeRadius_GL, "cg_smokeRadius_GL", "64", ' + retail_flags + ', "0", "64" },',
		'{ &cg_smokeRadius_haste, "cg_smokeRadius_haste", "8", ' + retail_flags + ', "0", "16" },',
		'{ &cg_smokeRadius_NG, "cg_smokeRadius_NG", "16", ' + retail_flags + ', "0", "16" },',
		'{ &cg_smokeRadius_RL, "cg_smokeRadius_RL", "32", ' + retail_flags + ', "0", "32" },',
	):
		assert expected in main_source

	for expected in (
		"extern\tvmCvar_t\t\tcg_scalePlayerModelsToBB;",
		"extern\tvmCvar_t\t\tcg_smoke_SG;",
		"extern\tvmCvar_t\t\tcg_smokeRadius_dust;",
		"extern\tvmCvar_t\t\tcg_smokeRadius_flight;",
		"extern\tvmCvar_t\t\tcg_smokeRadius_GL;",
		"extern\tvmCvar_t\t\tcg_smokeRadius_haste;",
		"extern\tvmCvar_t\t\tcg_smokeRadius_NG;",
		"extern\tvmCvar_t\t\tcg_smokeRadius_RL;",
	):
		assert expected in local_source

	player_scale = _block_from_marker(players_source, "static float CG_PlayerModelBoundingBoxScale")
	apply_scale = _block_from_marker(players_source, "static void CG_ApplyPlayerModelBoundingBoxScale")
	player_block = _block_from_marker(players_source, "void CG_Player( centity_t *cent )")
	player_shadow = _block_from_marker(players_source, "static qboolean CG_PlayerShadow")
	player_splash = _block_from_marker(players_source, "static void CG_PlayerSplash")
	powerups_block = _block_from_marker(players_source, "static void CG_PlayerPowerups")
	flight_trail = _block_from_marker(players_source, "static void CG_FlightTrail")
	haste_trail = _block_from_marker(players_source, "static void CG_HasteTrail")
	dust_trail = _block_from_marker(players_source, "static void CG_DustTrail")
	rocket_trail = _block_from_marker(weapons_source, "static void CG_RocketTrail")
	nail_trail = _block_from_marker(weapons_source, "static void CG_NailTrail")
	shotgun_fire = _block_from_marker(weapons_source, "void CG_ShotgunFire")

	for expected in (
		"!cg_scalePlayerModelsToBB.integer",
		"ci->headOffset[0] <= 1.0f",
		"return ci->headOffset[0];",
	):
		assert expected in player_scale
	for expected in (
		"legs->nonNormalizedAxes = qtrue;",
		"legs->origin[2] += 24.0f * ( scale - 1.0f );",
		"VectorScale( legs->axis[0], scale, legs->axis[0] );",
		"VectorScale( legs->axis[1], scale, legs->axis[1] );",
		"VectorScale( legs->axis[2], scale, legs->axis[2] );",
	):
		assert expected in apply_scale
	assert player_block.index("playerModelScale = CG_PlayerModelBoundingBoxScale( ci );") < player_block.index(
		"CG_ApplyPlayerModelBoundingBoxScale( &legs, playerModelScale );"
	)
	assert player_block.index("CG_ApplyPlayerModelBoundingBoxScale( &legs, playerModelScale );") < player_block.index(
		'CG_PositionRotatedEntityOnTag( &torso, &legs, ci->legsModel, "tag_torso");'
	)

	for expected in (
		"if ( cg_shadows.integer == 0 ) {",
		"if ( cg_shadows.integer != 1 ) {",
	):
		assert expected in player_shadow
	assert "if ( !cg_shadows.integer ) {" in player_splash
	assert "if ( cg_shadows.integer == 3 && shadow ) {" in player_block
	assert "cg_showmiss.integer" in predict_source

	for expected in (
		"radius = cg_smokeRadius_flight.value;",
		"if ( radius <= 0.0f ) {",
		"origin[2] -= 16.0f;",
		"origin[2] += 24.0f;",
		"CG_SmokePuff( origin, vec3_origin,",
		"1000,",
		"cgs.media.smokePuffShader );",
	):
		assert expected in flight_trail
	assert "CG_FlightTrail( cent );" in powerups_block
	assert "radius = cg_smokeRadius_haste.value;" in haste_trail
	assert "radius = cg_smokeRadius_dust.value;" in dust_trail
	assert "radius = cg_smokeRadius_GL.value;" in rocket_trail
	assert "radius = cg_smokeRadius_RL.value;" in rocket_trail
	assert "radius = cg_smokeRadius_NG.value;" in nail_trail
	assert "if ( cg_smoke_SG.integer && cgs.glconfig.hardwareType != GLHW_RAGEPRO ) {" in shotgun_fire


def test_cgame_event_dispatch_keeps_retail_impact_effect_wiring() -> None:
	event_block = _block_from_marker(_read(CG_EVENT), "void CG_EntityEvent( centity_t *cent, vec3_t position )")

	dmgthrough = _case_block(event_block, "case EV_MISSILE_MISS_DMGTHROUGH:")
	assert dmgthrough.index("ByteToDir( es->eventParm, dir );") < dmgthrough.index(
		"CG_MissileHitWallDmgThrough( position, dir, es->weapon );"
	)

	missile_hit = _case_block(event_block, "case EV_MISSILE_HIT:")
	assert "CG_MissileHitPlayer( es->weapon, position, dir, es->otherEntityNum );" in missile_hit

	missile_miss = _case_block(event_block, "case EV_MISSILE_MISS:")
	assert "CG_MissileHitWall( es->weapon, 0, position, dir, IMPACTSOUND_DEFAULT );" in missile_miss

	missile_metal = _case_block(event_block, "case EV_MISSILE_MISS_METAL:")
	assert "CG_MissileHitWall( es->weapon, 0, position, dir, IMPACTSOUND_METAL );" in missile_metal

	rail = _case_block(event_block, "case EV_RAILTRAIL:")
	assert rail.index("CG_RailTrail( ci, es->origin2, es->pos.trBase );") < rail.index(
		"CG_MissileHitWall( es->weapon, es->clientNum, position, dir, IMPACTSOUND_DEFAULT );"
	)

	bullet_wall = _case_block(event_block, "case EV_BULLET_HIT_WALL:")
	assert "CG_Bullet( es->pos.trBase, es->otherEntityNum, dir, qfalse, ENTITYNUM_WORLD );" in bullet_wall

	bullet_flesh = _case_block(event_block, "case EV_BULLET_HIT_FLESH:")
	assert "CG_Bullet( es->pos.trBase, es->otherEntityNum, dir, qtrue, es->eventParm );" in bullet_flesh

	shotgun = _case_block(event_block, "case EV_SHOTGUN:")
	assert "CG_ShotgunFire( es );" in shotgun

	shotgun_kill = _case_block(event_block, "case EV_SHOTGUN_KILL:")
	assert "CG_ShotgunKillEffect( cent, es );" in shotgun_kill

	lightning_bolt = _case_block(event_block, "case EV_LIGHTNINGBOLT:")
	assert 'DEBUGNAME("EV_LIGHTNINGBOLT");' in lightning_bolt
	assert "CG_LightningBoltBeam(es->origin2, es->pos.trBase);" in lightning_bolt

	lightning_discharge = _case_block(event_block, "case QL_EV_LIGHTNING_DISCHARGE:")
	assert 'DEBUGNAME("EV_LIGHTNING_DISCHARGE");' in lightning_discharge
	assert "CG_LightningDischargeEffect( cent->lerpOrigin, es->eventParm );" in lightning_discharge

	grenade_bounce = _case_block(event_block, "case EV_GRENADE_BOUNCE:")
	assert "DEBUGNAME(\"EV_GRENADE_BOUNCE\");" in grenade_bounce
	assert "rand() & 1" in grenade_bounce
	assert "cgs.media.hgrenb1aSound" in grenade_bounce
	assert "cgs.media.hgrenb2aSound" in grenade_bounce


def test_cgame_damage_through_impact_sparks_match_retail_surfacepuff_path() -> None:
	weapons = _read(CG_WEAPONS)
	dmgthrough = _block_from_marker(
		weapons,
		"void CG_MissileHitWallDmgThrough( vec3_t origin, vec3_t dir, int weapon )",
	)

	for expected in (
		"probeDistance = CG_GetDamageThroughProbeDistance();",
		"VectorMA( origin, probeDistance, dir, probeOrigin );",
		"CG_Trace( &trace, probeOrigin, NULL, NULL, origin, ENTITYNUM_NONE, CONTENTS_SOLID );",
		"if ( trace.fraction < 1.0f && !trace.startsolid ) {",
		"CG_ImpactMark( cgs.media.burnMarkShader, trace.endpos, trace.plane.normal,",
		"qfalse, 64.0f, qfalse );",
		"if ( cg_impactSparks.integer && cg_impactSparksLifetime.integer > 0 && cgs.media.surfacePuffShader ) {",
		"sparkLifetime = cg_impactSparksLifetime.integer;",
		"sparkSize = cg_impactSparksSize.value;",
		"sparkVelocity = cg_impactSparksVelocity.value;",
		"for ( i = 0; i < 10; i++ ) {",
		"velocity[2] = sparkVelocity + ( random() - 0.5f ) * 16.0f;",
		"sparkSize,",
		"sparkLifetime,",
		"cgs.media.surfacePuffShader );",
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_DEFAULT );",
	):
		assert expected in dmgthrough

	assert dmgthrough.index("if ( cg_impactSparks.integer && cg_impactSparksLifetime.integer > 0 && cgs.media.surfacePuffShader ) {") < dmgthrough.index(
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_DEFAULT );"
	)

	particles = _read(CG_PARTICLES)
	assert "static void CG_ParticleSparks (vec3_t org, vec3_t vel, int duration, float x, float y, float speed)" in particles
	assert particles.count("CG_ParticleSparks") == 1


def test_cgame_normal_impact_switch_and_media_registration_stay_wired() -> None:
	weapons = _read(CG_WEAPONS)
	main = _read(CG_MAIN)
	local = _read(CG_LOCAL)

	hitwall = _block_from_marker(
		weapons,
		"void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
	)
	for expected in (
		"case WP_MACHINEGUN:",
		"case WP_HEAVY_MACHINEGUN:",
		"case WP_SHOTGUN:",
		"case WP_CHAINGUN:",
		"case WP_NAILGUN:",
		"case WP_LIGHTNING:",
		"case WP_RAILGUN:",
		"case WP_PLASMAGUN:",
		"case WP_BFG:",
		"case WP_ROCKET_LAUNCHER:",
		"case WP_GRENADE_LAUNCHER:",
		"case WP_PROX_LAUNCHER:",
		"alphaFade = (mark == cgs.media.energyMarkShader);",
		"CG_ResolveClientWeaponColor( ci, NULL, color )",
		"CG_ImpactMark( mark, origin, dir, random()*360, color[0],color[1], color[2],1, alphaFade, radius, qfalse );",
	):
		assert expected in hitwall

	machinegun = _case_block(hitwall, "case WP_MACHINEGUN:")
	for expected in (
		"mod = cgs.media.bulletFlashModel;",
		"shader = cgs.media.bulletExplosionShader;",
		"mark = cgs.media.bulletMarkShader;",
		"sfx = cgs.media.sfx_ric1;",
		"sfx = cgs.media.sfx_ric2;",
		"sfx = cgs.media.sfx_ric3;",
		"radius = 8;",
	):
		assert expected in machinegun

	hmg = _case_block(hitwall, "case WP_HEAVY_MACHINEGUN:")
	for expected in (
		"mod = cgs.media.bulletFlashModel;",
		"shader = cgs.media.bulletExplosionShader;",
		"mark = cgs.media.bulletMarkShader;",
		"radius = 4;",
	):
		assert expected in hmg

	nail_hit = _case_block(hitwall, "case WP_NAILGUN:")
	for expected in (
		"if( soundType == IMPACTSOUND_FLESH ) {",
		"sfx = cgs.media.sfx_nghitflesh;",
		"} else if( soundType == IMPACTSOUND_METAL ) {",
		"sfx = cgs.media.sfx_nghitmetal;",
		"sfx = cgs.media.sfx_nghit;",
		"mark = cgs.media.holeMarkShader;",
		"radius = 12;",
	):
		assert expected in nail_hit

	lightning_hit = _case_block(hitwall, "case WP_LIGHTNING:")
	for expected in (
		"r = rand() & 3;",
		"sfx = cgs.media.sfx_lghit2;",
		"sfx = cgs.media.sfx_lghit1;",
		"sfx = cgs.media.sfx_lghit3;",
		"mark = cgs.media.holeMarkShader;",
		"radius = 12;",
	):
		assert expected in lightning_hit

	rail_hit = _case_block(hitwall, "case WP_RAILGUN:")
	for expected in (
		"mod = cgs.media.ringFlashModel;",
		"shader = cgs.media.railExplosionShader;",
		"sfx = cgs.media.sfx_plasmaexp;",
		"mark = cgs.media.energyMarkShader;",
		"radius = 24;",
	):
		assert expected in rail_hit

	plasma_hit = _case_block(hitwall, "case WP_PLASMAGUN:")
	for expected in (
		"mod = cgs.media.ringFlashModel;",
		"shader = cgs.media.plasmaExplosionShader;",
		"sfx = cgs.media.sfx_plasmaexp;",
		"mark = cgs.media.energyMarkShader;",
		"radius = 16;",
	):
		assert expected in plasma_hit

	bfg_hit = _case_block(hitwall, "case WP_BFG:")
	for expected in (
		"mod = cgs.media.dishFlashModel;",
		"shader = cgs.media.bfgExplosionShader;",
		"sfx = cgs.media.sfx_rockexp;",
		"mark = cgs.media.burnMarkShader;",
		"radius = 32;",
		"isSprite = qtrue;",
	):
		assert expected in bfg_hit

	rocket_hit = _case_block(hitwall, "case WP_ROCKET_LAUNCHER:")
	for expected in (
		"mod = cgs.media.dishFlashModel;",
		"shader = cgs.media.rocketExplosionShader;",
		"sfx = cgs.media.sfx_rockexp;",
		"mark = cgs.media.burnMarkShader;",
		"radius = 64;",
		"light = 300;",
		"isSprite = qtrue;",
		"duration = 1000;",
		"lightColor[0] = 1;",
		"lightColor[1] = 0.75;",
		"lightColor[2] = 0.0;",
		"if ( cg_rocketStyle.integer == 2 ) {",
		"CG_ParticleExplosion( \"explode1\", sprOrg, sprVel, 1400, 20, 30 );",
	):
		assert expected in rocket_hit

	grenade_hit = _case_block(hitwall, "case WP_GRENADE_LAUNCHER:")
	for expected in (
		"mod = cgs.media.dishFlashModel;",
		"shader = cgs.media.grenadeExplosionShader;",
		"sfx = cgs.media.sfx_rockexp;",
		"mark = cgs.media.burnMarkShader;",
		"radius = 64;",
		"light = 300;",
		"isSprite = qtrue;",
	):
		assert expected in grenade_hit

	register_weapon = _block_from_marker(
		weapons,
		"void CG_RegisterWeapon( int weaponNum )",
	)
	grenade_trail = _block_from_marker(
		weapons,
		"static void CG_GrenadeTrail",
	)
	nail_eject = _block_from_marker(
		weapons,
		"static void CG_NailgunEjectBrass",
	)
	nail_trail = _block_from_marker(
		weapons,
		"static void CG_NailTrail",
	)
	rocket_trail = _block_from_marker(
		weapons,
		"static void CG_RocketTrail",
	)
	machinegun_register = _case_block(register_weapon, "case WP_MACHINEGUN:")
	hmg_register = _case_block(register_weapon, "case WP_HEAVY_MACHINEGUN:")
	shotgun_register = _case_block(register_weapon, "case WP_SHOTGUN:")
	nailgun_register = _case_block(register_weapon, "case WP_NAILGUN:")
	lightning_register = _case_block(register_weapon, "case WP_LIGHTNING:")
	plasmagun_register = _case_block(register_weapon, "case WP_PLASMAGUN:")
	railgun_register = _case_block(register_weapon, "case WP_RAILGUN:")
	bfg_register = _case_block(register_weapon, "case WP_BFG:")
	rocket_register = _case_block(register_weapon, "case WP_ROCKET_LAUNCHER:")
	grenade_register = _case_block(register_weapon, "case WP_GRENADE_LAUNCHER:")
	for expected in (
		"step = 50;",
		"radius = cg_smokeRadius_GL.value;",
		"radius = cg_smokeRadius_RL.value;",
		"BG_EvaluateTrajectory( &es->pos, cg.time, origin );",
		"if ( es->pos.trType == TR_STATIONARY ) {",
		"CG_BubbleTrail( lastPos, origin, 8 );",
		"if ( radius <= 0.0f ) {",
		"CG_SmokePuff( lastPos, up,",
		"radius,",
		"wi->wiTrailTime,",
		"cgs.media.smokePuffShader );",
		"smoke->leType = LE_SCALE_FADE;",
	):
		assert expected in rocket_trail
	assert "CG_RocketTrail( ent, wi );" in grenade_trail
	for expected in (
		"offset[0] = 0;",
		"offset[1] = -12;",
		"offset[2] = 24;",
		"VectorSet( up, 0, 0, 64 );",
		"CG_SmokePuff( origin, up, 32, 1, 1, 1, 0.33f, 700, cg.time, 0, 0, cgs.media.smokePuffShader );",
		"smoke->leType = LE_SCALE_FADE;",
	):
		assert expected in nail_eject
	for expected in (
		"step = 50;",
		"radius = cg_smokeRadius_NG.value;",
		"BG_EvaluateTrajectory( &es->pos, cg.time, origin );",
		"if ( es->pos.trType == TR_STATIONARY ) {",
		"CG_BubbleTrail( lastPos, origin, 8 );",
		"if ( radius <= 0.0f ) {",
		"CG_SmokePuff( lastPos, up,",
		"radius,",
		"wi->wiTrailTime,",
		"cgs.media.nailPuffShader );",
		"smoke->leType = LE_SCALE_FADE;",
	):
		assert expected in nail_trail
	assert "weaponInfo->ejectBrassFunc = CG_MachineGunEjectBrass;" in machinegun_register
	assert "weaponInfo->ejectBrassFunc = CG_MachineGunEjectBrass;" in hmg_register
	assert "weaponInfo->ejectBrassFunc = CG_ShotgunEjectBrass;" in shotgun_register
	for expected in (
		"weaponInfo->ejectBrassFunc = CG_NailgunEjectBrass;",
		"weaponInfo->missileTrailFunc = CG_NailTrail;",
		"weaponInfo->trailRadius = 16;",
		"weaponInfo->wiTrailTime = 250;",
		'weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/nail.md3" );',
		"MAKERGB( weaponInfo->flashDlightColor, 1, 0.75f, 0 );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/nailgun/wnalfire.ogg", qfalse );',
	):
		assert expected in nailgun_register
	for expected in (
		"MAKERGB( weaponInfo->flashDlightColor, 0.6f, 0.6f, 1.0f );",
		'weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/melee/fsthum.ogg", qfalse );',
		'weaponInfo->firingSound = trap_S_RegisterSound( "sound/weapons/lightning/lg_hum.ogg", qfalse );',
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/lightning/lg_fire.ogg", qfalse );',
		'cgs.media.lightningShader = trap_R_RegisterShader( "lightningBolt1" );',
		'cgs.media.lightningExplosionModel = trap_R_RegisterModel( "models/weaphits/crackle.md3" );',
		'cgs.media.sfx_lghit1 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit.ogg", qfalse );',
		'cgs.media.sfx_lghit2 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit2.ogg", qfalse );',
		'cgs.media.sfx_lghit3 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit3.ogg", qfalse );',
	):
		assert expected in lightning_register
	for expected in (
		'weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/railgun/rg_hum.ogg", qfalse );',
		"MAKERGB( weaponInfo->flashDlightColor, 1, 0.5f, 0 );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/railgun/railgf1a.ogg", qfalse );',
		'cgs.media.railExplosionShader = trap_R_RegisterShader( "railExplosion" );',
		'cgs.media.railRingsShader = trap_R_RegisterShader( "railDisc" );',
		'cgs.media.railCoreShader = trap_R_RegisterShader( "railCore" );',
	):
		assert expected in railgun_register
	for expected in (
		"weaponInfo->missileTrailFunc = CG_PlasmaTrail;",
		'weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/plasma/lasfly.ogg", qfalse );',
		"MAKERGB( weaponInfo->flashDlightColor, 0.6f, 0.6f, 1.0f );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/plasma/hyprbf1a.ogg", qfalse );',
		'cgs.media.plasmaExplosionShader = trap_R_RegisterShader( "plasmaExplosion" );',
		'cgs.media.railRingsShader = trap_R_RegisterShader( "railDisc" );',
	):
		assert expected in plasmagun_register
	for expected in (
		'weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/bfg/bfg_hum.ogg", qfalse );',
		"MAKERGB( weaponInfo->flashDlightColor, 1, 0.7f, 1 );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/bfg/bfg_fire.ogg", qfalse );',
		'cgs.media.bfgExplosionShader = trap_R_RegisterShader( "bfgExplosion" );',
		'weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/bfg.md3" );',
		'weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/rocket/rockfly.ogg", qfalse );',
	):
		assert expected in bfg_register
	for expected in (
		'weaponInfo->missileModel = trap_R_RegisterModel( "models/ammo/rocket/rocket.md3" );',
		'weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/rocket/rockfly.ogg", qfalse );',
		"weaponInfo->missileTrailFunc = CG_RocketTrail;",
		"weaponInfo->missileDlight = 200;",
		"weaponInfo->wiTrailTime = 2000;",
		"weaponInfo->trailRadius = 64;",
		"MAKERGB( weaponInfo->missileDlightColor, 1, 0.75f, 0 );",
		"MAKERGB( weaponInfo->flashDlightColor, 1, 0.75f, 0 );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/rocket/rocklf1a.ogg", qfalse );',
		'cgs.media.rocketExplosionShader = trap_R_RegisterShader( "rocketExplosion" );',
	):
		assert expected in rocket_register
	for expected in (
		'weaponInfo->missileModel = trap_R_RegisterModel( "models/ammo/grenade1.md3" );',
		"weaponInfo->missileTrailFunc = CG_GrenadeTrail;",
		"weaponInfo->wiTrailTime = 700;",
		"weaponInfo->trailRadius = 32;",
		"MAKERGB( weaponInfo->flashDlightColor, 1, 0.70f, 0 );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/grenade/grenlf1a.ogg", qfalse );',
		'cgs.media.grenadeExplosionShader = trap_R_RegisterShader( "grenadeExplosion" );',
	):
		assert expected in grenade_register

	hitplayer = _block_from_marker(
		weapons,
		"void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum )",
	)
	for expected in (
		"case WP_GRENADE_LAUNCHER:",
		"case WP_ROCKET_LAUNCHER:",
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );",
	):
		assert expected in hitplayer
	assert hitplayer.index("case WP_GRENADE_LAUNCHER:") < hitplayer.index(
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );"
	)
	assert hitplayer.index("case WP_ROCKET_LAUNCHER:") < hitplayer.index(
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );"
	)

	shotgun = _case_block(hitwall, "case WP_SHOTGUN:")
	assert "sfx = 0;" in shotgun
	assert "radius = 4;" in shotgun

	for expected in (
		'cgs.media.surfacePuffShader = trap_R_RegisterShader( "surfacePuff" );',
		'cgs.media.bulletFlashModel = trap_R_RegisterModel("models/weaphits/bullet.md3");',
		'cgs.media.ringFlashModel = trap_R_RegisterModel("models/weaphits/ring02.md3");',
		'cgs.media.dishFlashModel = trap_R_RegisterModel("models/weaphits/boom01.md3");',
		'cgs.media.bulletMarkShader = trap_R_RegisterShader( "gfx/damage/bullet_mrk" );',
		'cgs.media.burnMarkShader = trap_R_RegisterShader( "gfx/damage/burn_med_mrk" );',
		'cgs.media.holeMarkShader = trap_R_RegisterShader( "gfx/damage/hole_lg_mrk" );',
		'cgs.media.energyMarkShader = trap_R_RegisterShader( "gfx/damage/plasma_mrk" );',
		'cgs.media.sfx_ric1 = trap_S_RegisterSound( "sound/weapons/machinegun/ric1.ogg", qfalse );',
		'cgs.media.sfx_nghit = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpd.ogg", qfalse );',
		'cgs.media.sfx_nghitflesh = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpl.ogg", qfalse );',
		'cgs.media.sfx_nghitmetal = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpm.ogg", qfalse );',
		'cgs.media.sfx_chghit = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpd.ogg", qfalse );',
		'cgs.media.sfx_railg = trap_S_RegisterSound( "sound/weapons/railgun/railgf1a.ogg", qfalse );',
		'cgs.media.sfx_plasmaexp = trap_S_RegisterSound( "sound/weapons/plasma/plasmx1a.ogg", qfalse );',
		'cgs.media.sfx_rockexp = trap_S_RegisterSound( "sound/weapons/rocket/rocklx1a.ogg", qfalse );',
		'cgs.media.nailPuffShader = trap_R_RegisterShader( "nailtrail" );',
	):
		assert expected in main

	for expected in (
		'cgs.media.lightningExplosionModel = trap_R_RegisterModel( "models/weaphits/crackle.md3" );',
		'cgs.media.sfx_lghit1 = trap_S_RegisterSound( "sound/weapons/lightning/lg_hit.ogg", qfalse );',
		'cgs.media.bulletExplosionShader = trap_R_RegisterShader( "bulletExplosion" );',
	):
		assert expected in weapons

	for expected in (
		"qhandle_t\tsurfacePuffShader;",
		"qhandle_t\tbulletFlashModel;",
		"qhandle_t\tbulletExplosionShader;",
		"qhandle_t\trailRingsShader;",
		"qhandle_t\trailCoreShader;",
		"qhandle_t\trailExplosionShader;",
		"qhandle_t\tplasmaBallShader;",
		"qhandle_t\tplasmaExplosionShader;",
		"qhandle_t\tbfgExplosionShader;",
		"qhandle_t\tnailPuffShader;",
		"sfxHandle_t\tsfx_rockexp;",
		"sfxHandle_t\tsfx_nghit;",
		"sfxHandle_t\tsfx_nghitflesh;",
		"sfxHandle_t\tsfx_nghitmetal;",
		"void CG_MissileHitWallDmgThrough( vec3_t origin, vec3_t dir, int weapon );",
		"void CG_Bullet( vec3_t origin, int sourceEntityNum, vec3_t normal, qboolean flesh, int fleshEntityNum );",
	):
		assert expected in local


def test_cgame_nailgun_projectile_trail_impact_and_media_wiring_match_retail() -> None:
	ents = _read(CG_ENTS)
	local = _read(CG_LOCAL)
	main = _read(CG_MAIN)
	weapons = _read(CG_WEAPONS)

	missile = _block_from_marker(ents, "static void CG_Missile( centity_t *cent )")
	nail_eject = _block_from_marker(weapons, "static void CG_NailgunEjectBrass")
	nail_trail = _block_from_marker(weapons, "static void CG_NailTrail")
	register_weapon = _block_from_marker(weapons, "void CG_RegisterWeapon( int weaponNum )")
	nailgun_register = _case_block(register_weapon, "case WP_NAILGUN:")
	hitwall = _block_from_marker(
		weapons,
		"void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
	)
	nail_hit = _case_block(hitwall, "case WP_NAILGUN:")
	hitplayer = _block_from_marker(
		weapons,
		"void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum )",
	)

	for expected in (
		'cgs.media.sfx_nghit = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpd.ogg", qfalse );',
		'cgs.media.sfx_nghitflesh = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpl.ogg", qfalse );',
		'cgs.media.sfx_nghitmetal = trap_S_RegisterSound( "sound/weapons/nailgun/wnalimpm.ogg", qfalse );',
		'cgs.media.nailPuffShader = trap_R_RegisterShader( "nailtrail" );',
		'cgs.media.holeMarkShader = trap_R_RegisterShader( "gfx/damage/hole_lg_mrk" );',
	):
		assert expected in main
	for expected in (
		"qhandle_t\tnailPuffShader;",
		"sfxHandle_t\tsfx_nghit;",
		"sfxHandle_t\tsfx_nghitflesh;",
		"sfxHandle_t\tsfx_nghitmetal;",
	):
		assert expected in local

	for expected in (
		"offset[0] = 0;",
		"offset[1] = -12;",
		"offset[2] = 24;",
		"AnglesToAxis( cent->lerpAngles, v );",
		"VectorAdd( cent->lerpOrigin, xoffset, origin );",
		"VectorSet( up, 0, 0, 64 );",
		"CG_SmokePuff( origin, up, 32, 1, 1, 1, 0.33f, 700, cg.time, 0, 0, cgs.media.smokePuffShader );",
		"smoke->leType = LE_SCALE_FADE;",
	):
		assert expected in nail_eject

	for expected in (
		"step = 50;",
		"t = step * ( (startTime + step) / step );",
		"radius = cg_smokeRadius_NG.value;",
		"BG_EvaluateTrajectory( &es->pos, cg.time, origin );",
		"contents = CG_PointContents( origin, -1 );",
		"if ( es->pos.trType == TR_STATIONARY ) {",
		"CG_BubbleTrail( lastPos, origin, 8 );",
		"if ( radius <= 0.0f ) {",
		"CG_SmokePuff( lastPos, up,",
		"radius,",
		"wi->wiTrailTime,",
		"cgs.media.nailPuffShader );",
		"smoke->leType = LE_SCALE_FADE;",
	):
		assert expected in nail_trail

	for expected in (
		"weaponInfo->ejectBrassFunc = CG_NailgunEjectBrass;",
		"weaponInfo->missileTrailFunc = CG_NailTrail;",
		"weaponInfo->trailRadius = 16;",
		"weaponInfo->wiTrailTime = 250;",
		'weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/nail.md3" );',
		"MAKERGB( weaponInfo->flashDlightColor, 1, 0.75f, 0 );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/nailgun/wnalfire.ogg", qfalse );',
	):
		assert expected in nailgun_register
	active_nailgun_register = "\n".join(
		line for line in nailgun_register.splitlines() if not line.lstrip().startswith("//")
	)
	assert "weaponInfo->missileSound" not in active_nailgun_register

	for expected in (
		"if ( weapon->missileTrailFunc )",
		"weapon->missileTrailFunc( cent, weapon );",
		"ent.hModel = weapon->missileModel;",
		"ent.renderfx = weapon->missileRenderfx | RF_NOSHADOW;",
		"VectorNormalize2( s1->pos.trDelta, ent.axis[0] )",
		"RotateAroundDirection( ent.axis, cg.time / 4 );",
		"CG_AddRefEntityWithPowerups( &ent, s1, TEAM_FREE );",
	):
		assert expected in missile
	assert "if ( cent->currentState.weapon == WP_NAILGUN )" not in missile

	for expected in (
		"if( soundType == IMPACTSOUND_FLESH ) {",
		"sfx = cgs.media.sfx_nghitflesh;",
		"} else if( soundType == IMPACTSOUND_METAL ) {",
		"sfx = cgs.media.sfx_nghitmetal;",
		"sfx = cgs.media.sfx_nghit;",
		"mark = cgs.media.holeMarkShader;",
		"radius = 12;",
	):
		assert expected in nail_hit

	assert "case WP_NAILGUN:" in hitplayer
	assert "CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );" in hitplayer
	assert hitplayer.index("case WP_NAILGUN:") < hitplayer.index(
		"CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );"
	)


def test_cgame_plasmagun_trail_projectile_and_media_wiring_match_retail() -> None:
	ents = _read(CG_ENTS)
	main = _read(CG_MAIN)
	weapons = _read(CG_WEAPONS)

	missile = _block_from_marker(ents, "static void CG_Missile( centity_t *cent )")
	trail = _block_from_marker(weapons, "static void CG_PlasmaTrail")
	register_weapon = _block_from_marker(weapons, "void CG_RegisterWeapon( int weaponNum )")
	plasmagun_register = _case_block(register_weapon, "case WP_PLASMAGUN:")
	hitwall = _block_from_marker(
		weapons,
		"void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
	)
	plasma_hit = _case_block(hitwall, "case WP_PLASMAGUN:")
	hitplayer = _block_from_marker(
		weapons,
		"void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum )",
	)

	for expected in (
		'{ &cg_plasmaStyle, "cg_plasmaStyle", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "2" },',
		'cgs.media.sfx_plasmaexp = trap_S_RegisterSound( "sound/weapons/plasma/plasmx1a.ogg", qfalse );',
		'cgs.media.plasmaBallShader = trap_R_RegisterShader( "sprites/plasma1" );',
		'cgs.media.energyMarkShader = trap_R_RegisterShader( "gfx/damage/plasma_mrk" );',
	):
		assert expected in main

	for expected in (
		"if ( cg_plasmaStyle.integer != 2 ) {",
		"step = 50;",
		"t = step * ( (startTime + step) / step );",
		"BG_EvaluateTrajectory( &es->pos, cg.time, origin );",
		"velocity[0] = 60 - 120 * crandom();",
		"velocity[1] = 40 - 80 * crandom();",
		"velocity[2] = 100 - 200 * crandom();",
		"le->leType = LE_MOVE_SCALE_FADE;",
		"le->leFlags = LEF_TUMBLE;",
		"le->fragmentBounceSoundType = LEBS_NONE;",
		"le->fragmentMarkType = LEMT_NONE;",
		"le->endTime = le->startTime + 600;",
		"le->pos.trType = TR_GRAVITY;",
		"offset[0] = 2;",
		"offset[1] = 2;",
		"offset[2] = 2;",
		"if ( CG_PointContents( re->origin, -1 ) & CONTENTS_WATER ) {",
		"waterScale = 0.10f;",
		"VectorScale( xvelocity, waterScale, le->pos.trDelta );",
		"re->reType = RT_SPRITE;",
		"re->radius = 0.25f;",
		"re->customShader = cgs.media.railRingsShader;",
		"re->shaderRGBA[0] = wi->flashDlightColor[0] * 63;",
		"le->color[0] = wi->flashDlightColor[0] * 0.2;",
		"le->angles.trType = TR_LINEAR;",
		"le->angles.trBase[0] = rand()&31;",
	):
		assert expected in trail
	assert "cg_noProjectileTrail" not in trail
	assert "cg_oldPlasma" not in trail

	for expected in (
		"weaponInfo->missileTrailFunc = CG_PlasmaTrail;",
		'weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/plasma/lasfly.ogg", qfalse );',
		"MAKERGB( weaponInfo->flashDlightColor, 0.6f, 0.6f, 1.0f );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/plasma/hyprbf1a.ogg", qfalse );',
		'cgs.media.plasmaExplosionShader = trap_R_RegisterShader( "plasmaExplosion" );',
		'cgs.media.railRingsShader = trap_R_RegisterShader( "railDisc" );',
	):
		assert expected in plasmagun_register

	for expected in (
		"if ( cent->currentState.weapon == WP_PLASMAGUN ) {",
		"ent.reType = RT_SPRITE;",
		"ent.radius = 16;",
		"ent.rotation = 0;",
		"ent.customShader = cgs.media.plasmaBallShader;",
		"trap_R_AddRefEntityToScene( &ent );",
		"return;",
	):
		assert expected in missile

	for expected in (
		"mod = cgs.media.ringFlashModel;",
		"shader = cgs.media.plasmaExplosionShader;",
		"sfx = cgs.media.sfx_plasmaexp;",
		"mark = cgs.media.energyMarkShader;",
		"radius = 16;",
	):
		assert expected in plasma_hit
	assert "case WP_PLASMAGUN:" not in hitplayer
	assert "CG_Bleed( origin, entityNum );" in hitplayer


def test_cgame_bfg_projectile_impact_and_media_wiring_match_retail() -> None:
	ents = _read(CG_ENTS)
	local = _read(CG_LOCAL)
	main = _read(CG_MAIN)
	weapons = _read(CG_WEAPONS)

	missile = _block_from_marker(ents, "static void CG_Missile( centity_t *cent )")
	register_weapon = _block_from_marker(weapons, "void CG_RegisterWeapon( int weaponNum )")
	bfg_register = _case_block(register_weapon, "case WP_BFG:")
	hitwall = _block_from_marker(
		weapons,
		"void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
	)
	bfg_hit = _case_block(hitwall, "case WP_BFG:")
	hitplayer = _block_from_marker(
		weapons,
		"void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum )",
	)

	for expected in (
		'cgs.media.sfx_rockexp = trap_S_RegisterSound( "sound/weapons/rocket/rocklx1a.ogg", qfalse );',
		'cgs.media.dishFlashModel = trap_R_RegisterModel("models/weaphits/boom01.md3");',
		'cgs.media.burnMarkShader = trap_R_RegisterShader( "gfx/damage/burn_med_mrk" );',
	):
		assert expected in main
	assert "qhandle_t\tbfgExplosionShader;" in local

	for expected in (
		'weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/bfg/bfg_hum.ogg", qfalse );',
		"MAKERGB( weaponInfo->flashDlightColor, 1, 0.7f, 1 );",
		'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/bfg/bfg_fire.ogg", qfalse );',
		'cgs.media.bfgExplosionShader = trap_R_RegisterShader( "bfgExplosion" );',
		'weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/bfg.md3" );',
		'weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/rocket/rockfly.ogg", qfalse );',
	):
		assert expected in bfg_register

	for expected in (
		"if ( weapon->missileSound ) {",
		"trap_S_AddLoopingSound( cent->currentState.number, cent->lerpOrigin, velocity, weapon->missileSound );",
		"ent.skinNum = cg.clientFrame & 1;",
		"ent.hModel = weapon->missileModel;",
		"ent.renderfx = weapon->missileRenderfx | RF_NOSHADOW;",
		"VectorNormalize2( s1->pos.trDelta, ent.axis[0] )",
		"RotateAroundDirection( ent.axis, cg.time / 4 );",
		"CG_AddRefEntityWithPowerups( &ent, s1, TEAM_FREE );",
	):
		assert expected in missile
	assert "if ( cent->currentState.weapon == WP_BFG )" not in missile

	for expected in (
		"mod = cgs.media.dishFlashModel;",
		"shader = cgs.media.bfgExplosionShader;",
		"sfx = cgs.media.sfx_rockexp;",
		"mark = cgs.media.burnMarkShader;",
		"radius = 32;",
		"isSprite = qtrue;",
	):
		assert expected in bfg_hit

	assert "case WP_BFG:" not in hitplayer
	assert "CG_Bleed( origin, entityNum );" in hitplayer


def test_cgame_rail_trail_prediction_and_event_wiring_match_retail() -> None:
	event = _read(CG_EVENT)
	main = _read(CG_MAIN)
	predict = _read(CG_PREDICT)
	weapons = _read(CG_WEAPONS)

	suppress = _block_from_marker(event, "static qboolean CG_ShouldSuppressPredictedRailEvent")
	event_block = _block_from_marker(event, "void CG_EntityEvent( centity_t *cent, vec3_t position )")
	rail_event = _case_block(event_block, "case EV_RAILTRAIL:")
	predict_update = _block_from_marker(predict, "static void CG_UpdatePredictedRailFire")
	rail_ring = _block_from_marker(weapons, "static void CG_SpawnRailRing")
	rail_trail = _block_from_marker(weapons, "void CG_RailTrail")
	predicted_rail = _block_from_marker(
		weapons,
		"qboolean CG_BuildPredictedRailForPlayerState",
	)
	stored_beam = _block_from_marker(weapons, "static qboolean CG_GetStoredPredictedBeam")
	spawn_trail = _block_from_marker(weapons, "static void CG_SpawnRailTrail")
	add_weapon = _block_from_marker(
		weapons,
		"void CG_AddPlayerWeapon( refEntity_t *parent, playerState_t *ps, centity_t *cent, int team )",
	)

	for expected in (
		'cgs.media.sfx_railg = trap_S_RegisterSound( "sound/weapons/railgun/railgf1a.ogg", qfalse );',
		'{ &cg_predictLocalRailshots, "cg_predictLocalRailshots", "1", 0 },',
		'{ &cg_railStyle, "cg_railStyle", "1", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "1", "2" },',
		'{ &cg_railTrailTime, "cg_railTrailTime", "400", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_CLOUD, "0", "2000" },',
		"cg.predictLocalRailshots = (qboolean)( cg_predictLocalRailshots.integer != 0 );",
	):
		assert expected in main

	for expected in (
		"if ( !cg.predictLocalRailshots ) {",
		"if ( cg.time - cg.predictedLocalRailTime > 200 ) {",
		"if ( es->clientNum != cg.predictedPlayerState.clientNum ) {",
		"if ( cg.predictedLocalRailHit != ( es->eventParm != 255 ) ) {",
		"if ( DistanceSquared( cg.predictedLocalRailEnd, es->pos.trBase ) > Square( 8.0f ) ) {",
	):
		assert expected in suppress
	for expected in (
		"cent->currentState.weapon = WP_RAILGUN;",
		"if ( CG_ShouldSuppressPredictedRailEvent( es ) ) {",
		"cg.predictedLocalRailValid = qfalse;",
		"CG_RailTrail( ci, es->origin2, es->pos.trBase );",
		"if ( es->eventParm != 255 ) {",
		"CG_MissileHitWall( es->weapon, es->clientNum, position, dir, IMPACTSOUND_DEFAULT );",
	):
		assert expected in rail_event

	for expected in (
		"le->leType = LE_FADE_RGB;",
		"le->endTime = cg.time + cg_railTrailTime.value;",
		"if ( le->endTime <= le->startTime ) {",
		"re->reType = RT_RAIL_RINGS;",
		"re->customShader = cgs.media.railRingsShader;",
		"CG_ResolveClientWeaponColorBytes( ci, rgb )",
		"CG_ResolveClientWeaponColor( ci, NULL, le->color )",
	):
		assert expected in rail_ring
	for expected in (
		"CG_AdjustRailTrailStart( ci, start );",
		"re->reType = RT_RAIL_CORE;",
		"re->customShader = cgs.media.railCoreShader;",
		"CG_ResolveClientWeaponColor( ci, rgb, le->color )",
		"AxisClear( re->axis );",
		"VectorMA(move, 20, vec, move);",
		"if ( cg_railStyle.integer != 2 ) {",
		"CG_SpawnRailRing( start, end, ci );",
		"le->leType = LE_MOVE_SCALE_FADE;",
		"re->reType = RT_SPRITE;",
		"re->radius = 1.1f;",
		"re->customShader = cgs.media.railRingsShader;",
		"le->pos.trType = TR_LINEAR;",
	):
		assert expected in rail_trail

	for expected in (
		"if ( !cg.predictLocalRailshots ) {",
		"if ( clientNum != cg.predictedPlayerState.clientNum ) {",
		"VectorMA( muzzle, 5, forward, muzzle );",
		"VectorMA( start, 4, right, start );",
		"VectorMA( start, -1, up, start );",
		"VectorMA( traceStart, 8192, forward, finish );",
		"CG_Trace( &trace, traceStart, vec3_origin, vec3_origin, finish, clientNum, MASK_SHOT );",
		"if ( trace.entityNum >= ENTITYNUM_MAX_NORMAL || trace.allsolid ) {",
		"if ( trace.contents & CONTENTS_SOLID ) {",
		"if ( railHits >= 4 ) {",
		"VectorMA( traceStart, 1.0f, forward, traceStart );",
		"CG_SnapVectorTowards( end, muzzle );",
		"*addImpact = (qboolean)( !( trace.surfaceFlags & SURF_NOIMPACT ) );",
		"VectorCopy( trace.plane.normal, impactDir );",
	):
		assert expected in predicted_rail
	for expected in (
		"case WP_RAILGUN:",
		"if ( !cg.predictedLocalRailValid ) {",
		"if ( cg.time - cg.predictedLocalRailTime > CG_PREDICTED_HITSCAN_LIFETIME ) {",
		"VectorCopy( cg.predictedLocalRailStart, start );",
		"VectorCopy( cg.predictedLocalRailEnd, end );",
		"*hitWorld = cg.predictedLocalRailHit;",
	):
		assert expected in stored_beam

	for expected in (
		"if ( cent->currentState.weapon != WP_RAILGUN ) {",
		"if ( !cent->pe.railgunFlash ) {",
		"cent->pe.railgunFlash = qfalse;",
		"VectorCopy( origin, start );",
		"VectorCopy( cent->pe.railgunImpact, end );",
		"ci = &cgs.clientinfo[ cent->currentState.clientNum ];",
		"CG_RailTrail( ci, start, end );",
	):
		assert expected in spawn_trail
	for expected in (
		"railReloadTime = CG_GetWeaponReloadTime( WP_RAILGUN );",
		"if ( railReloadTime <= 0 ) {",
		"railReloadTime = 1500;",
		"if ( weaponNum == WP_RAILGUN ) {",
		"CG_ResolveClientWeaponColor( ci, rgb, NULL )",
		"CG_SpawnRailTrail( cent, flash.origin );",
	):
		assert expected in add_weapon

	for expected in (
		"if ( cg.predictedPlayerState.weapon != WP_RAILGUN ) {",
		"if ( cmd->weapon != WP_RAILGUN ) {",
		"if ( !( cmd->buttons & BUTTON_ATTACK ) ) {",
		"if ( cmd->buttons & BUTTON_TALK ) {",
		"if ( cg.predictedPlayerState.ammo[ WP_RAILGUN ] == 0 ) {",
		"weaponTime = cg.predictedPlayerState.weaponTime - cg.frametime;",
		"if ( cg.time - cg.predictedLocalRailTime <= 100 ) {",
		"CG_BuildPredictedRailForPlayerState( &cg.predictedPlayerState, cg.predictedPlayerState.clientNum,",
		"cg.predictedLocalRailValid = qtrue;",
		"cg.predictedLocalRailHit = addImpact;",
		"CG_RailTrail( ci, predictedStart, predictedEnd );",
		"CG_MissileHitWall( WP_RAILGUN, cg.predictedPlayerState.clientNum, predictedEnd, impactDir, IMPACTSOUND_DEFAULT );",
	):
		assert expected in predict_update


def test_cgame_lightning_beam_and_impact_cap_match_retail_wiring() -> None:
	weapons = _read(CG_WEAPONS)
	effects = _read(REPO_ROOT / "src" / "code" / "cgame" / "cg_effects.c")

	impact = _block_from_marker(weapons, "static void CG_DrawLightningImpact")
	beam = _block_from_marker(weapons, "static void CG_LightningBolt")
	predicted = _block_from_marker(
		weapons,
		"qboolean CG_BuildPredictedBeamForPlayerState",
	)
	bounce = _block_from_marker(effects, "void CG_LightningBoltBeam")

	assert "static qboolean CG_CanDrawLightningImpact" not in weapons
	for expected in (
		"if ( cg_lightningImpact.integer == 0 || !cgs.media.lightningExplosionModel ) {",
		"VectorMA( endPos, -16, dir, origin );",
		"cap = cg_lightningImpactCap.integer;",
		"distance = Distance( endPos, startPos );",
		"if ( distance < (float)cap ) {",
		"scale = distance / (float)cap;",
		"if ( scale < 0.125f ) {",
		"VectorScale( impact.axis[0], scale, impact.axis[0] );",
		"VectorScale( impact.axis[1], scale, impact.axis[1] );",
		"VectorScale( impact.axis[2], scale, impact.axis[2] );",
		"impact.nonNormalizedAxes = qtrue;",
		"trap_R_AddRefEntityToScene( &impact );",
	):
		assert expected in impact

	for expected in (
		"addImpact = ( trace.fraction < 1.0f && !( trace.surfaceFlags & SURF_NOIMPACT ) );",
		"beam.reType = RT_LIGHTNING;",
		"beam.customShader = CG_LightningCurrentShader();",
		"CG_SubmitLightningBeams( &beam, CG_LightningSegmentCount() );",
		"CG_DrawLightningImpact( beam.origin, impactPoint, dir );",
	):
		assert expected in beam
	assert "trap_R_AddRefEntityToScene( &beam );\n\t\tCG_DrawLightningImpact" not in beam
	assert "localHit = ( trace.fraction < 1.0f && !( trace.surfaceFlags & SURF_NOIMPACT ) );" in predicted

	for expected in (
		"le->leType = LE_SHOWREFENTITY;",
		"le->endTime = cg.time + 50;",
		"beam->reType = RT_LIGHTNING;",
		"beam->radius = 256.0f;",
		"styleIndex = cg_lightningStyle.integer - 1;",
		"beam->customShader = cgs.media.lightningStyleShaders[styleIndex];",
		"beam->customShader = cgs.media.lightningShader;",
	):
		assert expected in bounce
