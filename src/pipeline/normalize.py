from __future__ import annotations
from datetime import date, datetime
from typing import Optional
import re

def map_age(age_raw: str | None) -> str:
    if not age_raw: return "ALL"
    a = age_raw.strip().lower()
    if "12" in a or "twelve" in a : return "12"
    elif "15" in a or "fifteen" in a : return "15"
    elif "19" in a or "nineteen" in a or "청소년" in a : return "19"
    else : return "ALL"

def map_status(raw: str | None) -> str:
    if not raw: return "unknown"
    r = raw.strip().lower()
    if "연재" in r or "ing" in r : return "ongoing"
    elif "완결" in r or "pause" in r: return "completed"
    elif "휴재" in r or "end" in r: return "hiatus"
    else : return "unknown"

def map_num(s: str | int) -> int:
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
            "%Y.%m.%d %H:%M", # munpia 시간
        )
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    return None
