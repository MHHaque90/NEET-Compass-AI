# tests/

Repository-wide **integration / end-to-end** tests (real PostgreSQL, real HTTP).

In Phase 1 these tests are not yet written: the unit suite lives under
`backend/tests/` and runs against fakes. Integration harness (testcontainers /
dockerized Postgres fixtures) is planned alongside Phase 2 API work.
