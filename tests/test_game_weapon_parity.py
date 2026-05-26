from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _function_body(source: str, signature: str) -> str:
    match = re.search(
        rf"{re.escape(signature)}\s*\{{(?P<body>.*?)^\}}",
        source,
        re.MULTILINE | re.DOTALL,
    )

    assert match is not None, f"{signature} definition missing"
    return match.group("body")


def test_first_ten_knockback_cvar_table_matches_retail_defaults_and_flags() -> None:
    config_c = _read("src/game/g_config.c")
    q_shared_h = _read("src/code/game/q_shared.h")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    assert "#define CVAR_GAMERULE\t0x100000" in q_shared_h
    assert "#define CONFIG_CVAR_FLAG_RETAIL_40000 0x00040000" in config_c
    for expected in (
        "#define DEFAULT_KNOCKBACK_G                 1",
        "#define DEFAULT_KNOCKBACK_MG                1",
        "#define DEFAULT_KNOCKBACK_SG                1",
        "#define DEFAULT_KNOCKBACK_GL                1.10",
        "#define DEFAULT_KNOCKBACK_RL                0.90",
        "#define DEFAULT_KNOCKBACK_RL_SELF           1.10",
        "#define DEFAULT_KNOCKBACK_LG                1.75",
        "#define DEFAULT_KNOCKBACK_RG                0.85",
        "#define DEFAULT_KNOCKBACK_PG                1.10",
        "#define DEFAULT_KNOCKBACK_PG_SELF           1.30",
    ):
        assert expected in config_c

    for expected in (
        '{ &g_knockback_g,          "g_knockback_g",          STRINGIZE( DEFAULT_KNOCKBACK_G ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_mg,         "g_knockback_mg",         STRINGIZE( DEFAULT_KNOCKBACK_MG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_sg,         "g_knockback_sg",         STRINGIZE( DEFAULT_KNOCKBACK_SG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_gl,         "g_knockback_gl",         STRINGIZE( DEFAULT_KNOCKBACK_GL ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_rl,         "g_knockback_rl",         STRINGIZE( DEFAULT_KNOCKBACK_RL ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_rl_self,    "g_knockback_rl_self",    STRINGIZE( DEFAULT_KNOCKBACK_RL_SELF ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_lg,         "g_knockback_lg",         STRINGIZE( DEFAULT_KNOCKBACK_LG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_rg,         "g_knockback_rg",         STRINGIZE( DEFAULT_KNOCKBACK_RG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_pg,         "g_knockback_pg",         STRINGIZE( DEFAULT_KNOCKBACK_PG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_pg_self,    "g_knockback_pg_self",    STRINGIZE( DEFAULT_KNOCKBACK_PG_SELF ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
    ):
        assert expected in config_c

    retail_rows = {
        'g_knockback_g': ('1008e674  char const (* data_1008e674)[0xe] = data_10086ba8 {"g_knockback_g"}', "data_1007d1d8"),
        'g_knockback_mg': ('1008e6ec  char const (* data_1008e6ec)[0xf] = data_10086b44 {"g_knockback_mg"}', "data_1007d1d8"),
        'g_knockback_sg': ('1008e7ac  char const (* data_1008e7ac)[0xf] = data_10086acc {"g_knockback_sg"}', "data_1007d1d8"),
        'g_knockback_gl': ('1008e6a4  char const (* data_1008e6a4)[0xf] = data_10086b84 {"g_knockback_gl"}', 'data_10086b7c {"1.10"}'),
        'g_knockback_rl': ('1008e77c  char const (* data_1008e77c)[0xf] = data_10086ae4 {"g_knockback_rl"}', 'data_10086adc {"0.90"}'),
        'g_knockback_rl_self': ('1008e794  char const (* data_1008e794)[0x14] = data_10085334 {"g_knockback_rl_self"}', 'data_10086b7c {"1.10"}'),
        'g_knockback_lg': ('1008e6d4  char const (* data_1008e6d4)[0xf] = data_10086b5c {"g_knockback_lg"}', 'data_10086b54 {"1.75"}'),
        'g_knockback_rg': ('1008e764  char const (* data_1008e764)[0xf] = data_10086afc {"g_knockback_rg"}', 'data_10086af4 {"0.85"}'),
        'g_knockback_pg': ('1008e71c  char const (* data_1008e71c)[0xf] = data_10086b24 {"g_knockback_pg"}', 'data_10086b7c {"1.10"}'),
        'g_knockback_pg_self': ('1008e734  char const (* data_1008e734)[0x14] = data_10085348 {"g_knockback_pg_self"}', 'data_10086b1c {"1.30"}'),
    }
    for marker, default_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert "00 00 14 00" in row_block

    for expected in (
        "1007d1d8  data_1007d1d8:",
        "1007d1d8                                                                          31 00 00 00",
        '10085334  char const data_10085334[0x14] = "g_knockback_rl_self", 0',
        '10085348  char const data_10085348[0x14] = "g_knockback_pg_self", 0',
        '10086acc  char const data_10086acc[0xf] = "g_knockback_sg", 0',
        '10086adc  char const data_10086adc[0x5] = "0.90", 0',
        '10086ae4  char const data_10086ae4[0xf] = "g_knockback_rl", 0',
        '10086af4  char const data_10086af4[0x5] = "0.85", 0',
        '10086afc  char const data_10086afc[0xf] = "g_knockback_rg", 0',
        '10086b1c  char const data_10086b1c[0x5] = "1.30", 0',
        '10086b24  char const data_10086b24[0xf] = "g_knockback_pg", 0',
        '10086b44  char const data_10086b44[0xf] = "g_knockback_mg", 0',
        '10086b54  char const data_10086b54[0x5] = "1.75", 0',
        '10086b5c  char const data_10086b5c[0xf] = "g_knockback_lg", 0',
        '10086b7c  char const data_10086b7c[0x5] = "1.10", 0',
        '10086b84  char const data_10086b84[0xf] = "g_knockback_gl", 0',
        '10086ba8  char const data_10086ba8[0xe] = "g_knockback_g", 0',
    ):
        assert expected in qagame_strings


