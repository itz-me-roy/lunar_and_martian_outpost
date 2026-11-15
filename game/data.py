"""Curated, ARCHIVED space-weather events used when the live NASA feed is not used.

These are real, well-documented events. They are static (not live) and the game
labels them that way. Class/speed values come from public NASA/NOAA summaries;
double-check against DONKI (https://kauai.ccmc.gsfc.nasa.gov/DONKI/) before
quoting them elsewhere.

kind:
  'flare' - fast X-ray burst. Light-speed: NO advance warning.
  'cme'   - big cloud of solar particles. Takes ~1-3 days to arrive: CAN be forecast.
dose    - game-scaled radiation (mSv) for an UNSHIELDED crew in the game.
"""

ARCHIVES = {
    "may2024": {
        "title": "May 2024 superstorm",
        "blurb": "The strongest solar storm in ~20 years, from sunspot region 3664.",
        "source": "Archive: May 2024 events (NASA DONKI / NOAA SWPC public summaries)",
        "events": [
            {"kind": "cme", "label": "Giant solar cloud (CME) hits - G5 storm", "date": "2024-05-10",
             "detail": "Several CMEs merged and caused a G5 (the top level) geomagnetic storm.", "dose": 10},
            {"kind": "flare", "label": "X5.8 solar flare", "date": "2024-05-11",
             "detail": "An X-class flare: the biggest flare category.", "dose": 5},
            {"kind": "flare", "label": "X8.7 solar flare", "date": "2024-05-14",
             "detail": "The strongest flare of Solar Cycle 25 so far.", "dose": 6},
        ],
    },
    "halloween2003": {
        "title": "Halloween 2003 storms",
        "blurb": "A burst of huge flares and fast clouds around Halloween 2003.",
        "source": "Archive: Oct-Nov 2003 events (NASA / NOAA public summaries)",
        "events": [
            {"kind": "flare", "label": "X17 solar flare", "date": "2003-10-28",
             "detail": "One of the largest flares of the space age.", "dose": 7},
            {"kind": "cme", "label": "Very fast solar cloud (CME)", "date": "2003-10-28",
             "detail": "Reached Earth in about a day.", "dose": 10},
            {"kind": "flare", "label": "X10 solar flare", "date": "2003-10-29",
             "detail": "Another giant flare, one day later.", "dose": 5},
            {"kind": "flare", "label": "X28 solar flare (estimated)", "date": "2003-11-04",
             "detail": "So strong it overloaded the instruments measuring it.", "dose": 7},
        ],
    },
    "apollo1972": {
        "title": "August 1972 (Apollo era)",
        "blurb": "A huge particle storm that happened between Apollo 16 and Apollo 17.",
        "source": "Archive: August 1972 solar particle event (pre-DONKI, NASA history)",
        "events": [
            {"kind": "cme", "label": "Huge particle storm (SEP event)", "date": "1972-08-04",
             "detail": "It happened between two Moon missions. Astronauts out on the Moon "
                       "then could have been in serious danger.", "dose": 10},
            {"kind": "flare", "label": "Strong flare", "date": "1972-08-04",
             "detail": "Flares came along with the particle storm.", "dose": 5},
            {"kind": "cme", "label": "Second particle burst", "date": "1972-08-07",
             "detail": "Storms often come in groups.", "dose": 7},
        ],
    },
}

# Real measurements used for the background radiation numbers (approximate).
# Mars surface: Curiosity RAD instrument, ~0.64 mSv/day on the surface.
# Mars cruise: Curiosity RAD on the trip to Mars, ~1.8 mSv/day.
# Chest X-ray: roughly 0.1 mSv.
SCIENCE_FACTS = {
    "moon_radiation": "On the Moon there is no air and no magnetic field to help, so radiation "
                      "reaches the ground. Measurements by China's Chang'e-4 lander show daily "
                      "doses several times higher than on the space station.",
    "mars_radiation": "NASA's Curiosity rover carries an instrument called RAD. It measured "
                      "about 0.64 millisieverts (mSv) per day on Mars. A chest X-ray is roughly 0.1 mSv.",
}


CARDS = [
 ("🌅", "A day on Mars", "is 24 hours 39 minutes. NASA calls it a sol!", "NASA Mars missions"),
 ("🌙", "Moon bounce!", "Moon gravity is 1/6 of Earth's. You could jump 6 times higher!", "NASA Moon facts"),
 ("🥬", "Space salad", "Astronauts ate lettuce they grew on the space station in 2015.", "NASA Veggie"),
 ("📡", "Slow mail", "A message from Mars takes 3 to 22 minutes to reach Earth.", "NASA communications"),
 ("🥶", "Brrr, Mars", "The average Mars temperature is about minus 60 degrees Celsius.", "NASA Mars facts"),
 ("💨", "Oxygen from air", "A rover on Mars turned Mars air into oxygen. Its tool, MOXIE, works at 800 degrees Celsius!", "MOXIE, Perseverance"),
 ("🔥", "Hot and cold Moon", "Moon ground can be about 127 degrees Celsius in sunshine and about minus 173 at night.", "LRO Diviner and NASA Moon facts"),
 ("☀️", "Fast sunbeam", "Light from a flare reaches Earth in 8 minutes. Particle clouds need 1 to 3 days.", "NASA DONKI"),
 ("☄️", "Rocks passing by", "NASA tracks thousands of near-Earth asteroids and checks how close each one comes.", "NASA NeoWs"),
 ("📸", "Rover photos", "Curiosity has explored Mars since 2012 and sends new photos home every sol.", "NASA Mars rover photos"),
 ("🧬", "Space science for all", "Plant, mouse and microbe studies flown to space are shared free by NASA OSDR.", "NASA OSDR"),
]


DATASETS = [
    {"name": "DONKI - Space Weather Database",
     "url": "https://kauai.ccmc.gsfc.nasa.gov/DONKI/",
     "use": "Real solar flares (FLR) and solar clouds (CME) become the storms in your mission."},
    {"name": "Curiosity RAD (Mars Science Laboratory)",
     "url": "https://science.nasa.gov/mission/msl-curiosity/",
     "use": "Real radiation measured on Mars sets the background dose for the Mars outpost."},
    {"name": "Chang'e-4 lunar lander dosimeter (LND)",
     "url": "https://www.science.org/doi/10.1126/sciadv.aaz1050",
     "use": "Real radiation measured on the Moon's surface sets the background dose for the Moon outpost."},
    {"name": "Artemis program / Open Science Data Repository (OSDR)",
     "url": "https://osdr.nasa.gov/",
     "use": "Background for why radiation and long stays matter. (Not yet pulled into the game.)"},
]
