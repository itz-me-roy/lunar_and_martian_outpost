# LUNAR and MARTIAN Outpost Game

Lunar and Martian Outpost Game is a browser-based Junior Astronaut Mission Trainer
for ages 7-12. It introduces outposts, radiation, and the challenges astronauts
face, using real NASA data and APIs.

Share a small power budget between Air, Greenhouse,
Storm shield, Science and the Radio. Nothing is free: power spent on science can't
protect the crew from a solar storm.

## Run it
    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py runserver
    # open http://127.0.0.1:8000/

No database setup or accounts are needed (state is kept in file sessions).
Optional: `export NASA_API_KEY=your_key` for a higher DONKI rate limit (default DEMO_KEY).

## Real NASA data
* **DONKI** (api.nasa.gov/DONKI): "Today's real Sun" fetches the last 30 days of M/X-class flares (FLR)
  and fast CMEs (CME). Flares become unwarned radiation spikes; CMEs become storms Earth can forecast.
  If the API fails the game says so and uses a labelled archive. It never calls archive data "live".
* **Archived storms** (static): May 2024, Halloween 2003, August 1972 (game/data.py).
* **Background radiation**: Curiosity RAD (~0.64 mSv/day on Mars); Chang'e-4 lander on the Moon.
* **OSDR**: listed as background only; not yet used.
Values are game-scaled. Verify archive numbers against DONKI before quoting them.

## Where the trade-offs are
* Power is shared by 4 machines + radio. Spending on one means less for another.
* Moon: ~14-day night (turns 8-14) cuts power sharply, so plan batteries ahead.
* Mars: dust storms cut power for 3 sols; warnings need the radio on 2 turns in a row (comm delay).
* Flares give no warning at all, so some shielding is always needed.

## Layout
* game/engine.py - pure-Python simulation (no Django needed; easy to unit test)
* game/nasa.py, game/data.py - live DONKI fetch and archived events
* game/views.py, templates/, static/ - Django UI
