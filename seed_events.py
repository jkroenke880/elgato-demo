#!/usr/bin/env python3
"""
Seed fake users and events into Corsair and Elgato Segment sources
to populate all 15 audiences across the three Unify spaces.
"""
import json, urllib.request, urllib.error, base64, time, datetime

CORSAIR_KEY = "8kaqLmYEhmEHzemxYWsD6rip6GHFaj9L"
ELGATO_KEY  = "TP7mEFeOwIMczsGdFmBQsbG08b6gXJTP"
BATCH_URL   = "https://api.segment.io/v1/batch"

def auth(write_key):
    return "Basic " + base64.b64encode((write_key + ":").encode()).decode()

def ts(days_ago=0, hours_ago=0):
    t = datetime.datetime.utcnow() - datetime.timedelta(days=days_ago, hours=hours_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")

def batch(write_key, events):
    payload = json.dumps({"batch": events}).encode()
    req = urllib.request.Request(
        BATCH_URL,
        data=payload,
        headers={"Authorization": auth(write_key), "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status

def send(write_key, events, label):
    # Segment batch max is 500 events; chunk to be safe
    for i in range(0, len(events), 100):
        status = batch(write_key, events[i:i+100])
        print(f"  [{label}] {min(i+100, len(events))}/{len(events)} events → HTTP {status}")
    time.sleep(0.3)

# ── Users ────────────────────────────────────────────────────────────────────
# Each dict: email, firstName, lastName, and which audiences they should land in

USERS = {
    # ── Corsair-only purchasers ───────────────────────────────────────────
    "sarah.okafor@gmail.com":     {"firstName": "Sarah",   "lastName": "Okafor",   "city": "Austin"},
    "james.whitfield@icloud.com": {"firstName": "James",   "lastName": "Whitfield","city": "Seattle"},
    "priya.nair@outlook.com":     {"firstName": "Priya",   "lastName": "Nair",     "city": "San Jose"},
    "derek.moss@yahoo.com":       {"firstName": "Derek",   "lastName": "Moss",     "city": "Denver"},
    # ── Elgato-only purchasers ────────────────────────────────────────────
    "chloe.bertrand@gmail.com":   {"firstName": "Chloe",   "lastName": "Bertrand", "city": "Portland"},
    "marcus.le@proton.me":        {"firstName": "Marcus",  "lastName": "Le",       "city": "Chicago"},
    "tariq.hassan@gmail.com":     {"firstName": "Tariq",   "lastName": "Hassan",   "city": "Miami"},
    "nina.volkov@outlook.com":    {"firstName": "Nina",    "lastName": "Volkov",   "city": "Boston"},
    # ── Cross-brand (appear in combined space audiences) ──────────────────
    "alex.chen@techco.io":        {"firstName": "Alex",    "lastName": "Chen",     "city": "San Francisco"},
    "jordan.kim@agency.com":      {"firstName": "Jordan",  "lastName": "Kim",      "city": "New York"},
    "mia.torres@studio.co":       {"firstName": "Mia",     "lastName": "Torres",   "city": "Los Angeles"},
}

# ── Corsair catalog ──────────────────────────────────────────────────────────
C_KEYBOARD = {"product_id": "k100-rgb",          "sku": "CH-9109114-NA", "name": "K100 RGB Optical-Mechanical Keyboard", "price": 169.99, "category": "Keyboards",  "brand": "Corsair"}
C_MOUSE    = {"product_id": "dark-core-pro-se",  "sku": "CH-9315511-NA", "name": "Dark Core RGB Pro SE Wireless Mouse",  "price": 109.99, "category": "Mice",       "brand": "Corsair"}
C_HEADSET  = {"product_id": "hs80-rgb-wireless", "sku": "CA-9011235-NA", "name": "HS80 RGB Wireless Gaming Headset",     "price": 159.99, "category": "Headsets",   "brand": "Corsair"}
C_STAND    = {"product_id": "st100-rgb",         "sku": "CA-9011167-NA", "name": "ST100 RGB Premium Headset Stand",      "price": 79.99,  "category": "Accessories","brand": "Corsair"}
C_COOLER   = {"product_id": "icue-h150i-elite",  "sku": "CW-9060060-WW", "name": "iCUE H150i RGB Elite Liquid CPU Cooler","price": 179.99,"category": "Cooling",   "brand": "Corsair"}

# ── Elgato catalog ───────────────────────────────────────────────────────────
E_DECK    = {"product_id": "stream-deck-mk2",  "sku": "10MUX01",    "name": "Stream Deck MK.2",               "price": 149.99, "category": "Stream Controllers","brand": "Elgato"}
E_DECK_XL = {"product_id": "stream-deck-xl",  "sku": "10020419",   "name": "Stream Deck XL",                 "price": 249.99, "category": "Stream Controllers","brand": "Elgato"}
E_CAMERA  = {"product_id": "facecam-pro",      "sku": "10WAA9901",  "name": "Facecam Pro",                    "price": 299.99, "category": "Cameras",          "brand": "Elgato"}
E_MIC     = {"product_id": "wave-3",           "sku": "10MAB9901",  "name": "Wave:3 USB Microphone",          "price": 149.99, "category": "Microphones",      "brand": "Elgato"}
E_LIGHT   = {"product_id": "key-light",        "sku": "10GAK9901",  "name": "Key Light",                      "price": 199.99, "category": "Lighting",         "brand": "Elgato"}
E_CAPTURE = {"product_id": "4k60-pro-mk2",     "sku": "10GBE9901",  "name": "4K60 Pro MK.2 Capture Card",    "price": 199.99, "category": "Capture Cards",    "brand": "Elgato"}

def identify(uid, traits, days_ago=0):
    return {"type": "identify", "userId": uid, "traits": traits, "timestamp": ts(days_ago)}

def page(uid, name, days_ago=0, hours_ago=0):
    return {"type": "page", "userId": uid, "name": name, "timestamp": ts(days_ago, hours_ago)}

def viewed(uid, product, days_ago=0, hours_ago=0):
    return {"type": "track", "event": "Product Viewed", "userId": uid,
            "properties": {**product, "quantity": 1}, "timestamp": ts(days_ago, hours_ago)}

def added(uid, product, qty=1, cart_id=None, days_ago=0, hours_ago=0):
    return {"type": "track", "event": "Product Added", "userId": uid,
            "properties": {**product, "quantity": qty, "cart_id": cart_id or uid[:8]},
            "timestamp": ts(days_ago, hours_ago)}

def checkout_started(uid, products, total, days_ago=0, hours_ago=0):
    return {"type": "track", "event": "Checkout Started", "userId": uid,
            "properties": {"order_id": uid[:6].upper() + "01", "value": total, "currency": "USD",
                           "products": [{**p, "quantity": 1} for p in products]},
            "timestamp": ts(days_ago, hours_ago)}

def order_completed(uid, products, total, days_ago=0, hours_ago=0):
    return {"type": "track", "event": "Order Completed", "userId": uid,
            "properties": {"order_id": uid[:6].upper() + "01", "total": total,
                           "revenue": total, "currency": "USD",
                           "products": [{**p, "quantity": 1} for p in products]},
            "timestamp": ts(days_ago, hours_ago)}


# ════════════════════════════════════════════════════════════════════════════
# CORSAIR EVENTS
# ════════════════════════════════════════════════════════════════════════════
print("\n── Corsair events ──")
corsair_events = []

u = "sarah.okafor@gmail.com"   # purchased_at_corsair + high_value_buyer (keyboard $169.99 + mouse $109.99 = $279.98)
corsair_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=10),
    page(u, "Home", days_ago=10),
    viewed(u, C_KEYBOARD, days_ago=10, hours_ago=2),
    viewed(u, C_MOUSE, days_ago=10, hours_ago=1),
    added(u, C_KEYBOARD, days_ago=9, hours_ago=3),
    added(u, C_MOUSE, days_ago=9, hours_ago=2),
    checkout_started(u, [C_KEYBOARD, C_MOUSE], 279.98, days_ago=9, hours_ago=1),
    order_completed(u, [C_KEYBOARD, C_MOUSE], 279.98, days_ago=9),
]

u = "james.whitfield@icloud.com"  # purchased_at_corsair (headset $159.99)
corsair_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=7),
    page(u, "Home", days_ago=7),
    viewed(u, C_HEADSET, days_ago=7, hours_ago=3),
    viewed(u, C_STAND, days_ago=7, hours_ago=2),
    added(u, C_HEADSET, days_ago=6),
    checkout_started(u, [C_HEADSET], 159.99, days_ago=5, hours_ago=2),
    order_completed(u, [C_HEADSET], 159.99, days_ago=5),
]

