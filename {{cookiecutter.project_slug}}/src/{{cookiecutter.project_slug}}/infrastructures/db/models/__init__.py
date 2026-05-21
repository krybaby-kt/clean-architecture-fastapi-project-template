"""SQLAlchemy models package.

Every model module is imported here so the ``@mapper_registry.mapped``
side effect runs and Alembic's autogenerate can see every table.
Add new models below as you create them.
"""

from {{cookiecutter.project_slug}}.infrastructures.db.models.artifact import ArtifactModel

__all__ = [
    "ArtifactModel",
]
