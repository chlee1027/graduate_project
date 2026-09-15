"""users.injuries · users.equipment 같은 "목록을 한 칸에 넣은" 컬럼의 읽기/쓰기.

이 두 컬럼은 모델 주석대로 쉼표로 이어 붙인 문자열이 정본이다. 그런데 온보딩만
json.dumps 로 써 온 탓에 같은 컬럼에 두 형식이 섞여 있었다.

    온보딩이 쓴 값:  '["knee"]'
    읽는 쪽 해석:    ['["knee"]']   <- 쉼표로 쪼개므로 통째로 한 덩어리

그래서 온보딩에서 넣은 부상이 운동의 avoid_if_pain 과 한 번도 맞지 않았고,
부상 부위를 피해 추천하는 기능이 그 경로에서는 동작하지 않았다.

parse_list_field 는 두 형식을 모두 받는다. 예전에 저장된 행을 고치지 않아도
읽기가 바르게 되도록 하기 위함이다. 쓸 때는 dump_list_field 로 정본 형식만 쓴다.
"""

import json
from typing import List, Optional


def parse_list_field(raw: Optional[str]) -> List[str]:
    """쉼표로 이은 문자열이든 JSON 배열이든 문자열 목록으로 돌려준다."""
    if not raw:
        return []

    text = raw.strip()
    if text.startswith("["):
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, list):
            return [str(item).strip() for item in loaded if str(item).strip()]

    # 두 형식이 한 칸에 섞인 값도 있다. 온보딩이 '[]' 를 쓴 뒤 통증이 쉼표로 덧붙어
    # '[],hip' 이 된 행이 그렇다. 쪼갠 뒤 대괄호와 따옴표 찌꺼기를 털어 낸다.
    parts = []
    for part in text.split(","):
        item = part.strip().strip("[]").strip().strip('"').strip("'").strip()
        if item:
            parts.append(item)
    return parts


def dump_list_field(values) -> str:
    """정본 형식(쉼표로 이은 문자열)으로 만든다. 순서는 유지하고 중복만 없앤다."""
    seen = []
    for value in values or []:
        item = str(value).strip()
        if item and item not in seen:
            seen.append(item)
    return ",".join(seen)