u = "priya.nair@outlook.com"   # corsair_cart_abandoner
corsair_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=3),
    page(u, "Home", days_ago=3),
    viewed(u, C_COOLER, days_ago=3, hours_ago=4),
    viewed(u, C_KEYBOARD, days_ago=3, hours_ago=3),
    added(u, C_COOLER, days_ago=3, hours_ago=2),
    checkout_started(u, [C_COOLER], 179.99, days_ago=3, hours_ago=1),
    # no order_completed → cart abandoner
]

u = "derek.moss@yahoo.com"     # viewed_corsair_product_no_purchase + corsair_keyboard_shopper
corsair_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=2),
    page(u, "Product List", days_ago=2),
    viewed(u, C_KEYBOARD, days_ago=2, hours_ago=5),
    viewed(u, C_KEYBOARD, days_ago=2, hours_ago=3),
    viewed(u, C_MOUSE, days_ago=2, hours_ago=2),
    # no purchase → viewed_no_purchase
]

# Cross-brand users: send Corsair side
u = "alex.chen@techco.io"      # cross_brand_buyer — Corsair cooler
corsair_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=14),
    viewed(u, C_COOLER, days_ago=14, hours_ago=2),
    added(u, C_COOLER, days_ago=13),
    checkout_started(u, [C_COOLER], 179.99, days_ago=13, hours_ago=1),
    order_completed(u, [C_COOLER], 179.99, days_ago=13),
]

