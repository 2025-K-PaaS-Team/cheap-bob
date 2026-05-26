import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from pathlib import Path
from logging.config import fileConfig
from alembic import context

# alembic 도 `from app.xxx` 절대 경로로 통일. /payment-backend 만 sys.path 에 둔다 (이중 모듈 로딩 방지).
_ROOT = Path(__file__).parent.parent              # /payment-backend
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.database.session import Base
import app.database.model  # noqa: F401 — Base.metadata 채우기 위한 side-effect import.
from app.config.setting import settings

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.SYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = settings.SYNC_DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
