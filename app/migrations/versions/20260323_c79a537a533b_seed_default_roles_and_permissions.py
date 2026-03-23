"""seed default roles and permissions

Revision ID: c79a537a533b
Revises: 9b59222efb14
Create Date: 2026-03-23 17:43:56.899041
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c79a537a533b"
down_revision: str | None = "9b59222efb14"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Stable UUIDs for seed data (reproducible across environments)
USER_ROLE_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
ADMIN_ROLE_ID = uuid.UUID("10000000-0000-0000-0000-000000000002")
PERM_USER_READ_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
PERM_USER_WRITE_ID = uuid.UUID("20000000-0000-0000-0000-000000000002")

now = datetime.now(UTC)


def upgrade() -> None:
    permission = sa.table(
        "permission",
        sa.column("id", sa.Uuid),
        sa.column("codename", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    role = sa.table(
        "role",
        sa.column("id", sa.Uuid),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    op.bulk_insert(
        permission,
        [
            {
                "id": PERM_USER_READ_ID,
                "codename": "user:read",
                "description": "View user profiles",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": PERM_USER_WRITE_ID,
                "codename": "user:write",
                "description": "Modify user profiles",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

    op.bulk_insert(
        role,
        [
            {
                "id": USER_ROLE_ID,
                "name": "user",
                "description": "Default role for registered users",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": ADMIN_ROLE_ID,
                "name": "admin",
                "description": "Administrator with full access",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM role WHERE id IN (:admin_id, :user_id)").bindparams(
            admin_id=ADMIN_ROLE_ID, user_id=USER_ROLE_ID
        )
    )
    op.execute(
        sa.text("DELETE FROM permission WHERE id IN (:read_id, :write_id)").bindparams(
            read_id=PERM_USER_READ_ID, write_id=PERM_USER_WRITE_ID
        )
    )