u = "jordan.kim@agency.com"    # cross_brand_buyer + high_engagement — Corsair keyboard
corsair_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=5),
    page(u, "Home", days_ago=5),
    viewed(u, C_KEYBOARD, days_ago=5, hours_ago=4),
    viewed(u, C_MOUSE, days_ago=5, hours_ago=3),
    viewed(u, C_STAND, days_ago=5, hours_ago=2),
    added(u, C_KEYBOARD, days_ago=4),
    checkout_started(u, [C_KEYBOARD], 169.99, days_ago=4, hours_ago=2),
    order_completed(u, [C_KEYBOARD], 169.99, days_ago=4),
]

u = "mia.torres@studio.co"     # any_brand_purchaser — Corsair headset
corsair_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=2),
    viewed(u, C_HEADSET, days_ago=2, hours_ago=3),
    viewed(u, C_STAND, days_ago=2, hours_ago=2),
    viewed(u, C_MOUSE, days_ago=2, hours_ago=1),
    added(u, C_HEADSET, days_ago=1, hours_ago=4),
    checkout_started(u, [C_HEADSET], 159.99, days_ago=1, hours_ago=2),
    order_completed(u, [C_HEADSET], 159.99, days_ago=1),
]

send(CORSAIR_KEY, corsair_events, "Corsair")


# ════════════════════════════════════════════════════════════════════════════
# ELGATO EVENTS
# ════════════════════════════════════════════════════════════════════════════
print("\n── Elgato events ──")
elgato_events = []

u = "chloe.bertrand@gmail.com"  # purchased_at_elgato + elgato_high_value_buyer (camera $299.99)
elgato_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=8),
    page(u, "Home", days_ago=8),
    viewed(u, E_CAMERA, days_ago=8, hours_ago=3),
    viewed(u, E_MIC, days_ago=8, hours_ago=2),
    added(u, E_CAMERA, days_ago=7),
    checkout_started(u, [E_CAMERA], 299.99, days_ago=7, hours_ago=2),
    order_completed(u, [E_CAMERA], 299.99, days_ago=7),
]

u = "marcus.le@proton.me"       # purchased_at_elgato (Stream Deck XL $249.99) + high_value
elgato_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=6),
    viewed(u, E_DECK_XL, days_ago=6, hours_ago=3),
    viewed(u, E_DECK, days_ago=6, hours_ago=2),
    added(u, E_DECK_XL, days_ago=5),
    checkout_started(u, [E_DECK_XL], 249.99, days_ago=5, hours_ago=2),
    order_completed(u, [E_DECK_XL], 249.99, days_ago=5),
]

