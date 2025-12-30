from __future__ import annotations
from datetime import date, datetime
from typing import Optional
import re

def map_age(age_raw: str | None) -> str:
    """
    연령 제한 문자열을 표준화된 코드로 변환한다.
    """
    if not age_raw: return "ALL"
    a = age_raw.strip().lower()
    if "12" in a or "twelve" in a : return "12"
    elif "15" in a or "fifteen" in a : return "15"
    elif "19" in a or "nineteen" in a or "청소년" in a : return "19"
    else : return "ALL"

def map_status(raw: str | None) -> str:
    """
       작품 상태 문자열을 표준 상태코드로 변환한다.
    """
    if not raw: return "unknown"
    r = raw.strip().lower()
    if "연재" in r or "ing" in r or "ongoing" in r : return "ongoing"
    elif "완결" in r or "pause" in r or "completed" in r : return "completed"
    elif "휴재" in r or "end" in r or "hiatus" in r : return "hiatus"
    else : return "unknown"

def map_num(s: str | int) -> int:
    """
    숫자/조회수/카운트 문자열을 정수 값으로 변환한다.
    """
    if not s : return 0
    s= str(s)
    s = s.replace(",", "")
    m = re.match(r"([\d.]+)", s)
    num = float(m.group(1))
    if "억" in s:
        return int(num * 100_000_000)
    elif "만" in s:
        return int(num * 10_000)
    else:
        return int(num)

def map_date(s: str | date | datetime) -> Optional[date]:
    """
       다양한 날짜 표현을 date 객체로 변환한다.

       지원 타입
       ---------
       - date → 그대로 반환
       - datetime → date 로 변환
       - 문자열 → 여러 포맷 시도
       - None → None
    """
    if s is None:
        return None
    # s = date 타입
    if isinstance(s, date) and not isinstance(s, datetime):
        return s
    # s = datetime 타입
    if isinstance(s, datetime):
        return s.date()
    # s = 문자열 타입
    if isinstance(s, str):
        s = s.strip()
        if not s:
            return None

        try: # KP 시간 (ISO)
            return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
        except ValueError:
            pass

        formats = (
            "%y.%m.%d", "%Y.%m.%d",
            "%y-%m-%d", "%Y-%m-%d",
            "%Y.%m.%d %H:%M",
        )
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    return None
