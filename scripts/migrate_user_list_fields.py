"""users.injuries / users.equipment 를 정본 형식(쉼표로 이은 문자열)으로 맞춘다.

온보딩만 JSON 배열로 써 온 탓에 한 컬럼에 두 형식이 섞여 있었다. 읽는 쪽은
이제 두 형식을 모두 받지만(app/core/list_field.py), 저장된 값 자체도 한 형식으로
정리해 두는 편이 낫다.

    python -m scripts.migrate_user_list_fields          # 무엇이 바뀌는지 보기만 한다
    python -m scripts.migrate_user_list_fields --apply  # 실제로 바꾼다
"""

import sys

from app.core.list_field import dump_list_field, parse_list_field
from app.db.database import SessionLocal
from app.db.models import User


def migrate(apply: bool) -> None:
    db = SessionLocal()
    try:
        users = db.query(User).all()
        changed = 0

        for user in users:
            for field in ("injuries", "equipment"):
                before = getattr(user, field)
                after = dump_list_field(parse_list_field(before))
                if (before or "") == after:
                    continue
                changed += 1
                print(f"{user.user_id}.{field}: {before!r} -> {after!r}")
                if apply:
                    setattr(user, field, after)

        if apply:
            db.commit()
            print(f"\n{len(users)}명 중 {changed}칸을 바꿨다.")
        else:
            print(f"\n{len(users)}명 중 {changed}칸이 바뀐다. 실제로 바꾸려면 --apply 를 붙인다.")
    finally:
        db.close()


if __name__ == "__main__":
    migrate(apply="--apply" in sys.argv)
