"""initial_schema

Revision ID: fead7fb55b5d
Revises:
Create Date: 2025-11-08 02:24:03.031076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fead7fb55b5d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar tabela de usuários
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Criar tabela de posições do portfólio
    op.create_table('portfolio_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('avg_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('market_value', sa.Float(), nullable=True),
        sa.Column('unrealized_pnl', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Criar tabela de alertas de risco
    op.create_table('risk_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=True),
        sa.Column('alert_type', sa.String(50), nullable=False),  # 'high_risk', 'stop_loss', 'take_profit'
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),  # 'low', 'medium', 'high', 'critical'
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['position_id'], ['portfolio_positions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Criar índices
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_portfolio_positions_user_id'), 'portfolio_positions', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_positions_ticker'), 'portfolio_positions', ['ticker'], unique=False)
    op.create_index(op.f('ix_risk_alerts_user_id'), 'risk_alerts', ['user_id'], unique=False)
    op.create_index(op.f('ix_risk_alerts_created_at'), 'risk_alerts', ['created_at'], unique=False)


def downgrade() -> None:
    # Remover índices
    op.drop_index(op.f('ix_risk_alerts_created_at'), table_name='risk_alerts')
    op.drop_index(op.f('ix_risk_alerts_user_id'), table_name='risk_alerts')
    op.drop_index(op.f('ix_portfolio_positions_ticker'), table_name='portfolio_positions')
    op.drop_index(op.f('ix_portfolio_positions_user_id'), table_name='portfolio_positions')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')

    # Remover tabelas
    op.drop_table('risk_alerts')
    op.drop_table('portfolio_positions')
    op.drop_table('users')
