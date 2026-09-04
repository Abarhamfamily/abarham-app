"""add admins table

Revision ID: a1b2c3d4e5f6
Revises: ef9dc035097e
Create Date: 2026-08-24 00:00:00.000000

این migration کاملاً افزایشی (additive) است: فقط جدول جدید «admins» را
اضافه می‌کند و هیچ جدول موجودی (users, trips, registrations, ...) را
تغییر نمی‌دهد. Admin کاملاً از User مجزاست (نه FK، نه ستون مشترک).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'ef9dc035097e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'admins',
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_admins_username'), ['username'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_admins_username'))
    op.drop_table('admins')
