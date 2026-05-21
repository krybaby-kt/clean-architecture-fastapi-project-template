"""Shared SQLAlchemy mapper registry.

All models in this package must register against this single registry so
that Alembic's autogenerate sees them all on the same ``MetaData``.
"""

from sqlalchemy.orm import registry

mapper_registry = registry()
