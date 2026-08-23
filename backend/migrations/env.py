import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(str(Path(__file__).parent.parent))

from src.core.database import Base
from src.core.config import settings
from src.models import (  # noqa: F401 -- ایمپورت برای autogenerate ضروری است
    user,
    trip,
    registration,
    waitlist,
    wallet,
    payment,
    notification,
    audit,
)

config = context.config

# آدرس دیتابیس را از تنظیمات برنامه (env vars) می‌خوانیم، نه فقط alembic.ini،
# تا در محیط production با DATABASE_URL هماهنگ بماند.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
