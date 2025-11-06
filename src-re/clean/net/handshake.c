#include "../include/qlr_net_handshake.h"

static qlr_net_handshake_context_t *qlr_net_handshake_ctx = NULL;

static void qlr_net_reset_challenge(qlr_net_handshake_context_t *ctx) {
    if (!ctx) {
        return;
    }

    ctx->has_challenge = false;
    ctx->challenge_token = 0;
}

static void qlr_net_set_state(qlr_net_handshake_context_t *ctx, qlr_connstate_t next_state) {
    if (!ctx || ctx->state == next_state) {
        return;
    }

    qlr_native_shim_logf("net", "state", "%d -> %d", ctx->state, next_state);
    ctx->state = next_state;
}

void QLR_NetHandshake_Bind(qlr_net_handshake_context_t *ctx) {
    qlr_net_handshake_ctx = ctx;
    if (ctx && ctx->resend_interval_ms <= 0) {
        ctx->resend_interval_ms = 3000;
    }

    if (ctx && (ctx->state < QLR_CONNSTATE_DISCONNECTED || ctx->state > QLR_CONNSTATE_ACTIVE)) {
        ctx->state = QLR_CONNSTATE_DISCONNECTED;
    }

    qlr_native_shim_logf("net", "BindContext", "ctx=%p", (void *)ctx);
}

void QLR_NetHandshake_Unbind(void) {
    qlr_native_shim_logf("net", "UnbindContext", "ctx=%p", (void *)qlr_net_handshake_ctx);
    qlr_net_handshake_ctx = NULL;
}

static void qlr_net_issue_getchallenge(qlr_net_handshake_context_t *ctx) {
    if (!ctx || !ctx->hooks.send_get_challenge) {
        return;
    }

    qlr_native_shim_logf("net", "handshake", "send_getchallenge(count=%d)", ctx->connect_packet_count);
    ctx->hooks.send_get_challenge();
}

static void qlr_net_issue_connect(qlr_net_handshake_context_t *ctx) {
    if (!ctx || !ctx->hooks.send_connect) {
        return;
    }

    qlr_native_shim_logf("net", "handshake", "send_connect(challenge=%d count=%d)",
                         ctx->challenge_token,
                         ctx->connect_packet_count);
    ctx->hooks.send_connect(ctx->challenge_token);
}

void QLR_NetHandshake_ProcessEvent(qlr_net_event_t event, const qlr_net_handshake_event_data_t *data) {
    qlr_net_handshake_context_t *ctx = qlr_net_handshake_ctx;
    if (!ctx) {
        return;
    }

    switch (event) {
        case QLR_NET_EVENT_START_CONNECT:
            qlr_native_shim_logf("net", "event", "start_connect");
            qlr_net_reset_challenge(ctx);
            ctx->connect_packet_count = 0;
            ctx->connect_time_ms = data ? data->timestamp_ms : 0;
            qlr_net_set_state(ctx, QLR_CONNSTATE_CONNECTING);
            qlr_net_issue_getchallenge(ctx);
            break;

        case QLR_NET_EVENT_CHALLENGE_RECEIVED:
            qlr_native_shim_logf("net", "event", "challenge token=%d", data ? data->challenge_token : -1);
            if (ctx->state < QLR_CONNSTATE_CONNECTING) {
                break;
            }
            ctx->challenge_token = data ? data->challenge_token : 0;
            ctx->has_challenge = true;
            ctx->connect_packet_count = 0;
            ctx->connect_time_ms = data ? data->timestamp_ms : ctx->connect_time_ms;
            qlr_net_set_state(ctx, QLR_CONNSTATE_CHALLENGING);
            qlr_net_issue_connect(ctx);
            break;

        case QLR_NET_EVENT_CONNECT_RESPONSE:
            qlr_native_shim_logf("net", "event", "connect_response");
            if (ctx->state < QLR_CONNSTATE_CHALLENGING) {
                break;
            }
            qlr_net_set_state(ctx, QLR_CONNSTATE_CONNECTED);
            if (ctx->hooks.request_gamestate) {
                qlr_native_shim_logf("net", "handshake", "request_gamestate");
                ctx->hooks.request_gamestate();
            }
            break;

        case QLR_NET_EVENT_GAMESTATE_COMPLETE:
            qlr_native_shim_logf("net", "event", "gamestate_complete");
            qlr_net_set_state(ctx, QLR_CONNSTATE_ACTIVE);
            if (ctx->hooks.on_connected) {
                qlr_native_shim_logf("net", "handshake", "connected");
                ctx->hooks.on_connected();
            }
            break;

        case QLR_NET_EVENT_TIMEOUT:
            qlr_native_shim_logf("net", "event", "timeout");
            if (ctx->hooks.on_reset) {
                ctx->hooks.on_reset();
            }
            qlr_net_reset_challenge(ctx);
            ctx->connect_packet_count = 0;
            ctx->connect_time_ms = data ? data->timestamp_ms : 0;
            qlr_net_set_state(ctx, QLR_CONNSTATE_CONNECTING);
            qlr_net_issue_getchallenge(ctx);
            break;

        case QLR_NET_EVENT_DISCONNECT:
            qlr_native_shim_logf("net", "event", "disconnect");
            if (ctx->hooks.on_reset) {
                ctx->hooks.on_reset();
            }
            qlr_net_reset_challenge(ctx);
            ctx->connect_packet_count = 0;
            ctx->connect_time_ms = 0;
            qlr_net_set_state(ctx, QLR_CONNSTATE_DISCONNECTED);
            break;
    }
}

void QLR_NetHandshake_Update(int now_ms) {
    qlr_net_handshake_context_t *ctx = qlr_net_handshake_ctx;
    if (!ctx) {
        return;
    }

    if (ctx->state != QLR_CONNSTATE_CONNECTING && ctx->state != QLR_CONNSTATE_CHALLENGING) {
        return;
    }

    int elapsed = now_ms - ctx->connect_time_ms;
    if (elapsed < ctx->resend_interval_ms) {
        return;
    }

    ctx->connect_time_ms = now_ms;
    ctx->connect_packet_count += 1;

    if (ctx->state == QLR_CONNSTATE_CONNECTING || !ctx->has_challenge) {
        qlr_net_issue_getchallenge(ctx);
        return;
    }

    qlr_net_issue_connect(ctx);
}
