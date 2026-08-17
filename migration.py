from sqlalchemy import inspect, text

from models import engine


def run_migrations() -> None:
    """
    Migrationهای کوچک و امن دیتابیس.
    اطلاعات موجود حذف نمی‌شوند.
    """

    inspector = inspect(engine)

    # اگر جدول participant وجود ندارد،
    # create_all در ادامه آن را خواهد ساخت.
    if "participant" not in inspector.get_table_names():
        return

    # گرفتن نام ستون‌های موجود
    columns = {
        column["name"]
        for column in inspector.get_columns("participant")
    }

    # اگر telegram_user_id وجود ندارد، آن را اضافه کن
    if "telegram_user_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    ALTER TABLE participant
                    ADD COLUMN telegram_user_id BIGINT
                    """
                )
            )

        print("✅ Migration: telegram_user_id به جدول participant اضافه شد.")
    else:
        print("ℹ️ Migration: telegram_user_id از قبل وجود دارد.")

    # -----------------------------------------------------------------------
    # telegram_group_link روی جدول trip
    # -----------------------------------------------------------------------
    if "trip" in inspector.get_table_names():
        trip_columns = {
            column["name"]
            for column in inspector.get_columns("trip")
        }

        if "telegram_group_link" not in trip_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE trip ADD COLUMN telegram_group_link TEXT"
                    )
                )

            print("✅ Migration: telegram_group_link به جدول trip اضافه شد.")
        else:
            print("ℹ️ Migration: telegram_group_link از قبل وجود دارد.")

    # -----------------------------------------------------------------------
    # status روی جدول trip
    # -----------------------------------------------------------------------
    if "trip" in inspector.get_table_names():
        trip_columns = {
            column["name"]
            for column in inspector.get_columns("trip")
        }

        if "status" not in trip_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE trip ADD COLUMN status VARCHAR "
                        "NOT NULL DEFAULT 'active'"
                    )
                )

            print("✅ Migration: status به جدول trip اضافه شد (پیش‌فرض active).")
        else:
            print("ℹ️ Migration: status از قبل وجود دارد.")

    # -----------------------------------------------------------------------
    # ایجاد جدول user (اگر وجود نداشته باشد)
    # -----------------------------------------------------------------------
    if "user" not in inspector.get_table_names():
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_user_id BIGINT UNIQUE,
                        full_name VARCHAR NOT NULL,
                        phone_number VARCHAR,
                        national_id VARCHAR,
                        status VARCHAR NOT NULL DEFAULT 'active',
                        created_at VARCHAR NOT NULL
                    )
                    """
                )
            )
        print("✅ Migration: جدول user ایجاد شد.")
    else:
        print("ℹ️ Migration: جدول user از قبل وجود دارد.")

    # -----------------------------------------------------------------------
    # ایجاد جدول registration (اگر وجود نداشته باشد)
    # -----------------------------------------------------------------------
    if "registration" not in inspector.get_table_names():
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE registration (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id BIGINT NOT NULL,
                        trip_id BIGINT NOT NULL,
                        status VARCHAR NOT NULL DEFAULT 'pending',
                        registered_at VARCHAR NOT NULL,
                        confirmed_at VARCHAR,
                        cancelled_at VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES user (id),
                        FOREIGN KEY (trip_id) REFERENCES trip (id),
                        UNIQUE (user_id, trip_id)
                    )
                    """
                )
            )
        print("✅ Migration: جدول registration ایجاد شد.")
    else:
        print("ℹ️ Migration: جدول registration از قبل وجود دارد.")
