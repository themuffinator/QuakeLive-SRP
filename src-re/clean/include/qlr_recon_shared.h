#ifndef QLR_RECON_SHARED_H
#define QLR_RECON_SHARED_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "../../prototypes/common/native_shim.h"

typedef struct qlr_recon_cvar_s {
    int integer;
    float value;
    const char *string;
} qlr_recon_cvar_t;

typedef struct qlr_recon_timer_s {
    int previous;
    int current;
    int delta;
} qlr_recon_timer_t;

#endif /* QLR_RECON_SHARED_H */
