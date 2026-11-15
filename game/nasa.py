"""Fetch REAL recent space weather from NASA's DONKI API (api.nasa.gov).

Uses only the standard library. If anything fails (no internet, rate limit,
bad data) it returns None and the caller falls back to a clearly-labelled archive.
Set NASA_API_KEY in your environment for a higher rate limit (default: DEMO_KEY).
"""
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta

API = "https://api.nasa.gov/DONKI/{endpoint}"
_CACHE = {"at": 0, "events": None}
CACHE_SECONDS = 3600


def _get(endpoint, start, end):
    params = urllib.parse.urlencode({
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "api_key": os.environ.get("NASA_API_KEY", "DEMO_KEY"),
    })
    with urllib.request.urlopen(API.format(endpoint=endpoint) + "?" + params, timeout=6) as r:
        return json.load(r)


def _flare_events(rows):
    out = []
    for f in rows or []:
        cls = str(f.get("classType", ""))
        if not cls or cls[0] not in "MX":
            continue
        dose = 5 if cls[0] == "X" else 2
        out.append({"kind": "flare", "label": "%s solar flare" % cls,
                    "date": str(f.get("peakTime") or f.get("beginTime", ""))[:10],
                    "detail": "Real flare recorded by NASA's DONKI database.", "dose": dose})
    return out


def _cme_events(rows):
    out = []
    for c in rows or []:
        speed = None
        for a in c.get("cmeAnalyses") or []:
            if a.get("isMostAccurate") and a.get("speed"):
                speed = float(a["speed"])
        if not speed or speed < 500:
            continue
        dose = 10 if speed >= 1000 else 6 if speed >= 700 else 3
        out.append({"kind": "cme", "label": "Solar cloud (CME) at %d km/s" % speed,
                    "date": str(c.get("startTime", ""))[:10],
                    "detail": "Real CME recorded by NASA's DONKI database.", "dose": dose})
    return out


def recent_events(days=30):
    """Return a list of real recent events, or None if the live feed is unavailable."""
    if _CACHE["events"] is not None and time.time() - _CACHE["at"] < CACHE_SECONDS:
        return _CACHE["events"]
    try:
        end = date.today()
        start = end - timedelta(days=days)
        events = _flare_events(_get("FLR", start, end)) + _cme_events(_get("CME", start, end))
    except Exception:
        return None
    events.sort(key=lambda e: e["date"])
    _CACHE.update(at=time.time(), events=events)
    return events
