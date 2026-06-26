"""add username audio notifications

Revision ID: e19ca914f103
Revises: a6ff78be82e8
Create Date: 2026-06-24

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "e19ca914f103"
down_revision: Union[str, Sequence[str], None] = "a6ff78be82e8"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # =====================================================
    # NOTIFICATIONS TABLE
    # =====================================================

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default="FALSE",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["recipient_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_notifications_recipient",
        "notifications",
        ["recipient_id"],
        unique=False,
    )

    op.create_index(
        "ix_notifications_created_at",
        "notifications",
        ["created_at"],
        unique=False,
    )

    # =====================================================
    # MESSAGE AUDIO SUPPORT
    # =====================================================

    op.add_column(
        "messages",
        sa.Column(
            "audio_url",
            sa.String(),
            nullable=True,
        ),
    )

    op.alter_column(
        "messages",
        "content",
        existing_type=sa.TEXT(),
        nullable=True,
    )

    # =====================================================
    # USERNAME SUPPORT
    # =====================================================

    op.add_column(
        "users",
        sa.Column(
            "username",
            sa.String(length=50),
            nullable=True,
        ),
    )

    # Fill existing users

    op.execute(
        """
        UPDATE users
        SET username = CONCAT('user_', id)
        WHERE username IS NULL
        """
    )

    op.alter_column(
        "users",
        "username",
        nullable=False,
    )

    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_users_username",
        "users",
        ["username"],
    )


def downgrade() -> None:

    # =====================================================
    # USERNAME
    # =====================================================

    op.drop_constraint(
        "uq_users_username",
        "users",
        type_="unique",
    )

    op.drop_index(
        "ix_users_username",
        table_name="users",
    )

    op.drop_column(
        "users",
        "username",
    )

    # =====================================================
    # MESSAGE AUDIO
    # =====================================================

    op.alter_column(
        "messages",
        "content",
        existing_type=sa.TEXT(),
        nullable=False,
    )

    op.drop_column(
        "messages",
        "audio_url",
    )

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    op.drop_index(
        "ix_notifications_created_at",
        table_name="notifications",
    )

    op.drop_index(
        "ix_notifications_recipient",
        table_name="notifications",
    )

    op.drop_table("notifications")