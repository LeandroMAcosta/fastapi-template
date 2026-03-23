"""Add role, permission tables and user.role_id

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "permission",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("codename", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("description", sa.String(255), nullable=False, server_default=""),
    )

    op.create_table(
        "role",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("description", sa.String(255), nullable=False, server_default=""),
    )

    op.create_table(
        "role_permission",
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "permission_id", UUID(as_uuid=True), sa.ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True
        ),
    )

    # Seed default roles and permissions
    permissions_table = sa.table("permission", sa.column("id", UUID), sa.column("codename"), sa.column("description"))
    roles_table = sa.table("role", sa.column("id", UUID), sa.column("name"), sa.column("description"))
    role_perm_table = sa.table("role_permission", sa.column("role_id", UUID), sa.column("permission_id", UUID))

    # Permission IDs (deterministic for FK references)
    perm_ids = {
        "user:read": "a0000000-0000-0000-0000-000000000001",
        "user:create": "a0000000-0000-0000-0000-000000000002",
        "user:update": "a0000000-0000-0000-0000-000000000003",
        "user:delete": "a0000000-0000-0000-0000-000000000004",
    }
    role_ids = {
        "admin": "b0000000-0000-0000-0000-000000000001",
        "user": "b0000000-0000-0000-0000-000000000002",
    }

    op.bulk_insert(
        permissions_table,
        [
            {"id": perm_ids["user:read"], "codename": "user:read", "description": "Read user data"},
            {"id": perm_ids["user:create"], "codename": "user:create", "description": "Create users"},
            {"id": perm_ids["user:update"], "codename": "user:update", "description": "Update users"},
            {"id": perm_ids["user:delete"], "codename": "user:delete", "description": "Delete users"},
        ],
    )

    op.bulk_insert(
        roles_table,
        [
            {"id": role_ids["admin"], "name": "admin", "description": "Full access"},
            {"id": role_ids["user"], "name": "user", "description": "Standard user"},
        ],
    )

    # Admin gets all permissions, user gets read only
    op.bulk_insert(
        role_perm_table,
        [
            {"role_id": role_ids["admin"], "permission_id": perm_ids["user:read"]},
            {"role_id": role_ids["admin"], "permission_id": perm_ids["user:create"]},
            {"role_id": role_ids["admin"], "permission_id": perm_ids["user:update"]},
            {"role_id": role_ids["admin"], "permission_id": perm_ids["user:delete"]},
            {"role_id": role_ids["user"], "permission_id": perm_ids["user:read"]},
        ],
    )

    # Add role_id to user table
    op.add_column("user", sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("role.id"), nullable=True))
    op.execute(f"UPDATE \"user\" SET role_id = '{role_ids['user']}'")
    op.alter_column("user", "role_id", nullable=False)


def downgrade() -> None:
    op.drop_column("user", "role_id")
    op.drop_table("role_permission")
    op.drop_table("role")
    op.drop_table("permission")
