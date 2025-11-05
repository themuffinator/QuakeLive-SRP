// Decompiled Quake Live game VM frame loop
// Address: 0x0010A740 (qagamex86.dll)
// Calling convention: __cdecl G_RunFrame(int levelTime)
// Notes: This translation preserves the original control flow while
//        renaming variables for clarity. The VM uses 32-bit ints for time
//        and relies on global state stored in levelLocals_t (see below).

#include "g_local.h" // Referenced for struct definitions in original source

// Relevant struct layout snapshot (extracted from static analysis):
// levelLocals_t (size 0x1384) {
//   0x0000: int time;
//   0x0004: int previousTime;
//   0x0008: int framenum;
//   0x000C: int startTime;
//   0x0010: int msec;
//   ...
//   0x012C: int num_entities;
//   0x0130: gentity_t *firstEntity;
// }
// gentity_t (size 0x210) {
//   0x0000: entityState_t s;
//   0x00B4: gclient_t *client;
//   0x00B8: void (__cdecl *think)(gentity_t *self);
//   0x00BC: int nextthink;
//   ...
// }

void __cdecl G_RunFrame(int levelTime) {
    // 0x0010A75C: prologue stores previous frame time
    int msec = levelTime - level.time;        // delta in ms since last frame
    if (msec < 0) {
        // 0x0010A776: guard against time rewinds (e.g. loading save)
        msec = 0;
    }

    level.previousTime = level.time;          // 0x0010A77E
    level.time = levelTime;                   // 0x0010A786
    level.msec = msec;                        // 0x0010A78E
    level.framenum++;                         // 0x0010A797

    // 0x0010A7A4: run world updates (damage over time, movers, etc.)
    G_RunThink(msec);

    // 0x0010A7B0: iterate active entities
    G_RunEntityFrame();

    // 0x0010A7BC: evaluate scheduled events
    CheckEvents();

    // 0x0010A7CA: send new snapshots to clients
    ClientEndFrame();

    // 0x0010A7D6: level-wide timers (warmup, intermission)
    LevelCheckTimers();
}

static void G_RunThink(int msec) {
    // 0x00108F40: tight loop over scheduled think callbacks
    gentity_t *ent = level.firstEntity;       // 0x00108F4B
    for (; ent; ent = ent->next) {            // 0x00108F58
        if (!ent->inuse) {
            continue;                         // 0x00108F60
        }

        if (!ent->nextthink) {                // 0x00108F66
            continue;                         // no think scheduled
        }

        if (ent->nextthink > level.time) {
            continue;                         // not yet time
        }

        ent->nextthink = 0;                   // 0x00108F7D
        if (ent->think) {
            ent->think(ent);                  // 0x00108F84 - indirect call
        }
    }
}

static void G_RunEntityFrame(void) {
    // 0x00109520: handles physics + AI updates for all entities
    for (int i = 0; i < level.num_entities; ++i) {
        gentity_t *ent = &g_entities[i];      // 0x00109530
        if (!ent->inuse) {
            continue;
        }

        // 0x0010953A: integrate entity physics
        G_PhysicsStep(ent);

        // 0x00109550: handle client-specific updates
        if (ent->client) {
            ClientThink_real(ent);
        }
    }
}

static void CheckEvents(void) {
    // 0x00109DA0: promotes queued entity events
    for (int i = 0; i < level.num_entities; ++i) {
        gentity_t *ent = &g_entities[i];
        if (!ent->inuse) {
            continue;
        }

        if (ent->eventTime && ent->eventTime <= level.time) {
            FireEntityEvent(ent);             // 0x00109DDE
        }
    }
}

static void ClientEndFrame(void) {
    // 0x0010A2C0: finalizes player states prior to snapshot
    for (int i = 0; i < level.maxclients; ++i) {
        gentity_t *ent = &g_entities[i];
        if (!ent->inuse || !ent->client) {
            continue;
        }
        ClientEndFrameVM(ent);                // 0x0010A30A
    }
}

static void LevelCheckTimers(void) {
    // 0x0010A520: handles warmup/intermission transitions
    if (level.warmupTime && level.time >= level.warmupTime) {
        level.warmupTime = 0;
        BeginMatch();                         // 0x0010A55E
    }

    if (level.intermissionQueued && level.time >= level.intermissionQueued) {
        BeginIntermission();                  // 0x0010A58A
    }
}
