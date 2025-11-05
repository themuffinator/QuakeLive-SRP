// Spawn logic reconstruction for Quake Live VM
// Primary address: 0x0010B000 (__cdecl G_SpawnEntitiesFromString)
// Helper routines: 0x0010AFA0 (ParseSpawnVars), 0x0010B4D0 (FinishSpawning)

#include "g_local.h"

// Partial spawnVar_t layout (size 0x34):
//   0x00: char *key;
//   0x04: char *value;
//   0x08: int keyHash;        // used for fast lookups
//   0x0C: spawnVar_t *next;
//
// The worldspawn entity is index 0 and occupies g_entities[0].

static void __cdecl SpawnAllEntities(void);
static void __cdecl SpawnSingleEntity(gentity_t *ent, spawnVar_t *vars);

void __cdecl G_SpawnEntitiesFromString(const char *mapname, int spawnFlags) {
    // 0x0010B01A: reset global spawn state
    level.numSpawnVars = 0;
    level.spawnVarsValid = qfalse;

    if (!ParseSpawnVars(mapname)) {           // 0x0010B032: parse entity lump
        Com_Error(ERR_DROP, "Spawn string parse failed");
        return;
    }

    SpawnAllEntities();                       // 0x0010B052: iterate entity defs
    FinishSpawning();                         // 0x0010B05A

    // 0x0010B06A: spawn flagged bots after world is ready
    if (spawnFlags & SPAWN_ENABLE_BOTS) {
        InitBotsForMap(mapname);
    }
}

static void __cdecl SpawnAllEntities(void) {
    // 0x0010B0A0: sequentially read spawnvars array
    for (int index = 0; index < level.numSpawnVars; ++index) {
        spawnVar_t *vars = &level.spawnVars[index];
        gentity_t *ent = G_Spawn();            // 0x0010B0BC

        // 0x0010B0C6: copy common fields
        ent->s.number = index;
        ent->classname = G_GetSpawnVar(vars, "classname");
        ent->spawnflags = atoi(G_GetSpawnVarDef(vars, "spawnflags", "0"));

        SpawnSingleEntity(ent, vars);

        if (!ent->inuse) {
            // 0x0010B108: spawn function may free entity; skip post steps
            continue;
        }

        // 0x0010B120: run think immediately if requested
        if (ent->think && ent->nextthink <= level.time) {
            ent->think(ent);
        }
    }
}

static void __cdecl SpawnSingleEntity(gentity_t *ent, spawnVar_t *vars) {
    // 0x0010B200: dispatch table keyed by classname hash
    const spawnEntry_t *entry = LookupSpawnEntry(vars);
    if (!entry) {
        Com_Printf("Unknown entity classname %s\n", ent->classname);
        G_FreeEntity(ent);
        return;
    }

    // 0x0010B236: call entity-specific spawn
    entry->spawn(ent, vars);                  // __cdecl target

    if (ent->team && !(ent->flags & FL_TEAMSLAVE)) {
        // 0x0010B260: link team chains after spawn
        G_AddToTeam(ent);
    }

    trap_LinkEntity(&ent->s);                 // 0x0010B28C: link to collision world
}
