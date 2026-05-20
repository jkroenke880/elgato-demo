#!/usr/bin/env python3
"""
Seed 3,000 dummy users with realistic events across Corsair and Elgato sources.

Distribution:
  - 1,000 Corsair-only users
  - 1,000 Elgato-only users
  - 1,000 cross-brand users (appear in both sources → Combined Profiles stitching)

Each user gets a random journey type that maps to one or more audiences.
Events are sent via the Segment Batch API in chunks of 500 using a thread pool.
"""

import json, random, string, uuid, base64, datetime, time
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Config ──────────────────────────────────────────────────────────────────
CORSAIR_KEY = "8kaqLmYEhmEHzemxYWsD6rip6GHFaj9L"
ELGATO_KEY  = "TP7mEFeOwIMczsGdFmBQsbG08b6gXJTP"
BATCH_URL   = "https://api.segment.io/v1/batch"
BATCH_SIZE  = 500      # Segment batch max
MAX_WORKERS = 8        # parallel HTTP threads

TOTAL_CORSAIR_ONLY  = 1000
TOTAL_ELGATO_ONLY   = 1000
TOTAL_CROSS_BRAND   = 1000

# ── Helpers ─────────────────────────────────────────────────────────────────
def auth_header(write_key):
    token = base64.b64encode((write_key + ":").encode()).decode()
    return {"Authorization": "Basic " + token, "Content-Type": "application/json"}

def ts(days_ago=0, hours_ago=0, minutes_ago=0):
    t = datetime.datetime.utcnow() - datetime.timedelta(
        days=days_ago, hours=hours_ago, minutes=minutes_ago
    )
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")

def rand_id():
    return str(uuid.uuid4())

def send_batch(write_key, events):
    payload = json.dumps({"batch": events}).encode()
    req = urllib.request.Request(
        BATCH_URL, data=payload, headers=auth_header(write_key), method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)

def flush(write_key, events, label, results):
    """Chunk events into BATCH_SIZE and dispatch each chunk as a future."""
    jobs = []
    for i in range(0, len(events), BATCH_SIZE):
        chunk = events[i:i + BATCH_SIZE]
        jobs.append((write_key, chunk))
    return jobs

# ── Fake data generators ─────────────────────────────────────────────────────
FIRST_NAMES = [
    "Aiden","Amara","Aria","Axel","Bella","Blake","Caleb","Cami","Carlos","Clara",
    "Cole","Dani","Diego","Elena","Eli","Elise","Emma","Ethan","Felix","Finn",
    "Grace","Hannah","Harper","Iris","Isaac","Isla","Ivy","Jade","Jake","James",
    "Jax","Jordan","Jules","Kai","Kira","Lara","Lena","Leo","Liam","Lily",
    "Luca","Luna","Marcus","Maya","Mia","Miles","Mira","Myles","Nadia","Nate",
    "Neil","Nia","Noah","Nora","Oliver","Omar","Owen","Paige","Piper","Quinn",
    "Ravi","Remi","Riley","River","Roman","Rosa","Ruby","Ryan","Sadie","Sam",
    "Sara","Sebastian","Sienna","Skylar","Sofia","Stella","Talia","Theo","Tia",
    "Tyler","Uma","Uri","Vance","Vera","Victor","Violet","Willa","Wyatt","Xander",
    "Yasmin","Yuki","Zara","Zeke","Zoe","Zoey","Andre","Anita","Ben","Bria"
]
LAST_NAMES = [
    "Adams","Ahmed","Allen","Anderson","Baker","Barnes","Bell","Bennett","Brooks",
    "Brown","Butler","Campbell","Carter","Chen","Clark","Cole","Collins","Cook",
    "Cooper","Cox","Davis","Diaz","Edwards","Evans","Fisher","Flores","Foster",
    "Garcia","Gomez","Gonzalez","Gray","Green","Hall","Harris","Hayes","Hernandez",
    "Hill","Howard","Hughes","Jackson","James","Jenkins","Johnson","Jones","Kelly",
    "Kim","King","Lee","Lewis","Lin","Long","Lopez","Martin","Martinez","Miller",
    "Mitchell","Moore","Morgan","Morris","Murphy","Nelson","Nguyen","Parker","Patel",
    "Perez","Peterson","Phillips","Powell","Price","Reed","Richardson","Rivera","Roberts",
    "Robinson","Rodriguez","Ross","Russell","Sanchez","Scott","Sharma","Singh","Smith",
    "Stewart","Sullivan","Taylor","Thomas","Thompson","Torres","Turner","Walker","Wang",
    "Ward","Watson","White","Williams","Wilson","Wood","Wright","Young","Zhang","Zhou"
]
DOMAINS = [
    "gmail.com","yahoo.com","outlook.com","icloud.com","proton.me","hotmail.com",
    "live.com","me.com","fastmail.com","hey.com","tutanota.com","aol.com"
]
CITIES = [
    "New York","Los Angeles","Chicago","Houston","Phoenix","San Antonio","San Diego",
    "Dallas","San Jose","Austin","Jacksonville","Fort Worth","Columbus","Charlotte",
    "Indianapolis","San Francisco","Seattle","Denver","Nashville","Portland",
    "Boston","Las Vegas","Detroit","Memphis","Louisville","Baltimore","Milwaukee",
    "Albuquerque","Tucson","Fresno","Sacramento","Atlanta","Miami","Minneapolis",
    "Cleveland","Pittsburgh","Oakland","Tampa","Raleigh","Arlington"
]

