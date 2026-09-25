"""Additional destination seed data: Ahmedabad, Kutch, Jaipur, Varanasi.

Continues the demo dataset beyond Vadodara. Places, artisans and businesses
are representative of real local culture and GI-tagged crafts; timings and
statistics are plausible demo values, not live statistics.
"""

import random
from datetime import datetime, timedelta

from sqlalchemy import text

from ..models import (
    Announcement,
    AudioStory,
    AuthorityAlert,
    Business,
    CommunityReport,
    CrowdData,
    Destination,
    EmergencyFacility,
    Event,
    Experience,
    Festival,
    FootfallData,
    ParkingArea,
    Place,
    Product,
    RoadClosure,
    TourismForecast,
    TransportFacility,
    User,
)

IMG = "https://images.unsplash.com/photo-"
# All IDs verified HTTP 200. The previous 1595850341629 / 1580582933907 /
# 1473470321118 / 1452860606245 IDs returned 404 and were removed.
GATE = IMG + "1524231757912-21f4fe3a7200?auto=format&fit=crop&w=900&q=70"
PALACE = IMG + "1548013146-72479768bada?auto=format&fit=crop&w=900&q=70"
SUNSET = IMG + "1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=70"
WEAVE = IMG + "1519710164239-da123dc03ef4?auto=format&fit=crop&w=900&q=70"
POT = IMG + "1544022613-e87ca75a784a?auto=format&fit=crop&w=900&q=70"
PAINT = IMG + "1551632811-561732d1e306?auto=format&fit=crop&w=900&q=70"
HERO = IMG + "1508737027454-e6454ef45afd?auto=format&fit=crop&w=1200&q=80"


def P(cat, lat, lng, img, cap=1500, **kw):
    """Compact place shorthand; kw carries name/category/period/summary/etc."""
    eff_cap = kw.pop("est_capacity", cap)
    return dict(
        category=cat, lat=lat, lng=lng, est_capacity=eff_cap,
        image_urls=[img, GATE], address="Open street map: city centre", **kw,
    )


def _add_place(db, dest_id, data):
    defaults = dict(
        category="heritage", subcategory="", summary="",
        description="", history="", cultural_significance="", architecture="",
        stories="", traditions="", visiting_info="", address="", entry_fee="Free",
        historical_period="",
        is_hidden=False, is_featured=False, best_time="Morning",
    )
    place = Place(
        destination_id=dest_id,
        image_urls=data.pop("image_urls", []),
        opening_hours=data.pop("opening_hours", {"display": "Open daily 9 AM – 6 PM"}),
        **{**defaults, **data},
    )
    db.add(place)
    db.flush()
    return place


def _story(db, place):
    for lang in ("en",):
        db.add(
            AudioStory(
                place_id=place.id,
                language=lang,
                title=f"{place.name} — Story in English",
                narrative=place.stories or place.history or place.summary,
                duration_sec=min(300, max(45, len(place.history or place.description) * 2)),
            )
        )
    db.flush()


def _add_business(db, dest_id, data):
    defaults = dict(
        owner_id=None, kind="artisan", craft="", craft_type="",
        story="", description="", cultural_significance="", address="", lat=0.0, lng=0.0,
        contact="+91-90000 00000", price_range="₹300 – ₹3,000", established_year="",
        workshop_available=False, status="Open", is_verified=True, featured=False,
    )
    biz = Business(
        destination_id=dest_id,
        image_urls=data.pop("image_urls", [WEAVE]),
        opening_hours=data.pop("opening_hours", {"display": "Open daily 10 AM – 7 PM"}),
        **{**defaults, **data},
    )
    db.add(biz)
    db.flush()
    return biz


def _add_product(db, biz, name, price, unit, material, image=""):
    db.add(Product(business_id=biz.id, name=name, price=price, unit=unit, material=material, image_url=image))


def _add_experience(db, dest_id, biz, title, category, description, duration, price, lat, lng, capacity=20, location=""):
    db.add(
        Experience(
            destination_id=dest_id,
            provider_business_id=biz.id,
            title=title, category=category, description=description,
            location=location, lat=lat, lng=lng,
            duration_minutes=duration, price=price, capacity=capacity,
            image_urls=[POT, GATE],
        )
    )


def _add_events(db, dest_id, festival_id, events):
    for e in events:
        db.add(Event(destination_id=dest_id, **e))
    db.flush()


def _add_facilities(db, dest_id, place_lat, place_lng):
    db.add(ParkingArea(destination_id=dest_id, name="Central visitor parking", lat=place_lat + 0.003, lng=place_lng - 0.002, capacity=160, available=90, is_temporary=False, notes="Main city parking"))
    db.add(ParkingArea(destination_id=dest_id, name="Festival overflow lot", lat=place_lat - 0.004, lng=place_lng + 0.003, capacity=600, available=600, is_temporary=True, notes="Activates on peak event nights"))
    db.add(TransportFacility(destination_id=dest_id, name="Central railway station", kind="rail", lat=place_lat - 0.01, lng=place_lng, details="Mainline connection; 45 min to neighbouring city"))
    db.add(TransportFacility(destination_id=dest_id, name="Local bus / city depot", kind="bus", lat=place_lat + 0.01, lng=place_lng - 0.005, details="Intercity + city buses"))
    db.add(EmergencyFacility(destination_id=dest_id, name="District hospital emergency", kind="hospital", lat=place_lat - 0.008, lng=place_lng + 0.008, phone="108", details="24×7 trauma & emergency"))
    db.add(EmergencyFacility(destination_id=dest_id, name="City police control room", kind="police", lat=place_lat, lng=place_lng, phone="100", details="112 tourist helpline"))
    db.flush()


def _seed_reports(db, dest_id, items):
    res = db.query(User).filter(User.role == "resident").all()
    uid = res[0].id if res else None
    for r in items:
        db.add(CommunityReport(destination_id=dest_id, user_id=uid, image_url="", **r))
    db.flush()


def _seed_announcements(db, dest_id, items):
    for a in items:
        db.add(Announcement(destination_id=dest_id, published_by="admin@demo.com", **a))
    db.flush()


def _history(db, dest_id, places, seed=7):
    """Simulated 60-day footfall + crowd snapshot + forecasts per destination."""
    rng = random.Random(seed + dest_id)
    now = datetime(2026, 9, 19, 10, 0, 0)
    for day in range(60):
        d = now - timedelta(days=day)
        w = 1.22 if d.weekday() >= 5 else 1.06 if d.weekday() == 4 else 0.92
        for p in places:
            cap = p.est_capacity or 1000
            for hour, frac in ((9, 0.06), (11, 0.12), (13, 0.16), (16, 0.2), (18, 0.22), (20, 0.16)):
                db.add(
                    FootfallData(
                        place_id=p.id, destination_id=dest_id,
                        timestamp=d.replace(hour=hour, minute=30),
                        visitor_count=int(cap * frac * w * (0.82 + rng.random() * 0.4)),
                        source="simulation",
                    )
                )
    for p in places:
        cap = p.est_capacity or 1000
        visitors = int(cap * (0.3 + 0.5 * rng.random()))
        level = "low" if visitors < 0.35 * cap else ("moderate" if visitors < 0.62 * cap else ("high" if visitors < 0.85 * cap else "critical"))
        db.add(CrowdData(place_id=p.id, destination_id=dest_id, timestamp=now, level=level, visitor_count=visitors, capacity=cap, source="simulation"))
    for offset in (10, 21, 33, 46):
        d = (now - timedelta(days=offset)).strftime("%Y-%m-%d")
        base = 12000 + rng.randint(-2000, 4000)
        db.add(
            TourismForecast(
                destination_id=dest_id, date=d, event_name="Seasonal baseline",
                expected_visitors=base, expected_peak_start="11:00", expected_peak_end="19:00",
                confidence=0.7, high_footfall_zones=[{"zone": "Zone A — Old City", "expected": round(base * 0.32)}],
                method="heuristic-baseline", is_demo=True,
            )
        )
    db.flush()


