"""Infrastructure implementations of the domain ports.

Contains the only code that touches SQLAlchemy, files, pandas, and (later)
ML frameworks. Nothing in this package may be imported by the domain layer
directly — it goes through the ports. Kept import-free to avoid circular
imports with the application composition root.
"""
