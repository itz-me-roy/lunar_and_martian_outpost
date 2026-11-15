import random

from django.shortcuts import redirect, render
from .data import CARDS
from . import data, engine, nasa

SYSTEMS = [
    {"key": "air", "emoji": "🫁", "name": "Air machine",
     "help": "Makes oxygen. Your crew of 4 breathes 4 air every turn.",
     "levels": ["+0 air", "+2 air", "+4 air", "+6 air"]},
    {"key": "food", "emoji": "🌱", "name": "Greenhouse",
     "help": "Grows food. The crew eats 4 every turn. Healthy plants also make 1 extra air.",
     "levels": ["+0 food", "+2 food", "+4 food (+1 air)", "+6 food (+1 air)"]},
    {"key": "shield", "emoji": "🛡️", "name": "Storm shield",
     "help": "Seals hatches and moves the crew into the shielded room. Cuts radiation, but you can't work as well.",
     "levels": ["storm: 100% in", "storm: 65% in", "storm: 35% in", "storm: 15% in"]},
    {"key": "science", "emoji": "🔭", "name": "Science lab",
     "help": "Experiments earn science points. This is how you win stars!",
     "levels": ["0 pts", "2 pts", "5 pts", "9 pts"]},
]


RANKS = ["A Student", "Space Cadet", "Mission Commander", "The Next Frontier"]


def _get_state(request):
    return request.session.get("game")

def _name(request):
    return request.session.get("name", "Explorer")


def _ctx(request, **kw):
    kw["name"] = _name(request)
    return kw


def welcome(request):
    if request.method == "POST":
        n = request.POST.get("name", "").strip()[:15] or "Explorer"
        request.session["name"] = n
        return redirect("hub")
    return render(request, "game/welcome.html", _ctx(request, cards=CARDS[:3]))

def cards(request):
    return render(request, "game/cards.html", _ctx(request, cards=CARDS))


def home(request):
    if request.method == "POST":
        site = request.POST.get("site")
        mode = request.POST.get("mode")
        if site not in engine.SITES:
            site = "moon"
        events, label = _events_for(mode)
        request.session["game"] = engine.new_game(site, events, label, seed=random.randrange(10**9))
        return redirect("play")
    return render(request, "game/home.html", {
        "sites": engine.SITES, "archives": data.ARCHIVES, "has_game": bool(_get_state(request)),
    })


def _events_for(mode):
    """Return (events, honest label). Live data is only called 'live' if it really was."""
    if mode == "live":
        live = nasa.recent_events()
        if live and len(live) >= 2:
            return live, "LIVE from NASA DONKI: real flares and solar clouds from the last 30 days"
        fallback = data.ARCHIVES["may2024"]
        return fallback["events"], "The live NASA feed was unavailable, so this uses the archive. " + fallback["source"]
    arch = data.ARCHIVES.get(mode, data.ARCHIVES["may2024"])
    return arch["events"], arch["source"]


def play(request):
    state = _get_state(request)
    if not state:
        return redirect("home")
    if state["over"]:
        return redirect("result")
    error = None
    chosen = {"air": 2, "food": 2, "shield": 1, "science": 0, "radio": True}
    if request.method == "POST":
        try:
            alloc = engine.parse_alloc(request.POST)
            chosen = alloc
            engine.play_turn(state, alloc)
            request.session["game"] = state
            request.session.modified = True
            return redirect("result" if state["over"] else "play")
        except (ValueError, TypeError) as exc:
            error = str(exc) if isinstance(exc, ValueError) and str(exc) else "Please pick a level for each machine."
    site = engine.SITES[state["site"]]
    gen = engine.current_power(state)
    warnings = engine.forecast(state)
    consts = {
        "gen": gen, "battery": state["battery"], "o2": state["o2"], "food": state["food"],
        "airProd": engine.AIR_PROD, "foodProd": engine.FOOD_PROD, "plantBonus": engine.PLANT_AIR_BONUS,
        "use": engine.O2_USE, "radioCost": engine.RADIO_COST,
        "batteryCap": engine.BATTERY_CAP, "tankCap": engine.TANK_CAP,
    }
    return render(request, "game/play.html", {
        "state": state, "site": site, "gen": gen, "systems": SYSTEMS, "chosen": chosen,
        "warnings": warnings, "error": error, "consts": consts,
        "levels": range(engine.MAX_LEVEL + 1), "turns": engine.TURNS,
        "dust": state["dust_left"] > 0, "dose_pct": min(100, round(100 * state["dose"] / site["dose_budget"])),
        "budget": site["dose_budget"], "radio_need": site["radio_turns_needed"],
        "report": state["last_report"],
    })


def result(request):
    state = _get_state(request)
    if not state:
        return redirect("home")
    if not state["over"]:
        return redirect("play")
    title, text = engine.OUTCOME_TEXT[state["outcome"]]
    site = engine.SITES[state["site"]]
    return render(request, "game/result.html", {
        "state": state, "site": site, "title": title, "text": text,
        "stars": engine.stars(state), "star_range": range(3),
        "rank": RANKS[engine.stars(state)],
        "lessons": engine.debrief(state), "history": state["history"],
        "goal": site["science_goal"], "budget": site["dose_budget"],
        "star_dose": round(site["dose_budget"] * 0.7, 1),
    })


def about(request):
    return render(request, "game/about.html", {
        "datasets": data.DATASETS, "archives": data.ARCHIVES, "facts": data.SCIENCE_FACTS,
    })
