# Feature Flags

Production-grade, provider-backed feature flag infrastructure for
NEET Compass AI. **Pure infrastructure** — no prediction logic, no business
logic, no frontend. It answers exactly one question:

> *Is this capability enabled, and from which source?*

## Scope and layout

| Path | Purpose |
| --- | --- |
| `feature_flags/` | The flag engine (models, providers, evaluator, service, container, introspection) |
| `feature_flags/models/` | Flag vocabulary (`definition`) + read-only introspection snapshots (`introspection`) |
| `feature_flags/introspection.py` | Lists every flag with resolved value, winning source, priority, and per-source overrides |
| `services/` | Engine capability gates (`Rule` / `ML` / `LLM` / `Experimental`) built on the flag service |
| `config/flags.yaml` | Flag catalogue (`definitions:`) + deploy-baseline toggles (`overrides:`) |

Supported capabilities toggled by flags:

- **Rule Engine** — `engines.rule`
- **ML Engine** — `engines.ml`
- **LLM Engine** — `engines.llm`
- **Experimental Features** — `experimental.<feature_name>`

## Enabling / disabling a flag

All three toggle sources are supported, resolved by precedence:

```
ENV  >  MEMORY  >  DATABASE  >  CONFIG_FILE  >  code default (highest wins)
```

| Source | How | When to use |
| --- | --- | --- |
| **Environment variable** | `FF_ENGINES_RULE=true` (dots→underscores, upper) | Emergency kill switches; per-instance toggles |
| **Database** | row in `feature_flags` table (`name`, `enabled`) | Real-time toggles without redeploy |
| **Configuration file** | uncomment a value under `overrides:` in `config/flags.yaml` | Deploy-baseline toggles shipped with a release |

Boolean env values: `true/false`, `1/0`, `yes/no`, `on/off`, `enabled/disabled`
(case-insensitive). Malformed values raise `MalformedFlagValueError` rather
than silently disabling a flag.

## Usage

```python
from feature_flags.container import build_feature_flags

flags = build_feature_flags()                      # reads config/flags.yaml
flags.ensure_schema()                              # create DB table on demand (dev)

flags.is_enabled("engines.rule")                   # -> bool
state = flags.get_state("engines.ml")              # -> FlagState (value + source + rules)
flags.set_override("engines.rule", True)           # in-process runtime override
flags.all_states()                                 # observability snapshot
```

Capability gates (services layer):

```python
from feature_flags.container import build_feature_flags
from services import build_engine_gates

gates = build_engine_gates(build_feature_flags())

gates.rule.is_enabled()
gates.ml.require_enabled()          # raises FeatureDisabledError when disabled
gates.llm.is_enabled()
gates.experimental_feature("choice_filling_v2").is_enabled(context)
```

Targeting rules are evaluated when a `FlagContext` is supplied
(`context = FlagContext(environment="production", request_id="...")`):

```python
from feature_flags.models import FlagContext

flags.is_enabled("experimental.choice_filling_v2",
                 context=FlagContext(request_id="abc123"))
```

## Introspection (Sprint 1.2)

List every flag and *why* it is in its current state — no UI, no REST layer:

```python
from feature_flags.container import build_flag_introspection

introspection = build_flag_introspection()          # reads config/flags.yaml
report = introspection.all_flags()                  # -> FlagIntrospectionReport
for flag in report.flags:
    print(flag.name, flag.current_value, flag.source, flag.priority)
```

`report.total` is the flag count; `report.generated_at` is the snapshot time.
`introspection.introspect_flag("engines.rule")` introspects a single flag
(`None` when unknown, or `UnknownFlagError` in strict mode).

Each `FlagIntrospection` record exposes:

| Field | Meaning |
| --- | --- |
| `name`, `description` | The flag's identity (from its definition). |
| `current_value` | The resolved verdict — identical to `is_enabled(...)`. |
| `source`, `source_provider` | Winning `FlagSource` + the concrete provider class that decided it (`definition-default` / `unknown-flag` otherwise). |
| `priority` | Precedence rank of the winning source (`0`=ENV, `1`=MEMORY, `2`=DATABASE, `3`=CONFIG_FILE, `4`=DEFAULT, `5`=UNKNOWN). |
| `default_value` | The code/config baseline. |
| `last_modified` | `updated_at` of the database row when the database owns the flag, else `None`. |
| `environment_var` | The exact env variable (`FF_…`) that would control the flag. |
| `environment_override` / `database_override` / `config_override` / `memory_override` | Each source's own value, so the flag that "won" is always traceable. |

