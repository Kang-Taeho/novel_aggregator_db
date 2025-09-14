from __future__ import annotations

def map_age(age_raw: str | None) -> str:
    if not age_raw: return "ALL"
    a = age_raw.strip().upper()
    return a if a in {"ALL","12","15","19"} else "ALL"

def map_status(raw: str | None) -> str:
    if not raw: return "unknown"
    r = raw.strip().lower()
    return {"연재중":"ongoing","완결":"completed","휴재":"hiatus"}.get(r, "unknown")
