#include "../include/qlr_game_frame.h"

static qlr_game_frame_context_t *qlr_game_frame_ctx = NULL;

void QLR_Game_BindFrameContext(qlr_game_frame_context_t *ctx) {
    qlr_game_frame_ctx = ctx;
    qlr_native_shim_logf("game", "BindContext", "ctx=%p", (void *)ctx);
}

void QLR_Game_UnbindFrameContext(void) {
    qlr_native_shim_logf("game", "UnbindContext", "ctx=%p", (void *)qlr_game_frame_ctx);
    qlr_game_frame_ctx = NULL;
}

static void qlr_game_run_scheduled_thinks(qlr_game_frame_context_t *ctx, int msec) {
    if (!ctx || !ctx->level) {
        return;
    }

    if (ctx->hooks.run_scheduled_thinks) {
        qlr_native_shim_logf("game", "hook", "run_scheduled_thinks(%d)", msec);
        ctx->hooks.run_scheduled_thinks(msec);
        return;
    }

    size_t count = ctx->entity_count;
    if (count == 0 && ctx->level) {
        count = (size_t)ctx->level->num_entities;
    }

    if (ctx->entities && count > 0) {
        for (size_t index = 0; index < count; ++index) {
            qlr_gentity_t *ent = &ctx->entities[index];
            if (!ent->inuse || ent->nextthink == 0 || ent->nextthink > ctx->level->time) {
                continue;
            }

            ent->nextthink = 0;
            if (ent->think) {
                qlr_native_shim_logf("game", "think", "ent=%zu", index);
                ent->think(ent);
            }
        }
        return;
    }

    for (qlr_gentity_t *ent = ctx->level->first_entity; ent; ent = ent->next) {
        if (!ent->inuse || ent->nextthink == 0 || ent->nextthink > ctx->level->time) {
            continue;
        }

        ent->nextthink = 0;
        if (ent->think) {
            qlr_native_shim_logf("game", "think", "ent=%p", (void *)ent);
            ent->think(ent);
        }
    }
}

static void qlr_game_step_entities(qlr_game_frame_context_t *ctx) {
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
            qlr_native_shim_logf("game", "hook", "physics_step(%zu)", index);
            ctx->hooks.physics_step(ent);
        }

        if (ent->client && ctx->hooks.client_think) {
            qlr_native_shim_logf("game", "hook", "client_think(%zu)", index);
            ctx->hooks.client_think(ent);
        }
    }
}

static void qlr_game_dispatch_events(qlr_game_frame_context_t *ctx) {
    if (!ctx || !ctx->level || !ctx->entities || !ctx->hooks.fire_event) {
        return;
    }

    size_t count = ctx->entity_count;
    if (count == 0) {
        count = (size_t)ctx->level->num_entities;
    }

    for (size_t index = 0; index < count; ++index) {
        qlr_gentity_t *ent = &ctx->entities[index];
        if (!ent->inuse || ent->event_time == 0) {
            continue;
        }

        if (ent->event_time > ctx->level->time) {
            continue;
        }

        qlr_native_shim_logf("game", "hook", "fire_event(%zu)", index);
        ctx->hooks.fire_event(ent);
    }
}

static void qlr_game_finish_client_frames(qlr_game_frame_context_t *ctx) {
    if (!ctx || !ctx->level || !ctx->entities || !ctx->hooks.client_end_frame) {
        return;
    }

    int max_clients = ctx->level->maxclients;
    for (int i = 0; i < max_clients; ++i) {
        qlr_gentity_t *ent = &ctx->entities[i];
        if (!ent->inuse || !ent->client) {
            continue;
        }

        qlr_native_shim_logf("game", "hook", "client_end_frame(%d)", i);
        ctx->hooks.client_end_frame(ent);
    }
}

static void qlr_game_check_timers(qlr_game_frame_context_t *ctx) {
    if (!ctx || !ctx->level) {
        return;
    }

    qlr_level_locals_t *level = ctx->level;

    if (level->warmup_time && level->time >= level->warmup_time) {
        level->warmup_time = 0;
        if (ctx->hooks.begin_match) {
            qlr_native_shim_logf("game", "hook", "begin_match()");
            ctx->hooks.begin_match();
        }
    }

    if (level->intermission_queued && level->time >= level->intermission_queued) {
        if (ctx->hooks.begin_intermission) {
            qlr_native_shim_logf("game", "hook", "begin_intermission()");
            ctx->hooks.begin_intermission();
        }
    }
}

void G_RunFrame(int level_time) {
    qlr_game_frame_context_t *ctx = qlr_game_frame_ctx;
    if (!ctx || !ctx->level) {
        qlr_native_shim_logf("game", "G_RunFrame", "unbound level_time=%d", level_time);
        return;
    }

    qlr_level_locals_t *level = ctx->level;
    int msec = level_time - level->time;
    if (msec < 0) {
        msec = 0;
    }

    qlr_native_shim_logf("game", "G_RunFrame", "start level_time=%d previous=%d msec=%d",
                         level_time,
                         level->time,
                         msec);

    level->previous_time = level->time;
    level->time = level_time;
    level->msec = msec;
    level->framenum += 1;

    qlr_game_run_scheduled_thinks(ctx, msec);
    qlr_game_step_entities(ctx);
    qlr_game_dispatch_events(ctx);
    qlr_game_finish_client_frames(ctx);
    qlr_game_check_timers(ctx);

    qlr_native_shim_logf("game", "G_RunFrame", "end framenum=%d time=%d",
                         level->framenum,
                         level->time);
}