def fake_user(idx):
    first = random.choice(FIRST_NAMES)
    last  = random.choice(LAST_NAMES)
    # unique email using index to guarantee no collisions
    domain = random.choice(DOMAINS)
    email  = f"{first.lower()}.{last.lower()}{idx}@{domain}"
    return {
        "email":     email,
        "firstName": first,
        "lastName":  last,
        "city":      random.choice(CITIES),
    }

# ── Corsair catalog ──────────────────────────────────────────────────────────
CORSAIR_PRODUCTS = [
    {"product_id":"k100-rgb",          "sku":"CH-9109114-NA","name":"K100 RGB Optical-Mechanical Keyboard","price":169.99,"category":"Keyboards",  "brand":"Corsair"},
    {"product_id":"dark-core-pro-se",  "sku":"CH-9315511-NA","name":"Dark Core RGB Pro SE Wireless Mouse", "price":109.99,"category":"Mice",       "brand":"Corsair"},
    {"product_id":"hs80-rgb-wireless", "sku":"CA-9011235-NA","name":"HS80 RGB Wireless Gaming Headset",    "price":159.99,"category":"Headsets",   "brand":"Corsair"},
    {"product_id":"st100-rgb",         "sku":"CA-9011167-NA","name":"ST100 RGB Premium Headset Stand",     "price":79.99, "category":"Accessories","brand":"Corsair"},
    {"product_id":"icue-h150i-elite",  "sku":"CW-9060060-WW","name":"iCUE H150i RGB Elite Liquid CPU Cooler","price":179.99,"category":"Cooling", "brand":"Corsair"},
]

# ── Elgato catalog ────────────────────────────────────────────────────────────
ELGATO_PRODUCTS = [
    {"product_id":"stream-deck-mk2","sku":"10MUX01",  "name":"Stream Deck MK.2",            "price":149.99,"category":"Stream Controllers","brand":"Elgato"},
    {"product_id":"stream-deck-xl", "sku":"10020419", "name":"Stream Deck XL",               "price":249.99,"category":"Stream Controllers","brand":"Elgato"},
    {"product_id":"facecam-pro",    "sku":"10WAA9901","name":"Facecam Pro",                  "price":299.99,"category":"Cameras",           "brand":"Elgato"},
    {"product_id":"wave-3",         "sku":"10MAB9901","name":"Wave:3 USB Microphone",        "price":149.99,"category":"Microphones",       "brand":"Elgato"},
    {"product_id":"key-light",      "sku":"10GAK9901","name":"Key Light",                    "price":199.99,"category":"Lighting",          "brand":"Elgato"},
    {"product_id":"4k60-pro-mk2",   "sku":"10GBE9901","name":"4K60 Pro MK.2 Capture Card",  "price":199.99,"category":"Capture Cards",     "brand":"Elgato"},
]

# ── Event builders ────────────────────────────────────────────────────────────
def e_identify(uid, traits, days_ago):
    return {"type":"identify","userId":uid,"traits":traits,"timestamp":ts(days_ago, random.randint(0,23))}

def e_page(uid, name, days_ago, h=0):
    return {"type":"page","userId":uid,"name":name,"timestamp":ts(days_ago, h)}

def e_viewed(uid, product, days_ago, h=0):
    return {"type":"track","event":"Product Viewed","userId":uid,
            "properties":{**product,"quantity":1},"timestamp":ts(days_ago, h, random.randint(0,59))}

