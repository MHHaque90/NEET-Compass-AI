"""Application-layer use cases and the dependency-injection container.

Kept import-free on purpose: ``__init__`` imports create circular-import
fragility because the composition root references the infrastructure layer.
Consumers import the concrete modules they need directly.
"""
