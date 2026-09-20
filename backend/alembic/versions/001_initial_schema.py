"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-09-13 22:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Ensure vector extension is created
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('body_type', sa.String(), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table('clothing_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('pattern', sa.String(), nullable=True),
        sa.Column('formality_score', sa.Float(), nullable=True),
        sa.Column('season', sa.String(), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=512), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('outfits',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('outfit_items',
        sa.Column('outfit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clothing_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['clothing_item_id'], ['clothing_items.id'], ),
        sa.ForeignKeyConstraint(['outfit_id'], ['outfits.id'], ),
        sa.PrimaryKeyConstraint('outfit_id', 'clothing_item_id')
    )

def downgrade() -> None:
    op.drop_table('outfit_items')
    op.drop_table('outfits')
    op.drop_table('clothing_items')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
