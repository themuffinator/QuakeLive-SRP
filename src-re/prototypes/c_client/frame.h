#ifndef QLR_PROTO_CLIENT_FRAME_H
#define QLR_PROTO_CLIENT_FRAME_H

#include <stdbool.h>
#include <stdint.h>

#include "../common/native_shim.h"

typedef enum {
    QLR_CA_UNINITIALIZED = -1,
    QLR_CA_DISCONNECTED = 0,
    QLR_CA_CONNECTING = 1,
    QLR_CA_CHALLENGING = 2,
    QLR_CA_CONNECTED = 3,
    QLR_CA_PRIMED = 4,
    QLR_CA_ACTIVE = 5,
    QLR_CA_CINEMATIC = 6,
} qlr_client_state_t;

typedef struct {
    int integer;
    float value;
    const char *string;
} qlr_cvar_shadow_t;

typedef struct {
    bool rendererStarted;
    bool soundStarted;
    bool soundRegistered;
    bool uiStarted;
    bool cddialog;
    qlr_client_state_t state;
    int keyCatchers;
    int realtime;
    int frametime;
    int realFrametime;
} qlr_client_static_shadow_t;

typedef struct {
    int32_t valid;
    int32_t snapFlags;
    int32_t serverTime;
    int32_t messageNum;
    int32_t deltaNum;
    int32_t ping;
    uint8_t areamask[32];
    int32_t cmdNum;
    uint8_t playerState[0x16C];
    int32_t numEntities;
    int32_t parseEntitiesNum;
    int32_t serverCommandNum;
} qlr_cl_snapshot_t;

typedef struct {
    qlr_cl_snapshot_t latest;
    int32_t serverTime;
    int32_t oldServerTime;
    int32_t oldFrameServerTime;
    int32_t serverTimeDelta;
    int32_t extrapolatedSnapshot;
    int32_t newSnapshots;
} qlr_client_timing_window_t;

typedef struct {
    int timeoutcount;
    qlr_client_timing_window_t timing;
} qlr_client_active_shadow_t;

typedef struct {
    bool demorecording;
    bool demowaiting;
    bool demoplaying;
    bool firstDemoFrameSkipped;
    int serverMessageSequence;
    int lastPacketTime;
    int timeDemoBaseTime;
    int timeDemoFrames;
    int timeDemoStart;
    int netchanSequence;
} qlr_client_connection_shadow_t;

typedef struct {
    qlr_cvar_shadow_t *com_cl_running;
    qlr_cvar_shadow_t *cl_avidemo;
    qlr_cvar_shadow_t *cl_forceavidemo;
    qlr_cvar_shadow_t *com_timescale;
    qlr_cvar_shadow_t *cl_timeNudge;
    qlr_cvar_shadow_t *cl_paused;
    qlr_cvar_shadow_t *sv_paused;
    qlr_cvar_shadow_t *com_sv_running;
    qlr_cvar_shadow_t *cl_timedemo;
    qlr_cvar_shadow_t *cl_showTimeDelta;
    qlr_cvar_shadow_t *cl_freezeDemo;
    qlr_cvar_shadow_t *cl_activeAction;
} qlr_client_frame_cvars_t;

typedef struct {
    void (*stopAllSounds)(void);
    void (*setActiveMenu)(int menuId);
    void (*writeDemoMessage)(void *msg, int header);
    void (*checkTimeout)(qlr_client_connection_shadow_t *clc,
                         qlr_client_static_shadow_t *cls,
                         qlr_client_active_shadow_t *cl);
    void (*checkUserinfo)(void);
    void (*readPackets)(void);
    void (*sendCmd)(void);
    void (*predictMovement)(void);
    void (*runConsole)(void);
    void (*updateScreen)(void);
    void (*setCGameTime)(void);
    void (*firstSnapshot)(void);
    void (*beginProfiling)(void);
} qlr_client_frame_hooks_t;

typedef struct {
    qlr_client_static_shadow_t *cls;
    qlr_client_active_shadow_t *cl;
    qlr_client_connection_shadow_t *clc;
    qlr_client_frame_cvars_t cvars;
    qlr_client_frame_hooks_t hooks;
} qlr_client_frame_context_t;

void QLR_ClientFrame_BindContext(qlr_client_frame_context_t *ctx);
void QLR_ClientFrame_UnbindContext(void);
void CL_Frame(int msec);

#endif /* QLR_PROTO_CLIENT_FRAME_H */