The report is built from the *same* definitions and providers the evaluation
path uses — there is no separate display state to drift from reality.

## Architectural decisions

1. **Single provider contract.** Every source implements the same
   `FlagProvider` interface returning `bool | None` (`None` = *not owned by
   this source*). Adding a source (e.g. Redis, a remote flag service) is a
   new provider class — nothing else changes (SOLID O/D).
2. **Precedence by declared rank, not registration order.** The evaluator
   sorts providers by `FlagSource`, so precedence (`ENV > MEMORY > DATABASE >
   CONFIG_FILE`) is stable no matter how the container is wired. This is the
   single most important correctness property for a flag system.
3. **Env vars are authoritative kill switches.** An env value bypasses
   targeting rules entirely, so incident response can force-disable a feature
   globally without reasoning about rollout rules.
4. **Rules narrow, they never widen.** Rules (environment / percentage /
   segment) are AND-ed onto the resolved value, so the platform can always
   *darker* a rollout safely.
5. **Deterministic percentage rollouts.** Rollout bucketing uses SHA-256
   (not Python's per-process-randomized `hash`) so the same `request_id`
   always lands in the same bucket across processes and machines.
6. **Unknown flags degrade safely, with an escape hatch.** By default an
   unknown flag evaluates to `disabled` (source `UNKNOWN`, warning logged) —
   safe when flags are retired before their consumers. `strict=True` turns
   that into `UnknownFlagError` to catch typos.
7. **Providers fail soft on infrastructure.** The DB provider returns `None`
   when the table is missing or the database is unreachable (with a warning),
   so a flag-table provisioning gap or DB outage can never crash the platform
   or lock features into an unknown state.
8. **The database owns only what it must.** The `feature_flags` table is
   tiny, stable, and isolated (`schema.sql`); dynamic toggles live there,
   everything else lives in code/config. Managed DBs apply the DDL via the
   platform migration tooling; dev/tests use `ensure_schema()`.
9. **Dependency injection throughout.** `FeatureFlagContainer` is the only
   place that wires providers; `FeatureFlagService` receives definitions +
   providers by constructor. The `services` gates receive a flag service by
   constructor. Tests inject fakes/providers directly.
10. **Provenance on every evaluation.** `FlagState` records `source` and
    `rule_matched`, so operators can answer "why is this flag on?" — a
    precondition for trusting the system under incidents.
11. **Fail fast on corrupt config.** A malformed env value, a bad YAML
    override, or an invalid flag definition raises typed errors — corruption
    is never silently treated as "disabled".
12. **No business logic.** The flag system knows flags, sources, and rules —
    nothing about NEET, colleges, or counselling. All domain concerns are
    configuration, owned by the platform.
13. **Introspection shares the evaluation path.** `FeatureFlagIntrospection`
    reuses the evaluator and the exact providers the service uses, so what it
    reports is always what flags evaluate to (no second "display state" that
    could drift). Per-source overrides are collected via the `FlagProvider`
    contract, so new providers appear automatically; time metadata is opt-in
    via `FlagProvider.get_updated_at()` (only the database overrides it).

## Tests

```
make test
```

Coverage: models, all four providers, precedence ordering, targeting rules,
the service facade (including strict/unknown behaviour), the container,
introspection (catalogue listing, every override source, priority ranking,
last-modified semantics, evaluation parity, container wiring), and the
services gates. The database provider is tested against in-memory SQLite.

## Notes

- Flag name convention: lowercase dotted (`engines.rule`,
  `experimental.choice_filling_v2`). Env var form: `FF_ENGINES_RULE`.
- Adding a new flag = add a definition to `config/flags.yaml` (no code).
- The `feature_flags` table is independent of the platform schema; it is not
  part of the platform Alembic metadata by design (see decision 8).