u = "tariq.hassan@gmail.com"    # elgato_cart_abandoner + stream_deck_interested
elgato_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=4),
    page(u, "Home", days_ago=4),
    viewed(u, E_DECK, days_ago=4, hours_ago=5),
    viewed(u, E_DECK_XL, days_ago=4, hours_ago=4),
    added(u, E_DECK, days_ago=4, hours_ago=2),
    checkout_started(u, [E_DECK], 149.99, days_ago=4, hours_ago=1),
    # no order_completed → cart abandoner
]

u = "nina.volkov@outlook.com"   # microphone_shopper + viewed no purchase
elgato_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=1),
    page(u, "Product List", days_ago=1),
    viewed(u, E_MIC, days_ago=1, hours_ago=6),
    viewed(u, E_MIC, days_ago=1, hours_ago=4),
    viewed(u, E_LIGHT, days_ago=1, hours_ago=2),
    # no purchase
]

# Cross-brand users: Elgato side
u = "alex.chen@techco.io"       # cross_brand_buyer — Elgato mic
elgato_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=10),
    viewed(u, E_MIC, days_ago=10, hours_ago=3),
    viewed(u, E_LIGHT, days_ago=10, hours_ago=2),
    added(u, E_MIC, days_ago=9),
    checkout_started(u, [E_MIC], 149.99, days_ago=9, hours_ago=1),
    order_completed(u, [E_MIC], 149.99, days_ago=9),
]

u = "jordan.kim@agency.com"     # cross_brand_buyer — Elgato Stream Deck + camera
elgato_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=3),
    page(u, "Home", days_ago=3),
    viewed(u, E_DECK, days_ago=3, hours_ago=5),
    viewed(u, E_CAMERA, days_ago=3, hours_ago=4),
    viewed(u, E_CAPTURE, days_ago=3, hours_ago=3),
    added(u, E_DECK, days_ago=2),
    added(u, E_CAMERA, days_ago=2),
    checkout_started(u, [E_DECK, E_CAMERA], 449.98, days_ago=2, hours_ago=2),
    order_completed(u, [E_DECK, E_CAMERA], 449.98, days_ago=2),
]

u = "mia.torres@studio.co"      # any_brand_purchaser — Elgato key light
elgato_events += [
    identify(u, {**USERS[u], "email": u}, days_ago=1),
    viewed(u, E_LIGHT, days_ago=1, hours_ago=5),
    viewed(u, E_MIC, days_ago=1, hours_ago=4),
    viewed(u, E_CAPTURE, days_ago=1, hours_ago=3),
    added(u, E_LIGHT, days_ago=1, hours_ago=2),
    checkout_started(u, [E_LIGHT], 199.99, days_ago=1, hours_ago=1),
    order_completed(u, [E_LIGHT], 199.99, days_ago=1),
]

send(ELGATO_KEY, elgato_events, "Elgato")

print("\n✓ Done. Summary:")
print(f"  Corsair events:  {len(corsair_events)}")
print(f"  Elgato events:   {len(elgato_events)}")
print(f"  Total events:    {len(corsair_events) + len(elgato_events)}")
print("""
Audience coverage:
  Corsair:
    purchased_at_corsair               → sarah, james, alex, jordan, mia
    corsair_high_value_buyer           → sarah (total $279.98)
    corsair_cart_abandoners            → priya
    viewed_corsair_product_no_purchase → derek, priya
    corsair_keyboard_shopper           → derek, jordan

  Elgato:
    purchased_at_elgato                → chloe, marcus, alex, jordan, mia
    elgato_high_value_buyer            → chloe ($299.99), marcus ($249.99), jordan ($449.98)
    elgato_cart_abandoners             → tariq
    stream_deck_interested             → tariq, jordan
    microphone_shopper                 → nina

  Combined:
    cross_brand_buyer                  → alex, jordan
    any_brand_purchaser                → sarah, james, chloe, marcus, alex, jordan, mia
    high_engagement_browser            → derek (3), jordan (6), mia (6), nina (3)
    combined_cart_abandoner            → priya, tariq
    recent_buyer_last_30_days          → all purchasers
""")
