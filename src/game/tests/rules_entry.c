#include "rules_fixtures.h"

/*
=============
GT_RunAllRulesFixtures

Executes all registered rules fixture suites sequentially and aggregates their results.
=============
*/
game_fixture_result_t GT_RunAllRulesFixtures(void) {
	game_fixture_result_t total = {0, 0};
	game_fixture_result_t result;

	result = GT_RunSampleRulesFixtures();
	total.executed += result.executed;
	total.failed += result.failed;

	result = GT_RunItemRulesFixtures();
	total.executed += result.executed;
	total.failed += result.failed;

	result = GT_RunVoteControlFixtures();
	total.executed += result.executed;
	total.failed += result.failed;

	result = GT_RunCosmeticTrainingFixtures();
	total.executed += result.executed;
	total.failed += result.failed;

	return total;
}