def test_first_ten_knockback_cvars_keep_retail_combat_wiring() -> None:
    config_c = _read("src/game/g_config.c")
    combat_c = _read("src/code/game/g_combat.c")
    main_c = _read("src/code/game/g_main.c")
    factory_c = _read("src/code/game/g_factory.c")

    init_body = _function_body(config_c, "void G_InitKnockbackConfig( void )")
    for expected in (
        'g_knockbackConfig.gauntlet = G_ReadKnockbackCvar( &g_knockback_g, DEFAULT_KNOCKBACK_G, "g_knockback_g" );',
        'g_knockbackConfig.machinegun = G_ReadKnockbackCvar( &g_knockback_mg, DEFAULT_KNOCKBACK_MG, "g_knockback_mg" );',
        'g_knockbackConfig.shotgun = G_ReadKnockbackCvar( &g_knockback_sg, DEFAULT_KNOCKBACK_SG, "g_knockback_sg" );',
        'g_knockbackConfig.grenadeLauncher = G_ReadKnockbackCvar( &g_knockback_gl, DEFAULT_KNOCKBACK_GL, "g_knockback_gl" );',
        'g_knockbackConfig.rocketLauncher = G_ReadKnockbackCvar( &g_knockback_rl, DEFAULT_KNOCKBACK_RL, "g_knockback_rl" );',
        'g_knockbackConfig.rocketLauncherSelf = G_ReadKnockbackCvar( &g_knockback_rl_self, DEFAULT_KNOCKBACK_RL_SELF, "g_knockback_rl_self" );',
        'g_knockbackConfig.lightningGun = G_ReadKnockbackCvar( &g_knockback_lg, DEFAULT_KNOCKBACK_LG, "g_knockback_lg" );',
        'g_knockbackConfig.railgun = G_ReadKnockbackCvar( &g_knockback_rg, DEFAULT_KNOCKBACK_RG, "g_knockback_rg" );',
        'g_knockbackConfig.plasmagun = G_ReadKnockbackCvar( &g_knockback_pg, DEFAULT_KNOCKBACK_PG, "g_knockback_pg" );',
        'g_knockbackConfig.plasmagunSelf = G_ReadKnockbackCvar( &g_knockback_pg_self, DEFAULT_KNOCKBACK_PG_SELF, "g_knockback_pg_self" );',
    ):
        assert expected in init_body

    scale_body = _function_body(combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")
    for expected in (
        "case MOD_GAUNTLET:",
        "return g_knockbackConfig.gauntlet;",
        "case MOD_MACHINEGUN:",
        "return g_knockbackConfig.machinegun;",
        "case MOD_SHOTGUN:",
        "return g_knockbackConfig.shotgun;",
        "case MOD_GRENADE:",
        "return g_knockbackConfig.grenadeLauncher;",
        "case MOD_ROCKET:",
        "return selfInflicted ? g_knockbackConfig.rocketLauncherSelf : g_knockbackConfig.rocketLauncher;",
        "case MOD_PLASMA:",
        "return selfInflicted ? g_knockbackConfig.plasmagunSelf : g_knockbackConfig.plasmagun;",
        "case MOD_LIGHTNING:",
        "return g_knockbackConfig.lightningGun;",
        "case MOD_RAILGUN:",
        "return g_knockbackConfig.railgun;",
    ):
        assert expected in scale_body

    assert "knockbackScale = G_KnockbackScaleForMOD( mod, selfInflicted );" in combat_c
    assert "knockbackValue *= knockbackScale;" in combat_c
    assert "G_Config_UpdateCvars();" in _function_body(main_c, "void G_UpdateCvars( void )")
    assert "G_UpdateKnockbackConfig();" in _function_body(main_c, "void G_UpdateCvars( void )")
    assert "G_UpdateKnockbackConfig();" in _function_body(factory_c, "static void Factory_RefreshMatchConfig( void )")


def test_second_ten_knockback_cvar_table_matches_retail_defaults_and_flags() -> None:
    main_c = _read("src/code/game/g_main.c")
    config_c = _read("src/game/g_config.c")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    assert '{ &g_knockback, "g_knockback", "1000", CVAR_GAMERULE, 0, qtrue' in main_c
    for expected in (
        "#define DEFAULT_KNOCKBACK_BFG               1",
        "#define DEFAULT_KNOCKBACK_CG                1",
        "#define DEFAULT_KNOCKBACK_GH                -5",
        "#define DEFAULT_KNOCKBACK_HMG               1",
        "#define DEFAULT_KNOCKBACK_NG                1",
        "#define DEFAULT_KNOCKBACK_PL                1",
        "#define DEFAULT_KNOCKBACK_VERTICAL          24",
        "#define DEFAULT_KNOCKBACK_VERTICAL_SELF     24",
        "#define DEFAULT_KNOCKBACK_CRIPPLE           0",
    ):
        assert expected in config_c

    for expected in (
        '{ &g_knockback_bfg,        "g_knockback_bfg",        STRINGIZE( DEFAULT_KNOCKBACK_BFG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_gh,         "g_knockback_gh",         STRINGIZE( DEFAULT_KNOCKBACK_GH ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_ng,         "g_knockback_ng",         STRINGIZE( DEFAULT_KNOCKBACK_NG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_pl,         "g_knockback_pl",         STRINGIZE( DEFAULT_KNOCKBACK_PL ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_cg,         "g_knockback_cg",         STRINGIZE( DEFAULT_KNOCKBACK_CG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_hmg,        "g_knockback_hmg",        STRINGIZE( DEFAULT_KNOCKBACK_HMG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE,',
        '{ &g_knockback_z,          "g_knockback_z",          STRINGIZE( DEFAULT_KNOCKBACK_VERTICAL ), CVAR_GAMERULE,',
        '{ &g_knockback_z_self,     "g_knockback_z_self",     STRINGIZE( DEFAULT_KNOCKBACK_VERTICAL_SELF ), CVAR_GAMERULE,',
        '{ &g_knockback_cripple,    "g_knockback_cripple",    STRINGIZE( DEFAULT_KNOCKBACK_CRIPPLE ), CVAR_GAMERULE,',
    ):
        assert expected in config_c

    retail_rows = {
        "g_knockback": ('1008e614  char const (* data_1008e614)[0xc] = data_10086bd8 {"g_knockback"}', 'data_1008747c {"1000"}', "00 00 10 00"),
        "g_knockback_bfg": ('1008e62c  char const (* data_1008e62c)[0x10] = data_10086bc8 {"g_knockback_bfg"}', "data_1007d1d8", "00 00 14 00"),
        "g_knockback_gh": ('1008e68c  char const (* data_1008e68c)[0xf] = data_10086b98 {"g_knockback_gh"}', "0x10086b94", "00 00 14 00"),
        "g_knockback_ng": ('1008e704  char const (* data_1008e704)[0xf] = data_10086b34 {"g_knockback_ng"}', "data_1007d1d8", "00 00 14 00"),
        "g_knockback_pl": ('1008e74c  char const (* data_1008e74c)[0xf] = data_10086b0c {"g_knockback_pl"}', "data_1007d1d8", "00 00 14 00"),
        "g_knockback_cg": ('1008e644  char const (* data_1008e644)[0xf] = data_10086bb8 {"g_knockback_cg"}', "data_1007d1d8", "00 00 14 00"),
        "g_knockback_hmg": ('1008e6bc  char const (* data_1008e6bc)[0x10] = data_10086b6c {"g_knockback_hmg"}', "data_1007d1d8", "00 00 14 00"),
        "g_knockback_z": ('1008e7c4  char const (* data_1008e7c4)[0xe] = data_10086abc {"g_knockback_z"}', "0x10086ab8", "00 00 10 00"),
        "g_knockback_z_self": ('1008e7dc  char const (* data_1008e7dc)[0x13] = data_10086aa4 {"g_knockback_z_self"}', "0x10086ab8", "00 00 10 00"),
        "g_knockback_cripple": ('1008e65c  char const (* data_1008e65c)[0x14] = data_1008535c {"g_knockback_cripple"}', "data_1007d0a8", "00 00 10 00"),
    }
    for marker, default_marker, flags_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert flags_marker in row_block

    for expected in (
        "1007d0a8  data_1007d0a8:",
        "1007d0a8                          30 00 00 00",
        "1007d1d8  data_1007d1d8:",
        "1007d1d8                                                                          31 00 00 00",
        '1008535c  char const data_1008535c[0x14] = "g_knockback_cripple", 0',
        '10086aa4  char const data_10086aa4[0x13] = "g_knockback_z_self", 0',
        "10086ab7                                                                       00 32 34 00 00",
        '10086abc  char const data_10086abc[0xe] = "g_knockback_z", 0',
        '10086b0c  char const data_10086b0c[0xf] = "g_knockback_pl", 0',
        '10086b34  char const data_10086b34[0xf] = "g_knockback_ng", 0',
        '10086b6c  char const data_10086b6c[0x10] = "g_knockback_hmg", 0',
        "10086b93                                                           00 2d 35 00 00",
        '10086b98  char const data_10086b98[0xf] = "g_knockback_gh", 0',
        '10086bb8  char const data_10086bb8[0xf] = "g_knockback_cg", 0',
        '10086bc8  char const data_10086bc8[0x10] = "g_knockback_bfg", 0',
        '10086bd8  char const data_10086bd8[0xc] = "g_knockback", 0',
        '1008747c  char const data_1008747c[0x5] = "1000", 0',
    ):
        assert expected in qagame_strings


def test_second_ten_knockback_cvars_keep_retail_combat_wiring() -> None:
    config_c = _read("src/game/g_config.c")
    combat_c = _read("src/code/game/g_combat.c")

    init_body = _function_body(config_c, "void G_InitKnockbackConfig( void )")
    for expected in (
        'g_knockbackConfig.bfg = G_ReadKnockbackCvar( &g_knockback_bfg, DEFAULT_KNOCKBACK_BFG, "g_knockback_bfg" );',
        'g_knockbackConfig.grapplingHook = G_ReadKnockbackCvar( &g_knockback_gh, DEFAULT_KNOCKBACK_GH, "g_knockback_gh" );',
        'g_knockbackConfig.nailgun = G_ReadKnockbackCvar( &g_knockback_ng, DEFAULT_KNOCKBACK_NG, "g_knockback_ng" );',
        'g_knockbackConfig.proximityLauncher = G_ReadKnockbackCvar( &g_knockback_pl, DEFAULT_KNOCKBACK_PL, "g_knockback_pl" );',
        'g_knockbackConfig.chaingun = G_ReadKnockbackCvar( &g_knockback_cg, DEFAULT_KNOCKBACK_CG, "g_knockback_cg" );',
        'g_knockbackConfig.heavyMachinegun = G_ReadKnockbackCvar( &g_knockback_hmg, DEFAULT_KNOCKBACK_HMG, "g_knockback_hmg" );',
        'g_knockbackConfig.vertical = G_ReadKnockbackCvar( &g_knockback_z, DEFAULT_KNOCKBACK_VERTICAL, "g_knockback_z" );',
        'g_knockbackConfig.verticalSelf = G_ReadKnockbackCvar( &g_knockback_z_self, DEFAULT_KNOCKBACK_VERTICAL_SELF, "g_knockback_z_self" );',
        'g_knockbackConfig.cripple = G_ReadKnockbackCvar( &g_knockback_cripple, DEFAULT_KNOCKBACK_CRIPPLE, "g_knockback_cripple" );',
    ):
        assert expected in init_body

    scale_body = _function_body(combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")
    for expected in (
        "case MOD_HMG:",
        "return g_knockbackConfig.heavyMachinegun;",
        "case MOD_BFG:",
        "case MOD_BFG_SPLASH:",
        "return g_knockbackConfig.bfg;",
        "case MOD_GRAPPLE:",
        "return g_knockbackConfig.grapplingHook;",
        "case MOD_NAIL:",
        "return g_knockbackConfig.nailgun;",
        "case MOD_CHAINGUN:",
        "return g_knockbackConfig.chaingun;",
        "case MOD_PROXIMITY_MINE:",
        "return g_knockbackConfig.proximityLauncher;",
    ):
        assert expected in scale_body

    vertical_body = _function_body(combat_c, "static float G_KnockbackVerticalBoost( qboolean selfInflicted )")
    cripple_body = _function_body(combat_c, "static float G_ApplyKnockbackCripple( gentity_t *targ, float knockbackValue, int dflags, float *outPenalty )")

    assert "return selfInflicted ? g_knockbackConfig.verticalSelf : g_knockbackConfig.vertical;" in vertical_body
    assert "if ( g_knockbackConfig.cripple <= 0.0f || !targ || !targ->client ) {" in cripple_body
    assert "scale -= g_knockbackConfig.cripple;" in cripple_body
    assert "scale -= g_knockbackConfig.cripple * deficitFraction;" in cripple_body
    assert "knockbackValue = G_ApplyKnockbackCripple( targ, knockbackValue, dflags, &cripplePenalty );" in combat_c
    assert "float verticalBoost = G_KnockbackVerticalBoost( selfInflicted );" in combat_c
    assert "VectorScale (dir, g_knockback.value * knockbackValue / mass, kvel);" in combat_c


def test_first_ten_damage_cvar_table_matches_retail_defaults_and_flags() -> None:
    main_c = _read("src/code/game/g_main.c")
    q_shared_h = _read("src/code/game/q_shared.h")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    assert "#define CVAR_GAMERULE\t0x100000" in q_shared_h
    assert "#define GAME_CVAR_FLAG_RETAIL_40000\t0x00040000" in main_c
    for expected in (
        '{ &g_damage_bfg, "g_damage_bfg", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_cg, "g_damage_cg", "8", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_damage_g, "g_damage_g", "50", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_gh, "g_damage_gh", "10", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_damage_hmg, "g_damage_hmg", "8", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_gl, "g_damage_gl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_lg, "g_damage_lg", "6", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_lg_falloff, "g_damage_lg_falloff", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_damage_mg, "g_damage_mg", "5", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_ng, "g_damage_ng", "12", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
    ):
        assert expected in main_c

    retail_rows = {
        "g_damage_bfg": ('1008dd44  char const (* data_1008dd44)[0xd] = data_10087308 {"g_damage_bfg"}', "data_1007e154"),
        "g_damage_cg": ('1008dd5c  char const (* data_1008dd5c)[0xc] = data_100872fc {"g_damage_cg"}', "data_1007e004"),
        "g_damage_g": ('1008dd74  char const (* data_1008dd74)[0xb] = data_100872f0 {"g_damage_g"}', "data_1007e1fc"),
        "g_damage_gh": ('1008dd8c  char const (* data_1008dd8c)[0xc] = data_100872e4 {"g_damage_gh"}', "data_1007e194"),
        "g_damage_hmg": ('1008dda4  char const (* data_1008dda4)[0xd] = data_100872d4 {"g_damage_hmg"}', "data_1007e004"),
        "g_damage_gl": ('1008ddbc  char const (* data_1008ddbc)[0xc] = data_100872c8 {"g_damage_gl"}', "data_1007e154"),
        "g_damage_lg": ('1008ddd4  char const (* data_1008ddd4)[0xc] = data_100872bc {"g_damage_lg"}', "0x100872b8"),
        "g_damage_lg_falloff": ('1008ddec  char const (* data_1008ddec)[0x14] = data_100872a4 {"g_damage_lg_falloff"}', "data_1007d0a8"),
        "g_damage_mg": ('1008de04  char const (* data_1008de04)[0xc] = data_10087298 {"g_damage_mg"}', "0x10087340"),
        "g_damage_ng": ('1008de1c  char const (* data_1008de1c)[0xc] = data_1008728c {"g_damage_ng"}', "0x10087288"),
    }
    for marker, default_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert "00 00 14 00" in row_block

    for expected in (
        "1007d0a8  data_1007d0a8:",
        "1007d0a8                          30 00 00 00",
        "1007e004  data_1007e004:",
        "1007e004              38 00 00 00",
        "1007e154  data_1007e154:",
        "1007e154                                                              31 30 30 00",
        "1007e194  data_1007e194:",
        "1007e194                                                              31 30 00 00",
        "1007e1fc  data_1007e1fc:",
        "1007e1fc                                                                                      35 30 00 00",
        "10087288                          31 32 00 00",
        '1008728c  char const data_1008728c[0xc] = "g_damage_ng", 0',
        '10087298  char const data_10087298[0xc] = "g_damage_mg", 0',
        '100872a4  char const data_100872a4[0x14] = "g_damage_lg_falloff", 0',
        "100872b8                                                                          36 00 00 00",
        '100872bc  char const data_100872bc[0xc] = "g_damage_lg", 0',
        '100872c8  char const data_100872c8[0xc] = "g_damage_gl", 0',
        '100872d4  char const data_100872d4[0xd] = "g_damage_hmg", 0',
        '100872e4  char const data_100872e4[0xc] = "g_damage_gh", 0',
        '100872f0  char const data_100872f0[0xb] = "g_damage_g", 0',
        '100872fc  char const data_100872fc[0xc] = "g_damage_cg", 0',
        '10087308  char const data_10087308[0xd] = "g_damage_bfg", 0',
        "10087340  35 00 00 00",
    ):
        assert expected in qagame_strings


def test_first_ten_damage_cvars_keep_retail_weapon_wiring() -> None:
    main_c = _read("src/code/game/g_main.c")
    weapon_c = _read("src/code/game/g_weapon.c")
    missile_c = _read("src/code/game/g_missile.c")
    combat_c = _read("src/code/game/g_combat.c")
    g_local_h = _read("src/code/game/g_local.h")
    config_c = _read("src/game/g_config.c")
    factory_c = _read("src/code/game/g_factory.c")

    init_body = _function_body(main_c, "void G_InitWeaponConfig( void )")
    for expected in (
        'g_weaponConfig.gauntletDamage = G_ReadWeaponCvar( &g_damage_g, 50, "g_damage_g" );',
        'g_weaponConfig.machinegunDamage = G_ReadWeaponCvar( &g_damage_mg, 5, "g_damage_mg" );',
        'g_weaponConfig.heavyMachinegunDamage = G_ReadWeaponCvar( &g_damage_hmg, 8, "g_damage_hmg" );',
        'g_weaponConfig.chaingunDamage = G_ReadWeaponCvar( &g_damage_cg, 8, "g_damage_cg" );',
        'g_weaponConfig.grenadeDamage = G_ReadWeaponCvar( &g_damage_gl, 100, "g_damage_gl" );',
        'g_weaponConfig.lightningDamage = G_ReadWeaponCvar( &g_damage_lg, 6, "g_damage_lg" );',
        'g_weaponConfig.lightningFalloffDamage = G_ReadWeaponCvarNonNegative( &g_damage_lg_falloff, 0, "g_damage_lg_falloff" );',
        'g_weaponConfig.bfgDamage = G_ReadWeaponCvar( &g_damage_bfg, 100, "g_damage_bfg" );',
        'g_weaponConfig.grappleDamage = G_ReadWeaponCvar( &g_damage_gh, 10, "g_damage_gh" );',
        'g_weaponConfig.nailgunDamage = G_ReadWeaponCvar( &g_damage_ng, 12, "g_damage_ng" );',
    ):
        assert expected in init_body

    clamp_body = _function_body(combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    for expected in (
        "case MOD_GAUNTLET:",
        "configuredDamage = g_weaponConfig.gauntletDamage;",
        "case MOD_MACHINEGUN:",
        "configuredDamage = g_weaponConfig.machinegunDamage;",
        "case MOD_HMG:",
        "configuredDamage = g_weaponConfig.heavyMachinegunDamage;",
        "case MOD_CHAINGUN:",
        "configuredDamage = g_weaponConfig.chaingunDamage;",
        "case MOD_GRENADE:",
        "configuredDamage = g_weaponConfig.grenadeDamage;",
        "case MOD_LIGHTNING:",
        "case MOD_LIGHTNING_DISCHARGE:",
        "configuredDamage = g_weaponConfig.lightningDamage;",
        "case MOD_BFG:",
        "configuredDamage = g_weaponConfig.bfgDamage;",
        "case MOD_GRAPPLE:",
        "configuredDamage = g_weaponConfig.grappleDamage;",
        "case MOD_NAIL:",
        "configuredDamage = g_weaponConfig.nailgunDamage;",
    ):
        assert expected in clamp_body
    assert "machinegunTeamDamage" not in g_local_h
    assert "g_damage_mg_team" not in main_c

    for expected in (
        "damage = g_weaponConfig.gauntletDamage * s_quadFactor;",
        "#define\tMACHINEGUN_DAMAGE\t(g_weaponConfig.machinegunDamage)",
        "#define\tHEAVY_MACHINEGUN_DAMAGE\t(g_weaponConfig.heavyMachinegunDamage)",
        "#define\tCHAINGUN_DAMAGE\t\t(g_weaponConfig.chaingunDamage)",
        "baseDamage = g_weaponConfig.lightningDamage;",
        "falloffDamage = g_weaponConfig.lightningFalloffDamage;",
        "damage = g_weaponConfig.lightningDamage;",
        "dischargeDamage = dischargeAmmo * g_weaponConfig.lightningDamage;",
        "m->damage *= s_quadFactor;",
        "hook->damage *= s_quadFactor;",
    ):
        assert expected in weapon_c

    for expected in (
        "bolt->damage = g_weaponConfig.grenadeDamage;",
        "bolt->damage = g_weaponConfig.bfgDamage;",
        "hook->damage = g_weaponConfig.grappleDamage;",
        "bolt->damage = g_weaponConfig.nailgunDamage;",
    ):
        assert expected in missile_c

    custom_mask_body = _function_body(config_c, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
    for expected in (
        "g_weaponConfig.gauntletDamage != 50",
        "g_weaponConfig.machinegunDamage != 5",
        "g_weaponConfig.grenadeDamage != 100",
        "g_weaponConfig.lightningDamage != 6",
        "g_weaponConfig.lightningFalloffDamage != 0",
        "g_weaponConfig.bfgDamage != 100",
        "g_weaponConfig.grappleDamage != 10",
        "g_weaponConfig.nailgunDamage != 12",
        "g_weaponConfig.chaingunDamage != 8",
    ):
        assert expected in custom_mask_body

    assert "G_UpdateWeaponConfig();" in _function_body(main_c, "void G_UpdateCvars( void )")
    assert "G_UpdateWeaponConfig();" in _function_body(factory_c, "static void Factory_RefreshMatchConfig( void )")
    assert "damage = G_ClampModDamage( damage, mod, attacker );" in combat_c


def test_second_ten_damage_cvar_table_matches_retail_defaults_and_flags() -> None:
    main_c = _read("src/code/game/g_main.c")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    for expected in (
        '{ &g_damage_pg, "g_damage_pg", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_pl, "g_damage_pl", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_damage_rg, "g_damage_rg", "80", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_rl, "g_damage_rl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_sg, "g_damage_sg", "5", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_damage_sg_falloff, "g_damage_sg_falloff", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_damage_sg_outer, "g_damage_sg_outer", "5", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_splashDamage_gl, "g_splashdamage_gl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_splashDamage_pg, "g_splashdamage_pg", "15", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_splashDamage_rl, "g_splashdamage_rl", "84", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
    ):
        assert expected in main_c

    retail_rows = {
        "g_damage_pg": ('1008de34  char const (* data_1008de34)[0xc] = data_1008727c {"g_damage_pg"}', "data_1007e1ac"),
        "g_damage_pl": ('1008de4c  char const (* data_1008de4c)[0xc] = data_10087270 {"g_damage_pl"}', "data_1007d0a8"),
        "g_damage_rg": ('1008de64  char const (* data_1008de64)[0xc] = data_10087264 {"g_damage_rg"}', "0x10087260"),
        "g_damage_rl": ('1008de7c  char const (* data_1008de7c)[0xc] = data_10087254 {"g_damage_rl"}', "data_1007e154"),
        "g_damage_sg": ('1008de94  char const (* data_1008de94)[0xc] = data_10087248 {"g_damage_sg"}', "0x10087340"),
        "g_damage_sg_falloff": ('1008deac  char const (* data_1008deac)[0x14] = data_10087234 {"g_damage_sg_falloff"}', "data_1007d0a8"),
        "g_damage_sg_outer": ('1008dec4  char const (* data_1008dec4)[0x12] = data_10087220 {"g_damage_sg_outer"}', "0x10087340"),
        "g_splashdamage_gl": ('1008f1b4  char const (* data_1008f1b4)[0x12] = data_10086228 {"g_splashdamage_gl"}', "data_1007e154"),
        "g_splashdamage_pg": ('1008f1cc  char const (* data_1008f1cc)[0x12] = data_10086214 {"g_splashdamage_pg"}', "data_1007e1d8"),
        "g_splashdamage_rl": ('1008f1fc  char const (* data_1008f1fc)[0x12] = data_100861ec {"g_splashdamage_rl"}', "0x100861e8"),
    }
    for marker, default_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert "00 00 14 00" in row_block

    for expected in (
        "1007d0a8                          30 00 00 00",
        "1007e154                                                              31 30 30 00",
        "1007e1ac                                      32 30 00 00",
        "1007e1d8                                                                          31 35 00 00",
        "100861e5                 00 00 00 38 34 00 00",
        '100861ec  char const data_100861ec[0x12] = "g_splashdamage_rl", 0',
        '10086214  char const data_10086214[0x12] = "g_splashdamage_pg", 0',
        '10086228  char const data_10086228[0x12] = "g_splashdamage_gl", 0',
        '10087220  char const data_10087220[0x12] = "g_damage_sg_outer", 0',
        '10087234  char const data_10087234[0x14] = "g_damage_sg_falloff", 0',
        '10087248  char const data_10087248[0xc] = "g_damage_sg", 0',
        '10087254  char const data_10087254[0xc] = "g_damage_rl", 0',
        "10087260  38 30 00 00",
        '10087264  char const data_10087264[0xc] = "g_damage_rg", 0',
        '10087270  char const data_10087270[0xc] = "g_damage_pl", 0',
        '1008727c  char const data_1008727c[0xc] = "g_damage_pg", 0',
        "10087340  35 00 00 00",
    ):
        assert expected in qagame_strings


def test_second_ten_damage_cvars_keep_retail_weapon_wiring() -> None:
    main_c = _read("src/code/game/g_main.c")
    weapon_c = _read("src/code/game/g_weapon.c")
    missile_c = _read("src/code/game/g_missile.c")
    combat_c = _read("src/code/game/g_combat.c")
    config_c = _read("src/game/g_config.c")
    factory_c = _read("src/code/game/g_factory.c")

    init_body = _function_body(main_c, "void G_InitWeaponConfig( void )")
    for expected in (
        'g_weaponConfig.shotgunDamage = G_ReadWeaponCvar( &g_damage_sg, 5, "g_damage_sg" );',
        'g_weaponConfig.shotgunOuterDamage = G_ReadWeaponCvar( &g_damage_sg_outer, 5, "g_damage_sg_outer" );',
        'g_weaponConfig.shotgunFalloffDamage = G_ReadWeaponCvarNonNegative( &g_damage_sg_falloff, 0, "g_damage_sg_falloff" );',
        'g_weaponConfig.grenadeSplashDamage = G_ReadWeaponCvar( &g_splashDamage_gl, 100, "g_splashdamage_gl" );',
        'g_weaponConfig.rocketDamage = G_ReadWeaponCvar( &g_damage_rl, 100, "g_damage_rl" );',
        'g_weaponConfig.rocketSplashDamage = G_ReadWeaponCvar( &g_splashDamage_rl, 84, "g_splashdamage_rl" );',
        'g_weaponConfig.plasmaDamage = G_ReadWeaponCvar( &g_damage_pg, 20, "g_damage_pg" );',
        'g_weaponConfig.plasmaSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pg, 15, "g_splashdamage_pg" );',
        'g_weaponConfig.railgunDamage = G_ReadWeaponCvar( &g_damage_rg, 80, "g_damage_rg" );',
        'g_weaponConfig.proximityLauncherDamage = G_ReadWeaponCvarNonNegative( &g_damage_pl, 0, "g_damage_pl" );',
    ):
        assert expected in init_body

    clamp_body = _function_body(combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    for expected in (
        "case MOD_SHOTGUN:",
        "configuredDamage = g_weaponConfig.shotgunDamage;",
        "case MOD_GRENADE_SPLASH:",
        "configuredDamage = g_weaponConfig.grenadeSplashDamage;",
        "case MOD_ROCKET:",
        "configuredDamage = g_weaponConfig.rocketDamage;",
        "case MOD_ROCKET_SPLASH:",
        "configuredDamage = g_weaponConfig.rocketSplashDamage;",
        "case MOD_PLASMA:",
        "configuredDamage = g_weaponConfig.plasmaDamage;",
        "case MOD_PLASMA_SPLASH:",
        "configuredDamage = g_weaponConfig.plasmaSplashDamage;",
        "case MOD_RAILGUN:",
        "configuredDamage = g_weaponConfig.railgunDamage;",
        "case MOD_PROXIMITY_MINE:",
        "g_weaponConfig.proximityLauncherDamage > g_weaponConfig.proximityLauncherSplashDamage",
    ):
        assert expected in clamp_body

    for expected in (
        "#define\tDEFAULT_SHOTGUN_DAMAGE\t(g_weaponConfig.shotgunDamage)",
        "#define\tDEFAULT_SHOTGUN_OUTER_DAMAGE\t(g_weaponConfig.shotgunOuterDamage)",
        "falloffDamage = g_weaponConfig.shotgunFalloffDamage;",
        "damage = g_weaponConfig.railgunDamage * s_quadFactor;",
    ):
        assert expected in weapon_c

    for expected in (
        "bolt->damage = g_weaponConfig.plasmaDamage;",
        "bolt->splashDamage = g_weaponConfig.plasmaSplashDamage;",
        "bolt->damage = g_weaponConfig.grenadeDamage;",
        "bolt->splashDamage = g_weaponConfig.grenadeSplashDamage;",
        "bolt->damage = g_weaponConfig.rocketDamage;",
        "bolt->splashDamage = g_weaponConfig.rocketSplashDamage;",
        "bolt->damage = g_weaponConfig.proximityLauncherDamage;",
    ):
        assert expected in missile_c

    custom_mask_body = _function_body(config_c, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
    for expected in (
        "g_weaponConfig.shotgunDamage != 5",
        "g_weaponConfig.shotgunOuterDamage != 5",
        "g_weaponConfig.shotgunFalloffDamage != 0",
        "g_weaponConfig.grenadeSplashDamage != 100",
        "g_weaponConfig.rocketDamage != 100",
        "g_weaponConfig.rocketSplashDamage != 84",
        "g_weaponConfig.plasmaDamage != 20",
        "g_weaponConfig.plasmaSplashDamage != 15",
        "g_weaponConfig.railgunDamage != 80",
        "g_weaponConfig.proximityLauncherDamage != 0",
    ):
        assert expected in custom_mask_body

    assert "G_UpdateWeaponConfig();" in _function_body(main_c, "void G_UpdateCvars( void )")
    assert "G_UpdateWeaponConfig();" in _function_body(factory_c, "static void Factory_RefreshMatchConfig( void )")
    assert "damage = G_ClampModDamage( damage, mod, attacker );" in combat_c


def test_third_ten_damage_cvar_table_matches_retail_defaults_and_flags() -> None:
    main_c = _read("src/code/game/g_main.c")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    for expected in (
        '{ &g_splashDamage_bfg, "g_splashdamage_bfg", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_splashDamage_pl, "g_splashdamage_pl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_splashRadius_bfg, "g_splashradius_bfg", "80", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_splashRadius_gl, "g_splashradius_gl", "150", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_splashRadius_pg, "g_splashradius_pg", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_splashRadius_pl, "g_splashradius_pl", "150", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_splashRadius_rl, "g_splashradius_rl", "120", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue }',
        '{ &g_range_lg_falloff, "g_range_lg_falloff", "768", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_range_sg_falloff, "g_range_sg_falloff", "768", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_rocketsplashOffset, "g_rocketsplashOffset", "-10.0", CVAR_GAMERULE, 0, qtrue, qfalse,',
    ):
        assert expected in main_c

    retail_rows = {
        "g_splashdamage_bfg": ('1008f19c  char const (* data_1008f19c)[0x13] = data_1008623c {"g_splashdamage_bfg"}', "data_1007e154", "00 00 14 00"),
        "g_splashdamage_pl": ('1008f1e4  char const (* data_1008f1e4)[0x12] = data_10086200 {"g_splashdamage_pl"}', "data_1007e154", "00 00 14 00"),
        "g_splashradius_bfg": ('1008f22c  char const (* data_1008f22c)[0x13] = data_100861b4 {"g_splashradius_bfg"}', "0x10087260", "00 00 14 00"),
        "g_splashradius_gl": ('1008f244  char const (* data_1008f244)[0x12] = data_100861a0 {"g_splashradius_gl"}', "0x10086414", "00 00 14 00"),
        "g_splashradius_pg": ('1008f25c  char const (* data_1008f25c)[0x12] = data_1008618c {"g_splashradius_pg"}', "data_1007e1ac", "00 00 14 00"),
        "g_splashradius_pl": ('1008f274  char const (* data_1008f274)[0x12] = data_10086178 {"g_splashradius_pl"}', "0x10086414", "00 00 14 00"),
        "g_splashradius_rl": ('1008f28c  char const (* data_1008f28c)[0x12] = data_10086164 {"g_splashradius_rl"}', "0x100869c8", "00 00 14 00"),
        "g_range_lg_falloff": ('1008ec5c  char const (* data_1008ec5c)[0x13] = data_1008672c {"g_range_lg_falloff"}', "0x10086728", "00 00 10 00"),
        "g_range_sg_falloff": ('1008ec74  char const (* data_1008ec74)[0x13] = data_10086714 {"g_range_sg_falloff"}', "0x10086728", "00 00 10 00"),
        "g_rocketsplashOffset": ('1008ed64  char const (* data_1008ed64)[0x15] = data_10086648 {"g_rocketsplashOffset"}', 'data_10086640 {"-10.0"}', "00 00 10 00"),
    }
    for marker, default_marker, flags_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert flags_marker in row_block

    for expected in (
        "1007e154                                                              31 30 30 00",
        "1007e1ac                                      32 30 00 00",
        "10086164  char const data_10086164[0x12] = \"g_splashradius_rl\", 0",
        "10086178  char const data_10086178[0x12] = \"g_splashradius_pl\", 0",
        "1008618c  char const data_1008618c[0x12] = \"g_splashradius_pg\", 0",
        "100861a0  char const data_100861a0[0x12] = \"g_splashradius_gl\", 0",
        "100861b4  char const data_100861b4[0x13] = \"g_splashradius_bfg\", 0",
        "10086200  char const data_10086200[0x12] = \"g_splashdamage_pl\", 0",
        "1008623c  char const data_1008623c[0x13] = \"g_splashdamage_bfg\", 0",
        '10086640  char const data_10086640[0x6] = "-10.0", 0',
        '10086648  char const data_10086648[0x15] = "g_rocketsplashOffset", 0',
        "10086727                       00 37 36 38 00",
        '10086714  char const data_10086714[0x13] = "g_range_sg_falloff", 0',
        '1008672c  char const data_1008672c[0x13] = "g_range_lg_falloff", 0',
        "100869c8                          31 32 30 00",
        "10087260  38 30 00 00",
    ):
        assert expected in qagame_strings


def test_third_ten_damage_cvars_keep_retail_weapon_wiring() -> None:
    main_c = _read("src/code/game/g_main.c")
    weapon_c = _read("src/code/game/g_weapon.c")
    missile_c = _read("src/code/game/g_missile.c")
    config_c = _read("src/game/g_config.c")
    factory_c = _read("src/code/game/g_factory.c")

    init_body = _function_body(main_c, "void G_InitWeaponConfig( void )")
    for expected in (
        'g_weaponConfig.shotgunFalloffRange = G_ReadWeaponCvarNonNegative( &g_range_sg_falloff, 768, "g_range_sg_falloff" );',
        'g_weaponConfig.grenadeSplashRadius = G_ReadWeaponCvar( &g_splashRadius_gl, 150, "g_splashradius_gl" );',
        'g_weaponConfig.rocketSplashRadius = G_ReadWeaponCvar( &g_splashRadius_rl, 120, "g_splashradius_rl" );',
        'g_weaponConfig.rocketSplashOffset = G_ReadWeaponCvarRaw( &g_rocketsplashOffset, -10, "g_rocketsplashOffset" );',
        'g_weaponConfig.plasmaSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pg, 20, "g_splashradius_pg" );',
        'g_weaponConfig.lightningFalloffRange = G_ReadWeaponCvarNonNegative( &g_range_lg_falloff, 768, "g_range_lg_falloff" );',
        'g_weaponConfig.bfgSplashDamage = G_ReadWeaponCvar( &g_splashDamage_bfg, 100, "g_splashdamage_bfg" );',
        'g_weaponConfig.bfgSplashRadius = G_ReadWeaponCvar( &g_splashRadius_bfg, 80, "g_splashradius_bfg" );',
        'g_weaponConfig.proximityLauncherSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pl, 100, "g_splashdamage_pl" );',
        'g_weaponConfig.proximityLauncherSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pl, 150, "g_splashradius_pl" );',
    ):
        assert expected in init_body

    for expected in (
        "falloffRange = g_weaponConfig.shotgunFalloffRange;",
        "falloffRange = g_weaponConfig.lightningFalloffRange;",
    ):
        assert expected in weapon_c

    for expected in (
        "bolt->splashDamage = g_weaponConfig.proximityLauncherSplashDamage;",
        "bolt->splashDamage = g_weaponConfig.bfgSplashDamage;",
        "bolt->splashRadius = g_weaponConfig.grenadeSplashRadius;",
        "bolt->splashRadius = g_weaponConfig.rocketSplashRadius;",
        "bolt->splashRadius = g_weaponConfig.plasmaSplashRadius;",
        "bolt->splashRadius = g_weaponConfig.bfgSplashRadius;",
        "bolt->splashRadius = g_weaponConfig.proximityLauncherSplashRadius;",
        "if ( haveNormal && g_splashdamageOffset.value != 0.0f ) {",
        "VectorMA( splashOrigin, g_splashdamageOffset.value, normal, splashOrigin );",
        "if ( ent->s.weapon == WP_ROCKET_LAUNCHER && g_weaponConfig.rocketSplashOffset != 0 ) {",
        "splashOffset = ( float )g_weaponConfig.rocketSplashOffset;",
    ):
        assert expected in missile_c

    custom_mask_body = _function_body(config_c, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
    for expected in (
        "g_weaponConfig.shotgunFalloffRange != 768",
        "g_weaponConfig.grenadeSplashRadius != 150",
        "g_weaponConfig.rocketSplashRadius != 120",
        "g_weaponConfig.rocketSplashOffset != -10",
        "g_weaponConfig.lightningFalloffRange != 768",
        "g_weaponConfig.plasmaSplashRadius != 20",
        "g_weaponConfig.bfgSplashDamage != 100",
        "g_weaponConfig.bfgSplashRadius != 80",
        "g_weaponConfig.proximityLauncherSplashDamage != 100",
        "g_weaponConfig.proximityLauncherSplashRadius != 150",
    ):
        assert expected in custom_mask_body

    assert "G_UpdateWeaponConfig();" in _function_body(main_c, "void G_UpdateCvars( void )")
    assert "G_UpdateWeaponConfig();" in _function_body(factory_c, "static void Factory_RefreshMatchConfig( void )")


def test_first_ten_velocity_acceleration_cvar_table_matches_retail_defaults_and_flags() -> None:
    main_c = _read("src/code/game/g_main.c")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    for expected in (
        '{ &g_accelFactor_bfg, "g_accelFactor_bfg", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_accelFactor_pg, "g_accelFactor_pg", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_accelFactor_rl, "g_accelFactor_rl", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_accelRate_bfg, "g_accelRate_bfg", "16", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_accelRate_pg, "g_accelRate_pg", "16", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_accelRate_rl, "g_accelRate_rl", "16", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_velocity_bfg, "g_velocity_bfg", "1800", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_velocity_gl, "g_velocity_gl", "700", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_velocity_pg, "g_velocity_pg", "2000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_velocity_rl, "g_velocity_rl", "1000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
    ):
        assert expected in main_c

    retail_rows = {
        "g_accelFactor_bfg": ('1008da5c  char const (* data_1008da5c)[0x12] = data_10087574 {"g_accelFactor_bfg"}', "data_1007d1d8", "00 00 14 00"),
        "g_accelFactor_pg": ('1008da74  char const (* data_1008da74)[0x11] = data_10087560 {"g_accelFactor_pg"}', "data_1007d1d8", "00 00 14 00"),
        "g_accelFactor_rl": ('1008da8c  char const (* data_1008da8c)[0x11] = data_1008754c {"g_accelFactor_rl"}', "data_1007d1d8", "00 00 14 00"),
        "g_accelRate_bfg": ('1008daa4  char const (* data_1008daa4)[0x10] = data_1008753c {"g_accelRate_bfg"}', "0x10087538", "00 00 10 00"),
        "g_accelRate_pg": ('1008dabc  char const (* data_1008dabc)[0xf] = data_10087528 {"g_accelRate_pg"}', "0x10087538", "00 00 10 00"),
        "g_accelRate_rl": ('1008dad4  char const (* data_1008dad4)[0xf] = data_10087518 {"g_accelRate_rl"}', "0x10087538", "00 00 10 00"),
        "g_velocity_bfg": ('1008f67c  char const (* data_1008f67c)[0xf] = data_10085e3c {"g_velocity_bfg"}', 'data_10085e34 {"1800"}', "00 00 14 00"),
        "g_velocity_gl": ('1008f6ac  char const (* data_1008f6ac)[0xe] = data_10085e14 {"g_velocity_gl"}', "0x10085e10", "00 00 14 00"),
        "g_velocity_pg": ('1008f6c4  char const (* data_1008f6c4)[0xe] = data_10085e00 {"g_velocity_pg"}', 'data_10086d78 {"2000"}', "00 00 14 00"),
        "g_velocity_rl": ('1008f6dc  char const (* data_1008f6dc)[0xe] = data_10085df0 {"g_velocity_rl"}', 'data_1008747c {"1000"}', "00 00 14 00"),
    }
    for marker, default_marker, flags_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert flags_marker in row_block

    for expected in (
        "1007d1d8                                                                          31 00 00 00",
        "10085df0  char const data_10085df0[0xe] = \"g_velocity_rl\", 0",
        "10085e00  char const data_10085e00[0xe] = \"g_velocity_pg\", 0",
        "10085e0e                                            00 00 37 30 30 00",
        "10085e14  char const data_10085e14[0xe] = \"g_velocity_gl\", 0",
        '10085e34  char const data_10085e34[0x5] = "1800", 0',
        "10085e3c  char const data_10085e3c[0xf] = \"g_velocity_bfg\", 0",
        '10086d78  char const data_10086d78[0x5] = "2000", 0',
        '1008747c  char const data_1008747c[0x5] = "1000", 0',
        "10087518  char const data_10087518[0xf] = \"g_accelRate_rl\", 0",
        "10087528  char const data_10087528[0xf] = \"g_accelRate_pg\", 0",
        "10087537                                                                       00 31 36 00 00",
        "1008753c  char const data_1008753c[0x10] = \"g_accelRate_bfg\", 0",
        "1008754c  char const data_1008754c[0x11] = \"g_accelFactor_rl\", 0",
        "10087560  char const data_10087560[0x11] = \"g_accelFactor_pg\", 0",
        "10087574  char const data_10087574[0x12] = \"g_accelFactor_bfg\", 0",
    ):
        assert expected in qagame_strings


def test_first_ten_velocity_acceleration_cvars_keep_retail_weapon_wiring() -> None:
    main_c = _read("src/code/game/g_main.c")
    missile_c = _read("src/code/game/g_missile.c")
    config_c = _read("src/game/g_config.c")
    factory_c = _read("src/code/game/g_factory.c")

    init_body = _function_body(main_c, "void G_InitWeaponConfig( void )")
    sync_rocket_body = _function_body(missile_c, "static void G_SynchronizeRocketConfig( gentity_t *bolt, vec3_t dir )")
    for expected in (
        'g_weaponConfig.grenadeSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gl, 700, "g_velocity_gl", 1 );',
        'g_weaponConfig.rocketSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_rl, 1000, "g_velocity_rl", 1 );',
        'g_weaponConfig.rocketAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_rl, 1.0f, "g_accelFactor_rl" );',
        'g_weaponConfig.rocketAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_rl, 16, "g_accelRate_rl" );',
        'g_weaponConfig.plasmaSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_pg, 2000, "g_velocity_pg", 1 );',
        'g_weaponConfig.plasmaAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_pg, 1.0f, "g_accelFactor_pg" );',
        'g_weaponConfig.plasmaAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_pg, 16, "g_accelRate_pg" );',
        'g_weaponConfig.bfgSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_bfg, 1800, "g_velocity_bfg", 1 );',
        'g_weaponConfig.bfgAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_bfg, 1.0f, "g_accelFactor_bfg" );',
        'g_weaponConfig.bfgAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_bfg, 16, "g_accelRate_bfg" );',
    ):
        assert expected in init_body

    for expected in (
        "bolt->speed = ( float )g_weaponConfig.grenadeSpeed;",
        "bolt->speed = ( float )g_weaponConfig.plasmaSpeed;",
        "bolt->speed = ( float )g_weaponConfig.bfgSpeed;",
        "VectorScale( ent->s.pos.trDelta, g_weaponConfig.rocketAccelerationFactor, ent->s.pos.trDelta );",
        "VectorScale( ent->s.pos.trDelta, g_weaponConfig.plasmaAccelerationFactor, ent->s.pos.trDelta );",
        "VectorScale( ent->s.pos.trDelta, g_weaponConfig.bfgAccelerationFactor, ent->s.pos.trDelta );",
        "ent->nextthink = level.time + G_GetMissileAccelerationThinkTime( g_weaponConfig.rocketAccelerationRate );",
        "ent->nextthink = level.time + G_GetMissileAccelerationThinkTime( g_weaponConfig.plasmaAccelerationRate );",
        "ent->nextthink = level.time + G_GetMissileAccelerationThinkTime( g_weaponConfig.bfgAccelerationRate );",
    ):
        assert expected in missile_c

    for expected in (
        "speed = ( float )g_weaponConfig.rocketSpeed;",
        "bolt->speed = speed;",
        "VectorScale( dir, speed, bolt->s.pos.trDelta );",
    ):
        assert expected in sync_rocket_body

    custom_mask_body = _function_body(config_c, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
    for expected in (
        "g_weaponConfig.grenadeSpeed != 700",
        "g_weaponConfig.rocketSpeed != 1000",
        "G_ConfigFloatDiffersFromDefault( g_weaponConfig.rocketAccelerationFactor, 1.0f )",
        "g_weaponConfig.rocketAccelerationRate != 16",
        "g_weaponConfig.plasmaSpeed != 2000",
        "G_ConfigFloatDiffersFromDefault( g_weaponConfig.plasmaAccelerationFactor, 1.0f )",
        "g_weaponConfig.plasmaAccelerationRate != 16",
        "g_weaponConfig.bfgSpeed != 1800",
        "G_ConfigFloatDiffersFromDefault( g_weaponConfig.bfgAccelerationFactor, 1.0f )",
        "g_weaponConfig.bfgAccelerationRate != 16",
    ):
        assert expected in custom_mask_body

    assert "G_UpdateWeaponConfig();" in _function_body(main_c, "void G_UpdateCvars( void )")
    assert "G_UpdateWeaponConfig();" in _function_body(factory_c, "static void Factory_RefreshMatchConfig( void )")


def test_first_ten_weapon_special_cvar_table_matches_retail_defaults_and_flags() -> None:
    main_c = _read("src/code/game/g_main.c")
    q_shared_h = _read("src/code/game/q_shared.h")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    assert "CVAR_TEMP\t\t\t256" in q_shared_h
    for expected in (
        '{ &g_velocity_gh, "g_velocity_gh", "1800", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_guidedRocket, "g_guidedRocket", "0", CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_lightningDischarge, "g_lightningDischarge", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_railJump, "g_railJump", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_gauntletSpeedFactor, "g_gauntletSpeedFactor", "1.0", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_headShotDamage_rg, "g_headShotDamage_rg", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_ironsights_mg, "g_ironsights_mg", "1.0", CVAR_TEMP | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailbounce, "g_nailbounce", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailbouncepercentage, "g_nailbouncepercentage", "65", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailcount, "g_nailcount", "10", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
    ):
        assert expected in main_c

    retail_rows = {
        "g_velocity_gh": ('1008f694  char const (* data_1008f694)[0xe] = data_10085e24 {"g_velocity_gh"}', 'data_10085e34 {"1800"}', "00 00 14 00"),
        "g_guidedRocket": ('1008e4f4  char const (* data_1008e4f4)[0xf] = data_10086cac {"g_guidedRocket"}', "data_1007d0a8", "00 00 10 00"),
        "g_lightningDischarge": ('1008e86c  char const (* data_1008e86c)[0x15] = data_100869fc {"g_lightningDischarge"}', "data_1007d0a8", "00 00 14 00"),
        "g_railJump": ('1008ec44  char const (* data_1008ec44)[0xb] = data_10086740 {"g_railJump"}', "data_1007d0a8", "00 00 14 00"),
        "g_gauntletSpeedFactor": ('1008e4ac  char const (* data_1008e4ac)[0x16] = data_10086ce4 {"g_gauntletSpeedFactor"}', "0x10086ce0", "00 00 10 00"),
        "g_headShotDamage_rg": ('1008e50c  char const (* data_1008e50c)[0x14] = data_10086c98 {"g_headShotDamage_rg"}', "data_1007d0a8", "00 00 14 00"),
        "g_ironsights_mg": ('1008e584  char const (* data_1008e584)[0x10] = data_10086c48 {"g_ironsights_mg"}', "0x10086ce0", "00 01 14 00"),
        "g_nailbounce": ('1008e98c  char const (* data_1008e98c)[0xd] = data_10086958 {"g_nailbounce"}', "data_1007d1d8", "00 00 14 00"),
        "g_nailbouncepercentage": ('1008e9a4  char const (* data_1008e9a4)[0x17] = data_10086940 {"g_nailbouncepercentage"}', "0x1008693c", "00 00 14 00"),
        "g_nailcount": ('1008e9bc  char const (* data_1008e9bc)[0xc] = data_10086930 {"g_nailcount"}', "data_1007e194", "00 00 14 00"),
    }
    for marker, default_marker, flags_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert flags_marker in row_block

    for expected in (
        "1007d0a8                          30 00 00 00",
        "1007d1d8                                                                          31 00 00 00",
        "1007e194                                                              31 30 00 00",
        '10085e24  char const data_10085e24[0xe] = "g_velocity_gh", 0',
        '10085e34  char const data_10085e34[0x5] = "1800", 0',
        '10086740  char const data_10086740[0xb] = "g_railJump", 0',
        '10086930  char const data_10086930[0xc] = "g_nailcount", 0',
        "1008693c                                                                                      36 35 00 00",
        '10086940  char const data_10086940[0x17] = "g_nailbouncepercentage", 0',
        '10086958  char const data_10086958[0xd] = "g_nailbounce", 0',
        '100869fc  char const data_100869fc[0x15] = "g_lightningDischarge", 0',
        '10086c48  char const data_10086c48[0x10] = "g_ironsights_mg", 0',
        '10086c98  char const data_10086c98[0x14] = "g_headShotDamage_rg", 0',
        '10086cac  char const data_10086cac[0xf] = "g_guidedRocket", 0',
        "10086ce0  31 2e 30 00",
        '10086ce4  char const data_10086ce4[0x16] = "g_gauntletSpeedFactor", 0',
    ):
        assert expected in qagame_strings


def test_first_ten_weapon_special_cvars_keep_retail_weapon_wiring() -> None:
    bg_public_h = _read("src/code/game/bg_public.h")
    g_config_c = _read("src/game/g_config.c")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_pmove_c = _read("src/code/game/g_pmove.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")

    init_body = _function_body(g_main_c, "void G_InitWeaponConfig( void )")
    config_mask_body = _function_body(g_config_c, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
    custom_mask_body = _function_body(g_main_c, "static uint64_t G_ComputeCustomSettingsMask( void )")
    sync_grapple_body = _function_body(g_missile_c, "static void G_SynchronizeGrappleConfig( gentity_t *hook, vec3_t dir )")
    fire_rocket_body = _function_body(g_missile_c, "gentity_t *fire_rocket (gentity_t *self, vec3_t start, vec3_t dir)")
    guided_rocket_body = _function_body(g_missile_c, "static void G_RunGuidedRocketThink( gentity_t *ent )")
    fire_nail_body = _function_body(g_missile_c, "gentity_t *fire_nail( gentity_t *self, vec3_t start, vec3_t forward, vec3_t right, vec3_t up )")
    nail_bounce_body = _function_body(g_missile_c, "static qboolean G_HandleNailgunBounce( gentity_t *ent, trace_t *trace )")
    cache_pmove_body = _function_body(g_pmove_c, "static void G_PmoveCacheSettings( void )")
    rail_jump_body = _function_body(g_weapon_c, "static void G_ApplyRailJump( gentity_t *ent )")
    lightning_discharge_body = _function_body(g_weapon_c, "static qboolean Weapon_LightningDischargeActive( void )")
    nailgun_body = _function_body(g_weapon_c, "void Weapon_Nailgun_Fire (gentity_t *ent)")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")

    for expected in (
        "grappleSpeed;",
        "gauntletSpeedFactor;",
        "lightningDischargeFlags;",
        "railgunHeadshotDamage;",
        "machinegunIronsightsScale;",
        "nailgunCount;",
        "nailgunBounceCount;",
        "nailgunBounceEnabled;",
        "nailgunBouncePercentage;",
        "guidedRocketEnabled;",
        "extern vmCvar_t g_velocity_gh;",
        "extern vmCvar_t g_guidedRocket;",
        "extern vmCvar_t g_lightningDischarge;",
        "extern vmCvar_t g_railJump;",
        "extern vmCvar_t g_gauntletSpeedFactor;",
        "extern vmCvar_t g_headShotDamage_rg;",
        "extern vmCvar_t g_ironsights_mg;",
        "extern vmCvar_t g_nailbounce;",
        "extern vmCvar_t g_nailbouncepercentage;",
        "extern vmCvar_t g_nailcount;",
    ):
        assert expected in g_local_h

    for expected in (
        '#define CUSTOM_SETTING_GRAPPLING_HOOK\t0x00000200u',
        '#define CUSTOM_SETTING_HEADSHOTS\t\t0x00800000u',
        '#define CUSTOM_SETTING_RAIL_JUMPING\t\t0x01000000u',
        '#define CUSTOM_SETTING_LIGHTNING_DISCHARGE\t0x08000000u',
        'g_weaponConfig.grappleSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gh, 1800, "g_velocity_gh", 1 );',
        'g_weaponConfig.gauntletSpeedFactor = G_ReadWeaponFloatCvarNonNegative( &g_gauntletSpeedFactor, 1.0f, "g_gauntletSpeedFactor" );',
        'g_weaponConfig.lightningDischargeFlags = G_ReadWeaponCvarNonNegative( &g_lightningDischarge, 0, "g_lightningDischarge" );',
        'g_weaponConfig.railJumpStrength = G_ReadWeaponCvarNonNegative( &g_railJump, 0, "g_railJump" );',
        'g_weaponConfig.railgunHeadshotDamage = G_ReadWeaponCvarNonNegative( &g_headShotDamage_rg, 0, "g_headShotDamage_rg" );',
        'g_weaponConfig.machinegunIronsightsScale = G_ReadWeaponFloatCvarNonNegative( &g_ironsights_mg, 1.0f, "g_ironsights_mg" );',
        'g_weaponConfig.nailgunCount = G_ReadWeaponCvarNonNegative( &g_nailcount, 10, "g_nailcount" );',
        'g_weaponConfig.nailgunBounceCount = G_ReadWeaponCvarNonNegative( &g_nailbounce, 1, "g_nailbounce" );',
        'g_weaponConfig.nailgunBouncePercentage = G_ReadWeaponCvarNonNegative( &g_nailbouncepercentage, 65, "g_nailbouncepercentage" );',
        'g_weaponConfig.guidedRocketEnabled = G_ReadWeaponBoolCvar( &g_guidedRocket, qfalse, "g_guidedRocket" );',
    ):
        assert expected in bg_public_h or expected in init_body

    for expected in (
        "g_weaponConfig.grappleSpeed != 1800",
        "G_ConfigFloatDiffersFromDefault( g_weaponConfig.machinegunIronsightsScale, DEFAULT_MACHINEGUN_IRONSIGHTS_SCALE )",
        "g_weaponConfig.nailgunCount != 10",
        "g_weaponConfig.nailgunBounceCount != 1",
        "g_weaponConfig.nailgunBouncePercentage != 65",
    ):
        assert expected in config_mask_body

    for expected in (
        "if ( g_headShotDamage_rg.integer != 0 ) {",
        "mask |= CUSTOM_SETTING_HEADSHOTS;",
        "if ( g_railJump.integer != 0 ) {",
        "mask |= CUSTOM_SETTING_RAIL_JUMPING;",
        "if ( g_lightningDischarge.integer != 0 ) {",
        "mask |= CUSTOM_SETTING_LIGHTNING_DISCHARGE;",
    ):
        assert expected in custom_mask_body

    for expected in (
        "speed = ( float )g_weaponConfig.grappleSpeed;",
        "hook->speed = speed;",
        "VectorScale( dir, speed, hook->s.pos.trDelta );",
    ):
        assert expected in sync_grapple_body

    for expected in (
        "if ( g_weaponConfig.guidedRocketEnabled ) {",
        "bolt->nextthink = level.time + GUIDED_ROCKET_INITIAL_THINK_TIME;",
        "bolt->think = G_RunGuidedRocketThink;",
        "AngleVectors( owner->client->ps.viewangles, forward, NULL, NULL );",
        "VectorScale( forward, GUIDED_ROCKET_SPEED, ent->s.pos.trDelta );",
    ):
        assert expected in fire_rocket_body or expected in guided_rocket_body

    for expected in (
        "machinegunIronsightsScale = g_weaponConfig.machinegunIronsightsScale;",
        "g_pmoveSettings.machinegunIronsightsScale = machinegunIronsightsScale;",
        "gauntletSpeedFactor = g_weaponConfig.gauntletSpeedFactor;",
        "g_pmoveSettings.gauntletSpeedFactor = gauntletSpeedFactor;",
        "g_pmoveSettings.nailgunBounceEnabled = ( g_weaponConfig.nailgunBounceEnabled != 0 );",
        "g_pmoveSettings.nailgunBouncePercentage = g_weaponConfig.nailgunBouncePercentage;",
        "g_pmoveSettings.guidedRocketEnabled = ( g_weaponConfig.guidedRocketEnabled != 0 );",
    ):
        assert expected in cache_pmove_body

    for expected in (
        "railJumpStrength = g_weaponConfig.railJumpStrength;",
        "if ( railJumpStrength <= 0 ) {",
        "trap_Trace( &trace, muzzle, NULL, NULL, end, ent->s.number, CONTENTS_SOLID );",
        "ent->client->ps.velocity[2] += 20.0f;",
        "return ( g_weaponConfig.lightningDischargeFlags > 0 );",
        "for( count = 0; count < g_weaponConfig.nailgunCount; count++ ) {",
        "ent->client->accuracy_shots += g_weaponConfig.nailgunCount;",
        "ent->client->pers.accuracy_shots[WP_NAILGUN] += g_weaponConfig.nailgunCount;",
    ):
        assert expected in rail_jump_body or expected in lightning_discharge_body or expected in nailgun_body or expected in fireweapon_body

    for expected in (
        "g_weaponConfig.nailgunBounceCount <= 0 ||",
        "ent->count >= g_weaponConfig.nailgunBounceCount ) {",
        "if ( g_weaponConfig.nailgunBounceEnabled ) {",
        "if ( bounceRoll > 100 - g_weaponConfig.nailgunBouncePercentage ) {",
        "bolt->s.eFlags = canBounce ? EF_NAIL_BOUNCE : 0;",
    ):
        assert expected in nail_bounce_body or expected in fire_nail_body

    for expected in (
        'trap_Cvar_Set( "g_velocity_gh", "1800" );',
        'trap_Cvar_Set( "g_gauntletSpeedFactor", "1.0" );',
        'trap_Cvar_Set( "g_ironsights_mg", "1.0" );',
        'trap_Cvar_Set( "g_nailbounce", "1" );',
        'trap_Cvar_Set( "g_nailbouncepercentage", "65" );',
        'trap_Cvar_Set( "g_nailcount", "10" );',
        'trap_Cvar_Set( "g_guidedRocket", "0" );',
    ):
        assert expected in g_pmove_c


def test_second_ten_weapon_special_cvar_table_matches_retail_defaults_and_flags() -> None:
    main_c = _read("src/code/game/g_main.c")
    q_shared_h = _read("src/code/game/q_shared.h")
    qagame_hlil = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt"
    )
    qagame_strings = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    assert "#define\tCVAR_SERVERINFO\t\t4" in q_shared_h
    assert "#define\tCVAR_LATCH\t\t\t32" in q_shared_h
    assert "#define CVAR_GAMERULE\t0x100000" in q_shared_h
    for expected in (
        '{ &g_midAirMinHeight, "g_midAirMinHeight", "96", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailspeed, "g_nailspeed", "1000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailspread, "g_nailspread", "400", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_damagePlums, "g_damagePlums", "2", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_quadDamageFactor, "g_quadDamageFactor", "3", CVAR_SERVERINFO | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_quadHog, "g_quadHog", "0", CVAR_LATCH | GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_quadHogIdle, "g_quadHogIdle", "20", CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_quadHogPingRate, "g_quadHogPingRate", "1500", CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_quadHogTime, "g_quadHogTime", "60", CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_proxMineTimeout, "g_proxMineTimeout", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse },',
    ):
        assert expected in main_c

    retail_rows = {
        "g_midAirMinHeight": ('1008e95c  char const (* data_1008e95c)[0x12] = data_10086970 {"g_midAirMinHeight"}', "0x10086da8", "00 00 10 00"),
        "g_nailspeed": ('1008e9d4  char const (* data_1008e9d4)[0xc] = data_10086924 {"g_nailspeed"}', 'data_1008747c {"1000"}', "00 00 14 00"),
        "g_nailspread": ('1008e9ec  char const (* data_1008e9ec)[0xd] = data_10086914 {"g_nailspread"}', "0x10087358", "00 00 14 00"),
        "g_damagePlums": ('1008dedc  char const (* data_1008dedc)[0xe] = data_10087210 {"g_damagePlums"}', "data_1007d53c", "00 00 10 00"),
        "g_quadDamageFactor": ('1008ebcc  char const (* data_1008ebcc)[0x13] = data_10086798 {"g_quadDamageFactor"}', "0x100874e0", "04 00 10 00"),
        "g_quadHog": ('1008ebe4  char const (* data_1008ebe4)[0xa] = data_1008678c {"g_quadHog"}', "data_1007d0a8", "20 00 14 00"),
        "g_quadHogIdle": ('1008ebfc  char const (* data_1008ebfc)[0xe] = data_1008677c {"g_quadHogIdle"}', "data_1007e1ac", "00 00 10 00"),
        "g_quadHogPingRate": ('1008ec14  char const (* data_1008ec14)[0x12] = data_10086768 {"g_quadHogPingRate"}', 'data_10086760 {"1500"}', "00 00 10 00"),
        "g_quadHogTime": ('1008ec2c  char const (* data_1008ec2c)[0xe] = data_10086750 {"g_quadHogTime"}', "0x1008674c", "00 00 10 00"),
        "g_proxMineTimeout": ('1008ebb4  char const (* data_1008ebb4)[0x12] = data_100867ac {"g_proxMineTimeout"}', "data_1007e1ac", "00 00 14 00"),
    }
    for marker, default_marker, flags_marker in retail_rows.values():
        row_block = qagame_hlil[qagame_hlil.index(marker) : qagame_hlil.index(marker) + 260]
        assert default_marker in row_block
        assert flags_marker in row_block

    for expected in (
        '10086750  char const data_10086750[0xe] = "g_quadHogTime", 0',
        '10086760  char const data_10086760[0x5] = "1500", 0',
        '10086768  char const data_10086768[0x12] = "g_quadHogPingRate", 0',
        '1008677c  char const data_1008677c[0xe] = "g_quadHogIdle", 0',
        '1008678c  char const data_1008678c[0xa] = "g_quadHog", 0',
        '10086798  char const data_10086798[0x13] = "g_quadDamageFactor", 0',
        '100867ac  char const data_100867ac[0x12] = "g_proxMineTimeout", 0',
        '10086914  char const data_10086914[0xd] = "g_nailspread", 0',
        '10086924  char const data_10086924[0xc] = "g_nailspeed", 0',
        '10086970  char const data_10086970[0x12] = "g_midAirMinHeight", 0',
        '10087210  char const data_10087210[0xe] = "g_damagePlums", 0',
        '1008747c  char const data_1008747c[0x5] = "1000", 0',
    ):
        assert expected in qagame_strings

    for marker, default_bytes in (
        ("1007d53c  data_1007d53c:", "32 00 00 00"),
        ("1007e1ac  data_1007e1ac:", "32 30 00 00"),
        ("1008674b", "36 30 00 00"),
        ("10086da5", "39 36 00 00"),
        ("10087355", "34 30 30 00"),
        ("100874e0", "33 00 00 00"),
    ):
        default_block = qagame_strings[qagame_strings.index(marker) : qagame_strings.index(marker) + 180]
        assert default_bytes in default_block


def test_second_ten_weapon_special_cvars_keep_retail_weapon_wiring() -> None:
    bg_pmove_c = _read("src/code/game/bg_pmove.c")
    bg_public_h = _read("src/code/game/bg_public.h")
    cg_servercmds_c = _read("src/code/cgame/cg_servercmds.c")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_pmove_c = _read("src/code/game/g_pmove.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    qagame_hlil_part02 = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )

    init_body = _function_body(g_main_c, "void G_InitWeaponConfig( void )")
    cache_pmove_body = _function_body(g_pmove_c, "static void G_PmoveCacheSettings( void )")
    custom_mask_body = _function_body(g_main_c, "static uint64_t G_ComputeCustomSettingsMask( void )")
    config_mask_body = _function_body(g_config_c, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
    midair_body = _function_body(g_missile_c, "qboolean G_IsMidAirEligibleTarget( gentity_t *target )")
    fire_nail_body = _function_body(g_missile_c, "gentity_t *fire_nail( gentity_t *self, vec3_t start, vec3_t forward, vec3_t right, vec3_t up )")
    prox_activate_body = _function_body(g_missile_c, "static void ProximityMine_Activate( gentity_t *ent )")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    powerup_scale_body = _function_body(g_combat_c, "static float G_CalcPowerupDamageScale( gentity_t *attacker )")
    server_settings_body = _function_body(g_main_c, "static void G_UpdateServerSettingsInfoConfigstrings( qboolean forceBroadcast )")
    quad_pickup_body = _function_body(g_main_c, "void G_QuadHogOnPickup( gentity_t *player )")
    quad_frame_body = _function_body(g_main_c, "void G_QuadHogFrame( void )")

    for expected in (
        "midAirMinimumHeight;",
        "nailgunSpeed;",
        "nailgunSpread;",
        "quadDamageMultiplier;",
        "quadHogEnabled;",
        "quadHogIdleSeconds;",
        "quadHogTimeSeconds;",
        "quadHogPingRateMilliseconds;",
        "extern vmCvar_t g_midAirMinHeight;",
        "extern vmCvar_t g_nailspeed;",
        "extern vmCvar_t g_nailspread;",
        "extern vmCvar_t g_damagePlums;",
        "extern vmCvar_t g_quadDamageFactor;",
        "extern vmCvar_t g_quadHog;",
        "extern vmCvar_t g_quadHogIdle;",
        "extern vmCvar_t g_quadHogTime;",
        "extern vmCvar_t g_quadHogPingRate;",
        "extern\tvmCvar_t\tg_proxMineTimeout;",
    ):
        assert expected in g_local_h

    for source in (bg_public_h, cg_servercmds_c, g_local_h, g_main_c, g_pmove_c):
        assert "quadHogPingRateSeconds" not in source

    for expected in (
        "midAirMinimumHeight;",
        "quadDamageMultiplier;",
        "quadHogEnabled;",
        "quadHogIdleSeconds;",
        "quadHogTimeSeconds;",
        "quadHogPingRateMilliseconds;",
        ".midAirMinimumHeight = 96,",
        ".quadDamageMultiplier = 3.0f,",
        ".quadHogIdleSeconds = 20,",
        ".quadHogTimeSeconds = 60,",
        ".quadHogPingRateMilliseconds = 1500,",
        "PMOVE_COMPACT_INT( quadHogPingRateMilliseconds );",
        "PMOVE_INT_FIELD( quadHogPingRateMilliseconds )",
    ):
        assert expected in bg_public_h or expected in bg_pmove_c or expected in cg_servercmds_c

    for expected in (
        'g_weaponConfig.midAirMinimumHeight = G_ReadWeaponCvarNonNegative( &g_midAirMinHeight, 96, "g_midAirMinHeight" );',
        'g_weaponConfig.nailgunSpeed = G_ReadWeaponCvarAtLeast( &g_nailspeed, 1000, "g_nailspeed", 1 );',
        'g_weaponConfig.nailgunSpread = G_ReadWeaponCvarNonNegative( &g_nailspread, 400, "g_nailspread" );',
        'g_weaponConfig.quadDamageMultiplier = G_ReadWeaponFloatCvarNonNegative( &g_quadDamageFactor, 3.0f, "g_quadDamageFactor" );',
        'g_weaponConfig.quadHogEnabled = G_ReadWeaponBoolCvar( &g_quadHog, qfalse, "g_quadHog" );',
        'g_weaponConfig.quadHogIdleSeconds = G_ReadWeaponCvarRaw( &g_quadHogIdle, 20, "g_quadHogIdle" );',
        'g_weaponConfig.quadHogTimeSeconds = G_ReadWeaponCvarRaw( &g_quadHogTime, 60, "g_quadHogTime" );',
        'g_weaponConfig.quadHogPingRateMilliseconds = G_ReadWeaponCvarRaw( &g_quadHogPingRate, 1500, "g_quadHogPingRate" );',
    ):
        assert expected in init_body

    for expected in (
        "return heightAboveGround >= ( float )g_weaponConfig.midAirMinimumHeight;",
        "u = sin(r) * crandom() * g_weaponConfig.nailgunSpread * 16;",
        "r = cos(r) * crandom() * g_weaponConfig.nailgunSpread * 16;",
        "scale = 555 + random() * g_weaponConfig.nailgunSpeed;",
        "s_quadFactor = g_weaponConfig.quadDamageMultiplier;",
        "scale *= g_weaponConfig.quadDamageMultiplier;",
        "ent->nextthink = level.time + g_proxMineTimeout.integer * 1000;",
    ):
        assert expected in midair_body or expected in fire_nail_body or expected in fireweapon_body or expected in powerup_scale_body or expected in prox_activate_body

    for expected in (
        "g_pmoveSettings.midAirMinimumHeight = g_weaponConfig.midAirMinimumHeight;",
        "g_pmoveSettings.quadDamageMultiplier = ( g_weaponConfig.quadDamageMultiplier > 0.0f ) ? g_weaponConfig.quadDamageMultiplier : ( defaults ? defaults->quadDamageMultiplier : 1.0f );",
        "g_pmoveSettings.quadHogEnabled = g_weaponConfig.quadHogEnabled;",
        "g_pmoveSettings.quadHogIdleSeconds = g_weaponConfig.quadHogIdleSeconds;",
        "g_pmoveSettings.quadHogTimeSeconds = g_weaponConfig.quadHogTimeSeconds;",
        "g_pmoveSettings.quadHogPingRateMilliseconds = g_weaponConfig.quadHogPingRateMilliseconds;",
    ):
        assert expected in cache_pmove_body

    for expected in (
        "level.quadHogExpireTime = level.time + g_weaponConfig.quadHogTimeSeconds * 1000;",
        "level.quadHogNextPingTime = level.time + g_weaponConfig.quadHogPingRateMilliseconds;",
        "int\tidleLimit = g_weaponConfig.quadHogIdleSeconds * 1000;",
        "trap_SendServerCommand( owner->s.number, va( \"print \\\"Quad Hog: %d seconds remaining\\\\n\\\"\", remainingMs / 1000 ) );",
        "if ( g_quadHog.integer != 0 ) {",
        "mask |= CUSTOM_SETTING_QUAD_HOG;",
    ):
        assert expected in quad_pickup_body or expected in quad_frame_body or expected in custom_mask_body

    for expected in (
        "g_weaponConfig.nailgunSpeed != 1000",
        "g_weaponConfig.nailgunSpread != 400",
        "#define DEFAULT_PROX_MINE_TIMEOUT         20",
        "g_proxMineTimeout.integer != DEFAULT_PROX_MINE_TIMEOUT",
    ):
        assert expected in g_config_c or expected in config_mask_body

    for expected in (
        'Info_SetValueForKey( payloadB, SERVER_SETTINGS_KEY_QUAD_DAMAGE_FACTOR, va( "%i", g_quadDamageFactor.integer ) );',
        'trap_Cvar_Set( "g_midAirMinHeight", "96" );',
        'trap_Cvar_Set( "g_nailspeed", "1000" );',
        'trap_Cvar_Set( "g_nailspread", "400" );',
        'trap_Cvar_Set( "g_quadDamageFactor", "3" );',
        'trap_Cvar_Set( "g_quadHogIdle", "20" );',
        'trap_Cvar_Set( "g_quadHogTime", "60" );',
        'trap_Cvar_Set( "g_quadHogPingRate", "1500" );',
    ):
        assert expected in server_settings_body or expected in g_pmove_c

    for expected in (
        "1005b8a0    int32_t sub_1005b8a0(void* arg1)",
        "1005b8c2  *(arg1 + 0x2f4) = data_105a4bac * 0x3e8 + data_105dce5c",
        "1004e09c      edi = data_105a44ec",
        "1004f24e                                  *(eax_15 + 0xc4) = data_104b196c",
    ):
        assert expected in qagame_hlil_part02

    assert "g_damagePlums.integer" not in g_combat_c


def test_server_weapon_parity_hooks_match_retail_ql() -> None:
    bg_public_h = _read("src/code/game/bg_public.h")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")

    assert "#define DEFAULT_SHOTGUN_COUNT\t20" in bg_public_h
    assert "chaingunDamage;" in g_local_h
    assert "shotgunOuterDamage;" in g_local_h
    assert "shotgunFalloffDamage;" in g_local_h
    assert "lightningFalloffDamage;" in g_local_h
    assert "railJumpStrength;" in g_local_h
    assert "grappleDamage;" in g_local_h
    assert 'g_weaponConfig.chaingunDamage = G_ReadWeaponCvar( &g_damage_cg, 8, "g_damage_cg" );' in g_main_c
    assert 'g_weaponConfig.shotgunOuterDamage = G_ReadWeaponCvar( &g_damage_sg_outer, 5, "g_damage_sg_outer" );' in g_main_c
    assert 'g_weaponConfig.shotgunFalloffDamage = G_ReadWeaponCvarNonNegative( &g_damage_sg_falloff, 0, "g_damage_sg_falloff" );' in g_main_c
    assert 'g_weaponConfig.lightningFalloffDamage = G_ReadWeaponCvarNonNegative( &g_damage_lg_falloff, 0, "g_damage_lg_falloff" );' in g_main_c
    assert 'g_weaponConfig.railJumpStrength = G_ReadWeaponCvarNonNegative( &g_railJump, 0, "g_railJump" );' in g_main_c
    assert 'g_weaponConfig.grappleDamage = G_ReadWeaponCvar( &g_damage_gh, 10, "g_damage_gh" );' in g_main_c

    assert "return ( ent->client->ps.pm_flags & PMF_DUCKED ) ? qtrue : qfalse;" in g_weapon_c
    assert "return 3.0f;" in g_weapon_c
    assert "return 5.0f;" in g_weapon_c
    assert "reach = 43.0f;" in g_weapon_c
    assert "#define\tMACHINEGUN_SPREAD\t150" in g_weapon_c
    assert "#define\tHEAVY_MACHINEGUN_SPREAD\t350" in g_weapon_c
    assert "#define\tCHAINGUN_DAMAGE\t\t(g_weaponConfig.chaingunDamage)" in g_weapon_c
    assert "chaingunSpin = (float)ent->client->ps.stats[STAT_CHAINGUN_SPINUP];" in g_weapon_c
    assert "spread = 700.0f + ( chaingunSpin / 1000.0f ) * 700.0f;" in g_weapon_c
    assert "distancePastFalloff = G_RoundFloatToInt( distance - falloffRange );" in g_weapon_c
    assert "baseDamage -= falloffDamage;" in g_weapon_c
    assert "trap_Trace( &trace, muzzle, NULL, NULL, end, ent->s.number, CONTENTS_SOLID );" in g_weapon_c
    assert "ent->client->ps.velocity[2] += 20.0f;" in g_weapon_c
    assert "ent->client->accuracy_shots += DEFAULT_SHOTGUN_COUNT;" in g_weapon_c
    assert "ent->client->pers.accuracy_shots[WP_SHOTGUN] += DEFAULT_SHOTGUN_COUNT;" in g_weapon_c


def test_shotgun_server_uses_retail_ring_damage_and_falloff() -> None:
    g_weapon_c = _read("src/code/game/g_weapon.c")

    offsets_body = _function_body(g_weapon_c, "static int G_GetShotgunPelletOffsets( int pelletIndex, float *r, float *u )")
    damage_body = _function_body(g_weapon_c, "static int G_GetShotgunPelletDamage( int pelletType, vec3_t impactPoint )")
    pellet_body = _function_body(g_weapon_c, "qboolean ShotgunPellet( vec3_t start, vec3_t end, gentity_t *ent, int pelletType )")
    pattern_body = _function_body(g_weapon_c, "void ShotgunPattern( vec3_t origin, vec3_t origin2, int seed, gentity_t *ent )")

    assert "angle = ( pelletIndex - 20 ) * 60.0f;" in offsets_body
    assert "radius = 4000.0f;" in offsets_body
    assert "pelletType = 1;" in offsets_body
    assert "angle = pelletIndex * 60.0f + 30.0f;" in offsets_body
    assert "radius = 8000.0f;" in offsets_body
    assert "pelletType = 2;" in offsets_body
    assert "angle = pelletIndex * 45.0f;" in offsets_body
    assert "radius = 12000.0f;" in offsets_body
    assert "pelletType = 3;" in offsets_body

    assert "if ( pelletType == 1 ) {" in damage_body
    assert "damage = DEFAULT_SHOTGUN_DAMAGE;" in damage_body
    assert "damage = DEFAULT_SHOTGUN_OUTER_DAMAGE;" in damage_body
    assert "damage = G_RoundFloatToInt( (float)damage * s_quadFactor );" in damage_body
    assert "falloffDamage = g_weaponConfig.shotgunFalloffDamage;" in damage_body
    assert "falloffRange = g_weaponConfig.shotgunFalloffRange;" in damage_body
    assert "VectorSubtract( impactPoint, muzzle, distanceVector );" in damage_body
    assert "distancePastFalloff = G_RoundFloatToInt( distance - falloffRange );" in damage_body
    assert "damage -= falloffDamage;" in damage_body

    assert "damage = G_GetShotgunPelletDamage( pelletType, tr.endpos );" in pellet_body
    assert "DEFAULT_SHOTGUN_DAMAGE * s_quadFactor" not in pellet_body
    assert "pelletType = G_GetShotgunPelletOffsets( i, &r, &u );" in pattern_body
    assert "ShotgunPellet( origin, end, ent, pelletType )" in pattern_body


def test_gauntlet_prefire_probe_latches_retail_fire_body_target() -> None:
    g_weapon_c = _read("src/code/game/g_weapon.c")

    weapon_body = _function_body(g_weapon_c, "void Weapon_Gauntlet( gentity_t *ent )")
    probe_body = _function_body(g_weapon_c, "qboolean CheckGauntletAttack( gentity_t *ent )")

    assert "traceEnt = ent->enemy;" in weapon_body
    assert "!ent || !ent->client" not in weapon_body
    assert "G_AddEvent( ent, EV_FIRE_WEAPON" not in weapon_body
    assert "VectorSubtract( ent->s.pos.trBase, traceEnt->s.pos.trBase, hitDir );" in weapon_body
    assert "G_TempEntity( traceEnt->s.pos.trBase, EV_MISSILE_HIT );" in weapon_body
    assert "tent->s.eventParm = DirToByte( hitDir );" in weapon_body
    assert "damage = g_weaponConfig.gauntletDamage * s_quadFactor;" in weapon_body
    assert "G_Damage( traceEnt, ent, ent, forward, hitDir," in weapon_body

    assert "reach = 43.0f;" in probe_body
    assert "!ent || !ent->client" not in probe_body
    assert "trap_Trace( &tr, muzzle, NULL, NULL, end, ent->s.number, MASK_SHOT );" in probe_body
    assert "ent->enemy = NULL;" in probe_body
    assert "ent->enemy = traceEnt;" in probe_body
    assert "G_TempEntity" not in probe_body
    assert "G_Damage" not in probe_body
    assert "EV_POWERUP_QUAD" not in probe_body


def test_fireweapon_and_railgun_paths_drop_non_retail_branches() -> None:
    g_combat_c = _read("src/code/game/g_combat.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")

    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    bullet_body = _function_body(g_weapon_c, "void Bullet_Fire( gentity_t *ent, float spread, int damage, meansOfDeath_t mod )")
    railgun_body = _function_body(g_weapon_c, "void weapon_railgun_fire (gentity_t *ent)")
    grapple_body = _function_body(g_weapon_c, "void Weapon_GrapplingHook_Fire (gentity_t *ent)")
    fire_grapple_body = _function_body(g_missile_c, "gentity_t *fire_grapple (gentity_t *self, vec3_t start, vec3_t dir)")

    assert "spread = MACHINEGUN_SPREAD;" in fireweapon_body
    assert "if ( G_PlayerUsesMachinegunTightSpread( ent ) ) {" in fireweapon_body
    assert "spread = (float)G_RoundFloatToInt( spread * G_GetMachinegunIronsightScale() );" in fireweapon_body
    assert "Bullet_Fire( ent, spread, MACHINEGUN_DAMAGE, MOD_MACHINEGUN );" in fireweapon_body
    assert "ironsightKick" not in bullet_body
    assert "ironsightScale" not in bullet_body
    assert "G_PlayerUsesMachinegunTightSpread" not in bullet_body
    assert "MACHINEGUN_TEAM_DAMAGE" not in fireweapon_body
    assert "G_GetChaingunSpread( ent )" in fireweapon_body
    assert "CHAINGUN_DAMAGE" in fireweapon_body

    assert "MOD_RAILGUN_HEADSHOT" not in railgun_body
    assert "G_ApplyRailJump( ent );" in railgun_body
    assert "G_Damage( traceEnt, ent, ent, forward, trace.endpos, shotDamage, 0, MOD_RAILGUN );" in railgun_body
    assert "if ( mod == MOD_RAILGUN && G_IsRailgunHeadshot( targ, point ) ) {" in g_combat_c
    assert "if ( mod == MOD_RAILGUN || mod == MOD_RAILGUN_HEADSHOT ) {" not in g_combat_c
    assert "hook = fire_grapple( ent, muzzle, forward );" in grapple_body
    assert "hook->damage *= s_quadFactor;" in grapple_body
    assert "hook->damage = g_weaponConfig.grappleDamage;" in fire_grapple_body
    assert "case MOD_GRAPPLE:" in g_combat_c
    assert "configuredDamage = g_weaponConfig.grappleDamage;" in g_combat_c


def test_grappling_hook_full_server_and_cgame_wiring_matches_retail() -> None:
    ai_chat_c = _read("src/code/game/ai_chat.c")
    ai_dmq3_c = _read("src/code/game/ai_dmq3.c")
    ai_main_c = _read("src/code/game/ai_main.c")
    bg_misc_c = _read("src/code/game/bg_misc.c")
    bg_pmove_c = _read("src/code/game/bg_pmove.c")
    bg_pmove_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md")
    bg_public_h = _read("src/code/game/bg_public.h")
    cgame_hlil = _read("references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt")
    cgame_symbols = _read("references/symbol-maps/cgame.json")
    cg_draw_c = _read("src/code/cgame/cg_draw.c")
    cg_ents_c = _read("src/code/cgame/cg_ents.c")
    cg_local_h = _read("src/code/cgame/cg_local.h")
    cg_main_c = _read("src/code/cgame/cg_main.c")
    cg_newdraw_c = _read("src/code/cgame/cg_newdraw.c")
    cg_playerstate_c = _read("src/code/cgame/cg_playerstate.c")
    cg_servercmds_c = _read("src/code/cgame/cg_servercmds.c")
    cg_weapons_c = _read("src/code/cgame/cg_weapons.c")
    cvar_c = _read("src/code/qcommon/cvar.c")
    g_active_c = _read("src/code/game/g_active.c")
    g_client_c = _read("src/code/game/g_client.c")
    g_cmds_c = _read("src/code/game/g_cmds.c")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_items_c = _read("src/code/game/g_items.c")
    g_items_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/g_items.md")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_pmove_c = _read("src/code/game/g_pmove.c")
    g_utils_c = _read("src/code/game/g_utils.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    inv_h = _read("src/code/game/inv.h")
    qagame_hlil_part02 = _read(
        "references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt"
    )
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    grapple_move_body = _function_body(bg_pmove_c, "static void PM_GrappleMove( void )")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    grapple_fire_body = _function_body(g_weapon_c, "void Weapon_GrapplingHook_Fire (gentity_t *ent)")
    hook_free_body = _function_body(g_weapon_c, "void Weapon_HookFree (gentity_t *ent)")
    update_hook_body = _function_body(g_weapon_c, "void Weapon_UpdateHookGrapplePoint( gentity_t *ent )")
    hook_think_body = _function_body(g_weapon_c, "void Weapon_HookThink (gentity_t *ent)")
    missile_impact_body = _function_body(g_missile_c, "void G_MissileImpact( gentity_t *ent, trace_t *trace )")
    sync_grapple_body = _function_body(g_missile_c, "static void G_SynchronizeGrappleConfig( gentity_t *hook, vec3_t dir )")
    fire_grapple_body = _function_body(g_missile_c, "gentity_t *fire_grapple (gentity_t *self, vec3_t start, vec3_t dir)")
    set_origin_body = _function_body(g_utils_c, "void G_SetOrigin( gentity_t *ent, vec3_t origin )")
    reload_config_body = _function_body(g_config_c, "void G_InitWeaponReloadConfig( void )")
    custom_mask_body = _function_body(g_config_c, "uint64_t G_ComputeConfigCustomSettingsMask( void )")
    starting_ammo_body = _function_body(g_config_c, "void G_InitStartingAmmoConfig( void )")
    knockback_config_body = _function_body(g_config_c, "void G_InitKnockbackConfig( void )")
    warmup_allowed_body = _function_body(
        g_client_c,
        "static qboolean G_WarmupLevelWeaponAllowed( weapon_t weapon, unsigned int startingWeaponsMask )",
    )
    warmup_ammo_body = _function_body(g_client_c, "static int G_WarmupLevelWeaponAmmo( weapon_t weapon )")
    pickup_weapon_body = _function_body(g_items_c, "int Pickup_Weapon (gentity_t *ent, gentity_t *other)")
    unlock_tier_body = _function_body(g_items_c, "static int G_GetItemUnlockTier( const gitem_t *item )")
    clamp_body = _function_body(g_combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    mod_to_weapon_body = _function_body(g_combat_c, "static weapon_t G_ModToWeapon( int mod )")
    knockback_body = _function_body(g_combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")
    grapple_trail_body = _function_body(cg_weapons_c, "void CG_GrappleTrail( centity_t *ent, const weaponInfo_t *wi )")
    register_weapon_body = _function_body(cg_weapons_c, "void CG_RegisterWeapon( int weaponNum )")
    add_player_weapon_body = _function_body(
        cg_weapons_c,
        "void CG_AddPlayerWeapon( refEntity_t *parent, playerState_t *ps, centity_t *cent, int team )",
    )
    cg_grapple_body = _function_body(cg_ents_c, "static void CG_Grapple( centity_t *cent )")
    respawn_token_body = _function_body(cg_playerstate_c, "static weapon_t CG_RespawnWeaponFromToken( const char *token )")
    reload_configstring_body = _function_body(cg_servercmds_c, "static void CG_ParseWeaponReloadConfigString( void )")

    assert "| Grappling Hook | 100 |" in bg_pmove_hlil
    assert "| Grappling Hook | 0 | -1 |" in bg_pmove_hlil
    assert "| 0x1B | 0x0E | Grapple |" in g_items_hlil
    for expected in (
        '"g_damage_gh"',
        '"weapon_reload_gh"',
        '"weapon_reload_hook"',
        '"g_velocity_gh"',
        '"g_startingAmmo_gh"',
        '"g_knockback_gh"',
        '"pmove_velocity_gh"',
        '"weapon_grapplinghook"',
        '"Grappling Hook"',
    ):
        assert expected in qagame_hlil_part02
    for expected in (
        "Retail keeps this separate from g_velocity_gh",
        "Retail grapple projectile constructor",
        "Retail grapple-fire gate",
        "Exact match for the grapple cleanup helper",
        "Retail grapple think routine",
        "the grapple hook handling",
        "Grapple chain trail callback installed for the hook weapon",
        "Grapple-hook renderer",
    ):
        assert expected in qagame_symbols or expected in cgame_symbols
    for expected in (
        "models/weapons2/grapple/grapple.md3",
        "models/weapons2/grapple/grapple_hook.md3",
        "icons/iconw_grapple",
        "icons/iconw_grapple.tga",
        "grapplingChain",
        "sound/weapons/grapple/grhang.ogg",
        "sound/weapons/grapple/grfire.ogg",
        "sound/weapons/grapple/grpull.ogg",
        "sound/weapons/grapple/grreset.ogg",
        "sound/weapons/grapple/grhit.ogg",
        "cg_weaponConfig_gh",
        "cg_disableLoadout_gh",
        "weapon_reload_hook",
    ):
        assert expected in cgame_hlil

    weapon_enum = bg_public_h[bg_public_h.index("typedef enum {\n\tWP_NONE"):bg_public_h.index("} weapon_t;")]
    enum_cursor = -1
    for expected in (
        "WP_BFG",
        "WP_GRAPPLING_HOOK",
        "WP_NAILGUN",
    ):
        enum_cursor = weapon_enum.index(expected, enum_cursor + 1)
    assert "#define ITEMTAG_WEAPON_GRAPPLING_HOOK\t\t10" in bg_public_h
    assert "#define CUSTOM_SETTING_GRAPPLING_HOOK" in bg_public_h
    assert "MOD_GRAPPLE," in bg_public_h
    assert "ET_GRAPPLE," in bg_public_h
    assert "#define PMF_GRAPPLE_PULL\t2048" in bg_public_h
    assert "#define WEAPONINDEX_GRAPPLING_HOOK              10" in inv_h

    for expected in (
        "{ WP_GRAPPLING_HOOK, 0, -1, 0, 0.317000002f, 0.666000009f, 0.861999989f, 1.000000000f }",
        "[WP_GRAPPLING_HOOK] = 0",
        "[WP_GRAPPLING_HOOK] = ITEMTAG_WEAPON_GRAPPLING_HOOK",
        "[ITEMTAG_WEAPON_GRAPPLING_HOOK] = \"Grappling Hook\"",
        '"weapon_grapplinghook"',
        '"models/weapons2/grapple/grapple.md3"',
        '"icons/iconw_grapple"',
        '"Grappling Hook"',
    ):
        assert expected in bg_misc_c
    assert "case WP_GRAPPLING_HOOK:" in unlock_tier_body
    assert "return 0x0E;" in unlock_tier_body

    assert "[WP_GRAPPLING_HOOK] = 100," in bg_pmove_c
    assert "settings->velocityGh" in grapple_move_body
    assert "maxSpeed = pm_defaultSettings.velocityGh;" in grapple_move_body
    assert "maxSpeed = 800.0f;" in grapple_move_body
    assert "VectorScale(pml.forward, -16, v);" in grapple_move_body
    assert "VectorAdd(pm->ps->grapplePoint, v, v);" in grapple_move_body
    assert "VectorSubtract(v, pm->ps->origin, vel);" in grapple_move_body
    assert "if (vlen <= 100)" in grapple_move_body
    assert "VectorScale(vel, 10 * vlen, vel);" in grapple_move_body
    assert "VectorScale( vel, maxSpeed, vel );" in grapple_move_body
    assert "pml.groundPlane = qfalse;" in grapple_move_body
    assert "pm->ps->ammo[ pm->ps->weapon ] || pm->ps->weapon == WP_GRAPPLING_HOOK" in bg_pmove_c
    assert "} else if (pm->ps->pm_flags & PMF_GRAPPLE_PULL) {" in bg_pmove_c

    assert "grappleDamage;" in g_local_h
    assert "grappleSpeed;" in g_local_h
    assert "grapplingHook;" in g_local_h
    assert "int\t\thook;" in g_local_h
    assert 'g_weaponConfig.grappleDamage = G_ReadWeaponCvar( &g_damage_gh, 10, "g_damage_gh" );' in g_main_c
    assert 'g_weaponConfig.grappleSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_gh, 1800, "g_velocity_gh", 1 );' in g_main_c
    assert 'trap_Cvar_Set( "g_velocity_gh", "1800" );' in g_pmove_c
    assert "return ( g_pmove_velocityGh_cvar.value != 800.0f ) ? qtrue : qfalse;" in g_pmove_c
    assert "case WP_GRAPPLING_HOOK:" in g_pmove_c
    assert "duration = config->grapplingHook;" in g_pmove_c
    assert 'g_weaponReloadConfig.grapplingHook = G_ReadWeaponReloadCvar( &weapon_reload_gh, DEFAULT_WEAPON_RELOAD_GH, "weapon_reload_gh" );' in reload_config_body
    assert 'g_weaponReloadConfig.hook = G_ReadWeaponReloadCvar( &weapon_reload_hook, DEFAULT_WEAPON_RELOAD_HOOK, "weapon_reload_hook" );' in reload_config_body
    assert "g_weaponConfig.grappleDamage != 10" in custom_mask_body
    assert "g_weaponReloadConfig.grapplingHook != DEFAULT_WEAPON_RELOAD_GH" in custom_mask_body
    assert "g_weaponReloadConfig.hook != DEFAULT_WEAPON_RELOAD_HOOK" in custom_mask_body
    assert "g_weaponConfig.grappleSpeed != 1800" in custom_mask_body
    assert "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.grapplingHook, DEFAULT_KNOCKBACK_GH )" in custom_mask_body
    assert "G_PmoveHasGrappleVelocityCustomSetting()" in custom_mask_body
    assert "mask |= CUSTOM_SETTING_GRAPPLING_HOOK;" in custom_mask_body
    assert 'g_startingAmmoConfig.grapplingHook = G_ReadStartingAmmoCvar( &g_startingAmmo_gh, DEFAULT_STARTING_AMMO_GH, "g_startingAmmo_gh" );' in starting_ammo_body
    assert 'g_knockbackConfig.grapplingHook = G_ReadKnockbackCvar( &g_knockback_gh, DEFAULT_KNOCKBACK_GH, "g_knockback_gh" );' in knockback_config_body
    assert '"weapon_reload_gh"' in cvar_c
    assert '"weapon_reload_hook"' in cvar_c

    assert "hook = fire_grapple( ent, muzzle, forward );" in grapple_fire_body
    assert "hook->damage *= s_quadFactor;" in grapple_fire_body
    assert "ent->client->fireHeld = qtrue;" in grapple_fire_body
    assert "!ent->client->fireHeld && !ent->client->hook" in grapple_fire_body
    assert "ent->parent->client->hook = NULL;" in hook_free_body
    assert "ent->parent->client->ps.pm_flags &= ~PMF_GRAPPLE_PULL;" in hook_free_body
    assert "G_FreeEntity( ent );" in hook_free_body
    assert "v[0] = ent->enemy->r.currentOrigin[0] + (ent->enemy->r.mins[0] + ent->enemy->r.maxs[0]) * 0.5;" in hook_think_body
    assert "SnapVectorTowards( v, oldorigin );" in hook_think_body
    assert "G_SetOrigin( ent, v );" in hook_think_body
    assert "viewOrigin[2] += ent->parent->client->ps.viewheight;" in update_hook_body
    assert "VectorSubtract( ent->r.currentOrigin, viewOrigin, offsetDir );" in update_hook_body
    assert "g_latchedHookOffset.value" in update_hook_body
    assert "VectorMA( ent->r.currentOrigin, g_latchedHookOffset.value, offsetDir," in update_hook_body
    assert "Weapon_UpdateHookGrapplePoint( ent );" in hook_think_body
    assert "client->ps.weapon == WP_GRAPPLING_HOOK" in g_active_c
    assert "Weapon_HookFree(client->hook);" in g_active_c

    assert "speed = ( float )g_weaponConfig.grappleSpeed;" in sync_grapple_body
    assert "VectorScale( dir, speed, hook->s.pos.trDelta );" in sync_grapple_body
    assert "SnapVector( hook->s.pos.trDelta );" in sync_grapple_body
    for expected in (
        'hook->classname = "hook";',
        "hook->nextthink = level.time + 10000;",
        "hook->think = Weapon_HookFree;",
        "hook->s.eType = ET_MISSILE;",
        "hook->r.svFlags = SVF_USE_CURRENT_ORIGIN;",
        "hook->s.weapon = WP_GRAPPLING_HOOK;",
        "hook->damage = g_weaponConfig.grappleDamage;",
        "hook->methodOfDeath = MOD_GRAPPLE;",
        "hook->clipmask = MASK_SHOT;",
        "hook->s.pos.trType = TR_LINEAR;",
        "hook->s.pos.trTime = level.time - MISSILE_PRESTEP_TIME;",
        "hook->s.otherEntityNum = self->s.number;",
        "G_SynchronizeGrappleConfig( hook, dir );",
        "self->client->hook = hook;",
    ):
        assert expected in fire_grapple_body
    assert 'if (!strcmp(ent->classname, "hook")) {' in missile_impact_body
    assert "nent = G_Spawn();" in missile_impact_body
    assert "G_AddEvent( nent, EV_MISSILE_HIT, DirToByte( trace->plane.normal ) );" in missile_impact_body
    assert "G_AddEvent( nent, EV_MISSILE_MISS, DirToByte( trace->plane.normal ) );" in missile_impact_body
    assert "ent->s.eType = ET_GRAPPLE;" in missile_impact_body
    assert "G_SetOrigin( ent, v );" in missile_impact_body
    assert "ent->think = Weapon_HookThink;" in missile_impact_body
    assert "ent->nextthink = level.time + FRAMETIME;" in missile_impact_body
    assert "ent->parent->client->ps.pm_flags |= PMF_GRAPPLE_PULL;" in missile_impact_body
    assert "Weapon_UpdateHookGrapplePoint( ent );" in missile_impact_body
    assert "ent->s.pos.trType = TR_STATIONARY;" in set_origin_body
    assert "VectorClear( ent->s.pos.trDelta );" in set_origin_body

    assert "case WP_GRAPPLING_HOOK:" in fireweapon_body
    assert "Weapon_GrapplingHook_Fire( ent );" in fireweapon_body
    assert "ent->s.weapon != WP_GRAPPLING_HOOK && ent->s.weapon != WP_GAUNTLET" in fireweapon_body
    assert "case MOD_GRAPPLE:" in clamp_body
    assert "configuredDamage = g_weaponConfig.grappleDamage;" in clamp_body
    assert "case MOD_GRAPPLE:" in mod_to_weapon_body
    assert "return WP_GRAPPLING_HOOK;" in mod_to_weapon_body
    assert "case MOD_GRAPPLE:" in knockback_body
    assert "return g_knockbackConfig.grapplingHook;" in knockback_body
    assert "case WP_GRAPPLING_HOOK:" in warmup_ammo_body
    assert "return -1;" in warmup_ammo_body
    assert "weapon != WP_MACHINEGUN && weapon != WP_GRAPPLING_HOOK" in warmup_allowed_body
    assert "startingAmmoTable[WP_GRAPPLING_HOOK] = g_startingAmmoConfig.grapplingHook;" in g_client_c
    assert "if ( weapon == WP_GRAPPLING_HOOK ) {" in pickup_weapon_body
    assert "other->client->ps.ammo[weapon] = -1;" in pickup_weapon_body
    assert "Weapon_HookFree( client->hook );" in g_client_c
    assert "Weapon_HookFree(self->client->hook);" in g_combat_c
    assert 'case MOD_GRAPPLE: return "Grapple";' in ai_chat_c
    assert "INVENTORY_GRAPPLINGHOOK" in ai_dmq3_c
    assert "ent->s.eType == ET_MISSILE && ent->s.weapon != WP_GRAPPLING_HOOK" in ai_main_c

    assert '{ &cg_disableLoadout_gh, "cg_disableLoadout_gh", "0", CVAR_ROM }' in cg_main_c
    assert '{ &cg_weaponConfig_gh, "cg_weaponConfig_gh", "", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD }' in cg_main_c
    assert '{ "gh", WP_GRAPPLING_HOOK, 10 }' in cg_main_c
    assert '{ "gh", WP_GRAPPLING_HOOK }' in cg_newdraw_c
    assert "{ CUSTOM_SETTING_GRAPPLING_HOOK, WP_GRAPPLING_HOOK }" in cg_newdraw_c
    assert '"g mg sg gl rl lg rg pg bfg gh cg ng pl hmg"' in cg_main_c
    assert "CG_DISABLE_LOADOUT_GH" in cg_servercmds_c
    assert "WP_GRAPPLING_HOOK" in cg_servercmds_c
    assert "cg_pmoveSettings.weaponReloadTimes[cg_retailWeaponReloadOrder[i]] = parsed[i];" in reload_configstring_body
    assert '"grapple"' in respawn_token_body
    assert '"grappling_hook"' in respawn_token_body
    assert "return WP_GRAPPLING_HOOK;" in respawn_token_body
    assert "case MOD_GRAPPLE:" in cg_draw_c
    assert "return cg_weapons[WP_GRAPPLING_HOOK].weaponIcon;" in cg_draw_c
    assert "was caught by" in cg_ents_c or "was caught by" in _read("src/code/cgame/cg_event.c")
    assert "qhandle_t\tgrapplingChainShader;" in cg_local_h
    assert "void CG_GrappleTrail( centity_t *ent, const weaponInfo_t *wi );" in cg_local_h

    for expected in (
        "BG_EvaluateTrajectory( &es->pos, cg.time, origin );",
        "VectorCopy ( cg_entities[ ent->currentState.otherEntityNum ].lerpOrigin, beam.origin );",
        "beam.origin[2] += DEFAULT_VIEWHEIGHT;",
        "AngleVectors( cg_entities[ ent->currentState.otherEntityNum ].lerpAngles, forward, NULL, up );",
        "VectorMA( beam.origin, 14, forward, beam.origin );",
        "VectorMA( beam.origin, -6, up, beam.origin );",
        "if (Distance( beam.origin, beam.oldorigin ) < 64 )",
        "beam.reType = RT_LIGHTNING;",
        "beam.customShader = cgs.media.grapplingChainShader;",
        "beam.customShader = cgs.media.lightningShader;",
        "trap_R_AddRefEntityToScene( &beam );",
    ):
        assert expected in grapple_trail_body

    grapple_register_start = register_weapon_body.index("case WP_GRAPPLING_HOOK:")
    grapple_register_end = register_weapon_body.index("case WP_CHAINGUN:", grapple_register_start)
    grapple_register_body = register_weapon_body[grapple_register_start:grapple_register_end]
    for expected in (
        'weaponInfo->missileModel = trap_R_RegisterModel( "models/weapons2/grapple/grapple_hook.md3" );',
        "weaponInfo->missileTrailFunc = CG_GrappleTrail;",
        "weaponInfo->missileDlight = 200;",
        "weaponInfo->wiTrailTime = 2000;",
        "weaponInfo->trailRadius = 64;",
        'cgs.media.grapplingChainShader = trap_R_RegisterShader( "grapplingChain" );',
        'weaponInfo->readySound = trap_S_RegisterSound( "sound/weapons/grapple/grhang.ogg", qfalse );',
        'weaponInfo->firingSound = trap_S_RegisterSound( "sound/weapons/grapple/grfire.ogg", qfalse );',
        'weaponInfo->missileSound = trap_S_RegisterSound( "sound/weapons/grapple/grfire.ogg", qfalse );',
        'trap_S_RegisterSound( "sound/weapons/grapple/grpull.ogg", qfalse );',
        'trap_S_RegisterSound( "sound/weapons/grapple/grreset.ogg", qfalse );',
    ):
        assert expected in grapple_register_body
    assert "continuousFlash = ( weaponNum == WP_LIGHTNING || weaponNum == WP_GAUNTLET || weaponNum == WP_GRAPPLING_HOOK );" in add_player_weapon_body
    assert "weaponNum == WP_GRAPPLING_HOOK && weapon->ammoModel" in add_player_weapon_body
    assert "CG_GrappleTrail ( cent, weapon );" in cg_grapple_body
    assert "ent.hModel = weapon->missileModel;" in cg_grapple_body
    assert "VectorNormalize2( s1->pos.trDelta, ent.axis[0] )" in cg_grapple_body
    assert "trap_R_AddRefEntityToScene( &ent );" in cg_grapple_body
    assert "case ET_GRAPPLE:" in cg_ents_c
    assert "CG_Grapple( cent );" in cg_ents_c
    assert "if ( weapon == WP_GAUNTLET || weapon == WP_GRAPPLING_HOOK ) {" in cg_newdraw_c
    assert "weaponNum == WP_GRAPPLING_HOOK && weapon->ammoModel" in cg_newdraw_c
    assert "WP_GRAPPLING_HOOK" in g_cmds_c
    assert '"Grapple"' in g_cmds_c


def test_hmg_full_server_and_cgame_wiring_matches_retail() -> None:
    bg_misc_c = _read("src/code/game/bg_misc.c")
    bg_pmove_c = _read("src/code/game/bg_pmove.c")
    bg_pmove_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md")
    bg_public_h = _read("src/code/game/bg_public.h")
    cgame_ghidra = _read("references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c")
    cgame_hlil = _read("references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil.txt")
    cgame_symbols = _read("references/symbol-maps/cgame.json")
    cg_draw_c = _read("src/code/cgame/cg_draw.c")
    cg_local_h = _read("src/code/cgame/cg_local.h")
    cg_main_c = _read("src/code/cgame/cg_main.c")
    cg_newdraw_c = _read("src/code/cgame/cg_newdraw.c")
    cg_playerstate_c = _read("src/code/cgame/cg_playerstate.c")
    cg_servercmds_c = _read("src/code/cgame/cg_servercmds.c")
    cg_weapons_c = _read("src/code/cgame/cg_weapons.c")
    g_active_c = _read("src/code/game/g_active.c")
    g_client_c = _read("src/code/game/g_client.c")
    g_cmds_c = _read("src/code/game/g_cmds.c")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_items_c = _read("src/code/game/g_items.c")
    g_items_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/g_items.md")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_pmove_c = _read("src/code/game/g_pmove.c")
    g_spawn_c = _read("src/code/game/g_spawn.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    inv_h = _read("src/code/game/inv.h")
    qagame_hlil_part02 = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
    qagame_hlil_part03 = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt")
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    lag_hax_body = _function_body(g_weapon_c, "static qboolean G_WeaponUsesLagHaxTimeshift( weapon_t weapon )")
    bullet_body = _function_body(g_weapon_c, "void Bullet_Fire( gentity_t *ent, float spread, int damage, meansOfDeath_t mod )")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    timer_body = _function_body(g_active_c, "void ClientTimerActions( gentity_t *ent, int msec )")
    warmup_ammo_body = _function_body(g_client_c, "static int G_WarmupLevelWeaponAmmo( weapon_t weapon )")
    unlock_tier_body = _function_body(g_items_c, "static int G_GetItemUnlockTier( const gitem_t *item )")
    clamp_body = _function_body(g_combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    mod_to_weapon_body = _function_body(g_combat_c, "static weapon_t G_ModToWeapon( int mod )")
    knockback_body = _function_body(g_combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")
    register_weapon_body = _function_body(cg_weapons_c, "void CG_RegisterWeapon( int weaponNum )")
    hitwall_body = _function_body(
        cg_weapons_c,
        "void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
    )
    hitplayer_body = _function_body(cg_weapons_c, "void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum )")

    hmg_hit_start = hitwall_body.index("case WP_HEAVY_MACHINEGUN:")
    hmg_hit_end = hitwall_body.index("case WP_SHOTGUN:", hmg_hit_start)
    hmg_hit_body = hitwall_body[hmg_hit_start:hmg_hit_end]
    hmg_register_start = register_weapon_body.index("case WP_HEAVY_MACHINEGUN:")
    hmg_register_end = register_weapon_body.index("case WP_SHOTGUN:", hmg_register_start)
    hmg_register_body = register_weapon_body[hmg_register_start:hmg_register_end]
    weapon_enum = bg_public_h[bg_public_h.index("typedef enum {\n\tWP_NONE"):bg_public_h.index("} weapon_t;")]

    assert "| Heavy Machinegun | 75 |" in bg_pmove_hlil
    assert "| Heavy Machinegun | 50 | 200 |" in bg_pmove_hlil
    assert "| 0x1F | 0x0F | Heavy Machine Gun |" in g_items_hlil
    for expected in (
        '"weapon_reload_hmg"',
        '"g_damage_hmg"',
        '"g_knockback_hmg"',
        '"g_startingAmmo_hmg"',
        '"MOD_HMG"',
        '"weapon_hmg"',
        '"ammo_hmg"',
        '"models/weapons3/hmg/hmg.md3"',
        '"models/powerups/ammo/hmgam.md3"',
        '"icons/weap_hmg"',
        '"icons/ammo_hmg"',
        '"gh bfg rl lg rg hmg cg sg pg mg ng gl g pl"',
    ):
        assert expected in qagame_hlil_part02
    assert '"g_ammoPack_hmg"' not in qagame_hlil_part02
    for expected in (
        'char const (* data_1008dda4)[0xd] = data_100872d4 {"g_damage_hmg"}',
        "void* data_1008dda8 = data_1007e004",
        'char const (* data_1008e6bc)[0x10] = data_10086b6c {"g_knockback_hmg"}',
        "void* data_1008e6c0 = data_1007d1d8",
        'char const (* data_1008f31c)[0x13] = data_100860ec {"g_startingAmmo_hmg"}',
        "void* data_1008f320 = data_1007e1fc",
        'char const (* data_1008fc1c)[0x12] = data_10085900 {"weapon_reload_hmg"}',
    ):
        assert expected in qagame_hlil_part03
    for expected in (
        '"normalized_name": "Bullet_Fire"',
        "void Bullet_Fire(gentity_t *ent, float spread, int damage, meansOfDeath_t mod)",
        "classic item-tag order (G, MG, SG, GL, RL, LG, RG, PG, BFG, hook, NG, PL, CG, HMG)",
    ):
        assert expected in qagame_symbols
    for expected in (
        '"cg_weaponConfig_hmg"',
        '"cg_disableLoadout_hmg"',
        '"weapon_reload_hmg"',
        '"weapon_hmg"',
        '"ammo_hmg"',
        '"models/weapons3/hmg/hmg.md3"',
        '"models/powerups/ammo/hmgam.md3"',
        '"icons/weap_hmg"',
        '"icons/ammo_hmg"',
        '"sound/weapons/hmg/machgf1b.ogg"',
        '"sound/weapons/hmg/machgf2b.ogg"',
        '"sound/weapons/hmg/machgf3b.ogg"',
        '"sound/weapons/hmg/machgf4b.ogg"',
    ):
        assert expected in cgame_hlil
    for expected in (
        "sound/weapons/hmg/machgf1b.ogg",
        "sound/weapons/hmg/machgf2b.ogg",
        "sound/weapons/hmg/machgf3b.ogg",
        "sound/weapons/hmg/machgf4b.ogg",
    ):
        assert expected in cgame_ghidra
    for expected in (
        "heavy machinegun in weapon-select order",
        "Machinegun and HMG brass-ejection callback installed by `CG_RegisterWeapon`",
    ):
        assert expected in cgame_symbols

    assert "WP_HEAVY_MACHINEGUN," in bg_public_h
    enum_cursor = -1
    for expected in (
        "WP_NONE",
        "WP_GAUNTLET",
        "WP_MACHINEGUN",
        "WP_SHOTGUN",
        "WP_GRENADE_LAUNCHER",
        "WP_ROCKET_LAUNCHER",
        "WP_LIGHTNING",
        "WP_RAILGUN",
        "WP_PLASMAGUN",
        "WP_BFG",
        "WP_GRAPPLING_HOOK",
        "WP_NAILGUN",
        "WP_PROX_LAUNCHER",
        "WP_CHAINGUN",
        "WP_HEAVY_MACHINEGUN",
        "WP_NUM_WEAPONS",
    ):
        enum_cursor = weapon_enum.index(expected, enum_cursor + 1)
    assert "#define ITEMTAG_WEAPON_HEAVY_MACHINEGUN\t\t14" in bg_public_h
    assert "MOD_HMG," in bg_public_h
    assert "[WP_HEAVY_MACHINEGUN] = 75," in bg_pmove_c
    assert "#define CUSTOM_SETTING_HMG" not in bg_public_h
    assert "CUSTOM_SETTING_HMG" not in g_config_c
    assert "CUSTOM_SETTING_HMG" not in cg_newdraw_c
    assert "CUSTOM_SETTING_CHAINGUN )" in bg_public_h

    for expected in (
        "{ WP_HEAVY_MACHINEGUN, 50, 200, 1, 0.806999981f, 0.647000015f, 0.000000000f, 1.000000000f }",
        "[WP_HEAVY_MACHINEGUN] = 200",
        "ITEMTAG_WEAPON_HEAVY_MACHINEGUN",
        "[ITEMTAG_WEAPON_HEAVY_MACHINEGUN] = \"Heavy Machinegun\"",
        '"weapon_hmg"',
        '"models/weapons3/hmg/hmg.md3"',
        '"icons/weap_hmg"',
        '"Heavy Machinegun"',
        '"ammo_hmg"',
        '"models/powerups/ammo/hmgam.md3"',
        '"icons/ammo_hmg"',
        '"Heavy Bullets"',
    ):
        assert expected in bg_misc_c
    assert "case WP_HEAVY_MACHINEGUN:" in unlock_tier_body
    assert "return 0x0F;" in unlock_tier_body
    assert "#define WEAPONINDEX_HEAVY_MACHINEGUN            14" in inv_h

    for expected in (
        "heavyMachinegunDamage;",
        "extern vmCvar_t g_damage_hmg;",
        "extern vmCvar_t g_knockback_hmg;",
        "extern\tvmCvar_t\tg_startingAmmo_hmg;",
        "extern\tvmCvar_t\tweapon_reload_hmg;",
        "int\t\theavyMachinegun;",
        "float           heavyMachinegun;",
    ):
        assert expected in g_local_h
    for expected in (
        '{ &g_damage_hmg, "g_damage_hmg", "8", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        'g_weaponConfig.heavyMachinegunDamage = G_ReadWeaponCvar( &g_damage_hmg, 8, "g_damage_hmg" );',
        "g_pmoveSettings.weaponReloadTimes[WP_HEAVY_MACHINEGUN]",
        "case WP_HEAVY_MACHINEGUN:",
        'return "HMG";',
        "case MOD_HMG:",
        "return WP_HEAVY_MACHINEGUN;",
    ):
        assert expected in g_main_c
    for expected in (
        "#define DEFAULT_STARTING_AMMO_HMG           50",
        "#define DEFAULT_WEAPON_RELOAD_HMG           75",
        "#define DEFAULT_KNOCKBACK_HMG               1",
        "#define DEFAULT_AMMOPACK_HMG                50",
        '{ &weapon_reload_hmg,      "weapon_reload_hmg",      "0", 0, "Heavy Machinegun refire delay override in milliseconds." }',
        '{ &g_startingAmmo_hmg,     "g_startingAmmo_hmg",     STRINGIZE( DEFAULT_STARTING_AMMO_HMG ), CVAR_GAMERULE, "Heavy Machinegun bullets issued alongside spawn loadouts that include the weapon." }',
        '{ &g_knockback_hmg,        "g_knockback_hmg",        STRINGIZE( DEFAULT_KNOCKBACK_HMG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, "Heavy Machinegun knockback scalar." }',
        'trap_Cvar_Set( "weapon_reload_hmg", "0" );',
        'g_weaponReloadConfig.heavyMachinegun = G_ReadWeaponReloadCvar( &weapon_reload_hmg, DEFAULT_WEAPON_RELOAD_HMG, "weapon_reload_hmg" );',
        'G_AssignAmmoPackEntry( WP_HEAVY_MACHINEGUN, DEFAULT_AMMOPACK_HMG );',
        'g_startingAmmoConfig.heavyMachinegun = G_ReadStartingAmmoCvar( &g_startingAmmo_hmg, DEFAULT_STARTING_AMMO_HMG, "g_startingAmmo_hmg" );',
        'g_knockbackConfig.heavyMachinegun = G_ReadKnockbackCvar( &g_knockback_hmg, DEFAULT_KNOCKBACK_HMG, "g_knockback_hmg" );',
    ):
        assert expected in g_config_c
    assert '"g_ammoPack_hmg"' not in g_config_c

    assert "#define\tHEAVY_MACHINEGUN_SPREAD\t350" in g_weapon_c
    assert "#define\tHEAVY_MACHINEGUN_DAMAGE\t(g_weaponConfig.heavyMachinegunDamage)" in g_weapon_c
    assert "case WP_HEAVY_MACHINEGUN:" in lag_hax_body
    assert "return qtrue;" in lag_hax_body
    assert "if ( mod == MOD_HMG ) {" in bullet_body
    assert "ent->client->pers.accuracy_hits[WP_HEAVY_MACHINEGUN]++;" in bullet_body
    assert "case WP_HEAVY_MACHINEGUN:" in fireweapon_body
    assert "Bullet_Fire( ent, HEAVY_MACHINEGUN_SPREAD, HEAVY_MACHINEGUN_DAMAGE, MOD_HMG );" in fireweapon_body
    assert "case MOD_HMG:" in clamp_body
    assert "configuredDamage = g_weaponConfig.heavyMachinegunDamage;" in clamp_body
    assert "case MOD_HMG:" in mod_to_weapon_body
    assert "return WP_HEAVY_MACHINEGUN;" in mod_to_weapon_body
    assert "case MOD_HMG:" in knockback_body
    assert "return g_knockbackConfig.heavyMachinegun;" in knockback_body

    assert "case WP_HEAVY_MACHINEGUN:" in timer_body
    assert "case WP_HEAVY_MACHINEGUN: max = 50; inc = 4; t = 1000; break;" in timer_body
    assert "case WP_HEAVY_MACHINEGUN:" in warmup_ammo_body
    assert "return 150;" in warmup_ammo_body
    assert "startingAmmoTable[WP_HEAVY_MACHINEGUN] = g_startingAmmoConfig.heavyMachinegun;" in g_client_c
    assert "case WP_HEAVY_MACHINEGUN:" in g_pmove_c
    assert "duration = config->heavyMachinegun;" in g_pmove_c
    assert "#define DISABLE_LOADOUT_HMG\t\t( 1u << 13 )" in g_spawn_c
    assert '{ "hmg", DISABLE_LOADOUT_HMG }' in g_spawn_c
    for expected in (
        "WP_HEAVY_MACHINEGUN",
        '"Gauntlet", "Machinegun", "Shotgun", "Grenade"',
        "WP_NAILGUN, WP_PROX_LAUNCHER, WP_CHAINGUN, WP_HEAVY_MACHINEGUN",
    ):
        assert expected in g_cmds_c

    for expected in (
        "extern\tvmCvar_t\t\tcg_disableLoadout_hmg;",
        "extern\tvmCvar_t\t\tcg_weaponConfig_hmg;",
    ):
        assert expected in cg_local_h
    for expected in (
        'vmCvar_t\tcg_disableLoadout_hmg;',
        'vmCvar_t\tcg_weaponConfig_hmg;',
        '{ &cg_damagePlum, "cg_damagePlum", "g mg sg gl rl lg rg pg bfg gh cg ng pl hmg", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD }',
        '{ &cg_disableLoadout_hmg, "cg_disableLoadout_hmg", "0", CVAR_ROM }',
        '{ &cg_weaponConfig_hmg, "cg_weaponConfig_hmg", "", CVAR_ARCHIVE | CVAR_PROTECTED | CVAR_CLOUD }',
        '{ "hmg", WP_HEAVY_MACHINEGUN, 14 }',
    ):
        assert expected in cg_main_c
    assert "case MOD_HMG:" in cg_draw_c
    assert "return cg_weapons[WP_HEAVY_MACHINEGUN].weaponIcon;" in cg_draw_c
    assert 'if ( !Q_stricmp( token, "heavy_machinegun" ) ) {' in cg_playerstate_c
    assert "return WP_HEAVY_MACHINEGUN;" in cg_playerstate_c
    assert '{ "hmg", WP_HEAVY_MACHINEGUN }' in cg_newdraw_c
    assert "CG_PlacementWeaponFired( WP_HEAVY_MACHINEGUN )" in cg_newdraw_c
    for expected in (
        "CG_1ST_PLYR_FRAGS_HMG",
        "CG_1ST_PLYR_HITS_HMG",
        "CG_1ST_PLYR_SHOTS_HMG",
        "CG_1ST_PLYR_DMG_HMG",
        "CG_1ST_PLYR_ACC_HMG",
    ):
        assert expected in cg_newdraw_c

    for expected in (
        "WP_HEAVY_MACHINEGUN",
        "#define CG_DISABLE_LOADOUT_HMG\t\t( 1u << 13 )",
        '{ "hmg", CG_DISABLE_LOADOUT_HMG }',
    ):
        assert expected in cg_servercmds_c
    assert cg_servercmds_c.index("WP_CHAINGUN,\n\tWP_HEAVY_MACHINEGUN") > cg_servercmds_c.index("static const weapon_t cg_retailWeaponReloadOrder[]")
    assert cg_servercmds_c.index("WP_CHAINGUN,\n\tWP_HEAVY_MACHINEGUN", cg_servercmds_c.index("static const weapon_t cg_retailAccuracyCommandOrder[]")) > 0

    for expected in (
        "case WP_HEAVY_MACHINEGUN:",
        'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/hmg/machgf1b.ogg", qfalse );',
        'weaponInfo->flashSound[1] = trap_S_RegisterSound( "sound/weapons/hmg/machgf2b.ogg", qfalse );',
        'weaponInfo->flashSound[2] = trap_S_RegisterSound( "sound/weapons/hmg/machgf3b.ogg", qfalse );',
        'weaponInfo->flashSound[3] = trap_S_RegisterSound( "sound/weapons/hmg/machgf4b.ogg", qfalse );',
        "weaponInfo->ejectBrassFunc = CG_MachineGunEjectBrass;",
        'cgs.media.bulletExplosionShader = trap_R_RegisterShader( "bulletExplosion" );',
    ):
        assert expected in hmg_register_body
    for expected in (
        "case WP_HEAVY_MACHINEGUN:",
        "mod = cgs.media.bulletFlashModel;",
        "shader = cgs.media.bulletExplosionShader;",
        "mark = cgs.media.bulletMarkShader;",
        "radius = 4;",
    ):
        assert expected in hmg_hit_body
    assert "sfx =" not in hmg_hit_body
    assert "case WP_HEAVY_MACHINEGUN:" not in hitplayer_body


def test_chaingun_full_server_and_cgame_wiring_matches_retail() -> None:
    bg_misc_c = _read("src/code/game/bg_misc.c")
    bg_public_h = _read("src/code/game/bg_public.h")
    bg_pmove_c = _read("src/code/game/bg_pmove.c")
    bg_pmove_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md")
    cgame_symbols = _read("references/symbol-maps/cgame.json")
    cg_local_h = _read("src/code/cgame/cg_local.h")
    cg_main_c = _read("src/code/cgame/cg_main.c")
    cg_newdraw_c = _read("src/code/cgame/cg_newdraw.c")
    cg_playerstate_c = _read("src/code/cgame/cg_playerstate.c")
    cg_weapons_c = _read("src/code/cgame/cg_weapons.c")
    g_active_c = _read("src/code/game/g_active.c")
    g_client_c = _read("src/code/game/g_client.c")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_items_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/g_items.md")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    qagame_hlil_part02 = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt")
    qagame_hlil_part03 = _read("references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part03.txt")
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    lag_hax_body = _function_body(g_weapon_c, "static qboolean G_WeaponUsesLagHaxTimeshift( weapon_t weapon )")
    spread_body = _function_body(g_weapon_c, "static float G_GetChaingunSpread( const gentity_t *ent )")
    bullet_body = _function_body(g_weapon_c, "void Bullet_Fire( gentity_t *ent, float spread, int damage, meansOfDeath_t mod )")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    finish_weapon_change_body = _function_body(bg_pmove_c, "static void PM_FinishWeaponChange( void )")
    pm_weapon_body = _function_body(bg_pmove_c, "static void PM_Weapon( void )")
    clamp_body = _function_body(g_combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    mod_to_weapon_body = _function_body(g_combat_c, "static weapon_t G_ModToWeapon( int mod )")
    knockback_body = _function_body(g_combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")
    spin_angle_body = _function_body(cg_weapons_c, "static float\tCG_MachinegunSpinAngle( centity_t *cent )")
    add_player_weapon_body = _function_body(cg_weapons_c, "void CG_AddPlayerWeapon( refEntity_t *parent, playerState_t *ps, centity_t *cent, int team )")
    register_weapon_body = _function_body(cg_weapons_c, "void CG_RegisterWeapon( int weaponNum )")
    hitwall_body = _function_body(
        cg_weapons_c,
        "void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
    )
    hitplayer_body = _function_body(cg_weapons_c, "void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum )")

    for expected in (
        "STAT_CHAINGUN_SPINUP",
        "WP_CHAINGUN +0xe0 spin accumulator",
        "doubles refire while below 1000 and drains on release",
        "derives chaingun spread from the shared playerState +0xe0 spin accumulator",
    ):
        assert expected in qagame_symbols

    for expected in (
        '"normalized_name": "CG_MachinegunSpinAngle"',
        "SPIN_SPEED",
        "COAST_TIME",
        "plays the chaingun wind-down sound",
    ):
        assert expected in cgame_symbols

    for expected in (
        '"weapon_reload_cg"',
        '"g_damage_cg"',
        '"g_knockback_cg"',
        'ebp_1 = ebp | 0x1000',
    ):
        assert expected in qagame_hlil_part02
    assert 'char const (* data_1008dd5c)[0xc] = data_100872fc {"g_damage_cg"}' in qagame_hlil_part03
    assert "void* data_1008dd60 = data_1007e004" in qagame_hlil_part03

    assert "#define CUSTOM_SETTING_CHAINGUN\t\t\t0x00001000u" in bg_public_h
    assert "STAT_CHAINGUN_SPINUP," in bg_public_h
    assert "WP_CHAINGUN," in bg_public_h
    assert "#define ITEMTAG_WEAPON_CHAINGUN\t\t\t\t13" in bg_public_h
    assert "| Chaingun | 50 |" in bg_pmove_hlil
    assert "| Chaingun | 100 | 400 |" in bg_pmove_hlil
    assert "| 0x17 | 0x0A | Chaingun |" in g_items_hlil

    for expected in (
        "{ WP_CHAINGUN, 100, 400, 0, 0.721000016f, 0.721000016f, 0.721000016f, 1.000000000f }",
        "[WP_CHAINGUN] = 400",
        "ITEMTAG_WEAPON_CHAINGUN",
        "[ITEMTAG_WEAPON_CHAINGUN] = \"Chaingun\"",
        '"ammo_belt"',
        '"models/powerups/ammo/chaingunam.md3"',
        '"icons/icona_chaingun"',
        '"Chaingun Belt"',
        '"weapon_chaingun"',
        '"models/weapons/vulcan/vulcan.md3"',
        '"icons/iconw_chaingun"',
        '"Chaingun"',
        '"sound/weapons/vulcan/wvulwind.wav"',
    ):
        assert expected in bg_misc_c

    for expected in (
        "chaingunDamage;",
        "extern\tvmCvar_t\tg_damage_cg;",
        "extern\tvmCvar_t\tweapon_reload_cg;",
        "extern\tvmCvar_t\tg_startingAmmo_cg;",
        "extern vmCvar_t g_knockback_cg;",
    ):
        assert expected in g_local_h

    for expected in (
        '{ &g_damage_cg, "g_damage_cg", "8", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        'g_weaponConfig.chaingunDamage = G_ReadWeaponCvar( &g_damage_cg, 8, "g_damage_cg" );',
    ):
        assert expected in g_main_c

    for expected in (
        "#define DEFAULT_WEAPON_RELOAD_CG            50",
        "#define DEFAULT_KNOCKBACK_CG                1",
        '{ &weapon_reload_cg,       "weapon_reload_cg",       "0", 0, "Chaingun refire delay override in milliseconds." }',
        '{ &g_startingAmmo_cg,      "g_startingAmmo_cg",      STRINGIZE( DEFAULT_STARTING_AMMO_CG ), CVAR_GAMERULE, "Chaingun bullets provided on spawn when the weapon is part of the configured loadout." }',
        '{ &g_knockback_cg,         "g_knockback_cg",         STRINGIZE( DEFAULT_KNOCKBACK_CG ), CONFIG_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, "Chaingun knockback scalar." }',
        'trap_Cvar_Set( "weapon_reload_cg", "0" );',
        'g_weaponReloadConfig.chaingun = G_ReadWeaponReloadCvar( &weapon_reload_cg, DEFAULT_WEAPON_RELOAD_CG, "weapon_reload_cg" );',
        "G_AssignAmmoPackEntry( WP_CHAINGUN, DEFAULT_AMMOPACK_CG );",
        "g_weaponReloadConfig.chaingun != DEFAULT_WEAPON_RELOAD_CG",
        "g_weaponConfig.chaingunDamage != 8",
        "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.chaingun, DEFAULT_KNOCKBACK_CG )",
        "mask |= CUSTOM_SETTING_CHAINGUN;",
        'g_startingAmmoConfig.chaingun = G_ReadStartingAmmoCvar( &g_startingAmmo_cg, DEFAULT_STARTING_AMMO_CG, "g_startingAmmo_cg" );',
        'g_knockbackConfig.chaingun = G_ReadKnockbackCvar( &g_knockback_cg, DEFAULT_KNOCKBACK_CG, "g_knockback_cg" );',
    ):
        assert expected in g_config_c
    assert '"g_ammoPack_cg"' not in g_config_c

    for expected in (
        "case WP_CHAINGUN:",
        "return qtrue;",
    ):
        assert expected in lag_hax_body

    for expected in (
        "return 700.0f;",
        "chaingunSpin = (float)ent->client->ps.stats[STAT_CHAINGUN_SPINUP];",
        "chaingunSpin = 0.0f;",
        "chaingunSpin = 1000.0f;",
        "spread = 700.0f + ( chaingunSpin / 1000.0f ) * 700.0f;",
        "spread = 700.0f;",
        "spread = 1400.0f;",
    ):
        assert expected in spread_body

    assert "#define\tCHAINGUN_DAMAGE\t\t(g_weaponConfig.chaingunDamage)" in g_weapon_c
    assert "case WP_CHAINGUN:" in fireweapon_body
    assert "Bullet_Fire( ent, G_GetChaingunSpread( ent ), CHAINGUN_DAMAGE, MOD_CHAINGUN );" in fireweapon_body
    assert "if ( mod == MOD_CHAINGUN ) {" in bullet_body
    assert "ent->client->pers.accuracy_hits[WP_CHAINGUN]++;" in bullet_body

    assert "pm->ps->stats[STAT_CHAINGUN_SPINUP] = 0;" in finish_weapon_change_body
    for expected in (
        "pm->ps->stats[STAT_CHAINGUN_SPINUP] -= pml.msec;",
        "pm->ps->stats[STAT_CHAINGUN_SPINUP] = 0;",
        "pm->ps->stats[STAT_CHAINGUN_SPINUP] = 1000;",
        "addTime = PM_GetWeaponReloadTime( (weapon_t)pm->ps->weapon );",
        "if ( pm->ps->weapon == WP_CHAINGUN ) {",
        "if ( pm->ps->stats[STAT_CHAINGUN_SPINUP] < 1000 ) {",
        "addTime *= 2;",
        "pm->ps->stats[STAT_CHAINGUN_SPINUP] += addTime;",
    ):
        assert expected in pm_weapon_body
    assert pm_weapon_body.index("if ( pm->ps->weapon == WP_CHAINGUN ) {") < pm_weapon_body.index("BG_PlayerHasPersistantPowerup( pm->ps, PW_SCOUT )")

    assert "case MOD_CHAINGUN:" in clamp_body
    assert "configuredDamage = g_weaponConfig.chaingunDamage;" in clamp_body
    assert "case MOD_CHAINGUN:" in mod_to_weapon_body
    assert "return WP_CHAINGUN;" in mod_to_weapon_body
    assert "case MOD_CHAINGUN:" in knockback_body
    assert "return g_knockbackConfig.chaingun;" in knockback_body
    assert "case MOD_CHAINGUN:" in g_main_c
    assert "return \"CHAINGUN\";" in g_main_c

    for expected in (
        "case WP_CHAINGUN: max = 100; inc = 5; t = 1000; break;",
        "startingAmmoTable[WP_CHAINGUN] = g_startingAmmoConfig.chaingun;",
    ):
        assert expected in g_active_c + g_client_c

    for expected in (
        "float\t\t\tbarrelAngle;",
        "int\t\t\t\tbarrelTime;",
        "qboolean\t\tbarrelSpinning;",
        "sfxHandle_t\tsfx_chghit;",
        "sfxHandle_t\tsfx_chghitflesh;",
        "sfxHandle_t\tsfx_chghitmetal;",
        "sfxHandle_t\tsfx_chgwind;",
    ):
        assert expected in cg_local_h

    for expected in (
        '{ "cg", WP_CHAINGUN, 13 }',
        'cgs.media.sfx_chghit = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpd.ogg", qfalse );',
        'cgs.media.sfx_chghitflesh = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpl.ogg", qfalse );',
        'cgs.media.sfx_chghitmetal = trap_S_RegisterSound( "sound/weapons/vulcan/wvulimpm.ogg", qfalse );',
        'cgs.media.sfx_chgwind = trap_S_RegisterSound( "sound/weapons/vulcan/wvulwind.ogg", qfalse );',
    ):
        assert expected in cg_main_c

    for expected in (
        'if ( !Q_stricmp( token, "chaingun" ) ) {',
        "return WP_CHAINGUN;",
        '{ "cg", WP_CHAINGUN }',
        "{ CUSTOM_SETTING_CHAINGUN, WP_CHAINGUN }",
        "CG_PlacementWeaponFired( WP_CHAINGUN )",
    ):
        assert expected in cg_playerstate_c + cg_newdraw_c

    for expected in (
        "#define\t\tSPIN_SPEED\t0.9",
        "#define\t\tCOAST_TIME\t1000",
    ):
        assert expected in cg_weapons_c
    for expected in (
        "delta = cg.time - cent->pe.barrelTime;",
        "angle = cent->pe.barrelAngle + delta * SPIN_SPEED;",
        "speed = 0.5 * ( SPIN_SPEED + (float)( COAST_TIME - delta ) / COAST_TIME );",
        "cent->pe.barrelAngle = AngleMod( angle );",
        "cent->pe.barrelSpinning = !!(cent->currentState.eFlags & EF_FIRING);",
        "if ( cent->currentState.weapon == WP_CHAINGUN && !cent->pe.barrelSpinning ) {",
        "trap_S_StartSound( NULL, cent->currentState.number, CHAN_WEAPON, cgs.media.sfx_chgwind );",
    ):
        assert expected in spin_angle_body
    assert "angles[ROLL] = CG_MachinegunSpinAngle( cent );" in add_player_weapon_body

    for expected in (
        "case WP_CHAINGUN:",
        'weaponInfo->firingSound = trap_S_RegisterSound( "sound/weapons/vulcan/wvulfire.ogg", qfalse );',
        "weaponInfo->loopFireSound = qtrue;",
        'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf1b.ogg", qfalse );',
        'weaponInfo->flashSound[1] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf2b.ogg", qfalse );',
        'weaponInfo->flashSound[2] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf3b.ogg", qfalse );',
        'weaponInfo->flashSound[3] = trap_S_RegisterSound( "sound/weapons/vulcan/vulcanf4b.ogg", qfalse );',
        "weaponInfo->ejectBrassFunc = CG_MachineGunEjectBrass;",
        'cgs.media.bulletExplosionShader = trap_R_RegisterShader( "bulletExplosion" );',
    ):
        assert expected in register_weapon_body

    for expected in (
        "case WP_CHAINGUN:",
        "mod = cgs.media.bulletFlashModel;",
        "sfx = cgs.media.sfx_chghitflesh;",
        "sfx = cgs.media.sfx_chghitmetal;",
        "sfx = cgs.media.sfx_chghit;",
        "mark = cgs.media.bulletMarkShader;",
        "r = rand() & 3;",
        "sfx = cgs.media.sfx_ric1;",
        "sfx = cgs.media.sfx_ric2;",
        "sfx = cgs.media.sfx_ric3;",
        "radius = 8;",
    ):
        assert expected in hitwall_body

    for expected in (
        "case WP_CHAINGUN:",
        "CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );",
    ):
        assert expected in hitplayer_body


def test_railgun_server_fire_path_matches_retail_trace_event_and_config_wiring() -> None:
    bg_public_h = _read("src/code/game/bg_public.h")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    railgun_body = _function_body(g_weapon_c, "void weapon_railgun_fire (gentity_t *ent)")
    railjump_body = _function_body(g_weapon_c, "static void G_ApplyRailJump( gentity_t *ent )")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    timeshift_body = _function_body(g_weapon_c, "static qboolean G_WeaponUsesLagHaxTimeshift( weapon_t weapon )")
    muzzle_offset_body = _function_body(g_weapon_c, "static float G_GetMuzzleForwardOffset( const gentity_t *ent )")

    assert '"normalized_name": "weapon_railgun_fire"' in qagame_symbols
    assert '"status": "matched"' in qagame_symbols
    assert "Exact match for g_weapon.c::weapon_railgun_fire" in qagame_symbols

    assert "railJumpStrength;" in g_local_h
    assert "railgunDamage;" in g_local_h
    assert "railgunHeadshotDamage;" in g_local_h
    assert 'extern vmCvar_t g_railJump;' in g_local_h
    assert 'extern vmCvar_t g_headShotDamage_rg;' in g_local_h
    assert '#define CUSTOM_SETTING_RAILGUN\t\t\t0x00000040u' in bg_public_h
    assert '#define CUSTOM_SETTING_HEADSHOTS\t\t0x00800000u' in bg_public_h
    assert '#define CUSTOM_SETTING_RAIL_JUMPING\t\t0x01000000u' in bg_public_h

    for expected in (
        '{ &g_damage_rg, "g_damage_rg", "80", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        '{ &g_railJump, "g_railJump", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_headShotDamage_rg, "g_headShotDamage_rg", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        'g_weaponConfig.railJumpStrength = G_ReadWeaponCvarNonNegative( &g_railJump, 0, "g_railJump" );',
        'g_weaponConfig.railgunDamage = G_ReadWeaponCvar( &g_damage_rg, 80, "g_damage_rg" );',
        'g_weaponConfig.railgunHeadshotDamage = G_ReadWeaponCvarNonNegative( &g_headShotDamage_rg, 0, "g_headShotDamage_rg" );',
        "if ( g_headShotDamage_rg.integer != 0 ) {",
        "mask |= CUSTOM_SETTING_HEADSHOTS;",
        "if ( g_railJump.integer != 0 ) {",
        "mask |= CUSTOM_SETTING_RAIL_JUMPING;",
    ):
        assert expected in g_main_c

    for expected in (
        "g_weaponReloadConfig.railgun != DEFAULT_WEAPON_RELOAD_RG",
        "g_weaponConfig.railgunDamage != 80",
        "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.railgun, DEFAULT_KNOCKBACK_RG )",
        "mask |= CUSTOM_SETTING_RAILGUN;",
    ):
        assert expected in g_config_c

    assert "case WP_RAILGUN:" in timeshift_body
    assert "return 3.0f;" in muzzle_offset_body
    assert "return 5.0f;" in muzzle_offset_body
    assert "case WP_RAILGUN:" in fireweapon_body
    assert "weapon_railgun_fire( ent );" in fireweapon_body

    for expected in (
        "railJumpStrength = g_weaponConfig.railJumpStrength;",
        "if ( railJumpStrength <= 0 ) {",
        "VectorMA( muzzle, 120.0f, forward, end );",
        "trap_Trace( &trace, muzzle, NULL, NULL, end, ent->s.number, CONTENTS_SOLID );",
        "if ( trace.fraction == 1.0f ) {",
        "VectorNormalize( pushDir );",
        "ent->client->ps.velocity[0] -= railJumpStrength * pushDir[0];",
        "ent->client->ps.velocity[1] -= railJumpStrength * pushDir[1];",
        "ent->client->ps.velocity[2] -= railJumpStrength * pushDir[2];",
        "ent->client->ps.velocity[2] += 20.0f;",
    ):
        assert expected in railjump_body

    assert "#define\tMAX_RAIL_HITS\t4" in g_weapon_c
    for expected in (
        "damage = g_weaponConfig.railgunDamage * s_quadFactor;",
        "G_ApplyRailJump( ent );",
        "VectorMA (muzzle, 8192, forward, end);",
        "passent = ent->s.number;",
        "trap_Trace (&trace, muzzle, NULL, NULL, end, passent, MASK_SHOT );",
        "if ( trace.entityNum >= ENTITYNUM_MAX_NORMAL ) {",
        "G_InvulnerabilityEffect( traceEnt, forward, trace.endpos, impactpoint, bouncedir )",
        "G_BounceProjectile( muzzle, impactpoint, bouncedir, end );",
        "tent = G_TempEntity( trace.endpos, EV_RAILTRAIL );",
        "tent->s.clientNum = ent->s.clientNum;",
        "VectorMA( tent->s.origin2, 4, right, tent->s.origin2 );",
        "VectorMA( tent->s.origin2, -1, up, tent->s.origin2 );",
        "tent->s.eventParm = 255;",
        "passent = ENTITYNUM_NONE;",
        "G_Damage( traceEnt, ent, ent, forward, trace.endpos, shotDamage, 0, MOD_RAILGUN );",
        "if ( trace.contents & CONTENTS_SOLID ) {",
        "trap_UnlinkEntity( traceEnt );",
        "trap_LinkEntity( unlinkedEntities[i] );",
        "SnapVectorTowards( trace.endpos, muzzle );",
        "tent->s.eventParm = DirToByte( trace.plane.normal );",
        "ent->client->accurateCount = 0;",
        "ent->client->accurateCount += hits;",
        "ent->client->ps.persistant[PERS_IMPRESSIVE_COUNT]++;",
        'G_RankSendPlayerMedal( ent, "IMPRESSIVE" );',
        "ent->client->accuracy_hits++;",
        "ent->client->pers.accuracy_hits[WP_RAILGUN]++;",
    ):
        assert expected in railgun_body

    assert "MOD_RAILGUN_HEADSHOT" not in railgun_body
    assert "if ( mod == MOD_RAILGUN && G_IsRailgunHeadshot( targ, point ) ) {" in g_combat_c
    assert "damage += g_weaponConfig.railgunHeadshotDamage;" in g_combat_c


def test_lightning_path_uses_retail_falloff_and_muzzle_discharge_gate() -> None:
    g_weapon_c = _read("src/code/game/g_weapon.c")
    lightning_body = _function_body(g_weapon_c, "void Weapon_LightningFire( gentity_t *ent )")

    assert "muzzleContents = trap_PointContents( muzzle, ENTITYNUM_NONE );" in lightning_body
    assert "trap_Trace( &dischargeTrace" not in lightning_body
    assert "dischargeAmmo = Weapon_GetLightningDischargeAmmoCount( ent );" in lightning_body
    assert "dischargeDamage = dischargeAmmo * g_weaponConfig.lightningDamage;" in lightning_body
    assert "dischargeRadius = dischargeDamage + 16.0f;" in lightning_body
    assert "ent->client->ps.ammo[WP_LIGHTNING] = 0;" in lightning_body
    assert "tent = G_TempEntity( dischargePoint, EV_LIGHTNING_DISCHARGE );" in lightning_body
    assert "tent->s.eventParm = dischargeAmmo;" in lightning_body
    assert "G_TempEntity( dischargePoint, EV_LIGHTNINGBOLT )" not in lightning_body
    assert "VectorCopy( muzzle, tent->s.origin2 );" not in lightning_body
    assert "Weapon_LightningDischargeDamage( dischargePoint, ent, dischargeDamage, dischargeRadius )" in lightning_body
    assert "MOD_LIGHTNING_DISCHARGE );" not in lightning_body
    assert "damage = G_GetLightningDamageForDistance( distance ) * s_quadFactor;" in lightning_body


def test_plasmagun_server_projectile_config_and_custom_mask_match_retail() -> None:
    bg_public_h = _read("src/code/game/bg_public.h")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    plasmagun_body = _function_body(g_weapon_c, "void Weapon_Plasmagun_Fire (gentity_t *ent)")
    fire_plasma_body = _function_body(g_missile_c, "gentity_t *fire_plasma (gentity_t *self, vec3_t start, vec3_t dir)")
    accel_enabled_body = _function_body(g_missile_c, "static qboolean G_MissileAccelerationEnabled( float accelerationFactor )")
    plasma_accel_body = _function_body(g_missile_c, "static void G_RunPlasmaAccelerationThink( gentity_t *ent )")
    clamp_body = _function_body(g_combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    knockback_body = _function_body(g_combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")

    assert '"normalized_name": "fire_plasma"' in qagame_symbols
    assert '"normalized_name": "Weapon_Plasmagun_Fire"' in qagame_symbols
    assert '"normalized_name": "G_RunPlasmaAccelerationThink"' in qagame_symbols
    assert "Exact plasma projectile constructor" in qagame_symbols
    assert "Retail plasma wrapper around the plasma projectile factory" in qagame_symbols

    assert '#define CUSTOM_SETTING_PLASMAGUN\t\t0x00000080u' in bg_public_h
    for expected in (
        "plasmaDamage;",
        "plasmaSplashDamage;",
        "plasmaSplashRadius;",
        "plasmaSpeed;",
        "plasmaAccelerationFactor;",
        "plasmaAccelerationRate;",
        "extern vmCvar_t g_accelFactor_pg;",
        "extern vmCvar_t g_velocity_pg;",
        "extern\tvmCvar_t\tg_damage_pg;",
        "extern\tvmCvar_t\tg_splashDamage_pg;",
        "extern\tvmCvar_t\tg_splashRadius_pg;",
    ):
        assert expected in g_local_h

    for expected in (
        '{ &g_damage_pg, "g_damage_pg", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        '{ &g_splashDamage_pg, "g_splashdamage_pg", "15", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        '{ &g_splashRadius_pg, "g_splashradius_pg", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        '{ &g_accelFactor_pg, "g_accelFactor_pg", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_accelRate_pg, "g_accelRate_pg", "16", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_velocity_pg, "g_velocity_pg", "2000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        'g_weaponConfig.plasmaDamage = G_ReadWeaponCvar( &g_damage_pg, 20, "g_damage_pg" );',
        'g_weaponConfig.plasmaSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pg, 15, "g_splashdamage_pg" );',
        'g_weaponConfig.plasmaSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pg, 20, "g_splashradius_pg" );',
        'g_weaponConfig.plasmaSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_pg, 2000, "g_velocity_pg", 1 );',
        'g_weaponConfig.plasmaAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_pg, 1.0f, "g_accelFactor_pg" );',
        'g_weaponConfig.plasmaAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_pg, 16, "g_accelRate_pg" );',
    ):
        assert expected in g_main_c

    for expected in (
        "g_weaponReloadConfig.plasmagun != DEFAULT_WEAPON_RELOAD_PG",
        "g_weaponConfig.plasmaDamage != 20",
        "g_weaponConfig.plasmaSplashDamage != 15",
        "g_weaponConfig.plasmaSplashRadius != 20",
        "g_weaponConfig.plasmaSpeed != 2000",
        "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.plasmagun, DEFAULT_KNOCKBACK_PG )",
        "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.plasmagunSelf, DEFAULT_KNOCKBACK_PG_SELF )",
        "G_ConfigFloatDiffersFromDefault( g_weaponConfig.plasmaAccelerationFactor, 1.0f )",
        "g_weaponConfig.plasmaAccelerationRate != 16",
        "mask |= CUSTOM_SETTING_PLASMAGUN;",
    ):
        assert expected in g_config_c
    assert "G_ConfigFloatDiffersFromDefault( g_weaponConfig.plasmaAccelerationFactor, 0.0f )" not in g_config_c

    assert "case WP_PLASMAGUN:" in fireweapon_body
    assert "Weapon_Plasmagun_Fire( ent );" in fireweapon_body
    assert "m = fire_plasma (ent, muzzle, forward);" in plasmagun_body
    assert "m->damage *= s_quadFactor;" in plasmagun_body
    assert "m->splashDamage *= s_quadFactor;" in plasmagun_body

    assert "return ( accelerationFactor != 1.0f ) ? qtrue : qfalse;" in accel_enabled_body
    assert "VectorScale( ent->s.pos.trDelta, g_weaponConfig.plasmaAccelerationFactor, ent->s.pos.trDelta );" in plasma_accel_body
    assert "ent->nextthink = level.time + G_GetMissileAccelerationThinkTime( g_weaponConfig.plasmaAccelerationRate );" in plasma_accel_body
    for expected in (
        "VectorNormalize (dir);",
        "bolt = G_Spawn();",
        'bolt->classname = "plasma";',
        "bolt->nextthink = level.time + 10000;",
        "bolt->think = G_ExplodeMissile;",
        "bolt->s.eType = ET_MISSILE;",
        "bolt->r.svFlags = SVF_USE_CURRENT_ORIGIN;",
        "bolt->s.weapon = WP_PLASMAGUN;",
        "bolt->r.ownerNum = self->s.number;",
        "bolt->parent = self;",
        "bolt->damage = g_weaponConfig.plasmaDamage;",
        "bolt->splashDamage = g_weaponConfig.plasmaSplashDamage;",
        "bolt->splashRadius = g_weaponConfig.plasmaSplashRadius;",
        "bolt->methodOfDeath = MOD_PLASMA;",
        "bolt->splashMethodOfDeath = MOD_PLASMA_SPLASH;",
        "bolt->clipmask = MASK_SHOT;",
        "bolt->target_ent = NULL;",
        "bolt->speed = ( float )g_weaponConfig.plasmaSpeed;",
        "bolt->s.pos.trType = TR_LINEAR;",
        "bolt->s.pos.trTime = level.time - MISSILE_PRESTEP_TIME;",
        "VectorCopy( start, bolt->s.pos.trBase );",
        "VectorScale( dir, ( float )g_weaponConfig.plasmaSpeed, bolt->s.pos.trDelta );",
        "SnapVector( bolt->s.pos.trDelta );",
        "VectorCopy (start, bolt->r.currentOrigin);",
        "if ( G_MissileAccelerationEnabled( g_weaponConfig.plasmaAccelerationFactor ) ) {",
        "bolt->nextthink = level.time + G_GetMissileAccelerationThinkTime( g_weaponConfig.plasmaAccelerationRate );",
        "bolt->think = G_RunPlasmaAccelerationThink;",
    ):
        assert expected in fire_plasma_body

    assert "case MOD_PLASMA:" in clamp_body
    assert "configuredDamage = g_weaponConfig.plasmaDamage;" in clamp_body
    assert "case MOD_PLASMA_SPLASH:" in clamp_body
    assert "configuredDamage = g_weaponConfig.plasmaSplashDamage;" in clamp_body
    assert "case MOD_PLASMA:" in knockback_body
    assert "case MOD_PLASMA_SPLASH:" in knockback_body
    assert "return selfInflicted ? g_knockbackConfig.plasmagunSelf : g_knockbackConfig.plasmagun;" in knockback_body


def test_bfg_server_projectile_config_and_custom_mask_match_retail() -> None:
    bg_public_h = _read("src/code/game/bg_public.h")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    bfg_body = _function_body(g_weapon_c, "void BFG_Fire ( gentity_t *ent )")
    fire_bfg_body = _function_body(g_missile_c, "gentity_t *fire_bfg (gentity_t *self, vec3_t start, vec3_t dir)")
    accel_enabled_body = _function_body(g_missile_c, "static qboolean G_MissileAccelerationEnabled( float accelerationFactor )")
    bfg_accel_body = _function_body(g_missile_c, "static void G_RunBfgAccelerationThink( gentity_t *ent )")
    clamp_body = _function_body(g_combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    knockback_body = _function_body(g_combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")

    assert '"normalized_name": "fire_bfg"' in qagame_symbols
    assert '"normalized_name": "BFG_Fire"' in qagame_symbols
    assert '"normalized_name": "G_RunBfgAccelerationThink"' in qagame_symbols
    assert "Exact BFG projectile constructor" in qagame_symbols
    assert "Retail BFG wrapper around the BFG projectile factory" in qagame_symbols
    assert "Descriptive retail-only BFG acceleration callback" in qagame_symbols

    assert "#define CUSTOM_SETTING_BFG" in bg_public_h
    assert "0x00000100u" in bg_public_h
    for expected in (
        "bfgDamage;",
        "bfgSplashDamage;",
        "bfgSplashRadius;",
        "bfgSpeed;",
        "bfgAccelerationFactor;",
        "bfgAccelerationRate;",
        "extern vmCvar_t g_accelFactor_bfg;",
        "extern vmCvar_t g_accelRate_bfg;",
        "extern vmCvar_t g_velocity_bfg;",
        "extern\tvmCvar_t\tg_damage_bfg;",
        "extern\tvmCvar_t\tg_splashDamage_bfg;",
        "extern\tvmCvar_t\tg_splashRadius_bfg;",
    ):
        assert expected in g_local_h

    for expected in (
        '{ &g_damage_bfg, "g_damage_bfg", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        '{ &g_splashDamage_bfg, "g_splashdamage_bfg", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        '{ &g_splashRadius_bfg, "g_splashradius_bfg", "80", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue },',
        '{ &g_accelFactor_bfg, "g_accelFactor_bfg", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_accelRate_bfg, "g_accelRate_bfg", "16", CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_velocity_bfg, "g_velocity_bfg", "1800", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        'g_weaponConfig.bfgDamage = G_ReadWeaponCvar( &g_damage_bfg, 100, "g_damage_bfg" );',
        'g_weaponConfig.bfgSplashDamage = G_ReadWeaponCvar( &g_splashDamage_bfg, 100, "g_splashdamage_bfg" );',
        'g_weaponConfig.bfgSplashRadius = G_ReadWeaponCvar( &g_splashRadius_bfg, 80, "g_splashradius_bfg" );',
        'g_weaponConfig.bfgSpeed = G_ReadWeaponCvarAtLeast( &g_velocity_bfg, 1800, "g_velocity_bfg", 1 );',
        'g_weaponConfig.bfgAccelerationFactor = G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_bfg, 1.0f, "g_accelFactor_bfg" );',
        'g_weaponConfig.bfgAccelerationRate = G_ReadWeaponCvarNonNegative( &g_accelRate_bfg, 16, "g_accelRate_bfg" );',
    ):
        assert expected in g_main_c

    for expected in (
        "g_weaponReloadConfig.bfg != DEFAULT_WEAPON_RELOAD_BFG",
        "g_weaponConfig.bfgDamage != 100",
        "g_weaponConfig.bfgSplashDamage != 100",
        "g_weaponConfig.bfgSplashRadius != 80",
        "g_weaponConfig.bfgSpeed != 1800",
        "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.bfg, DEFAULT_KNOCKBACK_BFG )",
        "G_ConfigFloatDiffersFromDefault( g_weaponConfig.bfgAccelerationFactor, 1.0f )",
        "g_weaponConfig.bfgAccelerationRate != 16",
        "mask |= CUSTOM_SETTING_BFG;",
    ):
        assert expected in g_config_c
    assert "G_ConfigFloatDiffersFromDefault( g_weaponConfig.bfgAccelerationFactor, 0.0f )" not in g_config_c

    assert "case WP_BFG:" in fireweapon_body
    assert "BFG_Fire( ent );" in fireweapon_body
    assert "m = fire_bfg (ent, muzzle, forward);" in bfg_body
    assert "m->damage *= s_quadFactor;" in bfg_body
    assert "m->splashDamage *= s_quadFactor;" in bfg_body

    assert "return ( accelerationFactor != 1.0f ) ? qtrue : qfalse;" in accel_enabled_body
    assert "VectorScale( ent->s.pos.trDelta, g_weaponConfig.bfgAccelerationFactor, ent->s.pos.trDelta );" in bfg_accel_body
    assert "ent->nextthink = level.time + G_GetMissileAccelerationThinkTime( g_weaponConfig.bfgAccelerationRate );" in bfg_accel_body
    for expected in (
        "VectorNormalize (dir);",
        "bolt = G_Spawn();",
        'bolt->classname = "bfg";',
        "bolt->nextthink = level.time + 10000;",
        "bolt->think = G_ExplodeMissile;",
        "bolt->s.eType = ET_MISSILE;",
        "bolt->r.svFlags = SVF_USE_CURRENT_ORIGIN;",
        "bolt->s.weapon = WP_BFG;",
        "bolt->r.ownerNum = self->s.number;",
        "bolt->parent = self;",
        "bolt->damage = g_weaponConfig.bfgDamage;",
        "bolt->splashDamage = g_weaponConfig.bfgSplashDamage;",
        "bolt->splashRadius = g_weaponConfig.bfgSplashRadius;",
        "bolt->methodOfDeath = MOD_BFG;",
        "bolt->splashMethodOfDeath = MOD_BFG_SPLASH;",
        "bolt->clipmask = MASK_SHOT;",
        "bolt->target_ent = NULL;",
        "bolt->speed = ( float )g_weaponConfig.bfgSpeed;",
        "bolt->s.pos.trType = TR_LINEAR;",
        "bolt->s.pos.trTime = level.time - MISSILE_PRESTEP_TIME;",
        "VectorCopy( start, bolt->s.pos.trBase );",
        "VectorScale( dir, ( float )g_weaponConfig.bfgSpeed, bolt->s.pos.trDelta );",
        "SnapVector( bolt->s.pos.trDelta );",
        "VectorCopy (start, bolt->r.currentOrigin);",
        "if ( G_MissileAccelerationEnabled( g_weaponConfig.bfgAccelerationFactor ) ) {",
        "bolt->nextthink = level.time + G_GetMissileAccelerationThinkTime( g_weaponConfig.bfgAccelerationRate );",
        "bolt->think = G_RunBfgAccelerationThink;",
    ):
        assert expected in fire_bfg_body

    assert "case MOD_BFG:" in clamp_body
    assert "configuredDamage = g_weaponConfig.bfgDamage;" in clamp_body
    assert "case MOD_BFG_SPLASH:" in clamp_body
    assert "configuredDamage = g_weaponConfig.bfgSplashDamage;" in clamp_body
    assert "case MOD_BFG:" in knockback_body
    assert "case MOD_BFG_SPLASH:" in knockback_body
    assert "return g_knockbackConfig.bfg;" in knockback_body


def test_nailgun_server_projectile_damage_bounce_and_custom_mask_match_retail() -> None:
    bg_public_h = _read("src/code/game/bg_public.h")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_local_h = _read("src/code/game/g_local.h")
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_pmove_c = _read("src/code/game/g_pmove.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    qagame_ghidra = _read("references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c")
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    nailgun_body = _function_body(g_weapon_c, "void Weapon_Nailgun_Fire (gentity_t *ent)")
    fire_nail_body = _function_body(g_missile_c, "gentity_t *fire_nail( gentity_t *self, vec3_t start, vec3_t forward, vec3_t right, vec3_t up )")
    run_missile_body = _function_body(g_missile_c, "void G_RunMissile( gentity_t *ent )")
    nail_bounce_body = _function_body(g_missile_c, "static qboolean G_HandleNailgunBounce( gentity_t *ent, trace_t *trace )")
    clamp_body = _function_body(g_combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    mod_to_weapon_body = _function_body(g_combat_c, "static weapon_t G_ModToWeapon( int mod )")
    knockback_body = _function_body(g_combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")

    assert '"normalized_name": "Weapon_Nailgun_Fire"' in qagame_symbols
    assert "Retail nailgun wrapper" in qagame_symbols
    assert '"normalized_name": "G_RunMissile"' in qagame_symbols
    assert "nail ricochet gating" in qagame_symbols
    for expected in (
        "if (0 < DAT_1059e9cc) {",
        "*(int *)(iVar1 + 0x328) = (int)_DAT_105950c8;",
        "*(undefined4 *)(iVar1 + 0x338) = 0x17;",
        "*(uint *)(iVar1 + 0xc) = (-(uint)(DAT_1059abec != 0) & 3) + 2;",
        "if ((DAT_105ab8cc != 0) && (iVar2 = rand(), 100 - _DAT_1059f74c < iVar2 % 100 + 1)) {",
        "*(undefined4 *)(iVar1 + 8) = 0x100000;",
        "} while (local_30 < DAT_1059e9cc);",
        "(*(int *)(param_2 + 0x36c) < DAT_105ab8cc)",
    ):
        assert expected in qagame_ghidra

    assert "#define CUSTOM_SETTING_NAILGUN" in bg_public_h
    assert "0x00000400u" in bg_public_h
    for expected in (
        "nailgunCount;",
        "nailgunDamage;",
        "nailgunSpeed;",
        "nailgunSpread;",
        "nailgunBounceCount;",
        "nailgunBounceEnabled;",
        "nailgunBouncePercentage;",
        "extern vmCvar_t g_nailbounce;",
        "extern vmCvar_t g_nailbouncepercentage;",
        "extern vmCvar_t g_nailcount;",
        "extern vmCvar_t g_nailspeed;",
        "extern vmCvar_t g_nailspread;",
        "extern\tvmCvar_t\tg_damage_ng;",
    ):
        assert expected in g_local_h
    assert "nailgunGravityEnabled" not in g_local_h
    assert "g_nailgravity" not in g_local_h

    for expected in (
        '{ &g_damage_ng, "g_damage_ng", "12", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_nailbounce, "g_nailbounce", "1", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailbouncepercentage, "g_nailbouncepercentage", "65", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailcount, "g_nailcount", "10", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailspeed, "g_nailspeed", "1000", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        '{ &g_nailspread, "g_nailspread", "400", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse, qfalse,',
        'g_weaponConfig.nailgunCount = G_ReadWeaponCvarNonNegative( &g_nailcount, 10, "g_nailcount" );',
        'g_weaponConfig.nailgunDamage = G_ReadWeaponCvar( &g_damage_ng, 12, "g_damage_ng" );',
        'g_weaponConfig.nailgunSpeed = G_ReadWeaponCvarAtLeast( &g_nailspeed, 1000, "g_nailspeed", 1 );',
        'g_weaponConfig.nailgunSpread = G_ReadWeaponCvarNonNegative( &g_nailspread, 400, "g_nailspread" );',
        'g_weaponConfig.nailgunBounceCount = G_ReadWeaponCvarNonNegative( &g_nailbounce, 1, "g_nailbounce" );',
        "g_weaponConfig.nailgunBounceEnabled = ( g_weaponConfig.nailgunBounceCount > 0 ) ? qtrue : qfalse;",
        'g_weaponConfig.nailgunBouncePercentage = G_ReadWeaponCvarNonNegative( &g_nailbouncepercentage, 65, "g_nailbouncepercentage" );',
        "if ( g_weaponConfig.nailgunBouncePercentage > 100 ) {",
        "g_weaponConfig.nailgunBouncePercentage = 100;",
    ):
        assert expected in g_main_c
    assert '"g_nailgravity"' not in g_main_c

    for expected in (
        "g_weaponReloadConfig.nailgun != DEFAULT_WEAPON_RELOAD_NG",
        "g_weaponConfig.nailgunCount != 10",
        "g_weaponConfig.nailgunDamage != 12",
        "g_weaponConfig.nailgunSpeed != 1000",
        "g_weaponConfig.nailgunSpread != 400",
        "g_weaponConfig.nailgunBounceCount != 1",
        "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.nailgun, DEFAULT_KNOCKBACK_NG )",
        "g_weaponConfig.nailgunBouncePercentage != 65",
        "mask |= CUSTOM_SETTING_NAILGUN;",
    ):
        assert expected in g_config_c
    assert "g_damage_ng.integer != 12" not in g_config_c
    assert "g_nailbounce.integer != 1" not in g_config_c
    assert "g_nailbouncepercentage.integer != 65" not in g_config_c

    for expected in (
        'trap_Cvar_Set( "g_nailbounce", "1" );',
        'trap_Cvar_Set( "g_nailbouncepercentage", "65" );',
        'trap_Cvar_Set( "g_nailcount", "10" );',
        'trap_Cvar_Set( "g_nailspeed", "1000" );',
        'trap_Cvar_Set( "g_nailspread", "400" );',
    ):
        assert expected in g_pmove_c
    assert '"g_nailgravity"' not in g_pmove_c

    assert "#define NUM_NAILSHOTS" not in g_weapon_c
    assert "case WP_NAILGUN:" in fireweapon_body
    assert "Weapon_Nailgun_Fire( ent );" in fireweapon_body
    assert "ent->client->accuracy_shots += g_weaponConfig.nailgunCount;" in g_weapon_c
    assert "ent->client->pers.accuracy_shots[WP_NAILGUN] += g_weaponConfig.nailgunCount;" in g_weapon_c
    assert "for( count = 0; count < g_weaponConfig.nailgunCount; count++ ) {" in nailgun_body
    assert "m = fire_nail (ent, muzzle, forward, right, up );" in nailgun_body
    assert "m->damage *= s_quadFactor;" in nailgun_body
    assert "m->splashDamage *= s_quadFactor;" in nailgun_body

    for expected in (
        "if ( !( ent->s.eFlags & EF_NAIL_BOUNCE ) ||",
        "g_weaponConfig.nailgunBounceCount <= 0 ||",
        "ent->count >= g_weaponConfig.nailgunBounceCount ) {",
        "if ( g_entities[trace->entityNum].takedamage ) {",
        "G_BounceMissile( ent, trace );",
        "ent->count++;",
        "G_AddEvent( ent, EV_GRENADE_BOUNCE, 0 );",
    ):
        assert expected in nail_bounce_body
    assert "if ( ent->s.weapon == WP_NAILGUN && G_HandleNailgunBounce( ent, &tr ) ) {" in run_missile_body

    for expected in (
        'bolt->classname = "nail";',
        "bolt->nextthink = level.time + NAILGUN_LIFETIME;",
        "bolt->think = G_ExplodeMissile;",
        "bolt->s.eType = ET_MISSILE;",
        "bolt->r.svFlags = SVF_USE_CURRENT_ORIGIN;",
        "bolt->s.weapon = WP_NAILGUN;",
        "bolt->s.eFlags = 0;",
        "bolt->r.ownerNum = self->s.number;",
        "bolt->parent = self;",
        "bolt->damage = g_weaponConfig.nailgunDamage;",
        "bolt->methodOfDeath = MOD_NAIL;",
        "bolt->clipmask = MASK_SHOT;",
        "bolt->target_ent = NULL;",
        "bolt->s.pos.trType = TR_LINEAR;",
        "bolt->s.pos.trTime = level.time;",
        "VectorCopy( start, bolt->s.pos.trBase );",
        "if ( g_weaponConfig.nailgunBounceEnabled ) {",
        "bounceRoll = Q_irand( 1, 100 );",
        "if ( bounceRoll > 100 - g_weaponConfig.nailgunBouncePercentage ) {",
        "bolt->s.eFlags = canBounce ? EF_NAIL_BOUNCE : 0;",
        "bolt->count = 0;",
        "r = random() * M_PI * 2.0f;",
        "u = sin(r) * crandom() * g_weaponConfig.nailgunSpread * 16;",
        "r = cos(r) * crandom() * g_weaponConfig.nailgunSpread * 16;",
        "VectorMA( start, 8192 * 16, forward, end);",
        "VectorSubtract( end, start, dir );",
        "VectorNormalize( dir );",
        "scale = 555 + random() * g_weaponConfig.nailgunSpeed;",
        "VectorScale( dir, scale, bolt->s.pos.trDelta );",
        "SnapVector( bolt->s.pos.trDelta );",
        "VectorCopy( start, bolt->r.currentOrigin );",
    ):
        assert expected in fire_nail_body
    assert "bolt->damage = 20;" not in fire_nail_body
    assert "NAILGUN_MAX_BOUNCES" not in g_missile_c
    assert "NAILGUN_SPREAD" not in g_missile_c
    assert "vectoangles( dir, angles );" not in fire_nail_body

    assert "case MOD_NAIL:" in clamp_body
    assert "configuredDamage = g_weaponConfig.nailgunDamage;" in clamp_body
    assert "case MOD_NAIL:" in mod_to_weapon_body
    assert "return WP_NAILGUN;" in mod_to_weapon_body
    assert "case MOD_NAIL:" in knockback_body
    assert "return g_knockbackConfig.nailgun;" in knockback_body


def test_prox_launcher_full_server_and_cgame_wiring_matches_retail() -> None:
    bg_pmove_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/bg_pmove.md")
    cgame_symbols = _read("references/symbol-maps/cgame.json")
    cg_ents_c = _read("src/code/cgame/cg_ents.c")
    cg_event_c = _read("src/code/cgame/cg_event.c")
    cg_local_h = _read("src/code/cgame/cg_local.h")
    cg_main_c = _read("src/code/cgame/cg_main.c")
    cg_weapons_c = _read("src/code/cgame/cg_weapons.c")
    g_combat_c = _read("src/code/game/g_combat.c")
    g_config_c = _read("src/game/g_config.c")
    g_items_hlil = _read("references/hlil/quakelive/qagamex86.dll_split/g_items.md")
    g_local_h = _read("src/code/game/g_local.h")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_mover_c = _read("src/code/game/g_mover.c")
    g_main_c = _read("src/code/game/g_main.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")
    qagame_symbols = _read("references/symbol-maps/qagame.json")

    prox_wrapper_body = _function_body(g_weapon_c, "void weapon_proxlauncher_fire (gentity_t *ent)")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")
    fire_prox_body = _function_body(g_missile_c, "gentity_t *fire_prox( gentity_t *self, vec3_t start, vec3_t dir )")
    run_missile_body = _function_body(g_missile_c, "void G_RunMissile( gentity_t *ent )")
    missile_impact_body = _function_body(g_missile_c, "void G_MissileImpact( gentity_t *ent, trace_t *trace )")
    prox_explode_body = _function_body(g_missile_c, "static void ProximityMine_Explode( gentity_t *mine )")
    prox_die_body = _function_body(
        g_missile_c,
        "static void ProximityMine_Die( gentity_t *ent, gentity_t *inflictor, gentity_t *attacker, int damage, int mod )",
    )
    prox_trigger_body = _function_body(g_missile_c, "void ProximityMine_Trigger( gentity_t *trigger, gentity_t *other, trace_t *trace )")
    prox_activate_body = _function_body(g_missile_c, "static void ProximityMine_Activate( gentity_t *ent )")
    prox_player_body = _function_body(g_missile_c, "static void ProximityMine_Player( gentity_t *mine, gentity_t *player )")
    prox_explode_player_body = _function_body(g_missile_c, "static void ProximityMine_ExplodeOnPlayer( gentity_t *mine )")
    prox_position_body = _function_body(g_mover_c, "qboolean G_CheckProxMinePosition( gentity_t *check )")
    prox_push_body = _function_body(g_mover_c, "qboolean G_TryPushingProxMine( gentity_t *check, gentity_t *pusher, vec3_t move, vec3_t amove )")
    mover_push_body = _function_body(g_mover_c, "qboolean G_MoverPush( gentity_t *pusher, vec3_t move, vec3_t amove, gentity_t **obstacle )")
    clamp_body = _function_body(g_combat_c, "static int G_ClampModDamage( int damage, int mod, gentity_t *attacker )")
    mod_to_weapon_body = _function_body(g_combat_c, "static weapon_t G_ModToWeapon( int mod )")
    knockback_body = _function_body(g_combat_c, "static float G_KnockbackScaleForMOD( int mod, qboolean selfInflicted )")
    cgame_missile_body = _function_body(cg_ents_c, "static void CG_Missile( centity_t *cent )")
    register_weapon_body = _function_body(cg_weapons_c, "void CG_RegisterWeapon( int weaponNum )")
    hitwall_body = _function_body(
        cg_weapons_c,
        "void CG_MissileHitWall( int weapon, int clientNum, vec3_t origin, vec3_t dir, impactSound_t soundType )",
    )
    hitplayer_body = _function_body(cg_weapons_c, "void CG_MissileHitPlayer( int weapon, vec3_t origin, vec3_t dir, int entityNum )")

    for expected in (
        '"normalized_name": "fire_prox"',
        "Exact proximity-mine projectile constructor",
        '"normalized_name": "weapon_proxlauncher_fire"',
        "Retail prox-launcher wrapper",
        '"normalized_name": "ProximityMine_Trigger"',
        "same-team rejection",
        '"normalized_name": "ProximityMine_Activate"',
        "creates the proxmine_trigger child entity",
        '"normalized_name": "ProximityMine_Player"',
        "already-ticking stack-up",
        '"normalized_name": "G_CheckProxMinePosition"',
        '"normalized_name": "G_TryPushingProxMine"',
    ):
        assert expected in qagame_symbols

    for expected in (
        '"normalized_name": "CG_DrawProxWarning"',
        '"normalized_name": "CG_Missile"',
        '"normalized_name": "CG_GrenadeTrail"',
        "Grenade and proximity-mine trail wrapper",
        '"normalized_name": "CG_MissileHitWall"',
        '"normalized_name": "CG_MissileHitPlayer"',
    ):
        assert expected in cgame_symbols

    assert "| Proximity Launcher | 800 |" in bg_pmove_hlil
    assert "| Proximity Launcher | 10 | 40 |" in bg_pmove_hlil
    assert "| 0x18 | 0x0B | Proximity Launcher |" in g_items_hlil
    assert "| 0x1A | 0x0D | Prox mine |" in g_items_hlil

    for expected in (
        "proximityLauncherDamage;",
        "proximityLauncherSplashDamage;",
        "proximityLauncherSplashRadius;",
        "extern\tvmCvar_t\tg_proxMineTimeout;",
        "extern\tvmCvar_t\tg_damage_pl;",
        "extern\tvmCvar_t\tg_splashDamage_pl;",
        "extern\tvmCvar_t\tg_splashRadius_pl;",
    ):
        assert expected in g_local_h

    for expected in (
        '{ &g_damage_pl, "g_damage_pl", "0", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_splashDamage_pl, "g_splashdamage_pl", "100", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_splashRadius_pl, "g_splashradius_pl", "150", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qtrue, qfalse,',
        '{ &g_proxMineTimeout, "g_proxMineTimeout", "20", GAME_CVAR_FLAG_RETAIL_40000 | CVAR_GAMERULE, 0, qfalse },',
        'g_weaponConfig.proximityLauncherDamage = G_ReadWeaponCvarNonNegative( &g_damage_pl, 0, "g_damage_pl" );',
        'g_weaponConfig.proximityLauncherSplashDamage = G_ReadWeaponCvar( &g_splashDamage_pl, 100, "g_splashdamage_pl" );',
        'g_weaponConfig.proximityLauncherSplashRadius = G_ReadWeaponCvar( &g_splashRadius_pl, 150, "g_splashradius_pl" );',
    ):
        assert expected in g_main_c

    for expected in (
        "g_weaponReloadConfig.proximityLauncher != DEFAULT_WEAPON_RELOAD_PROX",
        "g_weaponConfig.proximityLauncherDamage != 0",
        "g_weaponConfig.proximityLauncherSplashDamage != 100",
        "g_weaponConfig.proximityLauncherSplashRadius != 150",
        "G_ConfigFloatDiffersFromDefault( g_knockbackConfig.proximityLauncher, DEFAULT_KNOCKBACK_PL )",
        "g_proxMineTimeout.integer != DEFAULT_PROX_MINE_TIMEOUT",
        "mask |= CUSTOM_SETTING_PROX_LAUNCHER;",
    ):
        assert expected in g_config_c

    assert "case WP_PROX_LAUNCHER:" in fireweapon_body
    assert "weapon_proxlauncher_fire( ent );" in fireweapon_body
    assert "forward[2] += 0.2f;" in prox_wrapper_body
    assert "VectorNormalize( forward );" in prox_wrapper_body
    assert "m = fire_prox (ent, muzzle, forward);" in prox_wrapper_body
    assert "m->damage *= s_quadFactor;" in prox_wrapper_body
    assert "m->splashDamage *= s_quadFactor;" in prox_wrapper_body

    for expected in (
        "VectorNormalize (dir);",
        'bolt->classname = "prox mine";',
        "bolt->nextthink = level.time + 3000;",
        "bolt->think = G_ExplodeMissile;",
        "bolt->s.eType = ET_MISSILE;",
        "bolt->r.svFlags = SVF_USE_CURRENT_ORIGIN;",
        "bolt->s.weapon = WP_PROX_LAUNCHER;",
        "bolt->s.eFlags = 0;",
        "bolt->damage = g_weaponConfig.proximityLauncherDamage;",
        "bolt->splashDamage = g_weaponConfig.proximityLauncherSplashDamage;",
        "bolt->splashRadius = g_weaponConfig.proximityLauncherSplashRadius;",
        "bolt->methodOfDeath = MOD_PROXIMITY_MINE;",
        "bolt->splashMethodOfDeath = MOD_PROXIMITY_MINE;",
        "bolt->clipmask = MASK_SHOT;",
        "bolt->target_ent = NULL;",
        "bolt->count = 0;",
        "bolt->s.generic1 = self->client->sess.sessionTeam;",
        "bolt->s.pos.trType = TR_GRAVITY;",
        "bolt->s.pos.trTime = level.time - MISSILE_PRESTEP_TIME;",
        "VectorScale( dir, 700, bolt->s.pos.trDelta );",
        "SnapVector( bolt->s.pos.trDelta );",
    ):
        assert expected in fire_prox_body
    assert "bolt->splashDamage = 100;" not in fire_prox_body
    assert "bolt->splashRadius = 150;" not in fire_prox_body

    for expected in (
        "if (mine->activator) {",
        "G_FreeEntity(mine->activator);",
        "mine->activator = NULL;",
    ):
        assert expected in prox_explode_body
    assert "ent->think = ProximityMine_Explode;" in prox_die_body
    assert "ent->nextthink = level.time + 1;" in prox_die_body

    for expected in (
        "if( !other->client ) {",
        "VectorSubtract( trigger->s.pos.trBase, other->s.pos.trBase, v );",
        "if( VectorLength( v ) > trigger->parent->splashRadius ) {",
        "if (trigger->parent->s.generic1 == other->client->sess.sessionTeam) {",
        "if( !CanDamage( other, trigger->s.pos.trBase ) ) {",
        "mine = trigger->parent;",
        "mine->s.loopSound = 0;",
        "G_AddEvent( mine, EV_PROXIMITY_MINE_TRIGGER, 0 );",
        "mine->nextthink = level.time + 500;",
        "G_FreeEntity( trigger );",
    ):
        assert expected in prox_trigger_body

    for expected in (
        "ent->think = ProximityMine_Explode;",
        "ent->nextthink = level.time + g_proxMineTimeout.integer * 1000;",
        "ent->takedamage = qtrue;",
        "ent->health = 1;",
        "ent->die = ProximityMine_Die;",
        'ent->s.loopSound = G_SoundIndex( "sound/weapons/proxmine/wstbtick.wav" );',
        'trigger->classname = "proxmine_trigger";',
        "r = ent->splashRadius;",
        "trigger->r.contents = CONTENTS_TRIGGER;",
        "trigger->touch = ProximityMine_Trigger;",
        "ent->activator = trigger;",
    ):
        assert expected in prox_activate_body

    for expected in (
        "if( mine->s.eFlags & EF_NODRAW ) {",
        "G_AddEvent( mine, EV_PROXIMITY_MINE_STICK, 0 );",
        "if( player->s.eFlags & EF_TICKING ) {",
        "player->activator->splashDamage += mine->splashDamage;",
        "player->activator->splashRadius *= 1.50;",
        "mine->think = G_FreeEntity;",
        "player->client->ps.eFlags |= EF_TICKING;",
        "player->activator = mine;",
        "mine->s.eFlags |= EF_NODRAW;",
        "mine->r.svFlags |= SVF_NOCLIENT;",
        "mine->s.pos.trType = TR_LINEAR;",
        "VectorClear( mine->s.pos.trDelta );",
        "mine->think = ProximityMine_ExplodeOnPlayer;",
        "mine->nextthink = level.time + 2 * 1000;",
        "mine->nextthink = level.time + 10 * 1000;",
    ):
        assert expected in prox_player_body

    for expected in (
        "player->client->ps.eFlags &= ~EF_TICKING;",
        "G_Damage( player, mine->parent, mine->parent, vec3_origin, mine->s.origin, 1000, DAMAGE_NO_KNOCKBACK, MOD_JUICED );",
        "G_TempEntity( player->client->ps.origin, EV_JUICED );",
        "G_SetOrigin( mine, player->s.pos.trBase );",
        "mine->r.svFlags &= ~SVF_NOCLIENT;",
        "mine->splashMethodOfDeath = MOD_PROXIMITY_MINE;",
        "G_ExplodeMissile( mine );",
    ):
        assert expected in prox_explode_player_body

    for expected in (
        "else if (ent->s.weapon == WP_PROX_LAUNCHER && ent->count) {",
        "passent = ENTITYNUM_NONE;",
        "if (ent->s.weapon == WP_PROX_LAUNCHER && !ent->count) {",
        "ent->count = 1;",
    ):
        assert expected in run_missile_body

    for expected in (
        "if( ent->s.weapon == WP_PROX_LAUNCHER ) {",
        "if( ent->s.pos.trType != TR_GRAVITY ) {",
        "ProximityMine_Player( ent, other );",
        "SnapVectorTowards( trace->endpos, ent->s.pos.trBase );",
        "ent->s.pos.trType = TR_STATIONARY;",
        "G_AddEvent( ent, EV_PROXIMITY_MINE_STICK, trace->surfaceFlags );",
        "ent->think = ProximityMine_Activate;",
        "ent->nextthink = level.time + 2000;",
        "ent->die = ProximityMine_Die;",
        "VectorCopy(trace->plane.normal, ent->movedir);",
        "VectorSet(ent->r.mins, -4, -4, -4);",
        "VectorSet(ent->r.maxs, 4, 4, 4);",
    ):
        assert expected in missile_impact_body

    for expected in (
        "VectorMA(check->s.pos.trBase, 0.125, check->movedir, start);",
        "VectorMA(check->s.pos.trBase, 2, check->movedir, end);",
        "trap_Trace( &tr, start, NULL, NULL, end, check->s.number, MASK_SOLID );",
        "if (tr.startsolid || tr.fraction < 1)",
    ):
        assert expected in prox_position_body

    for expected in (
        "VectorSubtract (vec3_origin, amove, org);",
        "AngleVectors (org, forward, right, up);",
        "VectorAdd (check->s.pos.trBase, move, check->s.pos.trBase);",
        "VectorSubtract (check->s.pos.trBase, pusher->r.currentOrigin, org);",
        "ret = G_CheckProxMinePosition( check );",
        "VectorCopy( check->s.pos.trBase, check->r.currentOrigin );",
        "trap_LinkEntity (check);",
    ):
        assert expected in prox_push_body

    for expected in (
        'if ( !strcmp(check->classname, "prox mine") ) {',
        "if ( check->enemy == pusher ) {",
        "if (!G_TryPushingProxMine( check, pusher, move, amove )) {",
        "if (!G_CheckProxMinePosition( check )) {",
        "G_AddEvent( check, EV_PROXIMITY_MINE_TRIGGER, 0 );",
        "G_ExplodeMissile(check);",
    ):
        assert expected in mover_push_body

    assert "case MOD_PROXIMITY_MINE:" in clamp_body
    assert "g_weaponConfig.proximityLauncherDamage > g_weaponConfig.proximityLauncherSplashDamage" in clamp_body
    assert "g_weaponConfig.proximityLauncherDamage : g_weaponConfig.proximityLauncherSplashDamage;" in clamp_body
    assert "case MOD_PROXIMITY_MINE:" in mod_to_weapon_body
    assert "return WP_PROX_LAUNCHER;" in mod_to_weapon_body
    assert "case MOD_PROXIMITY_MINE:" in knockback_body
    assert "return g_knockbackConfig.proximityLauncher;" in knockback_body

    for expected in (
        "qhandle_t\tblueProxMine;",
        "sfxHandle_t\twstbimplSound;",
        "sfxHandle_t\twstbimpmSound;",
        "sfxHandle_t\twstbimpdSound;",
        "sfxHandle_t\twstbactvSound;",
        "sfxHandle_t\tsfx_proxexp;",
    ):
        assert expected in cg_local_h

    for expected in (
        'cgs.media.sfx_proxexp = trap_S_RegisterSound( "sound/weapons/proxmine/wstbexpl.ogg", qfalse );',
        'cgs.media.wstbimplSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbimpl.ogg", qfalse );',
        'cgs.media.wstbimpmSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbimpm.ogg", qfalse );',
        'cgs.media.wstbimpdSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbimpd.ogg", qfalse );',
        'cgs.media.wstbactvSound = trap_S_RegisterSound( "sound/weapons/proxmine/wstbactv.ogg", qfalse );',
        'cgs.media.blueProxMine = trap_R_RegisterModel( "models/weaphits/proxmineb.md3" );',
    ):
        assert expected in cg_main_c

    for expected in (
        "case EV_PROXIMITY_MINE_STICK:",
        'DEBUGNAME("EV_PROXIMITY_MINE_STICK");',
        "trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbimplSound );",
        "trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbimpmSound );",
        "trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbimpdSound );",
        "case EV_PROXIMITY_MINE_TRIGGER:",
        'DEBUGNAME("EV_PROXIMITY_MINE_TRIGGER");',
        "trap_S_StartSound (NULL, es->number, CHAN_AUTO, cgs.media.wstbactvSound );",
    ):
        assert expected in cg_event_c

    for expected in (
        "if ( cent->currentState.weapon == WP_PROX_LAUNCHER ) {",
        "if (s1->generic1 == TEAM_BLUE) {",
        "ent.hModel = cgs.media.blueProxMine;",
        "if ( s1->weapon == WP_PROX_LAUNCHER ) {",
        "AnglesToAxis( cent->lerpAngles, ent.axis );",
    ):
        assert expected in cgame_missile_body

    for expected in (
        "case WP_PROX_LAUNCHER:",
        'weaponInfo->missileModel = trap_R_RegisterModel( "models/weaphits/proxmine.md3" );',
        "weaponInfo->missileTrailFunc = CG_GrenadeTrail;",
        "weaponInfo->wiTrailTime = 700;",
        "weaponInfo->trailRadius = 32;",
        'weaponInfo->flashSound[0] = trap_S_RegisterSound( "sound/weapons/proxmine/wstbfire.ogg", qfalse );',
        'cgs.media.grenadeExplosionShader = trap_R_RegisterShader( "grenadeExplosion" );',
    ):
        assert expected in register_weapon_body

    for expected in (
        "case WP_PROX_LAUNCHER:",
        "sfx = cgs.media.sfx_proxexp;",
        "mark = cgs.media.burnMarkShader;",
        "radius = 64;",
        "light = 300;",
        "isSprite = qtrue;",
    ):
        assert expected in hitwall_body

    for expected in (
        "case WP_PROX_LAUNCHER:",
        "CG_MissileHitWall( weapon, 0, origin, dir, IMPACTSOUND_FLESH );",
    ):
        assert expected in hitplayer_body


def test_missile_pipeline_matches_retail_callback_schedule() -> None:
    g_config_c = _read("src/game/g_config.c")
    g_main_c = _read("src/code/game/g_main.c")
    g_missile_c = _read("src/code/game/g_missile.c")
    g_weapon_c = _read("src/code/game/g_weapon.c")

    run_missile_body = _function_body(g_missile_c, "void G_RunMissile( gentity_t *ent )")
    fire_grenade_body = _function_body(g_missile_c, "gentity_t *fire_grenade (gentity_t *self, vec3_t start, vec3_t dir)")
    fire_rocket_body = _function_body(g_missile_c, "gentity_t *fire_rocket (gentity_t *self, vec3_t start, vec3_t dir)")
    fire_plasma_body = _function_body(g_missile_c, "gentity_t *fire_plasma (gentity_t *self, vec3_t start, vec3_t dir)")
    fire_bfg_body = _function_body(g_missile_c, "gentity_t *fire_bfg (gentity_t *self, vec3_t start, vec3_t dir)")
    fire_nail_body = _function_body(g_missile_c, "gentity_t *fire_nail( gentity_t *self, vec3_t start, vec3_t forward, vec3_t right, vec3_t up )")
    nail_bounce_body = _function_body(g_missile_c, "static qboolean G_HandleNailgunBounce( gentity_t *ent, trace_t *trace )")
    grenade_launcher_body = _function_body(g_weapon_c, "void weapon_grenadelauncher_fire (gentity_t *ent)")
    rocket_launcher_body = _function_body(g_weapon_c, "void Weapon_RocketLauncher_Fire (gentity_t *ent)")
    fireweapon_body = _function_body(g_weapon_c, "void FireWeapon( gentity_t *ent )")

    assert "#define\tGUIDED_ROCKET_THINK_TIME\t25" in g_missile_c
    assert "#define\tGUIDED_ROCKET_SPEED\t20.0f" in g_missile_c
    assert "#define\tNAILGUN_LIFETIME\t4500" in g_missile_c
    assert "#define\tEF_NAIL_BOUNCE\tEF_READY" in g_missile_c
    assert "static void G_RunGuidedRocketThink( gentity_t *ent )" in g_missile_c
    assert "static void G_RunRocketAccelerationThink( gentity_t *ent )" in g_missile_c
    assert "static void G_RunPlasmaAccelerationThink( gentity_t *ent )" in g_missile_c
    assert "static void G_RunBfgAccelerationThink( gentity_t *ent )" in g_missile_c

    assert "g_weaponConfig.guidedRocketEnabled && ent->count" not in run_missile_body
    assert "G_UpdateMissileAcceleration( ent );" not in run_missile_body
    assert 'g_velocity_gl", "700"' in g_main_c
    assert 'G_ReadWeaponCvar( &g_damage_gl, 100, "g_damage_gl" );' in g_main_c
    assert 'G_ReadWeaponCvar( &g_splashDamage_gl, 100, "g_splashdamage_gl" );' in g_main_c
    assert 'G_ReadWeaponCvar( &g_splashRadius_gl, 150, "g_splashradius_gl" );' in g_main_c
    assert 'G_ReadWeaponCvarAtLeast( &g_velocity_gl, 700, "g_velocity_gl", 1 );' in g_main_c
    assert 'case WP_GRENADE_LAUNCHER:' in fireweapon_body
    assert 'weapon_grenadelauncher_fire( ent );' in fireweapon_body
    assert "forward[2] += 0.2f;" in grenade_launcher_body
    assert "VectorNormalize( forward );" in grenade_launcher_body
    assert "m = fire_grenade (ent, muzzle, forward);" in grenade_launcher_body
    assert "m->damage *= s_quadFactor;" in grenade_launcher_body
    assert "m->splashDamage *= s_quadFactor;" in grenade_launcher_body
    assert 'bolt->classname = "grenade";' in fire_grenade_body
    assert "bolt->nextthink = level.time + 2500;" in fire_grenade_body
    assert "bolt->think = G_ExplodeMissile;" in fire_grenade_body
    assert "bolt->s.eType = ET_MISSILE;" in fire_grenade_body
    assert "bolt->r.svFlags = SVF_USE_CURRENT_ORIGIN;" in fire_grenade_body
    assert "VectorSet( bolt->r.mins, -0.01f, -0.01f, -0.01f );" in fire_grenade_body
    assert "VectorSet( bolt->r.maxs, 0.01f, 0.01f, 0.01f );" in fire_grenade_body
    assert "bolt->s.weapon = WP_GRENADE_LAUNCHER;" in fire_grenade_body
    assert "bolt->s.eFlags = EF_BOUNCE_HALF;" in fire_grenade_body
    assert "bolt->damage = g_weaponConfig.grenadeDamage;" in fire_grenade_body
    assert "bolt->splashDamage = g_weaponConfig.grenadeSplashDamage;" in fire_grenade_body
    assert "bolt->splashRadius = g_weaponConfig.grenadeSplashRadius;" in fire_grenade_body
    assert "bolt->methodOfDeath = MOD_GRENADE;" in fire_grenade_body
    assert "bolt->splashMethodOfDeath = MOD_GRENADE_SPLASH;" in fire_grenade_body
    assert "bolt->clipmask = MASK_SHOT;" in fire_grenade_body
    assert "bolt->target_ent = NULL;" in fire_grenade_body
    assert "bolt->speed = ( float )g_weaponConfig.grenadeSpeed;" in fire_grenade_body
    assert "bolt->s.pos.trType = TR_GRAVITY;" in fire_grenade_body
    assert "bolt->s.pos.trTime = level.time - MISSILE_PRESTEP_TIME;" in fire_grenade_body
    assert "VectorScale( dir, ( float )g_weaponConfig.grenadeSpeed, bolt->s.pos.trDelta );" in fire_grenade_body
    assert "SnapVector( bolt->s.pos.trDelta );" in fire_grenade_body
    assert 'g_velocity_rl", "1000"' in g_main_c
    assert 'G_ReadWeaponCvar( &g_damage_rl, 100, "g_damage_rl" );' in g_main_c
    assert 'G_ReadWeaponCvar( &g_splashDamage_rl, 84, "g_splashdamage_rl" );' in g_main_c
    assert 'G_ReadWeaponCvar( &g_splashRadius_rl, 120, "g_splashradius_rl" );' in g_main_c
    assert 'G_ReadWeaponCvarAtLeast( &g_velocity_rl, 1000, "g_velocity_rl", 1 );' in g_main_c
    assert 'G_ReadWeaponCvarRaw( &g_rocketsplashOffset, -10, "g_rocketsplashOffset" );' in g_main_c
    assert 'G_ReadWeaponBoolCvar( &g_guidedRocket, qfalse, "g_guidedRocket" );' in g_main_c
    assert "G_ConfigFloatDiffersFromDefault( g_weaponConfig.rocketAccelerationFactor, 1.0f )" in g_config_c
    assert "G_ConfigFloatDiffersFromDefault( g_weaponConfig.rocketAccelerationFactor, 0.0f )" not in g_config_c
    assert 'case WP_ROCKET_LAUNCHER:' in fireweapon_body
    assert 'Weapon_RocketLauncher_Fire( ent );' in fireweapon_body
    assert "m = fire_rocket (ent, muzzle, forward);" in rocket_launcher_body
    assert "m->damage *= s_quadFactor;" in rocket_launcher_body
    assert "m->splashDamage *= s_quadFactor;" in rocket_launcher_body
    assert 'bolt->classname = "rocket";' in fire_rocket_body
    assert "bolt->nextthink = level.time + 15000;" in fire_rocket_body
    assert "bolt->think = G_ExplodeMissile;" in fire_rocket_body
    assert "bolt->s.eType = ET_MISSILE;" in fire_rocket_body
    assert "bolt->r.svFlags = SVF_USE_CURRENT_ORIGIN;" in fire_rocket_body
    assert "VectorSet( bolt->r.mins, -0.01f, -0.01f, -0.01f );" in fire_rocket_body
    assert "VectorSet( bolt->r.maxs, 0.01f, 0.01f, 0.01f );" in fire_rocket_body
    assert "bolt->s.weapon = WP_ROCKET_LAUNCHER;" in fire_rocket_body
    assert "bolt->damage = g_weaponConfig.rocketDamage;" in fire_rocket_body
    assert "bolt->splashDamage = g_weaponConfig.rocketSplashDamage;" in fire_rocket_body
    assert "bolt->splashRadius = g_weaponConfig.rocketSplashRadius;" in fire_rocket_body
    assert "bolt->methodOfDeath = MOD_ROCKET;" in fire_rocket_body
    assert "bolt->splashMethodOfDeath = MOD_ROCKET_SPLASH;" in fire_rocket_body
    assert "bolt->clipmask = MASK_SHOT;" in fire_rocket_body
    assert "bolt->target_ent = NULL;" in fire_rocket_body
    assert "bolt->s.pos.trType = TR_LINEAR;" in fire_rocket_body
    assert "bolt->s.pos.trTime = level.time - MISSILE_PRESTEP_TIME;" in fire_rocket_body
    assert "G_SynchronizeRocketConfig( bolt, dir );" in fire_rocket_body
    assert "bolt->nextthink = level.time + GUIDED_ROCKET_INITIAL_THINK_TIME;" in fire_rocket_body
    assert "bolt->think = G_RunGuidedRocketThink;" in fire_rocket_body
    assert "bolt->think = G_RunRocketAccelerationThink;" in fire_rocket_body
    assert "bolt->think = G_RunPlasmaAccelerationThink;" in fire_plasma_body
    assert "bolt->think = G_RunBfgAccelerationThink;" in fire_bfg_body

    assert 'g_accelFactor_rl", "1"' in g_main_c
    assert 'g_accelFactor_pg", "1"' in g_main_c
    assert 'g_accelFactor_bfg", "1"' in g_main_c
    assert 'G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_rl, 1.0f, "g_accelFactor_rl" );' in g_main_c
    assert 'G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_pg, 1.0f, "g_accelFactor_pg" );' in g_main_c
    assert 'G_ReadWeaponFloatCvarNonNegative( &g_accelFactor_bfg, 1.0f, "g_accelFactor_bfg" );' in g_main_c
    assert 'G_ReadWeaponCvarNonNegative( &g_accelRate_rl, 16, "g_accelRate_rl" );' in g_main_c
    assert 'G_ReadWeaponCvarNonNegative( &g_accelRate_pg, 16, "g_accelRate_pg" );' in g_main_c
    assert 'G_ReadWeaponCvarNonNegative( &g_accelRate_bfg, 16, "g_accelRate_bfg" );' in g_main_c

    assert "bolt->nextthink = level.time + NAILGUN_LIFETIME;" in fire_nail_body
    assert "bolt->s.eFlags = canBounce ? EF_NAIL_BOUNCE : 0;" in fire_nail_body
    assert "bolt->count = 0;" in fire_nail_body
    assert "vectoangles( dir, angles );" not in fire_nail_body
    assert "G_AddEvent( ent, EV_GRENADE_BOUNCE, 0 );" in nail_bounce_body
    assert "ent->count++;" in nail_bounce_body
    assert "g_weaponConfig.nailgunBounceEnabled" not in nail_bounce_body


def test_lightning_discharge_helper_matches_retail_radius_burst_shape() -> None:
    g_weapon_c = _read("src/code/game/g_weapon.c")
    discharge_helper = _function_body(
        g_weapon_c,
        "static qboolean Weapon_LightningDischargeDamage( vec3_t origin, gentity_t *attacker, float damage, float radius )",
    )
    discharge_ammo = _function_body(
        g_weapon_c,
        "static int Weapon_GetLightningDischargeAmmoCount( const gentity_t *ent )",
    )

    assert "#define LIGHTNING_DISCHARGE_DEFAULT_AMMO\t150" in g_weapon_c
    assert "if ( g_factoryCvarConfig.infiniteAmmo || ammoCount < 0 ) {" in discharge_ammo
    assert "return LIGHTNING_DISCHARGE_DEFAULT_AMMO;" in discharge_ammo
    assert "ammoCount += 1;" in discharge_ammo
    assert "numListedEntities = trap_EntitiesInBox( mins, maxs, entityList, MAX_GENTITIES );" in discharge_helper
    assert "points = damage * ( 1.0f - dist / radius );" in discharge_helper
    assert "if ( !CanDamage( ent, origin ) ) {" in discharge_helper
    assert "if ( LogAccuracyHit( ent, attacker ) ) {" in discharge_helper
    assert "dir[2] += 24.0f;" in discharge_helper
    assert "G_Damage( ent, NULL, attacker, dir, origin, (int)points, DAMAGE_RADIUS, MOD_LIGHTNING_DISCHARGE );" in discharge_helper


def test_client_true_shotgun_pattern_matches_server_ring() -> None:
    cg_weapons_c = _read("src/code/cgame/cg_weapons.c")
    pattern_body = _function_body(
        cg_weapons_c,
        "static void CG_ShotgunPattern( vec3_t origin, vec3_t origin2, int seed, int otherEntNum )",
    )

    assert "if ( i < 6 ) {" in pattern_body
    assert "angle = ( i - 20 ) * 60.0f;" in pattern_body
    assert "radius = 4000.0f;" in pattern_body
    assert "spreadJitter = 0.4f;" in pattern_body
    assert "} else if ( i < 12 ) {" in pattern_body
    assert "angle = i * 60.0f + 30.0f;" in pattern_body
    assert "radius = 8000.0f;" in pattern_body
    assert "spreadJitter = 0.3f;" in pattern_body
    assert "angle = i * 45.0f;" in pattern_body
    assert "radius = 12000.0f;" in pattern_body
    assert "spreadJitter = 0.2f;" in pattern_body
    assert "if ( cg_trueShotgun.integer ) {" in pattern_body
    assert "spreadJitter = 0.0f;" in pattern_body
    assert "r = ( cos( DEG2RAD( angle ) ) + Q_crandom( &seed ) * spreadJitter ) * radius;" in pattern_body
    assert "u = ( sin( DEG2RAD( angle ) ) + Q_crandom( &seed ) * spreadJitter ) * radius;" in pattern_body
    assert "DEFAULT_SHOTGUN_SPREAD" not in pattern_body


def test_retail_weapon_reload_defaults_match_recovered_cgame_table() -> None:
    bg_pmove_c = _read("src/code/game/bg_pmove.c")

    assert "[WP_BFG] = 300," in bg_pmove_c
    assert "[WP_GRAPPLING_HOOK] = 100," in bg_pmove_c
    assert "[WP_HEAVY_MACHINEGUN] = 75," in bg_pmove_c
