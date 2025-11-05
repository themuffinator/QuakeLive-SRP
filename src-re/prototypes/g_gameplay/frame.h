#ifndef QLR_PROTO_GAME_FRAME_H
#define QLR_PROTO_GAME_FRAME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "../common/native_shim.h"

typedef struct qlr_gentity_s qlr_gentity_t;
typedef struct qlr_gclient_s qlr_gclient_t;

typedef void (*qlr_gentity_think_t)(qlr_gentity_t *self);
typedef void (*qlr_game_void_hook_t)(void);
typedef void (*qlr_game_entity_hook_t)(qlr_gentity_t *ent);

typedef struct qlr_gentity_s {
    bool inuse;
    qlr_gentity_t *next;
    qlr_gclient_t *client;
    qlr_gentity_think_t think;
    int nextthink;
    int eventTime;
} qlr_gentity_t;

typedef struct {
    int time;
    int previousTime;
    int framenum;
    int startTime;
    int msec;
    int num_entities;
    int maxclients;
    int warmupTime;
    int intermissionQueued;
    qlr_gentity_t *firstEntity;
} qlr_level_locals_t;

typedef struct {
    void (*run_scheduled_thinks)(int msec);
    qlr_game_entity_hook_t physics_step;
    qlr_game_entity_hook_t client_think;
    qlr_game_entity_hook_t fire_event;
    qlr_game_entity_hook_t client_end_frame;
    qlr_game_void_hook_t begin_match;
    qlr_game_void_hook_t begin_intermission;
} qlr_game_frame_hooks_t;

typedef struct {
    qlr_level_locals_t *level;
    qlr_gentity_t *entities;
    size_t entity_count;
    qlr_game_frame_hooks_t hooks;
} qlr_game_frame_context_t;

void QLR_Game_BindFrameContext(qlr_game_frame_context_t *ctx);
void QLR_Game_UnbindFrameContext(void);
void G_RunFrame(int levelTime);

#endif /* QLR_PROTO_GAME_FRAME_H */
