# Local CI

All CI runs locally. Run `./.ci/local.sh` for the full required lane set, or name a lane explicitly. `--list` lists lanes; `--check` checks only the guard/Python syntax, not application coverage. Missing prerequisites/incomplete coverage return 2; command failures propagate. Results and command logs remain under `.ci/results/`.

Original matrix: Node 8, 10 and 12, each running npm install and npm test in podkast/ClientApp. Provision these legacy runtimes locally and set NODE8_BIN, NODE10_BIN, NODE12_BIN to their absolute node executables (matching npm must live next to each). Run default all, or an explicitly labelled node8/node10/node12 subset. Each uses an isolated .ci/work/nodeN copy so dependency installs and test outputs do not modify source. CI=true disables watch mode; --runInBand bounds Jest worker use without dropping tests. Other runtime lanes remain unverified when a subset passes. No dependencies/toolchains are installed globally.

## Original coverage

The byte-for-byte original YAML files are inactive archive references, not runnable hosted triggers. `archive-manifest.json` records their source commit, original path and SHA-256; `matrix-inventory.json` retains every original job, runner, condition, matrix, environment and step. GitHub expressions and action wrappers there require local values/tools/artifacts; never execute the archive as a workflow or fetch CI secrets. Existing remote logs/artifacts and retention remain unchanged.

## Publishing this migration

This commit removes every active workflow YAML atomically. A `[skip ci]` commit annotation is an additional push/PR safeguard; it is not a replacement for removing sources. Verify remote default-branch source and runs for the exact pushed commit using read-only API calls. Do not test by dispatching CI.
