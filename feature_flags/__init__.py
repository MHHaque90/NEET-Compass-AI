"""Feature flag infrastructure package.

A provider-backed feature flag engine with explicit source precedence, an
evaluation pipeline for targeting rules, and a dependency-injected service
facade. This is pure infrastructure: it contains no NEET business logic and
no prediction logic — it only answers the question *"is this capability
enabled, and from which source?"*.

Consumers interact with ``FeatureFlagService`` (built by
``FeatureFlagContainer``); capabilities are gated through the ``services``
package.
"""
