#include <stdio.h>
#include <stddef.h>
#include "src/code/game/q_shared.h"
#define OFF(name) printf(#name " %zu\n", offsetof(playerState_t, name));
int main(void) {
	OFF(stats);
	OFF(persistant);
	OFF(powerups);
	OFF(ammo);
	OFF(generic1);
	OFF(loopSound);
	OFF(jumppad_ent);
	OFF(ping);
	OFF(pmove_framecount);
	OFF(jumppad_frame);
	OFF(entityEventSequence);
	OFF(crouchTime);
	OFF(crouchSlideTime);
	OFF(armorTier);
	return 0;
}