def e_added(uid, product, cart_id, days_ago, h=0):
    return {"type":"track","event":"Product Added","userId":uid,
            "properties":{**product,"quantity":1,"cart_id":cart_id},"timestamp":ts(days_ago, h, random.randint(0,59))}

def e_checkout(uid, products, total, order_id, days_ago, h=0):
    return {"type":"track","event":"Checkout Started","userId":uid,
            "properties":{"order_id":order_id,"value":total,"currency":"USD",
                          "products":[{**p,"quantity":1} for p in products]},
            "timestamp":ts(days_ago, h, random.randint(0,59))}

def e_order(uid, products, total, order_id, days_ago, h=0):
    brand = products[0]["brand"] if products else ""
    return {"type":"track","event":"Order Completed","userId":uid,
            "properties":{"order_id":order_id,"total":total,"revenue":total,"currency":"USD",
                          "brand":brand,
                          "products":[{**p,"quantity":1} for p in products]},
            "timestamp":ts(days_ago, h, random.randint(0,59))}

# ── Journey builders ──────────────────────────────────────────────────────────
# Each journey returns a list of events for one user against one catalog.

def journey_purchaser(uid, user, catalog, days_ago):
    """Viewed 1-3 products, added 1-2, completed checkout. → purchased + maybe high_value"""
    events = []
    events.append(e_identify(uid, user, days_ago + 1))
    cart_id = rand_id()[:8]
    order_id = rand_id()[:8].upper()
    products = random.sample(catalog, k=random.randint(1, 2))
    for i, p in enumerate(products):
        events.append(e_viewed(uid, p, days_ago + 1, h=random.randint(1, 20)))
        events.append(e_added(uid, p, cart_id, days_ago, h=random.randint(1, 20)))
    total = round(sum(p["price"] for p in products), 2)
    events.append(e_checkout(uid, products, total, order_id, days_ago, h=1))
    events.append(e_order(uid, products, total, order_id, days_ago, h=0))
    return events

def journey_abandoner(uid, user, catalog, days_ago):
    """Added to cart and started checkout but never completed. → cart_abandoner"""
    events = []
    events.append(e_identify(uid, user, days_ago + 1))
    cart_id = rand_id()[:8]
    order_id = rand_id()[:8].upper()
    products = random.sample(catalog, k=random.randint(1, 2))
    for p in products:
        events.append(e_viewed(uid, p, days_ago + 1, h=random.randint(2, 22)))
        events.append(e_added(uid, p, cart_id, days_ago, h=random.randint(1, 10)))
    total = round(sum(p["price"] for p in products), 2)
    events.append(e_checkout(uid, products, total, order_id, days_ago, h=0))
    # no order completed
    return events

def journey_browser(uid, user, catalog, days_ago):
    """Viewed 3-5 products, never bought. → viewed_no_purchase + high_engagement + category audiences"""
    events = []
    events.append(e_identify(uid, user, days_ago + 2))
    products = random.sample(catalog, k=random.randint(3, min(5, len(catalog))))
    for i, p in enumerate(products):
        events.append(e_viewed(uid, p, days_ago + random.randint(0, 1), h=random.randint(0, 22)))
    return events

def journey_repeat_buyer(uid, user, catalog, days_ago):
    """Two separate orders. → purchased + high_value (likely)"""
    events = journey_purchaser(uid, user, catalog, days_ago + random.randint(5, 14))
    events += journey_purchaser(uid, user, catalog, days_ago)
    return events

# Weights: purchaser 40%, abandoner 25%, browser 20%, repeat_buyer 15%
CORSAIR_JOURNEYS = [
    (journey_purchaser,    0.40),
    (journey_abandoner,    0.25),
    (journey_browser,      0.20),
    (journey_repeat_buyer, 0.15),
]
ELGATO_JOURNEYS = CORSAIR_JOURNEYS  # same distribution

def pick_journey(journeys):
    r = random.random()
    cumulative = 0.0
    for fn, weight in journeys:
        cumulative += weight
        if r < cumulative:
            return fn
    return journeys[-1][0]

# ── Build all events ──────────────────────────────────────────────────────────
print("Building events for 3,000 users...")

corsair_events = []
elgato_events  = []

user_idx = 0

# 1,000 Corsair-only
for i in range(TOTAL_CORSAIR_ONLY):
    user = fake_user(user_idx); user_idx += 1
    uid  = user["email"]
    days = random.randint(0, 60)
    fn   = pick_journey(CORSAIR_JOURNEYS)
    corsair_events.extend(fn(uid, user, CORSAIR_PRODUCTS, days))

