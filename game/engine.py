"""Pure-Python simulation for the outpost game (no Django needed, so it is easy to test).

Everything is a trade-off:
  * Power is shared by Air, Food, Shield, Science and the Radio.
  * Air, Food and the Battery are stocks that carry over to the next turn.
  * Radiation dose only goes UP. Shielding costs power; science and shielding compete.
  * Listening to Earth (radio) costs power but is the only way to get storm warnings.
"""
import random

TURNS = 15
CREW = 4
O2_USE = 4
FOOD_USE = 4
BATTERY_CAP = 20
TANK_CAP = 20
RADIO_COST = 1
MAX_LEVEL = 3

AIR_PROD = [0, 2, 4, 6]
FOOD_PROD = [0, 2, 4, 6]
PLANT_AIR_BONUS = 1          # plants make a little oxygen when the greenhouse runs well
SCIENCE_PTS = [0, 2, 5, 9]
SHIELD_EVENT = [1.0, 0.65, 0.35, 0.15]   # multiplier on storm dose
SHIELD_BASE = [1.0, 0.92, 0.85, 0.78]    # multiplier on background dose

SITES = {
    "moon": {
        "name": "Moon outpost",
        "emoji": "🌙",
        "blurb": "Close to home (a radio message takes only about 1.3 seconds) but the Moon's "
                 "night lasts about 14 Earth days, so the Sun-powered panels go almost dark.",
        "turn_is": "Each turn is about 2 Earth days, so the Moon's day and night each last 7 turns.",
        "base_dose": 2.7,     # mSv per turn (about 2 days at ~1.4 mSv/day)
        "dose_budget": 60,
        "science_goal": 50,
        "delay_text": "A radio message from Earth takes about 1.3 seconds each way.",
        "radio_turns_needed": 1,
    },
    "mars": {
        "name": "Mars outpost",
        "emoji": "🔴",
        "blurb": "Far from home (a radio message takes 3 to 22 minutes each way) and dust storms "
                 "can blot out the Sun for days.",
        "turn_is": "Each turn is one Mars day (a 'sol').",
        "base_dose": 0.64,    # mSv per sol, Curiosity RAD surface measurement
        "dose_budget": 26,
        "science_goal": 28,
        "delay_text": "A radio message from Earth takes 3 to 22 minutes each way.",
        "radio_turns_needed": 2,
    },
}


def power_generated(site, turn, dust_left):
    if site == "moon":
        gen = 9 if (turn <= 7 or turn >= 15) else 3
    else:
        gen = 7
    if dust_left > 0:
        gen = max(1, gen - 4)
    return gen


def build_schedule(site, events, rng):
    """Pick up to 5 real events and place them on random turns (kept in real date order)."""
    pool = sorted(events, key=lambda e: e["date"])
    if len(pool) > 5:
        # keep the 5 biggest, then restore date order
        pool = sorted(sorted(pool, key=lambda e: -e["dose"])[:5], key=lambda e: e["date"])
    slots = sorted(rng.sample(range(3, TURNS), len(pool)))
    schedule = []
    for turn, ev in zip(slots, pool):
        item = dict(ev)
        item["turn"] = turn
        item["warn"] = ev["kind"] == "cme"
        schedule.append(item)
    if site == "mars":
        free = [t for t in range(4, 11) if t not in slots]
        t = rng.choice(free)
        schedule.append({"turn": t, "kind": "dust", "label": "Dust storm", "date": "",
                         "detail": "Dust blocks sunlight, so solar panels make much less power for 3 sols. "
                                   "In 2018 a dust storm ended NASA's Opportunity rover mission.",
                         "dose": 0, "warn": True})
    schedule.sort(key=lambda e: e["turn"])
    return schedule


def new_game(site, events, source_label, seed=None):
    rng = random.Random(seed)
    return {
        "site": site, "turn": 1, "battery": 10, "o2": 12, "food": 12,
        "dose": 0.0, "science": 0, "hunger": 0, "dust_left": 0,
        "radio_hist": [], "schedule": build_schedule(site, events, rng),
        "source": source_label, "history": [], "over": False, "outcome": None,
        "last_report": [],
    }


