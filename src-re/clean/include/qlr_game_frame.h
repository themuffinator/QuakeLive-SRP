#ifndef QLR_GAME_FRAME_H
#define QLR_GAME_FRAME_H

#include "qlr_recon_shared.h"

typedef struct qlr_gclient_s qlr_gclient_t;

typedef struct qlr_gentity_s {
    bool inuse;
    int nextthink;
    int event_time;
    int flags;
    const char *team;
    qlr_gclient_t *client;
    void (*think)(struct qlr_gentity_s *self);
    struct qlr_gentity_s *next;
} qlr_gentity_t;

typedef struct qlr_level_locals_s {
    int time;
    int previous_time;
    int msec;
    int framenum;
    int warmup_time;
    int intermission_queued;
    int maxclients;
    int num_entities;
    qlr_gentity_t *first_entity;
} qlr_level_locals_t;

typedef struct qlr_game_frame_hooks_s {
    void (*run_scheduled_thinks)(int msec);
    void (*physics_step)(qlr_gentity_t *ent);
    void (*client_think)(qlr_gentity_t *ent);
    void (*fire_event)(qlr_gentity_t *ent);
    void (*client_end_frame)(qlr_gentity_t *ent);
    void (*begin_match)(void);
    void (*begin_intermission)(void);
} qlr_game_frame_hooks_t;

typedef struct qlr_game_frame_context_s {
    qlr_level_locals_t *level;
    qlr_gentity_t *entities;
    size_t entity_count;
    qlr_game_frame_hooks_t hooks;
} qlr_game_frame_context_t;

void QLR_Game_BindFrameContext(qlr_game_frame_context_t *ctx);
void QLR_Game_UnbindFrameContext(void);
void G_RunFrame(int level_time);

#endif /* QLR_GAME_FRAME_H */
