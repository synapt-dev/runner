# synapt.runner

Shared OSS research-runner kernel for Synapt, distributed as `synapt-runner`
with import path `synapt.runner`.

This repository is the Phase 2 extraction of the runner prototype from
`synapt-dev/config`. It is publish-readiness staged, but no PyPI release is
authorized until Layne ratifies the first release.

## Scope

The kernel contains generic research-runner infrastructure that can be reused by
`vorn-mat` first, `research/vorn-active-eviction` second, and later
`active-compression` if the surface proves stable:

- terminal run records with success, runtime-failure, and capacity-missing
  invariants
- canonical JSON, SHA-256, and deterministic seed helpers
- pre-execution gates that fail closed before model generation
- stable-unit span delete and mask rendering
- Modal runtime metadata, GPU cost rates, and dashboard-cost reconciliation
- distinct cost surfaces for per-row model generation cost and Modal wall-clock
  app billing
- JSONL/local artifact sinks and markdown summary hooks
- wave fanout with per-cell failure capture
- preregistration method/version gates

The kernel intentionally does not include SEMU primitives, vorn scoring,
fixture loaders, selector policies, benchmark scoring, product claims, or model
execution code. Those remain project-specific.

## Cost Surfaces

Runner artifacts keep two cost surfaces separate:

- `GenerationCostSurface` is row-scoped model generation cost. It may carry
  model id, token counts, source, and modeled row cost.
- `ModalWallClockCostSurface` is app/runtime scoped Modal billing. It may carry
  runtime seconds, app/call ids, GPU, and dashboard reconciliation.

Do not collapse Modal wall-clock cost into a per-row generation field. Consumers
that need per-row estimates should allocate or model that explicitly and record
the allocation source.

## Package Shape

The package shape is:

- distribution: `synapt-runner`
- import path: `synapt.runner`
- license: MIT
- namespace: PEP 420 implicit `synapt` namespace

There is no `synapt/__init__.py` by design. This allows the future package to
coexist with the existing `synapt` namespace without forcing a shared release
unit.

Current gripspace caveat: the installed recall checkout may still present
`synapt` as a regular package during local tests. The test suite uses a
local-only `tests/conftest.py` path bridge until the parallel recall PEP 420
conversion lands. After that merge, remove the bridge and verify
`synapt.recall` and `synapt.runner` coexist from installed packages.

## Run Tests

```bash
python -m pytest
```

## Release Gate

Do not publish to PyPI from this repository until Layne explicitly ratifies the
first `synapt-runner` release.
