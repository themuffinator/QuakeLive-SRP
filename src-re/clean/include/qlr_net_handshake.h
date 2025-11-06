#ifndef QLR_NET_HANDSHAKE_H
#define QLR_NET_HANDSHAKE_H

#include "qlr_recon_shared.h"

typedef enum {
    QLR_CONNSTATE_DISCONNECTED = 0,
    QLR_CONNSTATE_CONNECTING,
    QLR_CONNSTATE_CHALLENGING,
    QLR_CONNSTATE_CONNECTED,
    QLR_CONNSTATE_ACTIVE
} qlr_connstate_t;

typedef enum {
    QLR_NET_EVENT_START_CONNECT,
    QLR_NET_EVENT_CHALLENGE_RECEIVED,
    QLR_NET_EVENT_CONNECT_RESPONSE,
    QLR_NET_EVENT_GAMESTATE_COMPLETE,
    QLR_NET_EVENT_TIMEOUT,
    QLR_NET_EVENT_DISCONNECT
} qlr_net_event_t;

typedef struct qlr_net_handshake_hooks_s {
    void (*send_get_challenge)(void);
    void (*send_connect)(int challenge);
    void (*request_gamestate)(void);
    void (*on_connected)(void);
    void (*on_reset)(void);
} qlr_net_handshake_hooks_t;

typedef struct qlr_net_handshake_context_s {
    qlr_connstate_t state;
    int connect_time_ms;
    int resend_interval_ms;
    int connect_packet_count;
    int challenge_token;
    bool has_challenge;
    qlr_net_handshake_hooks_t hooks;
} qlr_net_handshake_context_t;

typedef struct qlr_net_handshake_event_data_s {
    int timestamp_ms;
    int challenge_token;
} qlr_net_handshake_event_data_t;

void QLR_NetHandshake_Bind(qlr_net_handshake_context_t *ctx);
void QLR_NetHandshake_Unbind(void);
void QLR_NetHandshake_ProcessEvent(qlr_net_event_t event, const qlr_net_handshake_event_data_t *data);
void QLR_NetHandshake_Update(int now_ms);

#endif /* QLR_NET_HANDSHAKE_H */
