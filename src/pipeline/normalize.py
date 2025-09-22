from __future__ import annotations
import re

def map_age(age_raw: str | None) -> str:
    if not age_raw: return "ALL"
    a = age_raw.strip().upper()
    if "12" in a : return "12"
    elif "15" in a : return "15"
    elif "19" in a : return "19"
    else : return "ALL"

def map_status(raw: str | None) -> str:
    if not raw: return "unknown"
    r = raw.strip().lower()
    if "연재" in r : return "ongoing"
    elif "완결" in r : return "completed"
    elif "휴재" in r : return "hiatus"
    else : return "unknown"

def map_view(s: str) -> int:
    s = s.replace(",", "")
    m = re.match(r"([\d.]+)", s)
    num = float(m.group(1))
    if "억" in s:
        return int(num * 100_000_000)
    elif "만" in s:
        return int(num * 10_000)
    else:
        return int(num)
