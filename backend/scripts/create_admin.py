"""
ساخت حساب ادمین از طریق خط فرمان (نه از طریق API عمومی، برای امنیت بیشتر).

اجرا از پوشه‌ی backend/:
    python -m scripts.create_admin --username admin --password "StrongPass123" --full-name "مدیر سیستم"

برای super_admin:
    python -m scripts.create_admin --username admin --password "StrongPass123" --full-name "مدیر سیستم" --role super_admin
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.core.security import hash_password
from src.models.admin import Admin, AdminRole


async def create_admin(username: str, password: str, full_name: str, role: str) -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(Admin).where(Admin.username == username))
        if existing.scalar_one_or_none():
            print(f"خطا: نام کاربری '{username}' قبلاً استفاده شده است")
            return

        admin = Admin(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        print(f"ادمین با موفقیت ساخته شد: {admin.username} (id={admin.id}, role={admin.role})")


def main():
    parser = argparse.ArgumentParser(description="ساخت حساب ادمین برای Abarham App")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--full-name", required=True, dest="full_name")
    parser.add_argument(
        "--role",
        default=AdminRole.ADMIN.value,
        choices=[r.value for r in AdminRole],
    )
    args = parser.parse_args()

    if len(args.password) < 8:
        print("خطا: رمز عبور باید حداقل ۸ کاراکتر باشد")
        return

    asyncio.run(create_admin(args.username, args.password, args.full_name, args.role))


if __name__ == "__main__":
    main()
