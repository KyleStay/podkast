# Project instructions

## Local CI policy

Run checks through `.ci/local.sh`; read `.ci/README.md` for toolchains and matrix
coverage. Future agents must not use GitHub-hosted CI or consume GitHub Actions
credits. Keep workflow originals as inactive references in `.ci/archived-workflows`.
Never dispatch, rerun, enable or regenerate hosted workflows. Preserve test
coverage and report unavailable local platform/service gates explicitly. Do not
register self-hosted runners, create CI tokens, change security settings or alter
branch protection as part of CI work.
