// Entity think pipeline reconstruction
// Primary entry: 0x00108E20 (__cdecl G_RunThink)
// Secondary callsites: frame loop (0x0010A7A4) and spawning (0x0010B134)
// Purpose: invoke scheduled think callbacks and maintain AI/logic order.

#include "g_local.h"

// Additional struct snippets:
// gentity_t {
//   ...
//   0x00C0: int nextthink;     // absolute level.time the think fires
//   0x00C4: int health;        // used by some think functions to self-remove
//   0x00C8: void *scriptHook;  // mission pack only
//   0x00CC: int flags;         // ENTITY_FLAG_* bitmask
// }

static void __cdecl G_PreThink(gentity_t *ent);
static void __cdecl G_PostThink(gentity_t *ent);

void __cdecl G_RunThink_Pipeline(int timeDelta) {
    // 0x00108E34: load pointer to first entity in linked list
    gentity_t *ent = level.firstEntity;
    while (ent) {
        gentity_t *next = ent->next; // 0x00108E44: preserve next pointer as think may free

        if (!ent->inuse) {
            ent = next;
            continue;
        }

        // 0x00108E58: optional pre-think hook (covers movers and scripted logic)
        G_PreThink(ent);

        if (ent->nextthink && ent->nextthink <= level.time) {
            ent->nextthink = 0;              // 0x00108E7C
            if (ent->think) {                // 0x00108E82
                // __thiscall converted to __cdecl via thunk for C-style functions
                ent->think(ent);             // 0x00108E8E
            }
        }

        // 0x00108EA4: post-think ensures flags and linked portals update
        G_PostThink(ent);
        ent = next;                           // iterate
    }
}

static void __cdecl G_PreThink(gentity_t *ent) {
    // 0x00108C00: mover activation pipeline
    if (ent->flags & 0x00000020) {            // EF_TOUCHED
        ent->flags &= ~0x00000020;            // clear latched flag
        ActivateTriggered(ent);               // 0x00108C2E
    }

    if (ent->health <= 0 && (ent->flags & 0x00000004)) {
        // 0x00108C48: dead entities with removal flag call their die function
        if (ent->die) {
            ent->die(ent, ent->enemy, ent->damage, MOD_UNKNOWN);
        }
    }
}

static void __cdecl G_PostThink(gentity_t *ent) {
    // 0x00108D90: ensures event bits replicate to clients
    if (ent->eventTime && ent->eventTime <= level.time) {
        FireEntityEvent(ent);                 // matches frame loop version
    }

    if (ent->s.eType == ET_ITEM) {
        UpdateItemRespawn(ent);               // 0x00108DDA
    }

    if (ent->client) {
        ClientPostThink(ent);                 // 0x00108DF4
    }
}