def seed_more_destinations(db):
    if db.query(Destination).count() > 1:
        return

    # ------------------------------------------------------------------ AHMEDABAD
    amd = []

    dest2 = Destination(
        id=2, name="Ahmedabad Tourism", tagline="The heritage capital of India, alive and stirring every hour.",
        district="Ahmedabad", state="Gujarat",
        description="A walled city of pol-houses and jalis, of Gandhi's ashram and the world's largest night food street. Ahmedabad was India's first World Heritage City — this is where living heritage, mill history and a modern riverfront share one skyline.",
        image_url=PALACE, center_lat=23.0225, center_lng=72.5714, zoom=12, is_active=True,
    )
    db.add(dest2)
    db.flush()

    for d in [
        P("heritage", 23.0608, 72.5806, GATE, 1200, name="Sabarmati Ashram",
          historical_period="1917 · Mahatma Gandhi", summary="Gandhi's home during the salt march — a living museum of the freedom movement.",
          description="The Sabarmati Ashram (Hriday Kunj) was Mahatma Gandhi's headquarters from 1917 to 1930, from where he began the Dandi Salt March. The ashram courtyard, spinning cottage and Gandhi Smriti library preserve his daily life.",
          history="Gandhi chose the riverbank deliberately: on the edge of the city, near a jail and a crematorium — 'a site where soulful and pleasant surroundings could be had'.",
          cultural_significance="Code-named the 'ashram that launched a nation', its Sabarmati visitor grain is the single-most visited heritage site in Gujarat.",
          architecture="Simple clay-walled huts with tiled roofs, an open prayer shade and the reconstructed Hriday Kunj house with its famous baithak.",
          stories="During the salt march to Dandi, Gandhi suspended the Spinning Wheel God as his design: its triple purpose — self-reliance, unity and non-violence — remains the ashram's refrain.",
          traditions="Monday silence and evening prayer meetings are still observed by the volunteer trust.",
          visiting_info="Closed every Monday for cleaning; entry free.",
          entry_fee="Free", is_featured=True, est_capacity=800),
        P("heritage", 23.1656, 72.6061, PALACE, 900, name="Adalaj Stepwell",
          historical_period="1498 · Rani Rudabai", summary="A five-storey octagonal vav — a water temple carved in Indo-Islamic style.",
          description="The Adalaj Vav is a five-storey, 16.5 m-deep stepwell built in 1498 by Rani Rudabai in memory of her husband. Its carved pillars and niches hold 500+ stone portraits spanning folk, religious and secular life.",
          history="Built to reanimate the water table along the old pilgrim route, it was one of a chain of dosas (rest houses with water) the queens commissioned across Gujarat.",
          cultural_significance="Listed among the 'royal wells of Gujarat', its ventilation shafts and varved spring make it an architectural and hydrological marvel.",
          architecture="Octagonal with Bengali-style chhajjas, sunscreen-aired bays, and a temple-like entry; every soffit is panel-carved.",
          stories="A local legend says Rani Rudabai's fingers were stained red as she blessed each carver — the 'kumkum hand' motif survives in the sculptures.",
          traditions="Beside the well, an annual fair on the waning Kartak moon commemorates the queen's generosity.",
          visiting_info="15 km north of the old city; ASI ticket.", entry_fee="₹25", est_capacity=700),
        P("heritage", 23.0510, 72.5772, GATE, 800, name="Sidi Saiyyed Mosque",
          historical_period="1573 · Sidi Saiyyed", summary="Famous for the 'Tree of Life' — a stone lattice so fine it is called the 'breathed foliation'.",
          description="Built in 1573 by Sidi Saiyyed, a devotee of the Habshi saint, the mosque's western buffer lattice screen features the celebrated jali of ten grilles: a date palm whose radial branches fold into a flaming chatter.",
          history="Commissioned in the last year of the Gujarat Sultanate before Mughal annexation, the mosque stands near the Dilli Gate of the old city.",
          cultural_significance="The Tree of Life jali is among the finest flowering of Gujarati stone craftsmanship and graces the corporate logo of the state of Gujarat and of the Reserve Bank of India.",
          architecture="Two rectangular colonnaded halls; perforated windows with betel-leaf, lotus and acyclic piercing — light spells make the trees daily.",
          stories="Each of the ten stone trees is carved from a single block; the outermost curls preserve the keyhold of the city wall that once embraced the shrine.",
          traditions="Evening azaan still draws a small congregation; photographers gather at golden hour for the jali's shadow play.",
          visiting_info="Beside the Lal Darwaja wholesale market.", entry_fee="Free", est_capacity=600),
        P("heritage", 23.0270, 72.5811, PALACE, 1000, name="Bhadra Fort & Ahmed Shah Gate",
          historical_period="1411 · Sultan Ahmed Shah", summary="The original citadel of Ahmedabad with its clock-towered triple gateway.",
          description="Bhadra Fort, begun in 1411 by Sultan Ahmed Shah, was the royal residence, treasury and civic heart of the city. Its triple gateway is crowned by a clock tower, and the complex houses showcase of the Azad-e-Samad museum galleries.",
          history="Named after the Maratha goddess Bhadra Kali, the fort was expanded by the Nagarsheth (city headman) builders and remains the old city's anchor.",
          cultural_significance="Its courts hosted royal decrees, festivals and today's heritage-promoting museum; the eastern gate features the famous golden 'kangaras'.",
          architecture="Rajasthani-Gujarati fortress with bastions, a deep Mughal gate and an interior stepwell (Amdavad Kuva) beside the royal mosque.",
          stories="Sultans entered the city through Bhadra Gate; later, the British fired cannons from its ramparts during the 1857 revolt.",
          traditions="The city's civic processions still begin around Bhadra Fort precincts.",
          visiting_info="Old city, near Teen Darwaja.", entry_fee="Free", est_capacity=900),
        P("temple", 23.0441, 72.5670, GATE, 700, name="Hutheesing Jain Temple",
          historical_period="1848 · Sheth Hutheesing Kesarisinh", summary="A white marble temple to the 15th Jain tirthankara, ringed by 52 mini-shrines.",
          description="Built in 1848 by mill-owner Sheth Hutheesing Kesarisinh, this marble temple is a superb assembly of Jain temple architecture: a 52-celled salon, torana entries and a mirror-polished sanctum of Dharmanath.",
          history="Its construction was completed by the sheth's widow after his death; the endowment still funds it today.",
          cultural_significance="The temple doubles as the central Jain pilgrimage focus of the city and is a ceremonial site on three major Jain festivals.",
          architecture="Mandapa piers carved with a thousand-armed goddesses and a dome strung with a marang-drop lotus; the mirror-work is embedded in high polish.",
          stories="A geode above the sanctum reflects the celestial body; devotees ring a security bell of the temple treasury's ancient vault.",
          traditions="Jain monks' discourses (pravachan) and the temple's charitable kitchen run daily.",
          visiting_info="Inside a red sandstone 'compound', off Mithakhali Circle; dress-code applies.", entry_fee="Free", est_capacity=650),
        P("culture", 23.0020, 72.6010, SUNSET, 3000, name="Kankaria Lake & Garden",
          historical_period="1451 · Sultan Qutbuddin", summary="A 34-acre lake precinct with a Bal Vatika, dazzling light-and-water show and a narrow-gauge toy train.",
          description="Kankaria Lake, dug in 1451 by Sultan Qutbuddin, is Ahmedabad's 34-hectare recreational heart. The ring promenade, food-junction and a nightly laser-water-music show make it the city's family destination.",
          history="Nine benevolent stepped towers, a zoo grafted by the British, and in 2019 the walled lake became India's first fully solar-irrigated waterpark.",
          cultural_significance="Every December the lake hosts the nine-month International Kite-Reform where lakhs of diyas float at the annual 'Kankaria Carnival'.",
          architecture="The lake is stepped, its walkway planted with 3,000 trees; the Sorsut—the Gai Jali entrance—is a late-Mughal water structure.",
          stories="In the 1990s the shoreline was cleaned and reborn as a 'destination lake'; its toy train now ferries families around the 5.5 km perimeter.",
          traditions="Evening aarti at the lakeside Hanuman temple and the nightly Einstein laser show draw the largest crowds.",
          visiting_info="South-east Ahmedabad; one of the most-visited public spaces in the state.", entry_fee="₹25", est_capacity=4000),
        P("market", 23.0230, 72.5750, POT, 2500, name="Manek Chowk",
          historical_period="1411 · old city square", summary="A bazaar that transforms by the clock: vegetables, gold, then the city's most famous night food street.",
          description="Manek Chowk bustles as flower-and-vegetable market at dawn, a jewellery hub by day, and the overnight 'food street' of Ahmedabad, famed for its khadi mutton, bhuna-palak and the buttermilk-toast counter.",
          history="Named after Saint Maneknath who—by legend—held the rising sun for the city's builders, the square is among the oldest continuously used public plazas in India.",
          cultural_significance="Where the day-tripping tourist and the late-night office-worker eat side by side; the cyberspace city photo of Meh-Tej is taken from the chowk.",
          architecture="Ancient pavilions and the votary of the 15th-century square, flanked by 100-year-old trading 'pol' houses in two, three storeys.",
          stories="The 'Chinese Bowl' vendor bullock-men have served the same stall between the mosque and the square since 1925.",
          traditions="After 9 PM the square's banks of fry-stalls wake; a fixed-order 'famous list' culture persists.",
          visiting_info="Late night within the pedestrian old city.", entry_fee="Free", est_capacity=2200),
        P("heritage", 22.9967, 72.5224, PALACE, 1000, name="Sarkhej Roza",
          historical_period="1451 · Shaikh Ahmed Khattu", summary="'India's Akbar' — a garden-roza complex where Sultan Ahmed Shah's spiritual guide lies buried.",
          description="The Sarkhej Roza is an extensive mosque-tomb-garden complex commemorating the Sufi saint Shah Ahmed Khattu, spiritual preceptor of the Sultans. Its serene tanks once hosted the royal courts.",
          history="Evolved over a century (15th–16th), the complex blended Persian-style pierced screens with local bracketed construction to create the 'Sarkhej style' that later shaped Mughal architecture.",
          cultural_significance="Called 'the third pole of Ahmedabad', it merged civic ritual, water-engineering and marble carving into one integrated whole.",
          architecture="A 5,000-square-ft jalal entry, epigraphic lintels in stone and brick, and an acoustic tile roof piloting sound over water.",
          stories="Emperor Akbar visited the tomb; his royal city-vision is said to have drawn from the roza's stepped governance of tank and garden.",
          traditions="The annual urs of Shaikh Khattu draws devotees from across the state.",
          visiting_info="Now within the city's urban core, at Sarkhej.", entry_fee="Free", est_capacity=850),
        P("culture", 23.0382, 72.5760, SUNSET, 3000, name="Sabarmati Riverfront",
          historical_period="2012 · public riverfront", summary="An 11-km civic riverfront promenade linking Ahmedabad's principal bridges and ghats.",
          description="The Sabarmati Riverfront is an 11 km, linear green spine of parks, plazas, promenades, boating ghats and a butterfly park on the eastern bank that converted the city's neglected riverbed into its signature public space.",
          history="Nine bridges (including the heritage Ellis Bridge) now arch a landscaped river; the France-to-nature wall paths carry 20,000 daily walkers.",
          cultural_significance="The riverfront ties Sabarmati Ashram, the Gandhi bridge and the old city into one continuous cultural promenade.",
          architecture="Terrace-step ghats, tidal weirs and a designed flood-tolerance system; the Atal Ghat amphitheatre hosts events.",
          stories="Its river-crossing insect bridges let butterflies migrate across the water — a tiny design gesture the city celebrates.",
          traditions="Morning aarti at the riverfront ghats and weekend air-shows bring out families.",
          visiting_info="Public promenade; boating at several points.", entry_fee="Free", est_capacity=5000),
    ]:
        amd.append(_add_place(db, 2, d))
    for p in amd:
        _story(db, p)

    amd_artis = [
        _add_business(db, 2, dict(
            name="Matani Pachedi Artists' Cooperative", owner_id=None, kind="artisan",
            craft="Mata ni Pachedi — hand-painted temple cloth (GI)",
            craft_type="ritual textile painting",
            story="Generations of the Chittara family at Vasna paint the Mother Goddess on fabric with bamboo pens and natural dyes, renewing a living legacy of the goddess's cloth.",
            description="Ceremonial Mata ni Pachedi hangings, yard-goods and daily-use printed textiles, painted on khadi and finished with cow-dung seals.",
            cultural_significance="GI-tagged ritual craft of the Vaghari community of the Ahmedabad belt — painted temples that travel.",
            address="Vasna workshop, Ahmedabad", lat=23.0100, lng=72.5550,
            image_urls=[WEAVE, GATE], price_range="₹800 – ₹15,000", established_year="1975",
            workshop_available=True, featured=True),
        ),
        _add_business(db, 2, dict(
            name="Law Garden Bandhani Studio", kind="artisan",
            craft="Bandhani tie-dye (GI)", craft_type="resist-dyed textile",
            story="Dotted, leheriya-striped odhanis from a family that has tied tens of thousands of knots by fingernail since 1952.",
            description="Hand-tied bandhani dupattas, kurtas and leheriya stoles in natural and synthetic colours.",
            cultural_significance="Bandhani is the festive textile of Gujarat; each cluster's dot-grid is a signature of the tying clan.",
            address="Law Garden market lane", lat=23.0440, lng=72.5480,
            image_urls=[WEAVE, PALACE], price_range="₹400 – ₹8,000", established_year="1952", featured=True),
        ),
        _add_business(db, 2, dict(
            name="Calico Revival Double-Ikat", kind="artisan",
            craft="Double-ikat weave revival", craft_type="handloom weaving",
            story="A rare mill-of-ikat atelier recreating the famed double-ikat of the old weavers' quarter, dye-fixed in both warp and weft.",
            description="Modern sarees and yardage in the classic floral and diamond double-ikat motifs; looms on display.",
            cultural_significance="Double-ikat is among the most demanding weaving techniques known; the Calico family revival keeps it alive in the city.",
            address="Raipur, old city", lat=23.0260, lng=72.5790,
            image_urls=[WEAVE, GATE], price_range="₹1,500 – ₹25,000", established_year="1988", workshop_available=True),
        ),
        _add_business(db, 2, dict(
            name="Manek Chowk Brass & Copper Works", kind="artisan",
            craft="Brass & copper utensils", craft_type="metal craft",
            story="Hammer-beaten lotas and thali sets from the Piranha workshops ringing the chowk — the same craftsmen who supply the night-food stalls' kadhai.",
            description="Hand-beaten brass and copper ware: diyas, lotas, thalis, and the iconic 'dhuni' kettles.",
            cultural_significance="The brass street of Ahmedabad is a centuries-old craft precinct tied to the riverfront's founding trade.",
            address="Pirava & Manek Chowk lanes", lat=23.0240, lng=72.5760,
            image_urls=[POT, PALACE], price_range="₹150 – ₹6,000", established_year="1940"),
        ),
        _add_business(db, 2, dict(
            name="House of MG (heritage stay)", kind="hotel",
            craft="Heritage boutique stay", craft_type="hospitality",
            story="A restored 1924 pol-house in the old city turned boutique hotel and community gallery.",
            description="Twelve rooms above the famous garden café, with curated Gujarati decor and guided old-city walks.",
            cultural_significance="Hospitality that funds heritage conservation and employs artists from the pol community.",
            address="Dasdiyapada, old city", lat=23.0287, lng=72.5727,
            image_urls=[PALACE, SUNSET], price_range="₹6,500/night", established_year="1924", status="Open"),
        ),
        _add_business(db, 2, dict(
            name="Riverfront Garden Resort", kind="hotel",
            craft="City resort", craft_type="hospitality",
            story="A green resort on the eastern bank with river views and a weekend bazaar of local craft.",
            description="80 rooms, a riverfront restaurant and a craft courtyard booking bandhani and matani pachedi workshops.",
            cultural_significance="Direct-to-artisan tie-ups keep the crafts' margins with the makers.",
            address="Sabarmati Riverfront East", lat=23.0350, lng=72.5790,
            image_urls=[SUNSET, GATE], price_range="₹5,200/night", established_year="2018", status="Open"),
        ),
    ]
    _add_product(db, amd_artis[0], "Mata ni Pachedi hanging (1×1.5 m)", 3500, "piece", "khadi, bamboo-pen pigments", WEAVE)
    _add_product(db, amd_artis[0], "Pachedi panel (A4)", 900, "piece", "hand-painted cotton", WEAVE)
    _add_product(db, amd_artis[1], "Bandhani Odhani (plain borders)", 1900, "piece", "silk-cotton", WEAVE)
    _add_product(db, amd_artis[1], "Leheriya stole", 900, "piece", "cotton, hand-tied", WEAVE)
    _add_product(db, amd_artis[2], "Double-ikat saree", 9000, "piece", "mulberry silk", WEAVE)
    _add_product(db, amd_artis[3], "Hand-beaten brass diya (set of 6)", 500, "set", "brass", POT)
    _add_product(db, amd_artis[3], "Copper lota (1 l)", 700, "piece", "copper", POT)

    _add_experience(db, 2, amd_artis[0], "Night food & brass street walk", "food", "Manek Chowk from gold bazaar to chai-wallah, ending at the Pirava brass street.", 150, 350, 23.0230, 72.5750, capacity=15, location="Manek Chowk")
    _add_experience(db, 2, amd_artis[1], "Bandhani tying demo & dye day", "workshop", "Tie your own odhani border under the Law Garden studio awning; leave with the fabric.", 240, 1400, 23.0440, 72.5480, capacity=12, location="Law Garden Studio")

    _fet = Festival(
        destination_id=2, name="Uttarayan — Ahmedabad International Kite Festival",
        subtitle="A sky-full of India's largest kite carnival",
        description="From sunrise on January 14, the old city's rooftops blaze with tens of thousands of kites, while the riverfront hosts mammoth kite displays, tukkal battles and food booths for two full days.",
        start_date="2027-01-14", end_date="2027-01-15", status="upcoming",
        expected_visitors=260000, capacity=320000, is_festival_mode=True,
        hero_image_url=SUNSET, schedule_json={"day1": "Sunrise kite-flying · tukkal wars · specials till dusk", "day2": "International theme kites · tightrope & national anthems"},
    )
    db.add(_fet)
    db.flush()
    _add_events(db, 2, _fet.id, [
        dict(name="Riverfront Kite Mela", festival_id=_fet.id, category="festival", description="500-m kite carpet of giant motif kites with food and craft stalls.", location_name="Sabarmati Riverfront", lat=23.0360, lng=72.5750, start_date="2027-01-14", end_date="2027-01-15", start_time="06:30", end_time="18:00", expected_visitors=40000, capacity=50000, required_resources=["Flying zones", "Ambulance cover"], traffic_impact="High", parking_requirements="Riverfront lots"),
        dict(name="Manek Chowk Night Aft-Glow", category="culture", description="Photos, street food and the gold bazaar's candid glow after the kite day.", location_name="Manek Chowk", lat=23.0230, lng=72.5750, start_date="2027-01-14", end_date="2027-01-14", start_time="21:00", end_time="23:30", expected_visitors=8000, capacity=10000, required_resources=["Street closure mgmt"], traffic_impact="Medium", parking_requirements="Old-city walk-ins"),
    ])
    _add_facilities(db, 2, 23.0225, 72.5714)
    _seed_reports(db, 2, [
        dict(category="traffic", title="Toppling traffic at Lal Darwaja jali junction", description="Vehicles jam the Sidi Saiyyed roundabout through rush hours; a cycle of marshals would relieve tourists photographing the mosque.", lat=23.0500, lng=72.5770, status="Reported"),
        dict(category="waste", title="Manek Chowk overnight waste overflow", description="After the night-food hours, chowk bins overflow into the gold-bazaar laneways; an early-morning collection pass is needed.", lat=23.0232, lng=72.5752, status="Under Review"),
    ])
    _seed_announcements(db, 2, [
        dict(category="festival", title="Uttarayan 2027: rooftop rules", body="Civil supplies and BRTS zones are enforced; designated flying zones only on the riverfront. Fire-under 'tukkal' thread wires is prohibited.", important=True),
        dict(category="transport", title="Riverfront promenade timings", body="The eastern promenade gates close for watering at 7:30 PM; walkers are redirected to the western bank after dusk.", important=False),
    ])
    _history(db, 2, amd, seed=11)

    # ------------------------------------------------------------------ KUTCH
    kch = []

    dest3 = Destination(
        id=3, name="Kutch Tourism", tagline="Desert artistry, salt-white horizons and living village crafts.",
        district="Kutch (Bhuj)", state="Gujarat",
        description="The Rann of Kutch is Gujarat's wild frontier — a seasonal desert of salt, camel bells and festival lights, ringed by craft villages where Ajrakh, Rogan, embroidery and bell-metal survive as living family arts.",
        image_url=SUNSET, center_lat=23.2420, center_lng=69.6669, zoom=9, is_active=True,
    )
    db.add(dest3)
    db.flush()

    for d in [
        P("culture", 23.8872, 69.8297, SUNSET, 6000, name="White Rann & Rann Utsav (Dhordo)",
          historical_period="Annual · White desert", summary="The moon-white salt desert of the Great Rann — India's most surreal open-air festival ground.",
          description="The seasonal salt flats of the Great Rann of Kutch turn a glinting white biscuit-crust after the monsoon waters recede. At Dhordo the Rann Utsav erects a transparent tent-city with craft bazaars, folklore stages and desert safaris.",
          history="For millennia the empty rann was a caravan crossing; since 2005 the state has strung its salt into a flagship tourism festival.",
          cultural_significance="The White Rann is the single strongest visual identity of Gujarat's desert culture — weddings, wildlife and craft camps all gather here in the season.",
          architecture="Tent-cities, salt-ridge viewing decks and the iconic moonlight 'White Rann' stage.",
          stories="A 'Desert Challenge' four-wheeler concert, and the nightly folk 'Bharat' till the moon-swallowed hours.",
          traditions="Camel safaris at budge sunrise, a traditional dance stage of Rabari and Mutwa performers, and the 'Rann dev' salt prayers.",
          visiting_info="61 km from Bhuj. Best Nov–Feb; entry at Dhordo checkpost.", entry_fee="₹220", est_capacity=7000),
        P("heritage", 23.2538, 69.6586, PALACE, 900, name="Aina Mahal",
          historical_period="1752 · Rao Lakhpatji", summary="The 'Palace of Mirrors' — a mirror-work kothi built by a prince smitten with Dutch craftsmanship.",
          description="Aina Mahal is a mid-eighteenth-century palace of hand-cut mirror-work, porcelain, and a gold-and-red durbar hall, built during the rule of Rao Lakhpatji who filled it with European arts.",
          history="Its builder, Randra Malam, was trained in India and the Low Countries; the palace's taste literally imported the Baroque into the desert.",
          cultural_significance="Described as a 'Venetian palace in India', it anchors the eight-century Kutch royal story now curated as a living museum.",
          architecture="Mirror-paste inlay, painted wooden ceilings, stucco Bengal decor and the celebrated 'sheesh-ka-bara' effigies.",
          stories="The palace's famous 'Jadau' cabinets were so précised that the drawer runners are cut from a single plank.",
          traditions="The adjoining Prag Mahal complex hosts the state's leading heritage evening.",
          visiting_info="Inside Bhuj fort-sier walled town.", entry_fee="₹50", est_capacity=700),
        P("heritage", 23.2546, 69.6630, PALACE, 1200, name="Prag Mahal",
          historical_period="1879 · Rao Pragmalji II", summary="A Venetian-Gothic durbar palace ringed by one of the few intact royal ramparts in India.",
          description="Prag Mahal, completed in 1879 by Rao Pragmalji II, is a sumptuous Italian-gothic palace whose 45-m bell-tower dominates Bhuj; its hall houses a stunning painted ceiling and royal portraits.",
          history="Its architect Colonel H. St. Clair Wilkins engineered Neo-Renaissance forms with Indian ventilation and an underground water system.",
          cultural_significance="The backdrop of the Shravan-nights royal lamp ceremonies; the fort platform hosts the Kutch royal crest.",
          architecture="Ark roofs, indented towers, a 'gora-style' courtyard and a straight-east mosque-courtyard addition.",
          stories="The 'Prag Vij' coinage of the palace-treasury and the cannon 'Aina' were fired ceremonially on coronations.",
          traditions="A heritage light-and-sound evening runs on winter weekends.",
          visiting_info="Right beside Aina Mahal; steep 4-storey climb to the tower.", entry_fee="₹25", est_capacity=1000),
        P("museum", 23.2535, 69.6677, GATE, 800, name="Kutch Museum",
          historical_period="1877 · State museum", summary="Gujarat's oldest museum — 21 galleries of Kutch's archaeology, woodcraft, embroidery and musical instruments.",
          description="The Kutch Museum (est. 1877) preserves the single best collection of Kachchhi embroidery, illustrated textiles, war tents of the 'Rao', musical instruments and pre-Harappan antiquities from the rann.",
          history="Chartered under the Bhuj municipality, its turn-of-century curation made the desert's crafts legible to the world.",
          cultural_significance="The museum's embroidered shawl and mirror slabs are the definitive scholarly reference for Kutch craft research.",
          architecture="Gothic-revival red brick with a cast-iron verandah and a museum hall floor of gujrati marble inlay.",
          stories="Among the rarities are the world-intact palanquins of the old Rao court and a wooden Ganesh shrine.",
          traditions="Children's-craft mornings run each weekend translating the textiles into build-its.",
          visiting_info="Centre of Bhuj; 45–60 min visit.", entry_fee="₹20", est_capacity=600),
        P("culture", 23.2635, 69.6645, SUNSET, 2000, name="Hamirsar Lake",
          historical_period="17th century · royal tank", summary="The stepped rainwater lake that has quenched Bhuj for 300 years and hosts its kite-boat festival.",
          description="Hamirsar is the picturesque 300-year rainwater lake of Bhuj, fed by a cable-car ridge until modern piping; its palace-facing waterfront lights up with boats during festivals.",
          history="Excavated in the 17th century by Rao Hamirji to secure the palace water, it also fed the town's stepwells.",
          cultural_significance="Recently restored with a zip-line promenade, the lake is Bhuj's civic and wedding venue.",
          architecture="Three stepped ghats with 'vav' channels connecting four village tanks to the lake.",
          stories="Jalakrida — a prince-boat 'bosalling' festival — waxes each monsoon's full moon.",
          traditions="Folk boating and kite-viewing evenings on Rann Utsav weekends.",
          visiting_info="Central Bhuj, opposite the palace area.", entry_fee="Free", est_capacity=1500),
        P("artisans", 23.1586, 69.6419, WEAVE, 1200, name="Bhujodi Craft Village",
          historical_period="Living craft cluster", summary="Hundereds of weaving, emboltery and garment households that keep Kutch's cloth culture knot-taut.",
          description="Bhujodi village is the cotton-and-scarf metropolis of Kutch — its lanes ring with looms and the smell of dye; visitors can commission weaves, watch block printing and buy 100% artisan-direct.",
          history="Weaving households for generations have supplied Kutch's rulers and merchants; today they export to global boutiques.",
          cultural_significance="A living open-air museum of the Kachchhi shawl, the Rabari garment and the Odhni.",
          architecture="Atti courtyards of the 'meghwal' weavers with community 'rutti' kitchens and a tall temple gate.",
          stories="A women's cooperative runs the village experience center; weavers narrate a five-century family lineage.",
          traditions="Cash-warp Friday haat and a tree-shade craft bazaar every weekend.",
          visiting_info="5 km south of Bhuj on the Bhuj-Mandvi road; free entry.", entry_fee="Free", est_capacity=1500),
        P("artisans", 23.0450, 69.8370, POT, 1000, name="Nirona — Rogan & bell-metal village",
          historical_period="Living craft village", summary="One village, three endangered arts: Rogan painting, bell-metal casting and lacquer bangles.",
          description="Nirona houses the global survivors of Rogan — mirror-oil painting with a straight needle — alongside the bell-metal casting of the Luhars and the lacquer 'sakti' bangle makers.",
          history="The Rogan family traces its 400-year craft to Persia; the Luhar and Shilpkar families cast and lacquer in the same courtyards.",
          cultural_significance="With hundred-odd practitioners worldwide, Nirona's arts are UNESCO-watched and GI-adopted.",
          architecture="Village 'haath' (hand) workshops under neem shade beside the Kutch hills.",
          stories="The 'Rogan tree' motif — a spiral of oil-paint — appears in one family signature lineage; it reportedly takes an hour a swirl.",
          traditions="Each morning the artisans prepare pigment; visitors may try a single swirl.",
          visiting_info="~57 km (40 min) from Bhuj; off Mandvi road.", entry_fee="Free", est_capacity=900),
        P("culture", 22.8300, 69.3600, SUNSET, 2500, name="Mandvi Beach & Shipyard",
          historical_period="16th century · port town", summary="A palm-lined Arabian-Sea beach still graced by India's last wooden-ship builders at the old wooden wharf.",
          description="Mandvi's palm-fringed beach faces the Arabian Sea beside the 16th-century royal shipyard that built the 'Ganga' of sailing lore. Today craftsmen still haul out mahogany and teak hulls.",
          history="Mandvi once shipped indigo, salt and timber; the royal yard supplied boats for Haj pilgrims and the navy's early sail.",
          cultural_significance="Among the last indigenous wooden-ship building fronts in India, it is a UNESCO-icons-adjacent craft town.",
          architecture="The coral-pink old Haveli row, the shipyard theodolite ways and the duney beach hugged by dunes.",
          stories="The 'Sabarmati' and 'Maheshwari' square-riggers were laid at these ways.",
          traditions="A camel-riding beach festival at Kartak full moon; shad water currents keep swims within the marker buoys.",
          visiting_info="40 min from Bhuj; beach and yard free.", entry_fee="Free", est_capacity=3000),
        P("culture", 23.2497, 69.6413, GATE, 2000, name="Smritivan Earthquake Memorial",
          historical_period="2001 · memorial", summary="One of the world's largest memorial parks — 13,852 trees for every life lost in the 2001 earthquake.",
          description="Smritivan, a 470-acre hillside memorial-museum complex above Bhuj, dedicates a tree to each of the 13,852 victims of the 2001 Kutch earthquake and presents their stories in a bright earthen museum.",
          history="Opened in 2022 on the 21st anniversary, it is built atop the earthquake's epicentre ridge.",
          cultural_significance="The museum's 80 storytelling caves and the 'earthquake house' make tragedy into pedagogy.",
          architecture="A stepped ridge, marble-stele walk, solar-paled amphitheatre and the fifty-year-old hilltop ruins.",
          stories="At dusk its 13,852 lamps are lit for a minute each.",
          traditions="The memorial holds memorial-light evenings each January 26.",
          visiting_info="Bhuj hills' crown; lift to the observation; free.", entry_fee="Free", est_capacity=2000),
    ]:
        kch.append(_add_place(db, 3, d))
    for p in kch:
        _story(db, p)

    kch_artis = [
        _add_business(db, 3, dict(
            name="Ajrakhpur Ajrakh Blockprinters' Co-op", kind="artisan",
            craft="Ajrakh hand block-printing (GI)", craft_type="block-printed textile",
            story="Descendants of the Khatri printers of Tharparkar flame-print the geometric wonderland of ajrakh using natural indigo, iron and madder on kora cloth.",
            description="Ajrakh stoles, yardage and bed-linen in the classic mallow and jambal patterns; each cloth is 18–20 resist stages.",
            cultural_significance="GI-tagged craft of the Pakistani-Gujarati Khatri lineage; 14-days of washing and cow-dung fixing precede every print.",
            address="Ajrakhpur village, 6 km from Bhujodi", lat=23.1650, lng=69.6450,
            image_urls=[WEAVE, POT], price_range="₹600 – ₹9,000", established_year="1985",
            workshop_available=True, featured=True),
        ),
        _add_business(db, 3, dict(
            name="Rogan Art House of Nirona", kind="artisan",
            craft="Rogan painting (endangered art)", craft_type="oil-lacquer painting",
            story="The Rauf brothers carry an endangered 400-year-old Persian craft: drawing with a single metal needle dipped in boiled oil-paint to bloom mirror-shapes.",
            description="Rogan wall panels, saree borders and the famous 'tree of life'; order-a-piece visits include a live swirl.",
            cultural_significance="Practiced by fewer than 25 people worldwide; the art is protected and GI-tagged.",
            address="Nirona village", lat=23.0450, lng=69.8370,
            image_urls=[PAINT, GATE], price_range="₹300 – ₹30,000", established_year="1975", featured=True),
        ),
        _add_business(db, 3, dict(
            name="Suf Embroidery Kutchi Collective", kind="artisan",
            craft="Kutchi Suf & Rabari embroidery (GI)", craft_type="hand embroidery",
            story="Sisters double-darn mirror and chain motifs shaped by the desert's Ramji pathway — a virtuoso geometric embroidery.",
            description="Embroidered shawls, runal handkerchiefs, garments and cushion covers stitched by the group.",
            cultural_significance="Kutch's embroideries are GI-protected; the Suf 'tappi' stitch counts among the world's densest.",
            address="Aankhiadi now union-workshop in Bhuj", lat=23.2530, lng=69.6680,
            image_urls=[WEAVE, SUNSET], price_range="₹900 – ₹18,000", established_year="1992", featured=True),
        ),
        _add_business(db, 3, dict(
            name="Bhujodi Loom House", kind="artisan",
            craft="Kachchhi shawl weaving", craft_type="handloom",
            story="A generation-born weaver family from Bhujodi's hundered-loom lanes, weaving the seven-inch-gauge desert shawl and indigo guarani weaves.",
            description="Shawls, dhurries and stoles in camel-brown, indigo and green; commissioned by the metre.",
            cultural_significance="Handloom Kutch shawls are a recognition-protected export; the craft uses desert-knit wool.",
            address="Bhujodi village", lat=23.1586, lng=69.6419,
            image_urls=[WEAVE, POT], price_range="₹400 – ₹12,000", established_year="1968", workshop_available=True),
        ),
        _add_business(db, 3, dict(
            name="Nirona Luhar Bell-Metal Foundry", kind="artisan",
            craft="Kutch bell-metal casting", craft_type="metal craft",
            story="The Luhars cast the pilgrim bells that needle-tone across the desert with a hand-run melting of grey and 'lagam' bronze.",
            description="Bell-bronze hemos, diyas, lamps and the famous 'Kutch' bells in five sizes; visits include the tilt-pour thrill.",
            cultural_significance="GI-tagged Kutch bell metal; the ahar cast of 'jhanjhar' anklets travelled the trade routes.",
            address="Nirona village", lat=23.0452, lng=69.8372,
            image_urls=[POT, PALACE], price_range="₹150 – ₹8,000", established_year="1955", workshop_available=True),
        ),
        _add_business(db, 3, dict(
            name="Rann Utsav Tent City", kind="hotel",
            craft="Desert festival stay", craft_type="hospitality",
            story="The iconic luxury tent-city on the White Rann at Dhordo, with handcrafted tents and a folk-lit ambience.",
            description="King-size tents, all-meal buffets, camel safaris, folk stages and the moonlight views of the salt.",
            cultural_significance="Runs on Rann Utsav season (Nov–Feb) with 400+ local staff.",
            address="Dhordo, White Rann", lat=23.8872, lng=69.8297,
            image_urls=[SUNSET, PALACE], price_range="₹12,000/night", established_year="2005", status="Open"),
        ),
        _add_business(db, 3, dict(
            name="Mandvi Coastal Resort", kind="hotel",
            craft="Beach retreat", craft_type="hospitality",
            story="A small palm-grove resort beside Mandvi beach hosting shipyard-watch and craft-hub day trips.",
            description="Cottages, infinity pool, seafood and a courtyard of local embroidery.",
            cultural_significance="Brings visitors to the wooden-shipyard and Nirona-side flows.",
            address="Mandvi beach road", lat=22.8350, lng=69.3600,
            image_urls=[SUNSET, GATE], price_range="₹5,800/night", established_year="2012", status="Open"),
        ),
    ]
    _add_product(db, kch_artis[0], "Ajrakh stole (block silk-cotton)", 1400, "piece", "khadi silk-cotton", WEAVE)
    _add_product(db, kch_artis[0], "Ajrakh bed-cover (double)", 4200, "piece", "khadi cotton", WEAVE)
    _add_product(db, kch_artis[1], "Rogan wall panel (tree)", 12000, "piece", "oil pigment", PAINT)
    _add_product(db, kch_artis[2], "Suf embroidered shawl", 3400, "piece", "wool, mirror, thread", WEAVE)
    _add_product(db, kch_artis[2], "Runal (mirror) handkerchief set", 950, "set of 3", "silk-cotton", WEAVE)
    _add_product(db, kch_artis[3], "Kachchhi shawl (camel wool)", 2600, "piece", "camel wool", WEAVE)
    _add_product(db, kch_artis[4], "Kutch bell (large)", 1400, "piece", "bell bronze", POT)
    _add_product(db, kch_artis[4], "Bell-metal diya pair", 350, "pair", "bell bronze", POT)

    _add_experience(db, 3, kch_artis[2], "Camel safari at White Rann moonrise", "safari", "Moonlight camel ride across the salt to the salt-ridge viewpoint; dinner follows at the Rann field.", 180, 1500, 23.8872, 69.8297, capacity=20, location="Dhordo")
    _add_experience(db, 3, kch_artis[0], "Ajrakh print-your-own stole", "workshop", "Block-print your own ajrakh stole in the Ajrakhpur co-op with a natural indigo dip.", 200, 1800, 23.1650, 69.6450, capacity=12, location="Ajrakhpur")

    _fet = Festival(
        destination_id=3, name="Rann Utsav 2026–27",
        subtitle="Gujarat's desert carnival on the moon-white salt",
        description="From November to February the White Rann hosts India's grandest desert festival: tent-cities, folk galaxies, camel musters, craft make-and-take and the ethereal White Rann musical mausoleum.",
        start_date="2026-11-01", end_date="2027-02-28", status="upcoming",
        expected_visitors=1200000, capacity=1400000, is_festival_mode=True,
        hero_image_url=SUNSET, schedule_json={"flagship": "Monthly 'Full-Moon' packages with folk nights", "craft": "Daily craft make-and-take village", "camel": "Rann fair camel-muster in Nov"},
    )
    db.add(_fet)
    db.flush()
    _add_events(db, 3, _fet.id, [
        dict(name="Full-Moon Folk Nights", festival_id=_fet.id, category="festival", description="At barchha-torch evenings the Rabari and Mutwa musicians perform beside the salt rostrum.", location_name="White Rann stage, Dhordo", lat=23.8872, lng=69.8297, start_date="2026-11-15", end_date="2027-02-12", start_time="19:00", end_time="23:30", expected_visitors=15000, capacity=20000, required_resources=["Stage", "Crowd rail"], traffic_impact="Medium", parking_requirements="Rann-field lots"),
        dict(name="Kutch Fair — Bhuj", category="culture", description="The annual three-day craft bazaar of Bhuj with embroidery and printing stalls.", location_name="Bhuj fairground", lat=23.2420, lng=69.6700, start_date="2026-12-04", end_date="2026-12-06", start_time="09:00", end_time="21:00", expected_visitors=25000, capacity=30000, required_resources=["Craft pavilions"], traffic_impact="Medium", parking_requirements="Fairground lots"),
    ])
    _add_facilities(db, 3, 23.2420, 69.6669)
    _seed_reports(db, 3, [
        dict(category="traffic", title="Bhuj–Dhordo road washout stretch", description="A 2-km patch of the Rann road breaks up after rain; needs surface-repair before the festival shuttle runs.", lat=23.55, lng=69.75, status="Reported"),
        dict(category="overcrowding", title="Rann entry queue bottlenecks", description="At the Dhordo checkpost the queue forms a knot on peak-full-moon weekends; electronic vouchers recommended.", lat=23.8872, lng=69.8297, status="Under Review"),
    ])
    _seed_announcements(db, 3, [
        dict(category="festival", title="Rann Utsav 2026–27 bookings open", body="Full-moon packages and tent-city slots now open; craft make-and-take village badges released weekly.", important=True),
        dict(category="transport", title="Seasonal Bhuj–Dhordo shuttle", body="From Nov 1, a half-hourly shuttle to the White Rann field runs from Bhuj bus depot; last return 1 AM on moon-nights.", important=False),
    ])
    _history(db, 3, kch, seed=21)

    # ------------------------------------------------------------------ JAIPUR
    jpr = []

    dest4 = Destination(
        id=4, name="Jaipur Tourism", tagline="The Pink City — forts, bazaars and centuries of Rajasthani craft.",
        district="Jaipur", state="Rajasthan",
        description="A city planned in 1727 in rose-pink stucco, ringed by ghats, forts and two World Heritage observatories. Jaipur is also India's craft capital — blue pottery, block-printing, gota, zardozi and the famous quilt.",
        image_url=PALACE, center_lat=26.9124, center_lng=75.7873, zoom=12, is_active=True,
    )
    db.add(dest4)
    db.flush()

    for d in [
        P("heritage", 26.9855, 75.8513, PALACE, 8000, name="Amber Fort",
          historical_period="1592 · Man Singh I", summary="The palatial hill-fort of the Kachhawahas, glowing in amber-pink sandstone above Maota Lake.",
          description="Amber Fort, rising above Maota Lake, is the grand Rajput citadel of the 'Pink City's' royal dynasty. Its Sheesh Mahal, Diwan-i-Aam and labyrinth palaces glow with mirror, marble and frescoe inlay.",
          history="Founded in 1592 by Raja Man Singh I and expanded by his successors, the fort held court until Jaipur city took over in 1727.",
          cultural_significance="Elephant-back heritage and the Sheesh Mahal's infinite-mirror fireplace make it Rajasthan's premier tourist magnet.",
          architecture="Crenellated ramparts, a mirrored winter room, the floating garden of the Kesar-Kyari and a ramp rampart cut for artillery.",
          stories="The Sheesh Mahal's 'glass' is actually hand-cut mica mirror; a single flame scatters into 100 reflections.",
          traditions="Evening light-and-sound narration from 7:30 across three languages.",
          visiting_info="11 km from Jaipur city; steep climb by foot or hired palki.", entry_fee="₹100", est_capacity=12000),
        P("heritage", 26.9239, 75.8267, GATE, 6000, name="Hawa Mahal",
          historical_period="1799 · Sawai Pratap Singh", summary="The five-storey 'Palace of Winds' with 953 jharokha windows that let royal ladies watch the city unseen.",
          description="The Hawa Mahal's honeycombed 953-window pink facade commands the 'courtyard road' of the old city — a former royal observatory-window with a frontal rampart of breeze cells.",
          history="Commissioned in 1799 by Maharaja Sawai Pratap Singh, the building channels the crown of the Krishna-topped sun temple.",
          cultural_significance="The emblem of the city's maharaja-era pink architecture; its oblique façade vents cooled the zenana in summer.",
          architecture="A five-storey pyramid of jharokhas sheathed in pink stucco; the rear is a seven-storey void funneling air.",
          stories="Royal women watched processions through the sifs but remained unseen — the chirt of the city's name.",
          traditions="Dawn view from the hill opposite, when the facade catches the first light pink.",
          visiting_info="Old city, entrance from the rear except a museum.", entry_fee="₹50", est_capacity=4000),
        P("heritage", 26.9258, 75.8237, PALACE, 7000, name="City Palace, Jaipur",
          historical_period="1727 · Sawai Jai Singh II", summary="The maharaja's living palace-courtyards: Chandra Mahal, Mubarak Mahal and the museum of royal costume.",
          description="A grand complex of palaces, courtyards and gardens in the walled town's heart. The Buggi Khana and armoury host the famous royal-vehicle and costume collections.",
          history="The city and palace were laid together by Jai Singh II in 1727 following the Sihri treatise of architecture.",
          cultural_significance="A working royal residence, it practices the annual rituals that keep Jaipur's calendar.",
          architecture="Rajput-Mughal courts with a saffron-blue 'Tarun of seventeen' fresco and the notable doorway 'Prataparan'.",
          stories="The 'Shahi Vayu' courtyard hosts the royal guarding of the palm and the sultanate of the 'Dastar'.",
          traditions="The elephant festival, Teej and the March 'Red-light-copies' happen in its grounds.",
          visiting_info="Complete most courtyard way with 1-hr audio guides.", entry_fee="₹70", est_capacity=5000),
        P("heritage", 26.9247, 75.8245, GATE, 4000, name="Jantar Mantar",
          historical_period="1734 · Jai Singh II", summary="A UNESCO observatory of giant masonry instruments — the world's largest stone sundial.",
          description="Jantar Mantar's 19 marble-and-sandstone instruments read the positions of sun, moon and planets between 1734 and 1744. The Samrat Yantra's 27-m gnomon casts a shadow accurate to 2 seconds.",
          history="Jai Singh II built five observatories; Jaipur's is the best preserved and a UNESCO World Heritage site.",
          cultural_significance="As a working science site, guide-led readings of the sun's declination remain a favorite show.",
          architecture="Analemma Bengali parallels, the 27-m Samrat Yantra, and the smaller Misra yantra measuring the four cardinal hours.",
          stories="A summer solstice light ray falls precisely into the Jai Prakash bowl's crosshair.",
          traditions="Solar-noon shadow readings are demonstrated each day at midday sun.",
          visiting_info="Next to City Palace; audio-guide recommended.", entry_fee="₹50", est_capacity=3000),
        P("heritage", 26.9372, 75.8153, PALACE, 3000, name="Nahargarh Fort",
          historical_period="1734 · defence chain", summary="The ridge fort of Jaipur offering the classic sunset view of the Pink City plain.",
          description="Nahargarh ('abode of tigers') guards the western ridge above Jaipur; its madhusile apartments and the pillared Madhvendra Bhavan are restored for cafés and sunset picnics.",
          history="Built in 1734 alongside Jaigarh and Amber to seal the valley; henceforth the three forts 'sentineled' the state.",
          cultural_significance="Its restored royal rooms were a 2019 film location ('Shuddh Desi Romance') — and the sunset balcony is the city's ritual photo.",
          architecture="Lustral cistern pipes, a scalloped 'madhura' bow roof and defensive bastions strung by a walktube.",
          stories="A local spirit 'Nahar' was propitiated to let the walls rise; his name crowns the fort.",
          traditions="Art-bottle and music nights run on festival weekends.",
          visiting_info="On the ridge west of the city; 2-km uphill walk after parking.", entry_fee="₹50", est_capacity=3000),
        P("heritage", 26.9531, 75.8457, SUNSET, 2500, name="Jal Mahal",
          historical_period="1750s · water palace", summary="A five-storey 'Water Palace' floating in Man Sagar Lake — shimmering architectural mirage.",
          description="Jal Mahal is a sandstone hunting-lodge of which four storeys sit below the lake water; its azure reflection and floating contract with the hustle of the local ghats.",
          history="A 1750s renovation of an older lodge created the submerged upper palace above Man Sagar's monsoon fed water.",
          cultural_significance="Iconic across travel media; the lake supports winter migratory birds and a small portico of silts.",
          architecture="Mughal-Rajput with engraved arches, a painted lake-blanking and satkhuni interior unseen unless you boat.",
          stories="Only two floors are visible at low water; a mystery bell tolls from the submerged storey.",
          traditions="Boating and bird-watching evenings at the Mehrauli ghat.",
          visiting_info="On the Ameer-Jaipur road; view best from the nearby hill.", entry_fee="Free (view)", est_capacity=2000),
        P("museum", 26.9119, 75.8193, PALACE, 3500, name="Albert Hall Museum",
          historical_period="1887 · royal museum", summary="Jaipur's premier museum in an Indo-Saracenic confection of domed yellow sandstone.",
          description="The Albert Hall Museum (est. 1887) holds royal arms, carpets, Egyptian mummies and a continent-spanning collection in a turreted hall of many domes.",
          history="Built for the visit of Prince Albert to Rudyard Kipling's design-flair and financed partly by local kunstenz.",
          cultural_significance="The state's largest museum and the cultural hub of the peach gardens.",
          architecture="Indo-Saracenic horseshoe arches, domed yellow-ochre brick and cupolas that chant the City Beautiful plan.",
          stories="A Victorian Egypt room displays a 3000-year-old mummy — an oddity the local guides love.",
          traditions="Friday cultural evenings and the winter need-light shows at the museum gates.",
          visiting_info="In the Ram Niwas Garden; combine with the zoo path.", entry_fee="₹60", est_capacity=2500),
        P("market", 26.9200, 75.8240, POT, 6000, name="Bapu & Johri Bazaar",
          historical_period="1727 · royal markets", summary="The artisan bazaar of the walled city — jewellery, bandhani, gota and more along 2 km of lanes.",
          description="Bapu Bazaar and the diamond-stitch of Johri Bazaar form a living commercial strait of the pink city: lehariya odhanis, zardozi dupattas, meenakari, gota and street chaat.",
          history="Charted by Jai Singh II's planners, the city grid's bazaars were each assigned trades — Johri to the jeweller, Bapu to the retailer.",
          cultural_significance="A buzzing bazaar-craft laboratory: filters block-broidery, and the evening street light picks out gold-lace shops.",
          architecture="Pink-filtered arcades, artisan galleries over the lanes, and the 'Ratan Singh' gold mosque-chowk.",
          stories="Bapu Bazaar's bangles are bought by weight — and the famous 'Sanganeri' printing is done live in courts.",
          traditions="Evening chaat and the 'Gulabi' pink-light festival across December.",
          visiting_info="Walled city; walk from the Chaura Rasta below Hawa Mahal.", entry_fee="Free", est_capacity=5000),
        P("temple", 26.8875, 75.8600, GATE, 4000, name="Galta Ji (Monkey Temple)",
          historical_period="18th century · hill shrines", summary="A stepped-basin temple town with sacred kunds, temple ars, and its famous brazen monkey colony.",
          description="Galta Ji is a sublime group of shrines cut into the gorge east of Jaipur, its sacred spring feeding a chain of kunds (tanks) and its cliffs alive with resident langur monkeys.",
          history="An ancient pilgrimage site refreshed in the 18th century by the Gaur priests for the Narad panel.",
          cultural_significance="The 'Rigveda gate' of high Jaipur; monkeys are the celebrated wardens of the kunds.",
          architecture="Built faces of gorge rock, arcade-lined tanks, and a Brahmkund whose waters never seem to fade.",
          stories="Lying in the sun beside the yellow temple are the monkeys that have made this the 'Monkey Temple' of the world's photos.",
          traditions="A holy dip in the Brahmkund kund is considered both bremere restorative and ceremonial amnesty.",
          visiting_info="East Jaipur; park at the lower ridge and walk up; guard your snacks from the monkeys.", entry_fee="Free", est_capacity=5000),
        P("temple", 26.9046, 75.7990, GATE, 4000, name="Birla Mandir",
          historical_period="1985 · modern marble", summary="A white-marble Ganesha-Vishnu temple of pure Jharakh sanctum on the north-west ridge.",
          description="The Birla Mandir of Jaipur worships Ganesha and Vishnu in snow-white marble, with a painted niche gallery of mythological panel scenes and the evening 'arti' attracting vast crowds.",
          history="Built by the Birlas in 1985 on a rose-garden carpet across from its altar; all cascades of pink are avoided in purity.",
          cultural_significance="The marble 'Lakshmi-Narayan' relief stories and the panoramic view of the city's western ridges.",
          architecture="Beige-marble with twelve panels of Vedic dance and carved plinth of mythological motifs.",
          stories="The temple's design maps a lotus — with 9 domes over the sanctum and 108 small bells.",
          traditions="Evening aarti from 6:30; devotees fill the mandap before dusk.",
          visiting_info="Near Central Park / Bhawani Singh margin; free entry.", entry_fee="Free", est_capacity=3000),
    ]:
        jpr.append(_add_place(db, 4, d))
    for p in jpr:
        _story(db, p)

    jpr_artis = [
        _add_business(db, 4, dict(
            name="Neerja Blue Pottery Atelier", kind="artisan",
            craft="Jaipur blue pottery (GI)", craft_type="glazed ceramic",
            story="The family glaziers of the Vishwakarma quarter still fire the turquoise-and-cobalt pottery born of a Mughal-Turkic glaze—using the stone kajar for the blue.",
            description="Blue-pottery vases, tiles, lamps and tableware; kiln tours and colour-painting days.",
            cultural_significance="GI-protected Jaipur blue pottery, made without clay — a silica dough that 'never cracks like common ceramic'.",
            address="Neerja, Ramganj", lat=26.9200, lng=75.7920,
            image_urls=[POT, GATE], price_range="₹300 – ₹9,000", established_year="1985",
            workshop_available=True, featured=True),
        ),
        _add_business(db, 4, dict(
            name="Sanganeri Blockprint House", kind="artisan",
            craft="Sanganeri hand block-printing (GI)", craft_type="block-printed textile",
            story="Sanganer's printer families low-print the fine floral 'bel-buta' on muslin with metal-and-wood kalam blocks.",
            description="Block-printed bed-linen, kurtas, odhanis and table runs; hourly demos of the four-stage print.",
            cultural_significance="The GI-tagged Sanganeri pattern is the most exported of India's hand-print traditions.",
            address="Sanganer village", lat=26.8330, lng=75.7800,
            image_urls=[WEAVE, POT], price_range="₹450 – ₹6,000", established_year="1970", featured=True),
        ),
        _add_business(db, 4, dict(
            name="Gota Patti Emporia", kind="artisan",
            craft="Gota (Rajasthani applique work)", craft_type="metal-lace applique",
            story="Zari-edged gota strips hand-appliquéd onto odhani and lehengas for weddings — the shimmer of Rajasthani brides.",
            description="Gota dupattas, bralettes, cushion covers and zari-laced celebrate-wear.",
            cultural_significance="Rajasthan's hallmark festival/ornamental craft; GI-tagged variants protect the applique.",
            address="Johri Bazaar front", lat=26.9208, lng=75.8245,
            image_urls=[WEAVE, GATE], price_range="₹500 – ₹20,000", established_year="1964", featured=True),
        ),
        _add_business(db, 4, dict(
            name="Jaipuri Razai Quiltworks", kind="artisan",
            craft="Jaipuri razai (GI)", craft_type="quilted textile",
            story="Feather-light quilts stuffed carded-rubber with a kani-stitch border — the 'cloud-weight' razai of pink-city winters.",
            description="Jaipuri razai in dhussya prints and cotton-blend; four-season weights.",
            cultural_significance="GI-tagged Jaipuri razai, renowned for portability and the flying-feather stuffing.",
            address="Chauhan Rajput workshops, city north", lat=26.9290, lng=75.8060,
            image_urls=[WEAVE, SUNSET], price_range="₹600 – ₹8,000", established_year="1948"),
        ),
        _add_business(db, 4, dict(
            name="Meenakari Artisans Guild", kind="artisan",
            craft="Jaipur meenakari (enamel)", craft_type="enamel jewellery",
            story="Chitra-kar enamelists breathe translucent colour into gold and brass for the bangles and bote of the pink city.",
            description="Meenakari bangles, pendants, bantel boxes and plates with 18–20 colour firings.",
            cultural_significance="With root in the Vijayanagara art, Jaipur stands as the meenakari capital of the North Indian bazaar.",
            address="Johri Bazaar arcade", lat=26.9210, lng=75.8244,
            image_urls=[PAINT, GATE], price_range="₹800 – ₹40,000", established_year="1932", workshop_available=True),
        ),
        _add_business(db, 4, dict(
            name="Rambagh Palace (Heritage Hotel)", kind="hotel",
            craft="Royal palace hotel", craft_type="hospitality",
            story="The maharaja's own garden-palace hotel of 1825, pastel pink with peacock mosaics and palace butlers.",
            description="Suite rooms, the famous royal bar and golf lawns; guide-led palace stories at teatime.",
            cultural_significance="Jaipur's iconic luxury serrement where the Rajput calendar lives on.",
            address="Bhawani Singh Road", lat=26.8791, lng=75.8568,
            image_urls=[PALACE, SUNSET], price_range="₹25,000/night", established_year="1825", status="Open"),
        ),
        _add_business(db, 4, dict(
            name="Chomu Palace Boutique", kind="hotel",
            craft="Fort boutique stay", craft_type="hospitality",
            story="A 17th-century fortified haveli, 45 minutes out, reviving painted 'gajra' fresco walls with village craft pitches.",
            description="Elegant retreat rooms, Rajasthani kitchens and a craft terrace hosting print & pottery days.",
            cultural_significance="Every booking funds a village craft residency.",
            address="Chomu", lat=27.1690, lng=75.7100,
            image_urls=[GATE, PALACE], price_range="₹9,000/night", established_year="1667", status="Open"),
        ),
    ]
    _add_product(db, jpr_artis[0], "Blue pottery vase (medium)", 2200, "piece", "quartz-glaze silica", POT)
    _add_product(db, jpr_artis[0], "Blue pottery tile set (6)", 900, "set", "glazed ceramic", POT)
    _add_product(db, jpr_artis[1], "Sanganeri bed-cover", 2600, "piece", "cotton muslin", WEAVE)
    _add_product(db, jpr_artis[1], "Block-print table runner", 700, "piece", "cotton", WEAVE)
    _add_product(db, jpr_artis[2], "Gota dupatta (bridal)", 4200, "piece", "silk-cotton, zari", WEAVE)
    _add_product(db, jpr_artis[3], "Jaipuri razai (summer)", 1400, "piece", "cotton, carded rubber", WEAVE)
    _add_product(db, jpr_artis[4], "Meenakari bangle pair", 1800, "pair", "brass, enamel", PAINT)

    _add_experience(db, 4, jpr_artis[1], "Sanganer print-your-own apron", "workshop", "Block-print a muslin apron in the Sanganeri house and torch-dry it to take home.", 150, 1200, 26.8330, 75.7800, capacity=15, location="Sanganer")
    _add_experience(db, 4, jpr_artis[0], "Sunrise Amber–Hawa Mahal heritage walk", "heritage walk", "Clock in the pink light: Amber ramparts to Hawa Mahal's jharokha with a storyteller.", 240, 1600, 26.9855, 75.8513, capacity=18, location="Amber Fort")

    _fet = Festival(
        destination_id=4, name="Jaipur Literature Festival 2027",
        subtitle="The world's largest free literary gathering, behind the City Palace gates",
        description="Five days in late January bring 200+ writers, musicians and thinkers to the Diggi Palace lawns — panel sessions, glaude poetry and the famous 'Jaipur nights' of craft bazaars.",
        start_date="2027-01-28", end_date="2027-02-01", status="upcoming",
        expected_visitors=850000, capacity=900000, is_festival_mode=True,
        hero_image_url=PALACE, schedule_json={"format": "8 tented drawing rooms + 1 courtyard main", "feature": "The Gala Readings & Lit Quiz nights"},
    )
    db.add(_fet)
    db.flush()
    _add_events(db, 4, _fet.id, [
        dict(name="Main Podium Sessions (Diggi Palace)", festival_id=_fet.id, category="festival", description="Flagship lecture-theatre sessions with celebrity authors.", location_name="Diggi Palace lawns", lat=26.9130, lng=75.7910, start_date="2027-01-28", end_date="2027-02-01", start_time="10:00", end_time="19:00", expected_visitors=30000, capacity=35000, required_resources=["Tented auditoria", "Security"], traffic_impact="High", parking_requirements="Outer lots + shuttle"),
        dict(name="Craft & Book Bazaar", category="culture", description="Ministry-awarded printers and the bazaar's blue-pottery and gota stalls crowd the courtyard.", location_name="Diggi Palace courtyard", lat=26.9132, lng=75.7912, start_date="2027-01-29", end_date="2027-01-31", start_time="10:30", end_time="20:00", expected_visitors=18000, capacity=20000, required_resources=["Pavilions"], traffic_impact="Medium", parking_requirements="Street + lots"),
    ])
    _add_facilities(db, 4, 26.9124, 75.7873)
    _seed_reports(db, 4, [
        dict(category="traffic", title="Amber-Road Sunday congestion", description="Elephant-stand and tourist traffic overlap on Amber road weekends; timed gating could ease it.", lat=26.9855, lng=75.8510, status="Reported"),
        dict(category="waste", title="Bapu Bazaar night litter", description="Chaat lanes of Bapu Bazaar see litter peaks after 9 PM; extra bins needed for the weekend rush.", lat=26.9201, lng=75.8242, status="Under Review"),
    ])
    _seed_announcements(db, 4, [
        dict(category="festival", title="JLF 2027 registrations open", body="Free badge passes for Diggi Palace sessions go live Nov 1; on-site passes fetchable daily.", important=True),
        dict(category="parking", title="City-centre parking during JLF", body="Parking restricted within 1 km of Diggi; pick-up shuttles run from MI Road from 8 AM.", important=False),
    ])
    _history(db, 4, jpr, seed=31)

    # ------------------------------------------------------------------ VARANASI
    var = []

    dest5 = Destination(
        id=5, name="Varanasi Tourism", tagline="The eternal city — silk, ghats and the sound of sacred aarti.",
        district="Varanasi", state="Uttar Pradesh",
        description="One of the oldest continuously inhabited cities on earth, Varanasi is the spiritual capital of India — threaded with ghats, silk looms, temple bells and the Subah-e-Banaras dawn of music, yoga and rivers.",
        image_url=SUNSET, center_lat=25.3176, center_lng=82.9739, zoom=13, is_active=True,
    )
    db.add(dest5)
    db.flush()

    for d in [
        P("temple", 25.3109, 83.0106, GATE, 5000, name="Kashi Vishwanath Temple",
          historical_period="1780 · restored sanctum", summary="The 'Golden Temple of Varanasi' — Lord Shiva's holiest abode on the Ganges' western bank.",
          description="Kashi Vishwanath is one of the twelve jyotirlingas of Shiva, with a golden dome and a 15.5-m highlight spire. Around it swirl the eternal ghats and the famous Kashi corollary of the Koti-Tirth.",
          history="Destroyed and rebuilt several times — the present temple built by Rani Ahilyabai Holkar in 1780 and given its golden dome by Maharaja Ranjit Singh in 1835.",
          cultural_significance="Every Hindu aspires to 'Kashi yatra'; the sanctuary-yard's lamps outnumber the stars each evening.",
          architecture="Nagara spire, carved marble balcony and the 'Man Sarovar' observation corridor joining the temple to the river.",
          stories="A dip in the Manikarnika and a darshan of Vishwanath are held to complete one's life-journey.",
          traditions="Evening aarti at the adjoining ghat and the 5 AM 'Mangala' service draw the largest congregations.",
          visiting_info="Old city lanes, reached on foot; strict queue system at peak.", entry_fee="Free", est_capacity=20000),
        P("heritage", 25.3068, 83.0104, SUNSET, 8000, name="Dashashwamedh Ghat & Ganga Aarti",
          historical_period="18th century · ritual ghat", summary="Varanasi's grandest ghat — and the nightly fire-lamp aarti that seals the city's drama.",
          description="Dashashwamedh is the river-stage of Varanasi: the venue of the 'Dash-Ashwamedha' legend and, every sundown, the famous priest-coruscating Ganga aarti with towering fire-sceptres and chanted sacred shlokas.",
          history="Named for King Brahma's completion of ten horse-sacrifices; the ghat was built in marble by Hira Lal in 1740 and expanded in 1838.",
          cultural_significance="The aarti plaza (est. 1990s) is among the world's most-watched religious performances.",
          architecture="Terraced stone bays, lamp pylons, and a viewing marble pier lit by 21 flame-sterns.",
          stories="The aarti's seven chamar lamps are raised one by one; the last one sways toward the Ganga's current.",
          traditions="Boats moor off-shore for a 'boat-side' aarti view; the ghat stays alive till the last lit lamp.",
          visiting_info="Approachable by boat from Assi or by the old-city lanes.", entry_fee="Free", est_capacity=15000),
        P("culture", 25.2889, 83.0050, SUNSET, 4000, name="Assi Ghat",
          historical_period="Ancient · riverbank", summary="The poetic sunrise ghat where the Assi meets the Ganga — yogis, birds and dawn boats.",
          description="Assi Ghat, at the southern edge, hosts a nightly subah-e-Banaras cultural plaza of music, plus the sunrise boat makhana meter of rowing lams.",
          history="An ancient bathing circle named for the river Assi's siphon; its 'Subah-e-Banaras' stage revived the art ghat from the 1960s.",
          cultural_significance="Morning boat-lifts, burning ghat-heritage walks and the city's beating art corners.",
          architecture="Terrace steps, a snowfall-white Durga shrine and a needle of the Panch-tirth from the confluence.",
          stories="The poet Kabir is said to have sat a while with those mists at Assi.",
          traditions="Every dawn a fire-temple 'haath' pours riverwise; the evening aarti-lite is smaller than Dashashwamedh but more intimate.",
          visiting_info="Boat wharf; the point where the Assi dahya enters the Ganga.", entry_fee="Free", est_capacity=8000),
        P("heritage", 25.3762, 83.0246, PALACE, 6000, name="Sarnath — Deer Park",
          historical_period="528 BCE · first sermon", summary="Where the Buddha first taught — Ahimsa's cradle with a museum of the lion capital.",
          description="The Deer Park of Sarnath is where the Buddha preached his first sermon, the Dhammacakkappavattana-sutta. The Dhamek Stupa, the Ashokan lion-capital pillar, and the museum's Gupta-era figures define the site.",
          history="A center of the Sangha for 1,500 years until raided in the 12th century; rediscovered by archaeologists in 1836.",
          cultural_significance="India's national emblem — the Sarnath lion capital — was carved here; the Dhamek Stupa binds the world's Buddhist map.",
          architecture="The Dhamek Stupa (34 m) with its carved stones, the Mulagandha Kuti temple and gardens of deer.",
          stories="The deer of the park are direct descendants of the legendary herd that gave the Deer Park its name.",
          traditions="A home for Buddha-purnima gatherings and the revived evening resonances of the monks.",
          visiting_info="10 km north-east of Varanasi; ASI ticket includes the museum.", entry_fee="₹25", est_capacity=6000),
        P("heritage", 25.3115, 83.0148, GATE, 3000, name="Manikarnika Ghat",
          historical_period="Ancient · cremation ghat", summary="The burning ghat where Moksha is sought — Varanasi's oldest and most venerated cremation ground.",
          description="Manikarnika is the sacred cremation ghat of Varanasi. Devotees believe a final pyre here grants moksha; its ghat-steps and endless wood-bundles form the city's most emotionally staggering vista.",
          history="Legend ties the ghat's name to Shiva's earring (manikarnika) which fell here; the temple beside it watches each flame.",
          cultural_significance="The Ganges' ashes here are returned to the river as the classic of Hindu death-ritual.",
          architecture="Dark trampled steps, timber shacks and the famous 'Manikarnika Well' beside the temple.",
          stories="The town's 'eternal fire' is said never to have been extinguished; a day's lot of wood is measured to burn without noise.",
          traditions="Photography is forbidden out of respect; visitors should keep a reverent distance.",
          visiting_info="Approachable by boat for a discreet view.", entry_fee="Free", est_capacity=4000),
        P("heritage", 25.2699, 83.0238, PALACE, 2500, name="Ramnagar Fort & Museum",
          historical_period="1750 · Maharaja Balwant Singh", summary="The sandstone fortress-palace of the Maharaja across the Ganga, with its Durga-throne and rare vintage cars.",
          description="Ramnagar Fort, the ancestral palace of the Maharaja of Banaras, guards the eastern bank with kanji-balks towers, a Durga-trained cannon yard and a museum of royal palanquins, weapons and telescopes.",
          history="Built in 1750 by Maharaja Balwant Singh; the 'Ramnagar-style' palace-complex includes the famous clock with a 'U' face.",
          cultural_significance="The base of the city's great Ramlila (July–Oct) — the folk-epic cycle that covers the town week by week.",
          architecture="Sandstone-and-brick, Mughal arches, mirrored mahal rooms and a steep gate through the river road.",
          stories="Its museum's jade-handled sword was given by Lord Canning to the maharaja.",
          traditions="The annual 'Ramlila' begins here each September with a processional elephant.",
          visiting_info="Across the Ganga bridge/Sarkheswar ferry.", entry_fee="₹20", est_capacity=3000),
        P("temple", 25.3156, 83.0109, GATE, 3000, name="Tulsi Manas Mandir",
          historical_period="1964 · Tulsidas's Ramcharitmanas", summary="The gleaming white temple whose marble walls are engraved with all 12.8k couplets of the Ramcharitmanas.",
          description="Tulsi Manas Mandir commemorates the site where, per tradition, Tulsidas composed the Ramcharitmanas. Its courtyard marble is inscribed with the entire epic and painted panels depict the Ramayana.",
          history="Built in 1964 by a Ramdasia businessman in the modern 'Patan' style on the older temple site.",
          cultural_significance="A bridge between vernacular Hindi and classical Sanskrit devotion — the ghat of the waav for the common reader.",
          architecture="Rectangular hall flanked by sculpted towers and marble-panelled episodes from the epic.",
          stories="Sainte Tulsi grass grows at the site; devotees feel the 'poem' in the structure itself.",
          traditions="Daily recitations and an evening screening of the panel stories.",
          visiting_info="Near Durga Kund, new town.", entry_fee="Free", est_capacity=3000),
        P("temple", 25.2901, 82.9932, GATE, 3500, name="Durga Temple & Kund",
          historical_period="18th century · north Indian", summary="A blood-red shikhara temple of Goddess Durga beside the sacred tank with monkey-vibrant precincts.",
          description="The Durga Temple, crimson-spired in the 'Bengal' north-Indian style, houses the ancient paramount Durga image; its tank is believed to have sprung from Vishnu's left top-knot.",
          history="Blessed by the Maharani of Banaras and restored in the 18th century by the Bhumihar patron family.",
          cultural_significance="Its terracotta pinnacles and monkey courtyard make it the most-photographed of north Varanasi's temples.",
          architecture="Twisted-supra arc, octagonal base tank pavilion and the famous red-sandstone curfalides.",
          stories="Legend holds the tank's waters turn red at Navratri, when the goddess 'bleeds' — a hematite flourish devotees explain variously.",
          traditions="Large Navratri programmes two years in a row; Tuesday fliers fill the courtyard.",
          visiting_info="Beside Tulsi Manas, south of the ghats.", entry_fee="Free", est_capacity=4000),
        P("culture", 25.2680, 82.9910, WEAVE, 5000, name="Banaras Hindu University & Bharat Kala Bhavan",
          historical_period="1916 · Pandit Malviya's university", summary="India's living campus museum — the Bharat Kala Bhavan's ten galleries of classical sculpture and miniature art.",
          description="BHU's grand campus on the south bank hosts the Bharat Kala Bhavan: celebrated sculpture galleries, a treasury of fine arts and the famous 'Malviya' clock-tower quad.",
          history="Founded in 1916 by Madan Mohan Malviya; the arts museum opened in 1920 as one of India's first.",
          cultural_significance="The museum holds Sarnath-era sculpture, Mughal miniatures, Tibetan thankha and the modern art of the Banaras school.",
          architecture="A yellow-and-earthy arc of cloth-work, the Vishwanath new temple spire and the statue of the founder.",
          stories="Its courtyard hosts the March 'Kala Utsav' — the campus's craft-and-music carnival.",
          traditions="The 'Malviya' aarti at the new Vishwanath and the museum's Sunday sketch days.",
          visiting_info="From the university main gate; cycle-rickshaw inside.", entry_fee="₹10", est_capacity=6000),
    ]:
        var.append(_add_place(db, 5, d))
    for p in var:
        _story(db, p)

    var_artis = [
        _add_business(db, 5, dict(
            name="Banarasi Silk Weavers of Madhopatti", kind="artisan",
            craft="Banarasi silk & brocade (GI)", craft_type="handloom silk",
            story="From the jamdani-and-kinkhab looms of Madhopatti, a weaver family plies its sixth-generation craft — real gold-thread kamdani, zari and the famous Kadua buttis.",
            description="Banarasi sarees, dupattas and stoles: katan silk, organza, jamdani and gold 'danak' brocades, order-woven or from the loom floor.",
            cultural_significance="GI-tagged Banarasi brocade is among India's most precious weaves — a signatory of the eternal city.",
            address="Madhopatti, west Varanasi", lat=25.3200, lng=82.9500,
            image_urls=[WEAVE, PALACE], price_range="₹2,500 – ₹95,000", established_year="1962",
            workshop_available=True, featured=True),
        ),
        _add_business(db, 5, dict(
            name="Ganga Meenakari (Gulabi) Studio", kind="artisan",
            craft="Gulabi meenakari (pink enamel) (GI)", craft_type="enamel art",
            story="One of the last Gulabi (pink) meenakari craftsmen of the ghats, painting translucent rose enamel over brass and silver.",
            description="Gulabi boxes, bangle plaques, portrait pendants and painted art panels.",
            cultural_significance="The GI-tagged pink enamel of Varanasi traces to a 19th-century Persian technique kept by three families.",
            address="Brahmanal — Kotwalpura lane", lat=25.3150, lng=83.0070,
            image_urls=[PAINT, GATE], price_range="₹700 – ₹25,000", established_year="1978", featured=True),
        ),
        _add_business(db, 5, dict(
            name="Kashi Wooden Toy Carvers", kind="artisan",
            craft="Kashi wooden toys (GI)", craft_type="wood carving",
            story="Lambs, dancing peacocks and the famous articulating python-toy hand-carved from simul wood with lacquer colours.",
            description="Traditional wood toys, puppets and sacred 'tousa' figurines; lathe-and-lacquer demos.",
            cultural_significance="GI-tagged craft of the Manikarnika wood-turners who have whittled for the temple pilgrim trade.",
            address="Kashiwood, Azamgarh road corner", lat=25.3190, lng=83.0000,
            image_urls=[POT, WEAVE], price_range="₹80 – ₹5,000", established_year="1960", workshop_available=True),
        ),
        _add_business(db, 5, dict(
            name="Kashi Brass & Bell Foundry", kind="artisan",
            craft="Kashi brassware", craft_type="metal casting",
            story="The 'Kashiwala' bell-and-brass turners of the old city cast the temple bells that whisper across the ghats.",
            description="Bells, kunj damru, brass frames and engraved lotas in the classic Banarasi alloy.",
            cultural_significance="Varanasi's temple-bell craft is the un-monotone voice of the city's ritual acoustics.",
            address="Khojwa, old city", lat=25.3120, lng=83.0040,
            image_urls=[POT, GATE], price_range="₹120 – ₹6,000", established_year="1935"),
        ),
        _add_business(db, 5, dict(
            name="Zardozi Artisans of the Gold-Bazaar", kind="artisan",
            craft="Zardozi embroidery (gold-work)", craft_type="hand embroidery",
            story="Gitara and zari court-gauge craftsmen of the old bazaar couch gold-wire motifs on silk for weddings and temple-brooches.",
            description="Zardozi dupattas, temple-thrones, coats and hanging panels; order tours of the wire-beating street.",
            cultural_significance="Zardozi couples gold thread with the temple aesthetic — the 'shuddled' court embroidery of the city.",
            address="Kaldar / Minerva gold bazaar", lat=25.3130, lng=83.0050,
            image_urls=[WEAVE, PAINT], price_range="₹600 – ₹30,000", established_year="1945"),
        ),
        _add_business(db, 5, dict(
            name="BrijRama Palace Heritage Stay", kind="hotel",
            craft="Ghat-side palace hotel", craft_type="hospitality",
            story="A 220-year-old palace on Darbhanga Ghat turned boutique riverfront stay.",
            description="Sikhara-view rooms, rooftop Ganga-view dining and a private boat-keeper for the aarti.",
            cultural_significance="Funds the ghat heritage trust's cleaning of the riverbank terraces.",
            address="Darbhanga Ghat", lat=25.3090, lng=83.0102,
            image_urls=[PALACE, SUNSET], price_range="₹11,000/night", established_year="1800", status="Open"),
        ),
        _add_business(db, 5, dict(
            name="Shivala River Hotel", kind="hotel",
            craft="Riverside boutique", craft_type="hospitality",
            story="A small and storied ghat-side hotel famous for its terrace and somber morning rowing.",
            description="Riverfront rooms with gevegetarian kitchen and private ghat access.",
            cultural_significance="Anchors the Assi ‘Subah-e-Banaras’ cultural corridor.",
            address="Assi Ghat", lat=25.2890, lng=83.0052,
            image_urls=[SUNSET, GATE], price_range="₹6,500/night", established_year="1947", status="Open"),
        ),
    ]
    _add_product(db, var_artis[0], "Banarasi silk dupatta (kinkhab)", 5500, "piece", "mulberry silk, zari", WEAVE)
    _add_product(db, var_artis[0], "Banarasi saree (jed: katan)", 24000, "piece", "katan silk", WEAVE)
    _add_product(db, var_artis[1], "Gulabi box (pendant)", 950, "piece", "brass, pink enamel", PAINT)
    _add_product(db, var_artis[1], "Gulabi portrait panel", 4500, "piece", "brass, enamel", PAINT)
    _add_product(db, var_artis[2], "Dancing peacock wood toy", 400, "piece", "simul wood, lacquer", POT)
    _add_product(db, var_artis[3], "Temple bell (medium)", 1100, "piece", "brass alloy", POT)
    _add_product(db, var_artis[4], "Zardozi brocade coat-set", 8500, "set", "silk, gold-wire", WEAVE)

    _add_experience(db, 5, var_artis[0], "Sunrise boat & Ganga aarti evening", "boat tour", "Watch sunrise from a wooden avatar on the Ganga, then cruise back for a boat-side aarti view at Dashashwamedh.", 300, 1800, 25.3068, 83.0104, capacity=20, location="Assi Ghat")
    _add_experience(db, 5, var_artis[0], "Banarasi loom-floor morning", "workshop", "Walk the Madhopatti loom-floor with a weaver, try a pit-loom throw, and buy direct.", 120, 900, 25.3200, 82.9500, capacity=12, location="Madhopatti")

    _fet = Festival(
        destination_id=5, name="Dev Deepawali 2026",
        subtitle="The festival of 21 ghats lighting a lake of a lakh of lamps",
        description="On the full moon after Diwali, the ghats of Varanasi glow with lakhs of clay lamps and sky-firework archangels, coronated by the great aarti from Dashashwamedh to Assi.",
        start_date="2026-11-15", end_date="2026-11-16", status="upcoming",
        expected_visitors=500000, capacity=550000, is_festival_mode=True,
        hero_image_url=SUNSET, schedule_json={"lamps": "1,00,000 diyas lit at 5:30 PM", "aarti": "Mega aarti with 21 priests from Dashashwamedh", "fireworks": "Sky theatre 8:30 PM"},
    )
    db.add(_fet)
    db.flush()
    _add_events(db, 5, _fet.id, [
        dict(name="21-Ghat Mega Aarti", festival_id=_fet.id, category="festival", description="The city's giant coordinated aarti with 21 priests and boat-burner lines.", location_name="Dashashwamedh to Assi", lat=25.3068, lng=83.0104, start_date="2026-11-15", end_date="2026-11-15", start_time="17:30", end_time="21:00", expected_visitors=120000, capacity=130000, required_resources=["Boat barricades", "Medical"], traffic_impact="High", parking_requirements="Riverfront closures"),
        dict(name="Ghats of Light (lamp rows)", category="festival", description="Lakhs of earthen diyas lit in sequence up the ghat terraces at dusk.", location_name="All ganves ghats", lat=25.3040, lng=83.0100, start_date="2026-11-15", end_date="2026-11-15", start_time="17:00", end_time="20:00", expected_visitors=80000, capacity=90000, required_resources=["Diyas logistics"], traffic_impact="Medium", parking_requirements="Walled-city walk"),
    ])
    _add_facilities(db, 5, 25.3176, 82.9739)
    _seed_reports(db, 5, [
        dict(category="infrastructure", title="Assi-Ghat step lamps out", description="Several step lamps at Assi have failed; the ghat darkens early and walkers slip on the wet stones.", lat=25.2889, lng=83.0051, status="Reported"),
        dict(category="traffic", title="Havelock Road evening concertina", description="Auto and cyclerickshaw gridlock each evening between Godowlia and Dashashwamedh; a one-way sweep would help.", lat=25.3100, lng=83.0090, status="Assigned"),
    ])
    _seed_announcements(db, 5, [
        dict(category="festival", title="Dev Deepawali 2026: ghat closures", body="Riverfront steps from Dashashwamedh to Rajendra Prasad close to private gear 4–10 PM; boat lanes reserve for aarti viewers.", important=True),
        dict(category="transport", title="Godowlia–Dashashwamedh shuttle", body="Mini-bus shuttle from Godowlia toll gate to the ghat every 6 minutes during the festival weekend.", important=False),
    ])
    _history(db, 5, var, seed=41)

    db.flush()
    if db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT setval(pg_get_serial_sequence('destinations', 'id'), (SELECT MAX(id) FROM destinations))")
        )
        db.flush()