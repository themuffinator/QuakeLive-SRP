#include "rules_fixtures.h"

#if defined(__has_include)
#if __has_include("bg_public.h")
#include "bg_public.h"
#elif __has_include("../code/game/bg_public.h")
#include "../code/game/bg_public.h"
#elif __has_include("../../code/game/bg_public.h")
#include "../../code/game/bg_public.h"
#else
#error "Unable to locate bg_public.h for item fixtures"
#endif
#else
#include "../../code/game/bg_public.h"
#endif

#include <string.h>

static qboolean GT_ItemFindsRocketLauncher(void) {
    const gitem_t *rocket = BG_FindItemForWeapon(WP_ROCKET_LAUNCHER);

    if (!rocket) {
        return GT_Failf("BG_FindItemForWeapon(WP_ROCKET_LAUNCHER) returned NULL");
    }

    if (rocket->giType != IT_WEAPON) {
        return GT_Failf("expected giType IT_WEAPON, received %d", rocket->giType);
    }

    if (rocket->quantity != 10) {
        return GT_Failf("expected rocket launcher quantity 10, received %d", rocket->quantity);
    }

    if (Q_stricmp(rocket->pickup_name, "Rocket Launcher") != 0) {
        return GT_Failf("unexpected pickup name '%s'", rocket->pickup_name);
    }

    return qtrue;
}

static qboolean GT_PlayerTouchWithinPickupBounds(void) {
    playerState_t ps;
    entityState_t item;

    memset(&ps, 0, sizeof(ps));
    memset(&item, 0, sizeof(item));

    VectorSet(ps.origin, 128.0f, 64.0f, 24.0f);

    item.pos.trType = TR_STATIONARY;
    item.pos.trTime = 0;
    VectorCopy(ps.origin, item.pos.trBase);

    if (!BG_PlayerTouchesItem(&ps, &item, 0)) {
        return GT_Failf("expected player to touch item when aligned within bounds");
    }

    return qtrue;
}

static qboolean GT_PlayerTouchRejectsWideOffset(void) {
    playerState_t ps;
    entityState_t item;

    memset(&ps, 0, sizeof(ps));
    memset(&item, 0, sizeof(item));

    VectorSet(ps.origin, 0.0f, 0.0f, 0.0f);

    item.pos.trType = TR_STATIONARY;
    item.pos.trTime = 0;
    VectorSet(item.pos.trBase, 60.0f, 0.0f, 0.0f);

    if (BG_PlayerTouchesItem(&ps, &item, 0)) {
        return GT_Failf("expected player outside x-bounds to miss pickup");
    }

    return qtrue;
}

static qboolean GT_FindAmmoPackItem(void) {
    const gitem_t *ammo_pack = BG_FindItemByClassname("ammo_pack");

    if (!ammo_pack) {
        return GT_Failf("BG_FindItemByClassname(\"ammo_pack\") returned NULL");
    }

    if (ammo_pack->giType != IT_AMMO) {
        return GT_Failf("expected ammo_pack giType IT_AMMO, received %d", ammo_pack->giType);
    }

    if (ammo_pack->giTag != WP_NUM_WEAPONS) {
        return GT_Failf("expected ammo_pack giTag %d, received %d", WP_NUM_WEAPONS, ammo_pack->giTag);
    }

    return qtrue;
}

static qboolean GT_FindInvulnerabilityPowerupProxy(void) {
    const gitem_t *invulnerability = BG_FindItemForPowerup(PW_INVULNERABILITY);

    if (!invulnerability) {
        return GT_Failf("BG_FindItemForPowerup(PW_INVULNERABILITY) returned NULL");
    }

    if (invulnerability->giType != IT_HOLDABLE) {
        return GT_Failf(
            "expected invulnerability proxy giType IT_HOLDABLE, received %d",
            invulnerability->giType);
    }

    if (invulnerability->giTag != HI_INVULNERABILITY) {
        return GT_Failf(
            "expected invulnerability proxy giTag %d, received %d",
            HI_INVULNERABILITY,
            invulnerability->giTag);
    }

    return qtrue;
}

static qboolean GT_AmmoPackGrabTracksOwnedWeaponAmmo(void) {
    const gitem_t *ammo_pack = BG_FindItemByClassname("ammo_pack");
    playerState_t ps;
    entityState_t item;

    if (!ammo_pack) {
        return GT_Failf("ammo_pack lookup failed before grab validation");
    }

    memset(&ps, 0, sizeof(ps));
    memset(&item, 0, sizeof(item));

    item.modelindex = ITEM_INDEX(ammo_pack);
    ps.stats[STAT_WEAPONS] = 1 << WP_MACHINEGUN;
    ps.ammo[WP_MACHINEGUN] = 0;

    if (!BG_CanItemBeGrabbed(GT_FFA, 0, &item, &ps)) {
        return GT_Failf("expected ammo_pack to be grabbable when an owned weapon is below max ammo");
    }

    ps.ammo[WP_MACHINEGUN] = BG_GetWeaponMaxAmmo(WP_MACHINEGUN);
    if (BG_CanItemBeGrabbed(GT_FFA, 0, &item, &ps)) {
        return GT_Failf("expected ammo_pack to be blocked when all owned ammo is already full");
    }

    return qtrue;
}

static const game_fixture_t gt_item_rules_fixtures[] = {
    {
        "find_rocket_launcher",
        NULL,
        GT_ItemFindsRocketLauncher,
        NULL,
        "Ensures BG_FindItemForWeapon exposes the rocket launcher metadata"
    },
    {
        "touch_within_bounds",
        NULL,
        GT_PlayerTouchWithinPickupBounds,
        NULL,
        "Validates BG_PlayerTouchesItem accepts aligned pickups"
    },
    {
        "touch_rejects_wide_offset",
        NULL,
        GT_PlayerTouchRejectsWideOffset,
        NULL,
        "Validates BG_PlayerTouchesItem rejects pickups beyond the x tolerance"
    },
    {
        "find_ammo_pack",
        NULL,
        GT_FindAmmoPackItem,
        NULL,
        "Ensures the retail-only ammo_pack item is present in bg_itemlist"
    },
    {
        "find_invulnerability_proxy",
        NULL,
        GT_FindInvulnerabilityPowerupProxy,
        NULL,
        "Validates BG_FindItemForPowerup routes invulnerability through the holdable proxy"
    },
    {
        "ammo_pack_grab_logic",
        NULL,
        GT_AmmoPackGrabTracksOwnedWeaponAmmo,
        NULL,
        "Validates BG_CanItemBeGrabbed checks owned-weapon ammo for ammo_pack entities"
    }
};

game_fixture_result_t GT_RunItemRulesFixtures(void) {
    game_fixture_reporter_t reporter;
    GT_InitDefaultReporter(&reporter);
    return GT_RunFixtureSuite(
        "item_rules",
        gt_item_rules_fixtures,
        GAME_TESTS_ARRAY_LEN(gt_item_rules_fixtures),
        &reporter);
}
