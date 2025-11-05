#include "frame.h"

static qlr_game_frame_context_t *qlr_game_frame_ctx = NULL;

void QLR_Game_BindFrameContext(qlr_game_frame_context_t *ctx) {
    qlr_game_frame_ctx = ctx;
    qlr_native_shim_logf("game", "BindContext", "ctx=%p", (void *)ctx);
}

void QLR_Game_UnbindFrameContext(void) {
    qlr_native_shim_logf("game", "UnbindContext", "ctx=%p", (void *)qlr_game_frame_ctx);
    qlr_game_frame_ctx = NULL;
}

static void qlr_game_run_think(qlr_game_frame_context_t *ctx, int msec) {
    if (!ctx || !ctx->level) {
        return;
    }

    if (ctx->hooks.run_scheduled_thinks) {
        qlr_native_shim_logf("game", "hook", "run_scheduled_thinks(%d)", msec);
        ctx->hooks.run_scheduled_thinks(msec);
        return;
    }

    for (qlr_gentity_t *ent = ctx->level->firstEntity; ent; ent = ent->next) {
        if (!ent->inuse || !ent->nextthink) {
            continue;
        }
        if (ent->nextthink > ctx->level->time) {
            continue;
        }
        ent->nextthink = 0;
        if (ent->think) {
            qlr_native_shim_logf("game", "think", "ent=%p", (void *)ent);
            ent->think(ent);
        }
    }
}

static void qlr_game_run_entity_frame(qlr_game_frame_context_t *ctx) {
    if (!ctx || !ctx->level || !ctx->entities) {
        return;
    }

    size_t count = ctx->entity_count;
    if (count == 0) {
        count = (size_t)ctx->level->num_entities;
    }

    for (size_t index = 0; index < count; ++index) {
        qlr_gentity_t *ent = &ctx->entities[index];
        if (!ent->inuse) {
            continue;
        }
        if (ctx->hooks.physics_step) {
            qlr_native_shim_logf("game", "hook", "physics_step(ent=%zu)", index);
            ctx->hooks.physics_step(ent);
        }
        if (ent->client && ctx->hooks.client_think) {
            qlr_native_shim_logf("game", "hook", "client_think(ent=%zu)", index);
            ctx->hooks.client_think(ent);
        }
    }
}

static void qlr_game_check_events(qlr_game_frame_context_t *ctx) {
    if (!ctx || !ctx->level || !ctx->entities) {
        return;
    }

    size_t count = ctx->entity_count;
    if (count == 0) {
        count = (size_t)ctx->level->num_entities;
    }

    for (size_t index = 0; index < count; ++index) {
        qlr_gentity_t *ent = &ctx->entities[index];
        if (!ent->inuse || !ent->eventTime) {
            continue;
        }
        if (ent->eventTime > ctx->level->time) {
            continue;
        }
        if (ctx->hooks.fire_event) {
            qlr_native_shim_logf("game", "hook", "fire_event(ent=%zu)", index);
            ctx->hooks.fire_event(ent);
        }
    }
}

static void qlr_game_client_end_frame(qlr_game_frame_context_t *ctx) {
    if (!ctx || !ctx->level || !ctx->entities || !ctx->hooks.client_end_frame) {
        return;
    }

    int maxClients = ctx->level->maxclients;
    for (int i = 0; i < maxClients; ++i) {
        qlr_gentity_t *ent = &ctx->entities[i];
        if (!ent->inuse || !ent->client) {
            continue;
        }
        qlr_native_shim_logf("game", "hook", "client_end_frame(ent=%d)", i);
        ctx->hooks.client_end_frame(ent);
    }
}

static void qlr_game_check_timers(qlr_game_frame_context_t *ctx) {
    if (!ctx || !ctx->level) {
        return;
    }

    if (ctx->level->warmupTime && ctx->level->time >= ctx->level->warmupTime) {
        ctx->level->warmupTime = 0;
        if (ctx->hooks.begin_match) {
            qlr_native_shim_logf("game", "hook", "begin_match()");
            ctx->hooks.begin_match();
        }
    }

    if (ctx->level->intermissionQueued && ctx->level->time >= ctx->level->intermissionQueued) {
        if (ctx->hooks.begin_intermission) {
            qlr_native_shim_logf("game", "hook", "begin_intermission()");
            ctx->hooks.begin_intermission();
        }
    }
}

void G_RunFrame(int levelTime) {
    qlr_game_frame_context_t *ctx = qlr_game_frame_ctx;
    if (!ctx || !ctx->level) {
        qlr_native_shim_logf("game", "G_RunFrame", "unbound levelTime=%d", levelTime);
        return;
    }

    qlr_level_locals_t *level = ctx->level;
    int msec = levelTime - level->time;
    if (msec < 0) {
        msec = 0;
    }

    qlr_native_shim_logf("game", "G_RunFrame", "start levelTime=%d previous=%d -> msec=%d", levelTime, level->time, msec);

    level->previousTime = level->time;
    level->time = levelTime;
    level->msec = msec;
    level->framenum++;

    qlr_game_run_think(ctx, msec);
    qlr_game_run_entity_frame(ctx);
    qlr_game_check_events(ctx);
    qlr_game_client_end_frame(ctx);
    qlr_game_check_timers(ctx);

    qlr_native_shim_logf("game", "G_RunFrame", "end framenum=%d time=%d", level->framenum, level->time);
}