def current_power(state):
    dusty = state["dust_left"] > 0 or any(
        e["kind"] == "dust" and e["turn"] == state["turn"] for e in state["schedule"])
    return power_generated(state["site"], state["turn"], 3 if dusty else 0)


def _events_at(state, turn):
    return [e for e in state["schedule"] if e["turn"] == turn]


def _heard(state):
    """Did the radio listen long enough for Earth's warning to reach us?"""
    need = SITES[state["site"]]["radio_turns_needed"]
    h = state["radio_hist"]
    return len(h) >= need and all(h[-need:])


def forecast(state):
    """Warnings the player can see at the start of this turn."""
    if state["over"] or not _heard(state):
        return []
    return [e for e in _events_at(state, state["turn"]) if e["warn"]]


def preview(state, alloc):
    """What the stocks would be after this turn, ignoring surprise events."""
    gen = current_power(state)
    spend = _spend(alloc)
    air = AIR_PROD[alloc["air"]] + (PLANT_AIR_BONUS if alloc["food"] >= 2 else 0)
    return {
        "gen": gen, "spend": spend,
        "battery": min(BATTERY_CAP, state["battery"] + gen - spend),
        "o2": min(TANK_CAP, state["o2"] + air - O2_USE),
        "food": min(TANK_CAP, state["food"] + FOOD_PROD[alloc["food"]] - FOOD_USE),
    }


def _spend(alloc):
    return (alloc["air"] + alloc["food"] + alloc["shield"] + alloc["science"]
            + (RADIO_COST if alloc["radio"] else 0))


def parse_alloc(data):
    alloc = {}
    for key in ("air", "food", "shield", "science"):
        try:
            v = int(data.get(key, 0))
        except (TypeError, ValueError):
            raise ValueError("Pick a level from 0 to 3 for every machine.")
        if not 0 <= v <= MAX_LEVEL:
            raise ValueError("Pick a level from 0 to 3 for every machine.")
        alloc[key] = v
    alloc["radio"] = bool(data.get("radio"))
    return alloc


def play_turn(state, alloc):
    """Advance one turn. Raises ValueError if the plan needs more power than exists."""
    if state["over"]:
        return state
    site = SITES[state["site"]]
    turn = state["turn"]
    events = _events_at(state, turn)
    heard = _heard(state)

    # dust storms start now
    for e in events:
        if e["kind"] == "dust":
            state["dust_left"] = 3
    gen = current_power(state)
    spend = _spend(alloc)
    if spend > gen + state["battery"]:
        raise ValueError("That plan needs %d power but you only have %d (sun %d + battery %d)."
                         % (spend, gen + state["battery"], gen, state["battery"]))

    report = []
    # --- power
    state["battery"] = min(BATTERY_CAP, state["battery"] + gen - spend)
    if state["battery"] == 0:
        report.append(("warn", "The battery is empty! Any lights-out turn now would be dangerous."))
    # --- air
    air_made = AIR_PROD[alloc["air"]] + (PLANT_AIR_BONUS if alloc["food"] >= 2 else 0)
    state["o2"] = min(TANK_CAP, state["o2"] + air_made - O2_USE)
    # --- food
    state["food"] = min(TANK_CAP, state["food"] + FOOD_PROD[alloc["food"]] - FOOD_USE)
    if state["food"] < 0:
        state["food"] = 0
        state["hunger"] += 1
        report.append(("warn", "The crew went hungry. Science work slows down when everyone is hungry."))
    else:
        state["hunger"] = 0
    # --- radiation
    base = site["base_dose"] * SHIELD_BASE[alloc["shield"]]
    storm = 0.0
    unshielded = 0.0
    for e in events:
        if e["dose"]:
            unshielded += e["dose"]
            storm += e["dose"] * SHIELD_EVENT[alloc["shield"]]
    state["dose"] = round(state["dose"] + base + storm, 2)
    # --- science
    sci = SCIENCE_PTS[alloc["science"]]
    if state["hunger"]:
        sci //= 2
    state["science"] += sci

    for e in events:
        was_warned = e["warn"] and heard
        if e["kind"] == "dust":
            report.append(("event", "🌪️ Dust storm! Solar panels make less power for the next 3 turns."
                           + (" (Earth warned you.)" if was_warned else " (No warning - you weren't listening.)")))
        else:
            saved = unshielded - storm
            tag = "Earth warned you in time." if was_warned else (
                "No warning: this kind of event travels at the speed of light." if e["kind"] == "flare"
                else "You weren't listening to Earth, so there was no warning.")
            report.append(("event", "☀️ %s%s! %s Shield level %d turned %.1f mSv into %.1f mSv."
                           % (e["label"], " (" + e["date"] + ")" if e["date"] else "", tag,
                              alloc["shield"], e["dose"], e["dose"] * SHIELD_EVENT[alloc["shield"]])))
    if state["dust_left"] > 0:
        state["dust_left"] -= 1

    state["history"].append({
        "turn": turn, "alloc": alloc, "gen": gen, "heard": heard,
        "events": [{"kind": e["kind"], "label": e["label"], "warn": e["warn"],
                    "dose": e["dose"], "shield": alloc["shield"]} for e in events],
        "o2": state["o2"], "food": state["food"], "battery": state["battery"],
        "dose": state["dose"], "science": state["science"],
    })
    state["radio_hist"] = (state["radio_hist"] + [alloc["radio"]])[-2:]
    state["last_report"] = report

    # --- end conditions
    if state["o2"] < 0:
        state["over"], state["outcome"] = True, "air"
    elif state["hunger"] >= 2:
        state["over"], state["outcome"] = True, "food"
    elif state["dose"] > site["dose_budget"]:
        state["over"], state["outcome"] = True, "radiation"
    elif turn >= TURNS:
        state["over"], state["outcome"] = True, "win"
    else:
        state["turn"] = turn + 1
    return state


