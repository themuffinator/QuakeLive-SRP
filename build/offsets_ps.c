#include <stdio.h>
#include <stddef.h>
#include "src/code/game/q_shared.h"
int main(void) {
	printf("pm_flags %zu\n", offsetof(playerState_t, pm_flags));
	printf("velocity %zu\n", offsetof(playerState_t, velocity));
	printf("groundTraceLatestTime %zu\n", offsetof(playerState_t, groundTraceLatestTime));
	printf("doubleJumpTime %zu\n", offsetof(playerState_t, doubleJumpTime));
	printf("doubleJumpEntNum %zu\n", offsetof(playerState_t, doubleJumpEntNum));
	printf("legsTimer %zu\n", offsetof(playerState_t, legsTimer));
	printf("eventSequence %zu\n", offsetof(playerState_t, eventSequence));
	printf("crouchTime %zu\n", offsetof(playerState_t, crouchTime));
	printf("crouchSlideTime %zu\n", offsetof(playerState_t, crouchSlideTime));
	printf("armorTier %zu\n", offsetof(playerState_t, armorTier));
	return 0;
}
