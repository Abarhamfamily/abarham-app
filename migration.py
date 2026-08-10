from sqlalchemy import inspect, text

from models import engine


def run_migrations() -> None:
    """
    Migrationهای کوچک و امن دیتابیس.
    اطلاعات موجود حذف نمی‌شوند.
    """

    inspector = inspect(engine)

    # ---------------------------------------------------------
    # جدول participant
    # ---------------------------------------------------------

    if "participant" not in inspector.get_table_names():
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("participant")
    }

    # اضافه کردن telegram_user_id فقط در صورت نبودن
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

        print("✅ telegram_user_id به participant اضافه شد.")
    else:
        print("ℹ️ telegram_user_id از قبل وجود دارد.")