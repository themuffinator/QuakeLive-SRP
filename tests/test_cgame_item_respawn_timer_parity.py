"""Guard the retail world-item respawn timer and queued marker seams against drift."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CG_DRAW = REPO_ROOT / "src" / "code" / "cgame" / "cg_draw.c"
CG_ENTS = REPO_ROOT / "src" / "code" / "cgame" / "cg_ents.c"
CG_MAIN = REPO_ROOT / "src" / "code" / "cgame" / "cg_main.c"
CG_PREDICT = REPO_ROOT / "src" / "code" / "cgame" / "cg_predict.c"
G_ITEMS = REPO_ROOT / "src" / "code" / "game" / "g_items.c"
CG_BG_PLAN = REPO_ROOT / "docs" / "reverse-engineering" / "cgame-bg-parity-implementation-plan.md"


def _block_from_marker(source: str, marker: str) -> str:
	start = source.rindex(marker)
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


def test_item_respawn_timer_fallback_and_icon_boundaries_match_retail_family() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	uses_block = _block_from_marker(source, "static qboolean CG_ItemUsesRespawnTimer")
	duration_block = _block_from_marker(source, "static int CG_ItemRespawnTimerDuration")
	icon_block = _block_from_marker(source, "static qhandle_t CG_ItemRespawnTimerIcon")

	for expected in (
		"if ( item->giType == IT_ARMOR && item->quantity >= 25 ) {",
		"if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {",
		"if ( item->giType == IT_POWERUP ) {",
		"case PW_QUAD:",
		"case PW_BATTLESUIT:",
		"case PW_HASTE:",
		"case PW_INVIS:",
		"case PW_REGEN:",
		"if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {",
	):
		assert expected in uses_block

	for expected in (
		"return 25 * 1000;",
		"return 35 * 1000;",
		"return 120 * 1000;",
		"return 60 * 1000;",
	):
		assert expected in duration_block

	for expected in (
		"return cgs.media.itemTimerArmorShader;",
		"return cgs.media.itemTimerHealthShader;",
		"return cgs.media.itemTimerQuadShader;",
		"return cgs.media.itemTimerBattleSuitShader;",
		"return cgs.media.itemTimerHasteShader;",
		"return cgs.media.itemTimerInvisShader;",
		"return cgs.media.itemTimerRegenShader;",
		"return cgs.media.itemTimerMedkitShader;",
		"return cgs.media.itemTimerUnknownShader;",
	):
		assert expected in icon_block


def test_item_respawn_timer_slice_selection_and_draw_math_match_retail_shape() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	slices_block = _block_from_marker(source, "static void CG_ItemRespawnTimerSlices")
	rotation_block = _block_from_marker(source, "static float CG_ItemRespawnTimerSpriteRotation")
	sprite_block = _block_from_marker(source, "static void CG_DrawItemRespawnTimerSprite")
	draw_block = _block_from_marker(source, "static void CG_DrawItemRespawnTimer")

	for expected in (
		"durationBuckets = respawnDuration / 5000;",
		"if ( durationBuckets <= 5 ) {",
		"*sliceCount = 5;",
		"if ( durationBuckets <= 7 ) {",
		"*sliceCount = 7;",
		"if ( durationBuckets <= 12 ) {",
		"*sliceCount = 12;",
		"*sliceCount = 24;",
	):
		assert expected in slices_block

	assert "return retailRotation - 180.0f;" in rotation_block

	for expected in (
		"ent.reType = RT_SPRITE;",
		"ent.radius = 16.0f;",
		"ent.rotation = CG_ItemRespawnTimerSpriteRotation( rotation );",
		"ent.customShader = shader;",
		"ent.shaderRGBA[3] = alphaByte;",
	):
		assert expected in sprite_block

	for expected in (
		"if ( !item || !origin || !cg_itemTimers.integer ) {",
		"if ( respawnRemaining > respawnDuration ) {",
		"timerOrigin[2] += 8.0f;",
		"if ( distance <= 256.0f ) {",
		"} else if ( distance < 768.0f ) {",
		"alpha = ( 768.0f - distance ) * ( 1.0f / 512.0f );",
		"elapsedSlice = ( ( respawnDuration - respawnRemaining ) / 5000 ) + 1;",
		'CG_DrawItemRespawnTimerSprite( iconShader, timerOrigin, alpha, 180.0f );',
		"sliceStep = 360 / sliceCount;",
		"rotation = -( 180 / sliceCount );",
		"( sliceIndex == elapsedSlice ) ? currentSliceShader : sliceShader,",
	):
		assert expected in draw_block


def test_cg_item_calls_respawn_timer_before_skip_items_and_uses_time2_fallback() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	item_block = _block_from_marker(source, "static void CG_Item")

	for expected in (
		"if ( CG_ItemUsesRespawnTimer( item ) && es->time > cg.time ) {",
		"respawnDuration = es->time2;",
		"if ( respawnDuration <= 0 ) {",
		"respawnDuration = CG_ItemRespawnTimerDuration( item );",
		"respawnRemaining = es->time - cg.time;",
		"CG_DrawItemRespawnTimer( item, respawnRemaining, respawnDuration,",
		"cent->lerpOrigin, 0,",
		"(qboolean)( es->retailEventData != 0 ) );",
		'trap_Cvar_VariableStringBuffer( "cg_skipItems", skipItems, sizeof( skipItems ) );',
	):
		assert expected in item_block

	assert item_block.index("CG_DrawItemRespawnTimer(") < item_block.index('trap_Cvar_VariableStringBuffer( "cg_skipItems"')


def test_cg_item_simple_item_bob_mode_matches_retail_major_item_split() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	bob_mode_block = _block_from_marker(source, "static int CG_ItemSimpleItemsBobMode")
	uses_bob_block = _block_from_marker(source, "static qboolean CG_ItemUsesSimpleItemsBob")
	bob_offset_block = _block_from_marker(source, "static float CG_ItemSimpleItemsBobOffset")
	height_block = _block_from_marker(source, "static float CG_ItemSimpleItemsHeightOffset")
	simple_draw_block = _block_from_marker(source, "static void CG_DrawSimpleItem")
	item_block = _block_from_marker(source, "static void CG_Item")

	for expected in (
		"bobMode = (int)cg.simpleItemsBob;",
		"if ( bobMode < 0 ) {",
		"if ( bobMode > 2 ) {",
	):
		assert expected in bob_mode_block

	for expected in (
		"case 1:",
		"return qtrue;",
		"case 2:",
		"return CG_ItemUsesRespawnTimer( item );",
	):
		assert expected in uses_bob_block

	for expected in (
		"phase = (float)( cg.time & 1023 ) * ( (float)M_PI * 2.0f / 1024.0f );",
		"return 10.0f + sin( phase ) * 6.0f;",
	):
		assert expected in bob_offset_block

	for expected in (
		"if ( item && item->giType == IT_PERSISTANT_POWERUP ) {",
		"return 10.0f;",
		"return cg.simpleItemsHeightOffset;",
	):
		assert expected in height_block

	for expected in (
		"if ( CG_ItemUsesSimpleItemsBob( item ) ) {",
		"ent.origin[2] += CG_ItemSimpleItemsBobOffset();",
		"ent.origin[2] += CG_ItemSimpleItemsHeightOffset( item );",
		"ent.origin[2] += cg.simpleItemsRadius - 15.0f;",
		"VectorCopy( ent.origin, ent.oldorigin );",
	):
		assert expected in simple_draw_block

	assert "spriteBobScale" not in item_block
	assert "cos( ( cg.time + 1000 ) * spriteBobScale )" not in item_block
	assert "CG_DrawSimpleItem( cent, es, item );" in item_block


def test_simple_items_bob_cvar_cache_is_integer_mode_not_amplitude() -> None:
	source = CG_MAIN.read_text(encoding="utf-8")
	update_block = _block_from_marker(source, "static void CG_UpdateSimpleItemsSettings")

	for expected in (
		'{ &cg_simpleItemsBob, "cg_simpleItemsBob", "2",',
		' "0", "2" },',
	):
		assert expected in source

	for expected in (
		"cg.simpleItemsBob = (float)cg_simpleItemsBob.integer;",
		"if ( cg.simpleItemsBob < 0.0f ) {",
		"cg.simpleItemsBob = 0.0f;",
		"} else if ( cg.simpleItemsBob > 2.0f ) {",
		"cg.simpleItemsBob = 2.0f;",
	):
		assert expected in update_block

	assert "cg.simpleItemsBob = cg_simpleItemsBob.value;" not in update_block


def test_qagame_item_timer_transport_keeps_forced_hidden_items_snapshot_visible() -> None:
	source = G_ITEMS.read_text(encoding="utf-8")
	transport_block = _block_from_marker(source, "static qboolean G_ShouldSendItemRespawnTimerSnapshot")
	publisher_block = _block_from_marker(source, "static void G_SetItemRespawnTimerState")
	uses_block = _block_from_marker(source, "qboolean G_ItemUsesRespawnTimer")

	for expected in (
		"if ( respawnDuration <= 0 ) {",
		"if ( g_itemTimers.integer == 0 ) {",
		"if ( !ent || !ent->item || ent->item->quantity == 0 ) {",
		"return G_ItemUsesRespawnTimer( ent->item );",
	):
		assert expected in transport_block

	for expected in (
		"ent->s.time = markerTime;",
		"ent->s.time2 = respawnDuration;",
		"ent->s.retailEventData = ent->team ? 1 : 0;",
		"if ( G_ShouldSendItemRespawnTimerSnapshot( ent, respawnDuration ) ) {",
		"ent->r.svFlags &= ~SVF_NOCLIENT;",
	):
		assert expected in publisher_block

	assert publisher_block.index("ent->s.time2 = respawnDuration;") < publisher_block.index(
		"ent->r.svFlags &= ~SVF_NOCLIENT;"
	)

	for expected in (
		"if ( item->giType == IT_ARMOR && item->quantity >= 25 ) {",
		"case PW_QUAD:",
		"case PW_BATTLESUIT:",
		"case PW_HASTE:",
		"case PW_INVIS:",
		"case PW_REGEN:",
	):
		assert expected in uses_block


def test_cgame_prediction_skips_retail_item_timer_family() -> None:
	source = CG_PREDICT.read_text(encoding="utf-8")
	skip_block = _block_from_marker(source, "static qboolean CG_ItemSkipsPredictablePickup")
	touch_block = _block_from_marker(source, "static void CG_TouchItem")

	for expected in (
		"if ( item->giType == IT_ARMOR && item->quantity >= 25 ) {",
		"if ( item->giType == IT_HEALTH && item->quantity >= 100 ) {",
		"case PW_QUAD:",
		"case PW_BATTLESUIT:",
		"case PW_HASTE:",
		"case PW_INVIS:",
		"case PW_REGEN:",
		"if ( item->giType == IT_HOLDABLE && BG_HoldableForItemTag( item->giTag ) == HI_MEDKIT ) {",
	):
		assert expected in skip_block

	assert "if ( CG_ItemSkipsPredictablePickup( item ) ) {" in touch_block
	assert touch_block.index("item = &bg_itemlist[ cent->currentState.modelindex ];") < touch_block.index(
		"if ( CG_ItemSkipsPredictablePickup( item ) ) {"
	)
	assert touch_block.index("if ( CG_ItemSkipsPredictablePickup( item ) ) {") < touch_block.index(
		"BG_AddPredictableEventToPlayerstate( EV_ITEM_PICKUP"
	)


def test_cg_item_queues_poi_markers_from_raw_item_origin_before_render_offsets() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	item_block = _block_from_marker(source, "static void CG_Item")

	for expected in (
		"VectorCopy( cent->lerpOrigin, itemPOIOrigin );",
		"if ( !( es->eFlags & EF_NODRAW ) || item->giType == IT_POWERUP ) {",
		"CG_UpdatePOIObjectiveCache( item, itemPOIOrigin );",
		"CG_QueueItemPOIMarker( cent, item, itemPOIOrigin );",
	):
		assert expected in item_block

	assert item_block.index('trap_Cvar_VariableStringBuffer( "cg_skipItems"') < item_block.index(
		"VectorCopy( cent->lerpOrigin, itemPOIOrigin );"
	)
	assert item_block.index("CG_QueueItemPOIMarker( cent, item, itemPOIOrigin );") < item_block.index(
		"if ( es->eFlags & EF_NODRAW ) {"
	)
	assert item_block.index("CG_QueueItemPOIMarker( cent, item, itemPOIOrigin );") < item_block.index(
		"if ( cg_simpleItems.integer && item->giType != IT_TEAM ) {"
	)
	assert item_block.index("CG_QueueItemPOIMarker( cent, item, itemPOIOrigin );") < item_block.index(
		"cent->lerpOrigin[2] += 4 + cos"
	)
	assert "CG_QueueItemPOIMarker( cent, item, ent.origin );" not in item_block
	assert "CG_QueueItemPOIMarker( cent, item, cent->lerpOrigin );" not in item_block


def test_cg_item_weapon_pickup_children_and_railgun_color_match_retail_shape() -> None:
	source = CG_ENTS.read_text(encoding="utf-8")
	item_block = _block_from_marker(source, "static void CG_Item")

	for expected in (
		"if ( BG_WeaponForItemTag( item->giTag ) == WP_RAILGUN ) {",
		"ent.shaderRGBA[0] = 0;",
		"ent.shaderRGBA[1] = 255;",
		"ent.shaderRGBA[2] = 0;",
		"ent.shaderRGBA[3] = 255;",
		"if ( wi->barrelModel ) {",
		'CG_PositionRotatedEntityOnTag( &barrel, &ent, wi->weaponModel, "tag_barrel" );',
		"AxisCopy( ent.axis, barrel.axis );",
		"barrel.nonNormalizedAxes = ent.nonNormalizedAxes;",
		"if ( wi->weaponAmmoModel ) {",
		"ammo.hModel = wi->weaponAmmoModel;",
		'CG_PositionRotatedEntityOnTag( &ammo, &ent, wi->weaponModel, "tag_ammo" );',
		"AxisCopy( ent.axis, ammo.axis );",
		"ammo.nonNormalizedAxes = ent.nonNormalizedAxes;",
		"trap_R_AddRefEntityToScene( &ammo );",
	):
		assert expected in item_block

	assert item_block.index("if ( item->giType == IT_WEAPON ) {") < item_block.index(
		"if ( BG_WeaponForItemTag( item->giTag ) == WP_RAILGUN ) {"
	)
	assert item_block.index("trap_R_AddRefEntityToScene(&ent);") < item_block.index(
		"if ( wi->barrelModel ) {"
	)
	assert item_block.index('CG_PositionRotatedEntityOnTag( &barrel, &ent, wi->weaponModel, "tag_barrel" );') < item_block.index(
		"if ( wi->weaponAmmoModel ) {"
	)
	assert item_block.index('CG_PositionRotatedEntityOnTag( &ammo, &ent, wi->weaponModel, "tag_ammo" );') < item_block.index(
		"// accompanying rings / spheres for powerups"
	)
	assert "ammo.hModel = wi->ammoModel;" not in item_block
	assert "cgs.media.weaponHoverSound" not in item_block


def test_cgame_draw_lane_keeps_world_marker_owners_and_closes_appendix_gap() -> None:
	draw_source = CG_DRAW.read_text(encoding="utf-8")
	plan = CG_BG_PLAN.read_text(encoding="utf-8")

	for marker in (
		"cgQueuedWorldMarker_t *CG_AllocQueuedWorldMarker",
		"void CG_UpdateQueuedWorldMarkers",
		"void CG_DrawQueuedWorldMarkers",
	):
		assert marker in draw_source

	assert "| `CG-D2` | Completed 2026-04-05 |" in plan

	cg_d_rows = [line for line in plan.splitlines() if line.startswith("| `CG-D` |")]
	assert cg_d_rows
	assert cg_d_rows[-1].endswith("| None |")