def stars(state):
    if state["outcome"] != "win":
        return 0
    site = SITES[state["site"]]
    s = 1
    if state["science"] >= site["science_goal"]:
        s += 1
    if state["dose"] <= site["dose_budget"] * 0.7:
        s += 1
    return s


OUTCOME_TEXT = {
    "win": ("Mission complete!", "Your crew made it home healthy."),
    "air": ("Out of air", "The oxygen ran out. Real crews keep a big reserve for exactly this reason."),
    "food": ("Out of food", "The crew went hungry for too long and had to come home early."),
    "radiation": ("Radiation limit reached",
                  "The crew soaked up too much radiation and mission control called them home early."),
}


def debrief(state):
    """Plain-language lessons based on what the player actually did."""
    site = SITES[state["site"]]
    hist = state["history"]
    lessons = []
    storms = [(h, e) for h in hist for e in h["events"] if e["dose"]]
    unwarned = [(h, e) for h, e in storms if not (e["warn"] and h["heard"])]
    hit_bare = [(h, e) for h, e in storms if e["shield"] == 0]
    radio_on = sum(1 for h in hist if h["alloc"]["radio"])
    if hit_bare:
        lessons.append("Storms hit %d time(s) while your shield was off. Shielding costs power, "
                       "but radiation can't be undone - dose only goes up." % len(hit_bare))
    elif storms:
        lessons.append("You had shielding up for every storm. That kept the crew's dose low, "
                       "and it cost power you could have used for science.")
    if any(e["kind"] == "flare" for _, e in storms):
        lessons.append("Solar flares give NO warning because their light reaches us at light speed. "
                       "That's why real outposts need some shielding all the time.")
    if any(e["kind"] == "cme" for _, e in storms):
        lessons.append("Big solar clouds (CMEs) take a day or more to arrive, so Earth can warn the "
                       "crew - but only if someone is listening and the message arrives in time.")
    if state["site"] == "mars":
        lessons.append("On Mars, messages take minutes to arrive, so the crew must make many "
                       "decisions on their own. In the game you needed the radio on for 2 turns in a row to get warnings.")
    else:
        lessons.append("The Moon's night lasts about 14 Earth days. Outposts need big batteries or a power "
                       "source that doesn't need sunlight, like a small nuclear reactor.")
    if any(h["battery"] == 0 for h in hist):
        lessons.append("The battery hit zero at least once. Engineers plan power a long time ahead.")
    lessons.append("You kept the radio on for %d of %d turns. Listening costs power but buys warning time."
                   % (radio_on, len(hist)))
    return lessons
