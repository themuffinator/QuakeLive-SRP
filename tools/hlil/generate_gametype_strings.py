#!/usr/bin/env python3
"""Emit the shared gametype string header from HLIL-aligned metadata."""

#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = REPO_ROOT / "tools" / "hlil" / "gametype_strings.json"
HEADER_PATH = REPO_ROOT / "src" / "code" / "game" / "generated" / "ql_gametype_strings.h"


def _c_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
    return escaped


def _emit_header(data: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append(
        dedent(
            """\
            /*
            ===========================================================================
            Auto-generated file. Run tools/hlil/generate_gametype_strings.py after editing
            tools/hlil/gametype_strings.json.
            ===========================================================================
            */
            #ifndef QL_GAMETYPE_STRINGS_H_
            #define QL_GAMETYPE_STRINGS_H_

            #include "../bg_public.h"

            typedef struct {
            \tconst char\t*objective;
            \tconst char\t*thaw;
            \tconst char\t*freeze;
            \tconst char\t*shoot;
            \tconst char\t*summary;
            } qlFreezeHudTips_t;

            typedef struct {
            \tgametype_t\tgametype;
            \tconst char\t*name;
            \tconst char\t*text;
            \tconst qlFreezeHudTips_t\t*freezeTips;
            } qlGametypeTutorialDef_t;

            static const char *const ql_gametypeHudHints[GT_MAX_GAME_TYPE] = {
            """
        ).strip("\n")
    )

    hud_hints = data.get("hud_hints", [])
    for entry in hud_hints:
        gametype = entry["gametype"]
        hint = _c_literal(entry["hint"])
        lines.append(f"\t[{gametype}] = \"{hint}\",")
    lines.append("};\n")

    freeze_entry = None
    tutorials = data.get("tutorials", [])
    for entry in tutorials:
        tips = entry.get("freeze_tips")
        if tips:
            freeze_entry = tips
            break

    if freeze_entry:
        lines.append("static const qlFreezeHudTips_t ql_freezeHudTips = {")
        for key in ("objective", "thaw", "freeze", "shoot", "summary"):
            value = _c_literal(freeze_entry.get(key, ""))
            lines.append(f"\t.{key} = \"{value}\",")
        lines.append("};\n")
    else:
        lines.append("static const qlFreezeHudTips_t ql_freezeHudTips = { 0 };\n")

    lines.append("static const qlGametypeTutorialDef_t ql_gametypeTutorials[] = {")
    for entry in tutorials:
        gametype = entry["gametype"]
        name = _c_literal(entry["name"])
        text = _c_literal(entry["text"])
        tips = entry.get("freeze_tips")
        tip_ref = "&ql_freezeHudTips" if tips else "NULL"
        lines.append("\t{")
        lines.append(f"\t\t.gametype = {gametype},")
        lines.append(f"\t\t.name = \"{name}\",")
        lines.append(f"\t\t.text = \"{text}\",")
        lines.append(f"\t\t.freezeTips = {tip_ref}")
        lines.append("\t},")
    lines.append("};\n")

    lines.append(
        dedent(
            """\
            #define QL_GAMETYPE_TUTORIAL_COUNT \
            \t( sizeof( ql_gametypeTutorials ) / sizeof( ql_gametypeTutorials[0] ) )

            /*
            =============
            QL_FindGametypeTutorial

            Returns the tutorial entry for the supplied gametype, if present.
            =============
            */
            static inline const qlGametypeTutorialDef_t *QL_FindGametypeTutorial( gametype_t gametype ) {
            \tint\tindex;

            \tfor ( index = 0; index < (int)QL_GAMETYPE_TUTORIAL_COUNT; ++index ) {
            \t\tif ( ql_gametypeTutorials[index].gametype == gametype ) {
            \t\t\treturn &ql_gametypeTutorials[index];
            \t\t}
            \t}

            \treturn NULL;
            }

            /*
            =============
            QL_GametypeHudHint

            Returns the HUD hint string for the provided gametype, if available.
            =============
            */
            static inline const char *QL_GametypeHudHint( gametype_t gametype ) {
            \tif ( gametype < 0 || gametype >= GT_MAX_GAME_TYPE ) {
            \t\treturn NULL;
            \t}

            \treturn ql_gametypeHudHints[gametype];
            }

            #endif /* QL_GAMETYPE_STRINGS_H_ */
            """
        ).strip("\n")
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    HEADER_PATH.write_text(_emit_header(data), encoding="utf-8")


if __name__ == "__main__":
    main()
