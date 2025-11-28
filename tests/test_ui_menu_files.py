from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _extract_define(text: str, name: str) -> str:
    pattern = rf"#define\s+{re.escape(name)}\s+\"([^\"]+)\""
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"define for {name} not found")
    return match.group(1)


def test_ui_menu_defaults_use_existing_assets() -> None:
    ui_main = (REPO_ROOT / "src/code/ui/ui_main.c").read_text(encoding="utf-8")
    assert '"ui_menuFiles", UI_MENU_FILE_QUAKELIVE' in ui_main
    assert '"ui_menuFlow", "1"' in ui_main

    ui_local = (REPO_ROOT / "src/code/ui/ui_local.h").read_text(encoding="utf-8")
    quakelive_menu = _extract_define(ui_local, "UI_MENU_FILE_QUAKELIVE")
    quakelive_ingame = _extract_define(ui_local, "UI_INGAME_FILE_QUAKELIVE")
    main_menu = _extract_define(ui_local, "UI_MENU_FILE_QUAKELIVE_MAIN")
    ingame_menu = _extract_define(ui_local, "UI_MENU_FILE_QUAKELIVE_INGAME")

    search_roots = [REPO_ROOT / "src", REPO_ROOT / "assets/quakelive/baseq3"]

    for menu_file in (quakelive_menu, quakelive_ingame, main_menu, ingame_menu):
        assert any((root / menu_file).exists() for root in search_roots), menu_file


def test_web_commands_exposed_to_client_vm() -> None:
    cl_main = (REPO_ROOT / "src/code/client/cl_main.c").read_text(encoding="utf-8")
    cl_cgame = (REPO_ROOT / "src/code/client/cl_cgame.c").read_text(encoding="utf-8")

    for command in ("web_showBrowser", "web_changeHash", "web_browserActive", "web_stopRefresh"):
        assert f'Cmd_AddCommand ("{command}"' in cl_main
        assert command in cl_cgame
