from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_cg_loading_string_keeps_retail_null_fatal_contract() -> None:
	cg_info = _read("src/code/cgame/cg_info.c")

	assert "static const char *CG_SanitizeLoadingString" not in cg_info
	assert "display = s ? s : \"\";" not in cg_info
	assert "Q_strncpyz( cg.infoScreenText, text, sizeof( cg.infoScreenText ) );" in cg_info
	assert "CG_SetLoadingScreenText( s );" in cg_info
	assert "trap_AdvertisementBridge_UpdateLoadingViewParameters();" in cg_info
	assert "trap_AdvertisementBridge_SetFrameTime( 1000 );" in cg_info


def test_cg_loading_client_uses_retail_model_skin_split_and_fallback() -> None:
	cg_info = _read("src/code/cgame/cg_info.c")

	assert "CG_GetLoadingClientIconSkin" not in cg_info
	assert "team = atoi( Info_ValueForKey( info, \"t\" ) );" not in cg_info
	assert "slash = Q_strrchr( model, '/' );" in cg_info
	assert "skin = \"default\";" in cg_info
	assert "Com_sprintf( iconName, MAX_QPATH, \"models/players/%s/icon_%s.tga\", \"sarge\", \"default\" );" in cg_info


def test_cg_draw_information_uses_retail_title_and_author_rules() -> None:
	cg_info = _read("src/code/cgame/cg_info.c")

	assert "CG_GetLoadingMapTitle" not in cg_info
	assert "title = CG_ConfigString( CS_MESSAGE );" in cg_info
	assert "CG_DrawLoadingText( LOADING_TITLE_X, LOADING_TITLE_Y, LOADING_TITLE_SCALE, title, qfalse );" in cg_info
	assert "author = CG_ConfigString( CS_MAP_AUTHOR );" in cg_info
	assert "authorAlt = CG_ConfigString( CS_MAP_AUTHOR_ALT );" in cg_info