# 1,000 Elgato-only
for i in range(TOTAL_ELGATO_ONLY):
    user = fake_user(user_idx); user_idx += 1
    uid  = user["email"]
    days = random.randint(0, 60)
    fn   = pick_journey(ELGATO_JOURNEYS)
    elgato_events.extend(fn(uid, user, ELGATO_PRODUCTS, days))

# 1,000 cross-brand (same email → both sources)
for i in range(TOTAL_CROSS_BRAND):
    user = fake_user(user_idx); user_idx += 1
    uid  = user["email"]
    days_c = random.randint(0, 60)
    days_e = random.randint(0, 60)
    fn_c   = pick_journey(CORSAIR_JOURNEYS)
    fn_e   = pick_journey(ELGATO_JOURNEYS)
    corsair_events.extend(fn_c(uid, user, CORSAIR_PRODUCTS, days_c))
    elgato_events.extend(fn_e(uid, user, ELGATO_PRODUCTS, days_e))

print(f"  Corsair events:  {len(corsair_events):,}")
print(f"  Elgato events:   {len(elgato_events):,}")
print(f"  Total:           {len(corsair_events) + len(elgato_events):,}")
print(f"\nSending in batches of {BATCH_SIZE} using {MAX_WORKERS} threads...")

# ── Send ──────────────────────────────────────────────────────────────────────
all_jobs = []  # (write_key, chunk, label)

for i in range(0, len(corsair_events), BATCH_SIZE):
    all_jobs.append((CORSAIR_KEY, corsair_events[i:i+BATCH_SIZE], "Corsair"))

for i in range(0, len(elgato_events), BATCH_SIZE):
    all_jobs.append((ELGATO_KEY, elgato_events[i:i+BATCH_SIZE], "Elgato"))

total_batches = len(all_jobs)
completed = 0
errors    = 0

start = time.time()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
    futures = {
        pool.submit(send_batch, wk, chunk): (label, len(chunk))
        for wk, chunk, label in all_jobs
    }
    for future in as_completed(futures):
        label, size = futures[future]
        status = future.result()
        completed += 1
        if status != 200:
            errors += 1
            print(f"  [!] {label} batch failed — HTTP {status}")
        if completed % 5 == 0 or completed == total_batches:
            pct = completed / total_batches * 100
            elapsed = time.time() - start
            print(f"  {completed}/{total_batches} batches ({pct:.0f}%) — {elapsed:.1f}s — {errors} errors")

elapsed = time.time() - start
total_events = len(corsair_events) + len(elgato_events)

print(f"""
✓ Done in {elapsed:.1f}s
  Batches sent:    {total_batches} ({errors} errors)
  Total events:    {total_events:,}
  Events/second:   {total_events/elapsed:.0f}

Approximate audience populations:
  Corsair space:
    purchased_at_corsair               ~{int((TOTAL_CORSAIR_ONLY + TOTAL_CROSS_BRAND) * 0.55):,} users
    corsair_high_value_buyer           ~{int((TOTAL_CORSAIR_ONLY + TOTAL_CROSS_BRAND) * 0.30):,} users
    corsair_cart_abandoners            ~{int((TOTAL_CORSAIR_ONLY + TOTAL_CROSS_BRAND) * 0.25):,} users
    viewed_corsair_product_no_purchase ~{int((TOTAL_CORSAIR_ONLY + TOTAL_CROSS_BRAND) * 0.45):,} users
    corsair_keyboard_shopper           ~{int((TOTAL_CORSAIR_ONLY + TOTAL_CROSS_BRAND) * 0.35):,} users

  Elgato space:
    purchased_at_elgato                ~{int((TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.55):,} users
    elgato_high_value_buyer            ~{int((TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.30):,} users
    elgato_cart_abandoners             ~{int((TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.25):,} users
    stream_deck_interested             ~{int((TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.35):,} users
    microphone_shopper                 ~{int((TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.20):,} users

  Combined Profiles space:
    cross_brand_buyer                  ~{int(TOTAL_CROSS_BRAND * 0.55):,} users
    any_brand_purchaser                ~{int((TOTAL_CORSAIR_ONLY + TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.55):,} users
    high_engagement_browser            ~{int((TOTAL_CORSAIR_ONLY + TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.20):,} users
    combined_cart_abandoner            ~{int((TOTAL_CORSAIR_ONLY + TOTAL_ELGATO_ONLY + TOTAL_CROSS_BRAND) * 0.25):,} users
    recent_buyer_last_30_days          (subset of purchasers with events within 30 days)
""")
