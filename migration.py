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
    # اضافه کردن transportation_type به جدول trip
    # -----------------------------------------------------------------------
    if "trip" in inspector.get_table_names():
        trip_columns = {
            column["name"]
            for column in inspector.get_columns("trip")
        }

        if "transportation_type" not in trip_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE trip ADD COLUMN transportation_type VARCHAR NOT NULL DEFAULT 'group_vehicle'"
                    )
                )

            print("✅ Migration: transportation_type به جدول trip اضافه شد (پیش‌فرض group_vehicle).")
        else:
            print("ℹ️ Migration: transportation_type از قبل وجود دارد.")

    # -----------------------------------------------------------------------
    # اضافه کردن vehicle_fare به جدول trip
    # -----------------------------------------------------------------------
    if "trip" in inspector.get_table_names():
        trip_columns = {
            column["name"]
            for column in inspector.get_columns("trip")
        }

        if "vehicle_fare" not in trip_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE trip ADD COLUMN vehicle_fare FLOAT NOT NULL DEFAULT 0.0"
                    )
                )

            print("✅ Migration: vehicle_fare به جدول trip اضافه شد (پیش‌فرض 0.0).")
        else:
            print("ℹ️ Migration: vehicle_fare از قبل وجود دارد.")

    # -----------------------------------------------------------------------
    # اضافه کردن vehicle_choice به جدول participant
    # -----------------------------------------------------------------------
    if "participant" in inspector.get_table_names():
        columns = {
            column["name"]
            for column in inspector.get_columns("participant")
        }

        if "vehicle_choice" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE participant ADD COLUMN vehicle_choice VARCHAR"
                    )
                )

            print("✅ Migration: vehicle_choice به جدول participant اضافه شد.")
        else:
            print("ℹ️ Migration: vehicle_choice از قبل وجود دارد.")

