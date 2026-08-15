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
