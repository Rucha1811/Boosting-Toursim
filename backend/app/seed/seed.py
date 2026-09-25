"""Demo seed data for Vadodara (Baroda), Gujarat.

Everything here is openly labelled as demonstration data. Places, artisans,
businesses and events are representative of real local culture; timings and
statistics are plausible demo values, not live statistics.
"""
import random
from datetime import datetime, timedelta

from ..core.database import Base, SessionLocal
from ..core.security import hash_password
from ..models import (
    AlternativeRecommendation,
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
    TransportFacility,
    User,
)

from .more_destinations import seed_more_destinations


from . import photos as _photos


def _normalize_seed_images(db):
    """Guarantee: every image points at a real, verified photograph.

    Falls back to the generated SVG art if the photo pass cannot complete, so
    an image always exists either way.
    """
    try:
        n = _photos.restore(db)
        db.flush()
        return n
    except Exception as _e:  # never let a decorative concern fail a seed
        db.rollback()
        print(f"photo normalize skipped: {_e}")
        try:
            from .img_gen import apply as _apply_themed_images

            _apply_themed_images(db)
            db.flush()
        except Exception:
            db.rollback()
        return 0


dest_id = 1
DEMO_PASSWORD = "demo1234"


def seed_all():
    db = SessionLocal()
    try:
        if db.query(Destination).count() > 0:
            return
        if db.bind.dialect.name == "postgresql":
            # Postgres sequences are non-transactional: a previously rolled-back
            # seed leaves id sequences advanced, so a fresh DB isn't actually
            # id-starting-at-1. Reset everything so literal id references hold.
            from sqlalchemy import text

            for table in Base.metadata.sorted_tables:
                db.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
        _seed_users(db)
        _seed_destination(db)
        _seed_places(db)
        _seed_businesses(db)
        _seed_experiences(db)
        _seed_festival_and_events(db)
        _seed_facilities(db)
        _seed_reports(db)
        _seed_announcements_and_alerts(db)
        _seed_history(db)
        _seed_recommendation(db)
        seed_more_destinations(db)
        _normalize_seed_images(db)
        db.commit()
    finally:
        db.close()


def is_seeded() -> bool:
    db = SessionLocal()
    try:
        return db.query(Destination).count() > 0
    finally:
        db.close()


from ..services import classifier


def train_classifier_from_reports():
    db = SessionLocal()
    try:
        samples = [
            (r.description, r.category) for r in db.query(CommunityReport).limit(200).all()
        ]
        if samples:
            classifier.train(samples)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def _seed_users(db):
    pw = hash_password(DEMO_PASSWORD)
    db.add_all(
        [
            User(email="tourist@demo.com", password_hash=pw, name="Aarav Mehta", role="tourist", verified=True, avatar_url=""),
            User(email="resident@demo.com", password_hash=pw, name="Sneha Patel", role="resident", verified=True, avatar_url=""),
            User(email="artisan@demo.com", password_hash=pw, name="Ramesh Rathwa", role="artisan", verified=True, avatar_url=""),
            User(email="business@demo.com", password_hash=pw, name="Kalpana Khatri", role="business", verified=True, avatar_url=""),
            User(email="admin@demo.com", password_hash=pw, name="Tourism Officer — Vadodara", role="authority_admin", verified=True, avatar_url=""),
            User(email="officer@demo.com", password_hash=pw, name="Anita Desai", role="authority_officer", verified=True, avatar_url=""),
            User(email="priya@demo.com", password_hash=pw, name="Priya Joshi", role="tourist", verified=True),
            User(email="vivek@demo.com", password_hash=pw, name="Vivek Shah", role="resident", verified=True),
        ]
    )
    db.flush()


# ---------------------------------------------------------------------------
# Destination
# ---------------------------------------------------------------------------

def _seed_destination(db):
    db.add(
        Destination(
            id=dest_id,
            name="Vadodara Tourism",
            tagline="Discover the culture. Support the community. Manage tourism intelligently.",
            district="Vadodara",
            state="Gujarat",
            description=(
                "Vadodara — the 'Sanskari Nagari' — is a living museum of Maratha and "
                "British-era heritage, UNESCO-listed Sultanate architecture, world-class "
                "museums, living craft traditions and the world's largest participatory "
                "folk dance, Garba. This platform connects visitors with the people who "
                "keep that culture alive."
            ),
            image_url="https://images.unsplash.com/photo-1568602471122-7832951cc4c5?auto=format&fit=crop&w=1200&q=80",
            center_lat=22.3072,
            center_lng=73.1812,
            zoom=13,
        )
    )
    db.flush()


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------

def _add_place(db, **kwargs):
    defaults = dict(
        destination_id=dest_id, category="heritage", subcategory="", summary="",
        description="", history="", cultural_significance="", architecture="",
        stories="", traditions="", visiting_info="", address="", entry_fee="Free",
        is_hidden=False, is_featured=False,
    )
    p = Place(
        image_urls=kwargs.pop("image_urls", []),
        opening_hours=kwargs.pop("opening_hours", {"display": "Open daily 9 AM – 6 PM"}),
        **{**defaults, **kwargs},
    )
    db.add(p)
    db.flush()
    return p


def _seed_places(db):
    IMG = "https://images.unsplash.com/photo-"
    places = [
        dict(
            name="Laxmi Vilas Palace",
            category="heritage",
            historical_period="1890 · Maharaja Sayajirao Gaekwad III",
            summary="One of the largest private residences in the world and the heart of Baroda's royal heritage.",
            description=(
                "The Laxmi Vilas Palace was commissioned by Maharaja Sayajirao Gaekwad III in 1890 and "
                "designed by British architect Charles Mant in the Indo-Saracenic style. Four times the size "
                "of Buckingham Palace, it remains the residence of the royal Gaekwad family."
            ),
            history=(
                "Built at a reported cost of ₹6 million during the golden age of Baroda state, the palace symbolised "
                "the progressive vision of Sayajirao III — an emperor who made primary education compulsory in his "
                "state a decade before the rest of India."
            ),
            cultural_significance="Its Darbar Hall houses the famous M. F. Husain triptych and a remarkable collection of Gaekwad family arts.",
            architecture="Indo-Saracenic with an octagonal tower, Italian marble, stained glass, and ornate columns blending Gujarati, Mughal and European motifs.",
            stories="The private golf course was built so Sayajirao could play without leaving the palace grounds — it remains functional today.",
            traditions="The palace hosts the annual Navratri at its grounds and cultural evenings through the winter season.",
            visiting_info="The Maharaja Fateh Singh Museum and the Loyola Hall art gallery are part of the palace complex.",
            address="Vizlibai, Palace Road, Moti Baug",
            lat=22.2948, lng=73.1907, est_capacity=6000,
            is_featured=True, entry_fee="₹200 (museum)",
            image_urls=[IMG + "1580582933907-f2e4b0a2e8a5?auto=format&fit=crop&w=900&q=70", IMG + "1473470321118-50e9d1e4e1f2?auto=format&fit=crop&w=900&q=70"],
            audio=True,
        ),
        dict(
            name="Champaner-Pavagadh Archaeological Park",
            category="heritage",
            historical_period="8th–16th century · UNESCO 2004",
            summary="A UNESCO World Heritage site crowning an ancient volcanic hill — capital of the Gujarat Sultanate.",
            description=(
                "Perched on Pavagadh hill, this vast heritage park preserves the 16th-century capital of the "
                "Chauhan Rajputs and Gujarat Sultanate, including forts, palaces, stepwells and exquisite "
                "Indo-Islamic mosques."
            ),
            history="Visited by the Byzantine traveller Ibn Battuta and later the site where Mahmud Begada shifted his capital, 1348 steps lead to the Kalika Mata temple atop the hill.",
            cultural_significance="The only complete, unchanged Sultanate capital in the world — a testament to Gujarat's medieval architecture.",
            architecture="More than 100 monuments spanning Hindu and Islamic styles, crowned by the Jami Masjid with its ten domes and 124 ornate pillars.",
            stories="Many visitors describe the dawn ascent of Pavagadh as a pilgrimage in itself, with panoramic views across the Panchmahal countryside.",
            traditions="The Kalika Mata shrine draws pilgrims through the year; the hill is a living religious site above an ancient archaeological city.",
            visiting_info="About 45 km from Vadodara. Allow a full day; the hill ascent involves climbing the historic 1,348 steps or a ropeway.",
            address="Champaner, Panchmahal district",
            lat=22.4867, lng=73.5367, est_capacity=12000,
            is_featured=True, entry_fee="₹50 (park)",
            image_urls=[IMG + "1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=900&q=70", IMG + "1441974231531-c6227db76b6e?auto=format&fit=crop&w=900&q=70"],
            audio=True,
        ),
        dict(
            name="Sayaji Baug (Kamati Baug)",
            category="garden",
            historical_period="1879 · Maharaja Sayajirao III",
            summary="One of the largest gardens in western India, home to a museum, aquarium and planetarium.",
            description="A 113-acre riverside garden laid out on the Vishwamitri river, abounding with century-old trees and family evening life.",
            history="Commissioned by Sayajirao Gaekwad III in 1879 and designed by William Goldring, the garden was intended as 'a park for everyone'.",
            cultural_significance="Embedded within it are the Baroda Museum & Picture Gallery (1894) and the Kirti Stambh, blending recreation with culture.",
            architecture="Formal Victorian-era landscaping crossed with tropical avenues; the museum building is an early Saracenic revival structure.",
            visiting_info="Best at dawn and on weekends; the aquarium is popular with families.",
            address="Sayaji Baug, Vishwamitri riverfront",
            lat=22.3009, lng=73.1862, est_capacity=20000,
            is_featured=True, entry_fee="₹10",
            image_urls=[IMG + "1470770903676-69b98201ea1c?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Baroda Museum & Picture Gallery",
            category="museum",
            historical_period="1894 · Gaekwad era",
            summary="Marble Vishnu statues, Mughal miniatures and a celebrated European art collection.",
            description="Founded by Maharaja Sayajirao III, the museum houses over 7,000 artefacts including rare Chinese and Japanese jade, ancient coins and a renowned gallery of European masters.",
            history="Designed by Robert Chisolm after a British museum model, it was enriched by Sayajirao's world travels and the family's art patronage.",
            cultural_significance="One of the finest small museums in India — a cultural bridge between Baroda's royal collection and the global arts.",
            architecture="Venetian Gothic with Saracenic flourishes in deep stone.",
            visiting_info="Closed on Wednesdays. Photography is restricted inside the galleries.",
            address="Inside Sayaji Baug",
            lat=22.2998, lng=73.1877, est_capacity=2500,
            entry_fee="₹20",
            image_urls=[IMG + "1519338381661-deb4d4b1e9a4?auto=format&fit=crop&w=900&q=70"],
            audio=True,
        ),
        dict(
            name="Maharaja Fateh Singh Museum",
            category="museum",
            historical_period="1961 · palace museum",
            summary="Royal paintings by Raja Ravi Varma and European artworks inside the palace complex.",
            description="Housed in the Laxmi Vilas Palace complex, this museum exhibits the royal collection including the celebrated works of Raja Ravi Varma, commissioned by Sayajirao III.",
            history="The building was originally the palace school; converted to a museum in 1961.",
            cultural_significance="Raja Ravi Varma's oils here are among the most culturally formative images of Hindu mythology ever painted.",
            visiting_info="Combined entry with the palace grounds.",
            address="Palace complex, Moti Baug",
            lat=22.2957, lng=73.1934, est_capacity=1800,
            entry_fee="₹100",
            image_urls=[IMG + "1519225421980-715cb0215aed?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="EME Temple (Shiv Mandir)",
            category="temple",
            historical_period="1966 · modern sacred architecture",
            summary="A unique geodesic-dome temple devoted to Lord Shiva — pure geometry in devotion.",
            description="Built by the Corps of Engineers using the principles of geodesic dome construction, the EME temple draws devotees and architecture lovers alike.",
            history="Conceived by the Indian Army's Electrical & Mechanical Engineering Corps in 1966, the prayer hall uses no horizontal beams.",
            cultural_significance="Demonstrates how modern engineering serves sacred tradition — proof that innovation and reverence can co-exist.",
            architecture="A 100-foot domed structure supported only by its perimeter — a landmark of geometric architecture.",
            stories="Its dome is shaped so that every point on the outer surface keeps the structure standing — teachings, marble idols and a serene ambience draw daily visitors.",
            visiting_info="Open from early morning aarti to night aarti; modest dress is appreciated.",
            address="EME Road, Fatehgunj",
            lat=22.2879, lng=73.1764, est_capacity=1500,
            image_urls=[IMG + "1584556812952-a9c0cb2ce02e?auto=format&fit=crop&w=900&q=70"],
            audio=True,
        ),
        dict(
            name="Mandvi Gate",
            category="history",
            historical_period="1907 · gateway to the walled city",
            summary="The grand clock-tower gate that marked the old walled city's southern entrance.",
            description="One of the six historic gates of Vadodara, topped by a working clock tower, Mandvi Gate anchors the old city's busy bazaars.",
            history="Completed in 1907 to commemorate the visit of the Prince of Wales, it once regulated entry into the walled city where royal processions began.",
            cultural_significance="A daily meeting point for the city — where old-city commerce, street food and colonial-era civic pride collide.",
            traditions="The surrounding lane, Kansara Bazaar, is a living brass and copper market unchanged in structure for a century.",
            address="Mandvi, Old City",
            lat=22.2969, lng=73.2052, est_capacity=8000,
            image_urls=[IMG + "1548013144-25a5d58323fc?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Nyay Mandir (BMC House)",
            category="history",
            historical_period="1932 · civic heritage",
            summary="The grand court building at Kalaghoda — a landmark of civic architecture.",
            description="Built by Maharaja Sayajirao on his 70th birthday to foster justice accessible to all, Nyay Mandir houses civic administration and courts.",
            history="Dedicated in 1932, Jain builder Vithhaldas Mangaldas sheathed the building in fine grey stone at the Maharaja's insistence.",
            cultural_significance="Its placement facing the city square reflected a belief that justice should stand at the centre of public life.",
            architecture="A symmetrical Indo-Saracenic structure with a commanding central dome and classical colonnades.",
            address="Kalaghoda Circle",
            lat=22.3095, lng=73.1812, est_capacity=6000,
            image_urls=[IMG + "1524678292122-44c67f1a9e5f?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Sevasi Vav",
            category="history",
            historical_period="18th–19th century · stepwell",
            summary="A graceful multi-storey stepwell on Vadodara's western edge.",
            description="An ornate stepwell (vav) built for water storage and cool rest-stops, decorated with carved pillars and niches.",
            history="Stepwells like Sevasi Vav once provided the city's water, sustained pilgrims and served as cool community retreats.",
            cultural_significance="A surviving monument to traditional Gujarati water architecture and community engineering.",
            visiting_info="Quiet and off the main tourist trail — ideal for an unhurried visit.",
            address="Sevasi, west Vadodara",
            lat=22.3315, lng=73.0592, est_capacity=900,
            is_hidden=True,
            image_urls=[IMG + "1596494293740-08f3f2ff32a1?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Sursagar Lake",
            category="landmark",
            historical_period="18th century · Gaekwad era",
            summary="The sacred lake hosting the towering 120-ft Shiva statue and nightly spotlights.",
            description="A step-banked lake built during the Gaekwad era, now the city's landmark evening destination with a colossal white Shiva at its centre.",
            history="The 120-foot statue of Lord Shiva installed at the lake (2005) flows from Vadodara's deep Lingayat traditions.",
            cultural_significance="A living water body at the heart of festival life — Deepotsav celebrations ring the lake each Diwali.",
            visiting_info="Best viewed at sunset when the statue is dramatically lit.",
            address="Raopura Road",
            lat=22.3182, lng=73.1725, est_capacity=15000,
            image_urls=[IMG + "1518709268805-4e9042af9f23?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Nazarbaug Palace",
            category="history",
            historical_period="1861 · royal residence",
            summary="The royal residence and secretariat building east of the old city.",
            description="Completed in 1861, Nazarbaug served as a royal residence and the state's administrative secretariat.",
            history="Legend holds the palace was named 'Naaz' (grace) for the beloved queen it was initially intended to please.",
            cultural_significance="Bridging the walled city and the Laxmi Vilas era, it marks Vadodara's transition into a modern state.",
            address="Nazarbaug",
            lat=22.2935, lng=73.2100, est_capacity=2500,
            image_urls=[IMG + "1561538026-3baa4a7f1f1e?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Kirti Mandir",
            category="temple",
            historical_period="1936 · birthplace of Sri Aurobindo",
            summary="The quiet birthplace temple of Sri Aurobindo, set beside a graceful lotus pool.",
            description="The austere white Greek-style temple marks the birthplace of Sri Aurobindo, with his writing desk and personal effects preserved inside.",
            history="Built in 1936 by the citizens of Baroda in memory of the yogi and freedom philosopher who began his spiritual journey here.",
            cultural_significance="A place of quiet pilgrimage for thinkers and devotees from across the world.",
            visiting_info="Dress modestly; meditation is encouraged in the serene gardens.",
            address="Sigra Road",
            lat=22.3075, lng=73.1856, est_capacity=1200,
            image_urls=[IMG + "1526403591628-5b42e3c00116?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Tambekar Wada",
            category="culture",
            historical_period="19th century · heritage residence",
            summary="The lace-like wooden family mansion of poet Kavi Shastri — now a living cultural venue.",
            description="A beautiful 19th-century wooden haveli in the old city, now a cultural centre hosting poetry, theatre and classical music evenings.",
            history="Belonged to Kavi Shastri, the court poet of Sayajirao III; later developed as Baroda's cultural landmark.",
            cultural_significance="Symbolises Vadodara's tradition of art patronage and the city's affectionate tag, Kala-nagari (city of arts).",
            address="Old City",
            lat=22.3079, lng=73.1831, est_capacity=1000,
            image_urls=[IMG + "1531482615713-2afd69097998?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Kansara Bazaar",
            category="market",
            historical_period="living · brass & copper lane",
            summary="A narrow lane of hereditary brass and copper craftsmen beneath Mandvi Gate.",
            description="An open-air workshop where thakar (hammer-beaten) brass and copper vessels are shaped by hand, as they have been for generations.",
            cultural_significance="One of India's last living brass-market lanes, feeding export and wedding trade from a few quiet metres of street.",
            visiting_info="Best visited mid-morning when the craftsmen are at their benches.",
            address="Mandvi, Old City",
            lat=22.2964, lng=73.2045, est_capacity=4000,
            is_hidden=True, category_main="market",
            image_urls=[IMG + "1555005390-2b75f4c2a0c4?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Sone Ni Chhavni",
            category="market",
            historical_period="living · goldsmiths' street",
            summary="The heritage goldsmith's lane of the old city, gleaming with 'Kala and Khichadi' gold.",
            description="A storied street where hereditary goldsmiths craft the distinctive half-portrait (Kala) gold ornaments for which Baroda was renowned.",
            cultural_significance="Embodies the old city's fine craftsmanship and its marriage, in legend and jewellery, to the Gaekwad court.",
            visiting_info="Karva Chauth and wedding seasons bring special evening bustle.",
            address="Old City",
            lat=22.2988, lng=73.2030, est_capacity=3000,
            is_hidden=True,
            image_urls=[IMG + "1598971302040-3c0d8f1dd3f7?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Ajwa Nimeta Lake & Gardens",
            category="garden",
            historical_period="1960s · green reservoir",
            summary="The 'garden of five thousand trees' and second water source of the city.",
            description="A lakeside greenspace with a reservoir temple, boating and dramatic gates built as a gift from Maharaja Malhar Rao — a favourite weekend escape.",
            cultural_significance="A green lung of Vadodara where the old city comes to picnic, pray and marvel.",
            visiting_info="Best before 10 AM for cool walks along the lake edge.",
            address="Ajwa Road, ~15 km from centre",
            lat=22.2027, lng=73.2132, est_capacity=5000,
            image_urls=[IMG + "1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=70"],
        ),
        dict(
            name="Makarpura Palace",
            category="heritage",
            historical_period="1870 · Gaekwad hunting lodge",
            summary="A soaring Tuscan-arched palace built for hunting-season retreats.",
            description="Built in Italianate style by Maharaja Khanderao, Makarpura Palace shows Europe's influence within Baroda's royal imagination.",
            visiting_info="View from the outside; the palace remains in guarded use.",
            address="Makarpura, east Vadodara",
            lat=22.2494, lng=73.2272, est_capacity=800,
            is_hidden=True,
            image_urls=[IMG + "1520250497591-112f2f40a3f4?auto=format&fit=crop&w=900&q=70"],
        ),
    ]
    for p in places:
        p.pop("category_main", None)
        audio = p.pop("audio", False)
        place = _add_place(db, **p)
        if audio:
            _seed_audio_story(db, place)


def _seed_audio_story(db, place: Place):
    narratives = {
        "Laxmi Vilas Palace": "This palace, raised in 1890 for Maharaja Sayajirao the Third, is four times the size of the royal residence in London. Its tower, its stained glass and its golf course all tell the story of a ruler who modernised a state while guarding its culture.",
        "Champaner-Pavagadh Archaeological Park": "Marco Polo's world described Pavagadh as a city without equal. Today its thirteenth storeys of fortifications, its stepped wells and its mosque with a hundred and twenty four pillars form a UNESCO world heritage park that travellers must climb, step by step, to truly read.",
        "Baroda Museum & Picture Gallery": "Within these Victorian halls rest the treasures that Sayajirao gathered from across the world — marble wonders, ancient coins and paintings that shaped how India imagined its gods.",
        "EME Temple": "Built by the army's engineers in nineteen sixty six, this temple is a dome of pure geometry. No beams support it — only devotion and mathematics, standing as one.",
    }
    for lang, title in (("en", "Story in English"), ("hi", "कहानी हिंदी में"), ("gu", "વાર્તા ગુજરાતીમાં")):
        narrative = narratives.get(place.name, place.history or place.summary)
        db.add(
            AudioStory(
                place_id=place.id,
                language=lang,
                title=f"{place.name} — {title}",
                narrative=narrative,
                duration_sec=min(300, max(45, len(narrative) * 2)),
            )
        )
    db.flush()


# ---------------------------------------------------------------------------
# Businesses & artisans
# ---------------------------------------------------------------------------

def _add_business(db, **kwargs):
    defaults = dict(
        destination_id=dest_id, owner_id=None, kind="artisan", craft="", craft_type="",
        story="", description="", cultural_significance="", address="", lat=0.0, lng=0.0,
        image_urls=[], opening_hours={"display": "Open daily 10 AM – 7 PM"},
        contact="+91-98654 00000", price_range="₹200 – ₹2,000", established_year="",
        workshop_available=False, status="Open", is_verified=True, featured=False,
    )
    b = Business(**{**defaults, **kwargs})
    db.add(b)
    db.flush()
    return b


def _add_product(db, business, price, name, unit, material="", image="", description=""):
    db.add(Product(business_id=business.id, name=name, price=price, unit=unit, material=material, image_url=image, description=description))
    db.flush()


def _seed_businesses(db):
    IMG = "https://images.unsplash.com/photo-"

    # -- Artisans ----------------------------------------------------------
    artisan_user = db.query(User).filter(User.email == "artisan@demo.com").first()

    beadwork = _add_business(
        db,
        name="Putlibai Beadwork Collective",
        owner_id=artisan_user.id,
        kind="artisan",
        craft="Bead & mirror work (Motibharat)",
        craft_type="traditional embroidery craft",
        story=(
            "From the village of Bekar, a collective of thirty women hand-stitch lakhs of beads and "
            "tiny mirrors into odhani borders and festive garments — a craft passed through mothers for generations."
        ),
        description="Authentic motibharat textiles: odhanis, dupattas, cushion covers and festival wear, each piece requiring three to six weeks of handwork.",
        cultural_significance="Beadwork is the signature craft of the Vadodara belt, synonymous with bridal Gujarat.",
        address="Bekar village workshops + city showroom, Alkapuri",
        lat=22.3135, lng=73.1789,
        image_urls=[IMG + "1519710164239-da123dc03ef4?auto=format&fit=crop&w=900&q=70"],
        workshop_available=True,
        price_range="₹800 – ₹12,000",
        established_year="1998",
        featured=True,
    )
    for name, price, unit in (
        ("Motibharat Odhani", 4800, "piece"),
        ("Mirror-work Dupatta", 2400, "piece"),
        ("Embroidered Cushion Set", 1200, "set of 2"),
        ("Beaded Jewellery Jar", 900, "piece"),
    ):
        _add_product(db, beadwork, price, name, unit, material="glass beads, mirror, silk")

    pottery = _add_business(
        db,
        name="Gotri Kumhar Pottery Studio",
        kind="artisan",
        craft="Terracotta pottery",
        story="The Kumhar potters of Gotri still turn the same river clay their ancestors did — shaping matki, kulhads and festival diyas on clacking wheels.",
        description="Live pottery demos and hands-on workshops; earthenware kitchenware and decorative terracotta.",
        cultural_significance="Pottery is among Gujarat's oldest crafts; the Gotri wheel tradition is a link to Harappan-era claywork.",
        address="Gotri village, west Vadodara",
        lat=22.3100, lng=73.1276,
        image_urls=[IMG + "1452860606245-08befc0ff44b?auto=format&fit=crop&w=900&q=70"],
        workshop_available=True,
        price_range="₹100 – ₹1,500",
        established_year="1972",
        featured=True,
    )
    for name, price, unit in (("Hand-thrown Matki (water pot)", 350, "piece"), ("Ember-painted Kulhad Set", 220, "set of 6"), ("Terracotta Diyas Box", 150, "box of 10")):
        _add_product(db, pottery, price, name, unit, material="terracotta clay")

    pithora = _add_business(
        db,
        name="Ramesh Rathwa — Pithora Wall Art",
        owner_id=artisan_user.id,
        kind="artisan",
        craft="Pithora tribal painting",
        story=(
            "Married to 'Bado Pithora', the god who rides a horse, Ramesh paints ritual walls for the Rathwa "
            "tribal community and now carries the art to city walls across Gujarat."
        ),
        description="Commissioned wall pieces, canvas paintings and wedding pithora rituals painted with natural mineral colours.",
        cultural_significance="Pithora painting is the ritual art of the Chhota Udepur-Vadodara tribal belt, made to request blessings from the divine.",
        address="Studio near Chhani; works by appointment",
        lat=22.3510, lng=73.1900,
        image_urls=[IMG + "1580136576312-09cbc57b85e6?auto=format&fit=crop&w=900&q=70"],
        workshop_available=True,
        price_range="₹1,500 – ₹25,000",
        established_year="2005",
        featured=True,
    )
    for name, price, unit in (("Canvas Pithora (small)", 3500, "piece"), ("Wall Panel Commission", 9000, "per panel"), ("Pithora Bookmark Set", 250, "set of 4")):
        _add_product(db, pithora, price, name, unit, material="natural mineral pigments")

    oil = _add_business(
        db,
        name="Ravivari Canvas — Oil Painting Atelier",
        kind="artisan",
        craft="Traditional oil painting",
        story="Descendants of Baroda's famous pujari-painters keep alive an unbroken lineage of sacred oil portraiture that began with Ravi Varma's contemporaries.",
        description="Commissioned devotional oils, framed replicas of the Gaekwad court's masterworks and pigment workshops.",
        cultural_significance="The Ravi family's paintings of gods and darbars seeded Baroda's identity as the city of fine arts.",
        address="Kalaghoda lane, old city",
        lat=22.3082, lng=73.1800,
        image_urls=[IMG + "1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=900&q=70"],
        price_range="₹2,000 – ₹60,000",
        established_year="1960",
    )
    for name, price, unit in (("Framed Devotional Oil", 6000, "piece"), ("Miniature Darbar Scene", 9000, "piece")):
        _add_product(db, oil, price, name, unit, material="oil on canvas")

    bells = _add_business(
        db,
        name="Bhuraj Bell Foundry",
        kind="artisan",
        craft="Brass & bronze bell casting",
        story="The bell-makers of Bhuraj have cast temple bells India-wide for three centuries, hand-finishing each bell's unique tone.",
        description="Temple bells, elephant bells and miniature souvenir bells, each tuned by hand.",
        cultural_significance="Vadodara's bell foundries once supplied sound for Indian temples from Kashmir to Kanyakumari.",
        address="Bhuraj, south Vadodara",
        lat=22.2772, lng=73.1823,
        image_urls=[IMG + "1506150284243-f9c7520c44c6?auto=format&fit=crop&w=900&q=70"],
        price_range="₹300 – ₹8,000",
        established_year="1870",
    )
    _add_product(db, bells, 1500, "Hand-tuned Temple Bell (small)", "piece", material="bell metal")
    _add_product(db, bells, 650, "Souvenir Bell", "piece", material="brass")

    embroidery = _add_business(
        db,
        name="Manek Embroidery House",
        kind="artisan",
        craft="Gujarati folk embroidery & gota",
        story="Three generations of the Manek family stitch kathi, heer bharat and gota patti — the glittering lace-foil embroidery of festive Gujarat.",
        description="Bridal gota, panel embroidery, patchwork quilts and custom heer bharat work.",
        cultural_significance="Gujarati embroidery is one of eight crafts the state has promoted to UNESCO recognition.",
        address="Raopura, old city",
        lat=22.3180, lng=73.1760,
        image_urls=[IMG + "1534498513598-1a16c142f9d3?auto=format&fit=crop&w=900&q=70"],
        price_range="₹500 – ₹15,000",
        established_year="1988",
    )
    _add_product(db, embroidery, 900, "Gota Patti Border Set", "set", material="zardozi wire, satin")
    _add_product(db, embroidery, 2600, "Embroidered Panel (kathi)", "panel", material="cotton, mirror")

    # -- Food ---------------------------------------------------------------
    _add_business(
        db,
        name="Sanjay Sev Usal House",
        kind="food",
        craft="Sev usal — Vadodara's signature street food",
        story="Sev usal is Baroda's own crush of spicy dried-pea curry under a mountain of sev — this famous old-city counter has served it since 1978.",
        description="Sev usal, dabeli, ghughra and fresh lime; the lunchtime 'sev usal thali' is a local institution.",
        cultural_significance="Sev usal originated in the old city's Sindhi and Gujarati kitchens and is the pride of Baroda's street food.",
        address="Opp. Mandvi Gate",
        lat=22.2972, lng=73.2048,
        image_urls=[IMG + "1547576440-41467e3e23ae?auto=format&fit=crop&w=900&q=70"],
        status="Open",
        price_range="₹40 – ₹150",
    )
    _add_business(
        db,
        name="Vishala — Gujarati Village Dhaba",
        kind="restaurant",
        story="A village-style dining experience where thalis are served on low tables with paachhadi songs — a favourite of tourists and locals alike.",
        description="Unlimited Gujarati thali with undhiyu, dal-bhaat, seasonal shaak and jaggery desserts in a lantern-lit courtyard.",
        cultural_significance="Celebrates and sustains the agro-food heritage of the region's traditional kitchens.",
        address="Ajwa Road, ~5 km from centre",
        lat=22.2820, lng=73.1320,
        image_urls=[IMG + "1533777857889-4be7c70b33f7?auto=format&fit=crop&w=900&q=70"],
        price_range="₹350 – ₹600",
        status="Open",
    )
    _add_business(
        db,
        name="Maharaja Farsan",
        kind="food",
        story="A heritage farsan (snack) shop selling hand-puffed gathiya, khakhra, chakli and seasonal specialities since 1954.",
        description="Fresh gathiya, dholka, khakhra and Namkeen gift boxes.",
        address="Champaner Gate Road",
        lat=22.3045, lng=73.1985,
        image_urls=[IMG + "1601050690597-943f08d8d905?auto=format&fit=crop&w=900&q=70"],
        price_range="₹60 – ₹400",
    )

    # -- Hotels / homestays -------------------------------------------------
    _add_business(
        db,
        name="Welcomhotel Vadodara",
        kind="hotel",
        story="Full-service hotel in Alkapuri with a rooftop pool and palace-inspired interiors.",
        description="196 rooms; business and leisure amenities; 5 minutes to Sayaji Baug.",
        address="Warasiya Road, Alkapuri",
        lat=22.3140, lng=73.1740,
        image_urls=[IMG + "1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=70"],
        price_range="₹5,500 / night",
        status="Open",
    )
    _add_business(
        db,
        name="Express Hotel",
        kind="hotel",
        story="A comfortable mid-range hotel right behind Vadodara Junction — ideal base for heritage walks.",
        description="140 rooms; station pickup; rooftop restaurant.",
        address="Sayajigunj",
        lat=22.3130, lng=73.1840,
        image_urls=[IMG + "1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=900&q=70"],
        price_range="₹2,400 / night",
        status="Open",
    )
    _add_business(
        db,
        name="Darbargadh Heritage Homestay",
        kind="homestay",
        story="Sleep inside a restored 1905 walled-city wada with original teak pillars and family hosts.",
        description="6 rooms; family-cooked Gujarati meals; guided old-city walks included.",
        address="Old City, near Tambekar Wada",
        lat=22.3085, lng=73.1825,
        image_urls=[IMG + "1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=900&q=70"],
        price_range="₹2,000 / night incl. meals",
        status="Open",
    )
    _add_business(
        db,
        name="Nilkanth Nilayam Homestay",
        kind="homestay",
        story="Lake-view rooms by Sursagar run by a family of history teachers.",
        description="4 rooms; rooftop breakfast over the lake and the Shiva statue.",
        address="Raopura, off Sursagar",
        lat=22.3194, lng=73.1710,
        image_urls=[IMG + "1571896349842-33c89424de2d?auto=format&fit=crop&w=900&q=70"],
        price_range="₹1,600 / night",
        status="Open",
    )

    # -- Guides -------------------------------------------------------------
    _add_business(
        db,
        name="Pratik Barot — Heritage Walk Leader",
        kind="guide",
        story="A walking-tour leader born in the walled city, Pratik narrates Baroda's gates, palaces and food stories with a storyteller's ease.",
        description="Walled City heritage walks, ghost-story lanes, and palace histories for small groups.",
        contact="+91-97123 44412",
        lat=22.2990, lng=73.2030,
        image_urls=[IMG + "1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=900&q=70"],
        price_range="₹800 / walk (up to 8)",
        status="Open",
    )
    _add_business(
        db,
        name="Daksha Trivedi — Culture & Craft Guide",
        kind="guide",
        story="An artisan-relations officer turned guide, Daksha arranges studio visits and tells the craftsmen's stories with respect.",
        description="Craft-trail walks, museum deep-dives and Chhota Udepur day trips.",
        contact="+91-98244 33190",
        lat=22.3135, lng=73.1885,
        image_urls=[IMG + "1580136576312-09cbc57b85e6?auto=format&fit=crop&w=900&q=70"],
        price_range="₹1,200 / half-day",
        status="Open",
    )

    # Business portal owner
    biz_user = db.query(User).filter(User.email == "business@demo.com").first()
    _add_business(
        db,
        name="Kalpana's Handmade Studio",
        owner_id=biz_user.id,
        kind="workshop",
        craft="Crafted gifts & kundan accessories",
        story="Founded by Kalpana Khatri, the studio makes kundan jewellery and gift work with apprentice artisans and runs weekend craft circles.",
        description="Kundan sets, gift hampers and craft workshops for visitors.",
        address="Alkapuri",
        lat=22.3125, lng=73.1765,
        image_urls=[IMG + "1522337360788-8b13dee7a37e?auto=format&fit=crop&w=900&q=70"],
        workshop_available=True,
        price_range="₹300 – ₹3,500",
        status="Open",
    )


# ---------------------------------------------------------------------------
# Experiences
# ---------------------------------------------------------------------------

def _add_experience(db, **kwargs):
    x = Experience(destination_id=dest_id, image_urls=kwargs.pop("image_urls", []), **kwargs)
    db.add(x)
    db.flush()
    return x


def _seed_experiences(db):
    IMG = "https://images.unsplash.com/photo-"
    guide_walk = db.query(Business).filter(Business.name.like("%Pratik Barot%")).first()
    craft_guide = db.query(Business).filter(Business.name.like("%Daksha Trivedi%")).first()
    pottery = db.query(Business).filter(Business.name.like("%Gotri Kumhar%")).first()
    pithora = db.query(Business).filter(Business.name.like("%Ramesh Rathwa%")).first()
    studio = db.query(Business).filter(Business.name.like("%Kalpana%")).first()

    _add_experience(
        db,
        title="Walled City Heritage Walk",
        category="heritage",
        provider_business_id=guide_walk.id if guide_walk else None,
        description="Walk the six gates of old Vadodara — Mandvi, brass markets, hidden havelis and street-food stops — narrated by a local storyteller.",
        location="Mandvi Gate, start point",
        lat=22.2969, lng=73.2052,
        duration_minutes=150, price=800, price_note="includes chai & sev usal stop",
        availability="Weekends 8 AM; private weekdays by request",
        capacity=12,
        image_urls=[IMG + "1531482615713-2afd69097998?auto=format&fit=crop&w=900&q=70"],
        featured=True,
    )
    _add_experience(
        db,
        title="Royal Laxmi Vilas Palace Tour",
        category="heritage",
        description="Guided tour of the palace's Darbar Hall, M. F. Husain triptych, the Fateh Singh Museum and the royal golf course.",
        location="Laxmi Vilas Palace",
        lat=22.2948, lng=73.1907,
        duration_minutes=90, price=300, price_note="excludes entry tickets",
        availability="Daily 10 AM – 4 PM",
        capacity=20,
        image_urls=[IMG + "1580582933907-f2e4b0a2e8a5?auto=format&fit=crop&w=900&q=70"],
        featured=True,
    )
    _add_experience(
        db,
        title="Pottery at Gotri — Hands-on Wheel",
        category="craft workshop",
        provider_business_id=pottery.id if pottery else None,
        description="Throw your own matki or diya at the living Kumhar wheel; the studio fires and posts your pieces home.",
        location="Gotri Pottery Studio",
        lat=22.3100, lng=73.1276,
        duration_minutes=120, price=400,
        availability="Tue–Sun, 10 AM & 4 PM batches",
        capacity=10,
        image_urls=[IMG + "1452860606245-08befc0ff44b?auto=format&fit=crop&w=900&q=70"],
    )
    _add_experience(
        db,
        title="Pithora Painting Workshop",
        category="craft workshop",
        provider_business_id=pithora.id if pithora else None,
        description="Learn the symbols and mineral-pigment method of tribal pithora wall painting with a master painter, and take home your own panel.",
        location="Chhani studio",
        lat=22.3510, lng=73.1900,
        duration_minutes=180, price=600,
        availability="By appointment, weekends",
        capacity=8,
        image_urls=[IMG + "1580136576312-09cbc57b85e6?auto=format&fit=crop&w=900&q=70"],
    )
    _add_experience(
        db,
        title="Gujarati Cooking & Thali Evening",
        category="food",
        provider_business_id=studio.id if studio else None,
        description="Cook undhiyu, dal and soft rotlis with a Baroda family, then dine together over a full thali with seasonal shaak and dessert.",
        location="Alkapuri residential kitchen",
        lat=22.3125, lng=73.1765,
        duration_minutes=150, price=700,
        availability="Weekdays 6 PM; max 8 guests",
        capacity=8,
        image_urls=[IMG + "1533777857889-4be7c70b33f7?auto=format&fit=crop&w=900&q=70"],
    )
    _add_experience(
        db,
        title="Garba Evening Experience",
        category="cultural",
        description="Learn garba and dandiya steps with a folk troupe, then join the crowd under the lights during Navratri season.",
        location="Navratri Mahotsav grounds, Gotri",
        lat=22.3330, lng=73.1281,
        duration_minutes=120, price=450, price_note="donation to the troupe",
        availability="Navratri season (Oct 11–20)",
        capacity=40,
        image_urls=[IMG + "1508737027454-e6454ef45afd?auto=format&fit=crop&w=900&q=70"],
    )
    _add_experience(
        db,
        title="Champaner–Pavagadh Heritage Day Trip",
        category="heritage",
        provider_business_id=craft_guide.id if craft_guide else None,
        description="Full-day guided exploration of the UNESCO park — forts, the Jami Masjid, stepwells and the Pavagadh summit ropeway.",
        location="Departure: Sayaji Baug Gate 1",
        lat=22.3010, lng=73.1862,
        duration_minutes=480, price=1500, price_note="AC car + guide, entry not included",
        availability="Daily 7:30 AM",
        capacity=4,
        image_urls=[IMG + "1470770903676-69b98201ea1c?auto=format&fit=crop&w=900&q=70"],
        featured=True,
    )


# ---------------------------------------------------------------------------
# Festival & events
# ---------------------------------------------------------------------------

def _seed_festival_and_events(db):
    festival = Festival(
        destination_id=dest_id,
        name="Navratri Mahotsav 2026",
        subtitle="Nine nights of Garba — the world's largest participatory folk dance",
        description=(
            "Vadodara is the Garba capital of Gujarat. For nine nights from 11 October 2026, the city's maidaans "
            "and lanes fill with lakhs of dancers in resplendent chaniya-choli, encircling the clay garbo under "
            "festoon lights. The platform tracks footfall, parking and road access so the festival runs safely."
        ),
        start_date="2026-10-11",
        end_date="2026-10-20",
        status="upcoming",
        expected_visitors=75000,
        capacity=100000,
        is_festival_mode=True,
        hero_image_url="https://images.unsplash.com/photo-1508737027454-e6454ef45afd?auto=format&fit=crop&w=1200&q=80",
        schedule_json={
            "daily flow": "Puja 6:00 PM · Garba 7:30 PM · Dandiya 9:00 PM · Aarti 10:30 PM",
            "ashtami": "Maha Ashtami Maha Puja & Kanya Pujan — Oct 19",
            "finale": "Vijayadashami — Oct 20",
        },
    )
    db.add(festival)
    db.flush()

    events = [
        dict(
            name="Main Garba Nights — Gotri Mahotsav Grounds",
            festival_id=festival.id,
            category="festival",
            description="The flagship ticketed garba: organised raas, celebrity singers and a 10,000-capacity ground.",
            location_name="Gotri Navratri Grounds",
            lat=22.3330, lng=73.1281,
            start_date="2026-10-11", end_date="2026-10-20", start_time="18:00", end_time="00:30",
            expected_visitors=42000, capacity=50000,
            required_resources=["Security 240", "Medical 3 ambulances", "Shuttle fleet 40", "Water points"],
            traffic_impact="High", parking_requirements="1500 dedicated + 800 temporary",
        ),
        dict(
            name="Street Garba — Old City Lanes",
            festival_id=festival.id,
            category="festival",
            description="Open, free, participatory garba on the lamp-lit lanes around Mandvi Gate.",
            location_name="Mandvi Gate & old city",
            lat=22.2969, lng=73.2052,
            start_date="2026-10-11", end_date="2026-10-20", start_time="19:30", end_time="23:30",
            expected_visitors=12000, capacity=15000,
            required_resources=["Traffic diversion", "Fire safety", "Public address"],
            traffic_impact="Medium", parking_requirements="Street closures 6 PM–11 PM",
        ),
        dict(
            name="Dandiya Raas Arena — Police Maidan",
            festival_id=festival.id,
            category="festival",
            description="Ticketed dandiya arena with choreographed raas and guest folk troupes.",
            location_name="Police Maidan, Sayajigunj",
            lat=22.3154, lng=73.1729,
            start_date="2026-10-13", end_date="2026-10-18", start_time="19:00", end_time="23:30",
            expected_visitors=8000, capacity=9000,
            required_resources=["Security 90", "Bleacher seating", "First-aid"],
            traffic_impact="Medium", parking_requirements="Alkapuri parking + shuttle",
        ),
        dict(
            name="Women's Garba Collective — United Way",
            festival_id=festival.id,
            category="festival",
            description="A women-led garba circle devoted to preserving the pure Gujarati raas form.",
            location_name="United Way Grounds, Navapura",
            lat=22.3260, lng=73.1900,
            start_date="2026-10-11", end_date="2026-10-19", start_time="19:00", end_time="23:00",
            expected_visitors=5000, capacity=6000,
            required_resources=["Volunteers 60", "Segregated queues"],
            traffic_impact="Low", parking_requirements="Nearby street parking",
        ),
        dict(
            name="Deepotsav — Diwali Lights at Sursagar",
            category="cultural",
            description="Diwali eve: lakhs of clay diyas ring Sursagar lake with a laser-and-drone show and cultural stage.",
            location_name="Sursagar Lake",
            lat=22.3182, lng=73.1725,
            start_date="2026-11-07", end_date="2026-11-07", start_time="18:00", end_time="23:00",
            expected_visitors=25000, capacity=30000,
            required_resources=["Crowd barricades", "150 volunteers", "Boat safety"],
            traffic_impact="High", parking_requirements="Temporary lots at Kirti Stambh",
        ),
        dict(
            name="Uttarayan — Vaishali International Kite Festival",
            category="festival",
            description="Vadodara's skyline fills with kites; a dedicated park hosts kite-flying craft and food booths.",
            location_name="Vaishali Park grounds",
            lat=22.3220, lng=73.1580,
            start_date="2027-01-14", end_date="2027-01-15", start_time="06:30", end_time="17:00",
            expected_visitors=18000, capacity=20000,
            required_resources=["Flying zones", "Ambulance cover", "Parking 400"],
            traffic_impact="Medium", parking_requirements="School grounds overflow parking",
        ),
        dict(
            name="Gandhi Jayanti Heritage Lecture & Walk",
            category="heritage",
            description="A morning heritage walk linking the sites of Baroda's freedom movement.",
            location_name="Kirti Mandir lawns",
            lat=22.3075, lng=73.1856,
            start_date="2026-10-02", end_date="2026-10-02", start_time="07:00", end_time="10:30",
            expected_visitors=600, capacity=900,
            required_resources=["Guides 6", "PA system"],
            traffic_impact="Low", parking_requirements="On-street",
        ),
    ]
    for e in events:
        db.add(Event(destination_id=dest_id, **e))
    db.flush()


# ---------------------------------------------------------------------------
# Facilities
# ---------------------------------------------------------------------------

def _seed_facilities(db):
    db.add_all(
        [
            ParkingArea(destination_id=dest_id, name="Sayaji Baug Gate Parking", lat=22.3010, lng=73.1870, capacity=220, available=140, is_temporary=False, notes="Main city parking"),
            ParkingArea(destination_id=dest_id, name="Kalaghoda (Nyay Mandir) Parking", lat=22.3093, lng=73.1810, capacity=120, available=85, is_temporary=False, notes="Old-city shuttle point"),
            ParkingArea(destination_id=dest_id, name="Alkapuri Plaza Parking", lat=22.3145, lng=73.1775, capacity=260, available=200, is_temporary=False, notes="Multi-level"),
            ParkingArea(destination_id=dest_id, name="Navratri Grounds Official Parking", lat=22.3335, lng=73.1290, capacity=1500, available=1500, is_temporary=False, notes="Festival season parking"),
            ParkingArea(destination_id=dest_id, name="Temporary Parking — MSU Grounds", lat=22.3295, lng=73.1810, capacity=800, available=0, is_temporary=True, notes="Activates during Navratri peak nights; shuttle to Gotri grounds"),
            ParkingArea(destination_id=dest_id, name="Temporary Parking — Kirti Stambh Lot", lat=22.3060, lng=73.1950, capacity=350, available=0, is_temporary=True, notes="Deepotsav / festival overflow"),
        ]
    )
    db.add_all(
        [
            TransportFacility(destination_id=dest_id, name="Vadodara Junction Railway Station", kind="rail", lat=22.3130, lng=73.1840, details="Western Railway main line; 45 min to Ahmedabad by Shatabdi"),
            TransportFacility(destination_id=dest_id, name="Vadodara Airport (Harni)", kind="air", lat=22.3240, lng=73.2240, details="Domestic flights; 7 km from city centre"),
            TransportFacility(destination_id=dest_id, name="City / GSRTC Bus Terminal (Subhanpura)", kind="bus", lat=22.3050, lng=73.1610, details="Intercity + city buses, BRTS"),
            TransportFacility(destination_id=dest_id, name="BRTS Old-City Corridor", kind="brts", lat=22.3030, lng=73.1990, details="Air-conditioned bus rapid transit along the heritage corridor"),
            TransportFacility(destination_id=dest_id, name="Auto-rickshaw Stand — Mandvi", kind="auto", lat=22.2970, lng=73.2045, details="Licensed old-city autorickshaws; fixed fares to major sites"),
        ]
    )
    db.add_all(
        [
            EmergencyFacility(destination_id=dest_id, name="SSG Hospital Emergency", kind="hospital", lat=22.3042, lng=73.1880, phone="+91 265 241 3000", details="24×7 trauma & emergency, 500+ beds"),
            EmergencyFacility(destination_id=dest_id, name="GMERS Gotri Hospital", kind="hospital", lat=22.3170, lng=73.1270, phone="+91 265 278 1100", details="Close to Navratri grounds"),
            EmergencyFacility(destination_id=dest_id, name="City Police Control Room (Kothi)", kind="police", lat=22.3095, lng=73.1812, phone="100", details="155260 tourist helpline"),
            EmergencyFacility(destination_id=dest_id, name="Vadodara City Fire Brigade", kind="fire", lat=22.3020, lng=73.1750, phone="+91 265 242 1631", details="Central station, all-weather crew"),
            EmergencyFacility(destination_id=dest_id, name="First-aid Post — Navratri Grounds", kind="first_aid", lat=22.3330, lng=73.1289, phone="+91 265 278 1191", details="Seasonal post at Gotri grounds with ambulance bay"),
        ]
    )
    db.flush()


# ---------------------------------------------------------------------------
# Community reports
# ---------------------------------------------------------------------------

def _seed_reports(db):
    residents = db.query(User).filter(User.role == "resident").all()
    r0, r1 = residents[0], residents[1]
    reports = [
        dict(category="traffic", title="Congestion at Mandvi junctions during garba hours", description="Vehicles queueing across Mandvi Gate lanes after 7 PM; no traffic aide on duty. Needs diversion planning before Navratri.", user_id=r0.id, lat=22.2971, lng=73.2050, status="Reported"),
        dict(category="waste", title="Overflowing bins near Kansara Bazaar", description="Market bins overflow by afternoon on weekends, attracting strays; needs frequent weekend collection.", user_id=r1.id, lat=22.2966, lng=73.2046, status="Under Review"),
        dict(category="parking", title="No-parking zone ignored outside Sayaji Baug gate", description="Private cars block the north gate lane; families struggle to cross. Suggest marshals during peak season.", user_id=r0.id, lat=22.3015, lng=73.1872, status="Assigned"),
        dict(category="infrastructure", title="Street lights out on Sevasi stepwell approach", description="Approach road to the stepwell is pitch-dark after 8 PM; creates safety risk for early evening visitors.", user_id=r1.id, lat=22.3318, lng=73.0594, status="In Progress"),
        dict(category="overcrowding", title="Sayaji Baug aquarium queue spills onto road", description="Weekend aquarium queues exceed pavement and push into the road; additional barriers and entry slots needed.", user_id=r0.id, lat=22.3001, lng=73.1879, status="Resolved"),
        dict(category="safety", title="Unlit autostand at Ajwa crossing", description="Auto stand at Ajwa Road crossing is unlit and isolated after 10 PM; regular patrol requested.", user_id=r1.id, lat=22.2850, lng=73.1850, status="Reported"),
        dict(category="traffic", title="BRTS lane blocked by parked festival trailers", description="Temporary festival trailers occupy the BRTS lane near Gotri grounds; public buses delayed by 15 min.", user_id=r0.id, lat=22.3332, lng=73.1295, status="Reported"),
    ]
    for r in reports:
        db.add(CommunityReport(destination_id=dest_id, image_url="", **r))
    db.flush()


# ---------------------------------------------------------------------------
# announcements + alerts + closures
# ---------------------------------------------------------------------------

def _seed_announcements_and_alerts(db):
    db.add_all(
        [
            Announcement(
                destination_id=dest_id,
                category="festival",
                title="Navratri 2026: Road closures 6 PM – 11 PM",
                body="From 11–20 October, Gotri Road and Mandvi-lane approach roads close to private vehicles between 6:00 PM and 11:00 PM. Free shuttles run from MSU and Alkapuri lots.",
                important=True,
                published_by="admin@demo.com",
            ),
            Announcement(
                destination_id=dest_id,
                category="transport",
                title="Additional BRTS night service during Navratri",
                body="BRTS will run till 1:30 AM on Navratri nights with extra buses from the Gotri grounds. Last regular city bus remains 11 PM.",
                important=False,
                published_by="admin@demo.com",
            ),
            Announcement(
                destination_id=dest_id,
                category="parking",
                title="Temporary parking opened at MSU grounds",
                body="Peak-night overflow parking is available at Maharaja Sayajirao University grounds with 800 spaces and a shuttle every 10 minutes.",
                important=True,
                published_by="officer@demo.com",
            ),
            Announcement(
                destination_id=dest_id,
                category="general",
                title="Sayaji Baug museum ticket desks accept UPI",
                body="All museum entry points now accept UPI/digital payments to reduce weekend queues.",
                important=False,
                published_by="admin@demo.com",
            ),
        ]
    )
    db.add_all(
        [
            AuthorityAlert(
                destination_id=dest_id,
                category="crowd",
                place_id=1,
                title="High Visitor Activity — Laxmi Vilas Palace",
                message="The palace museum is experiencing heavy visitor activity. Nearby cultural experiences include the Maharaja Fateh Singh Museum, the Baroda Museum and the Kansara Bazaar heritage lane.",
                severity="warning",
                is_active=True,
                starts_at="2026-09-20 11:00",
                ends_at="2026-09-25 18:00",
                created_by="admin@demo.com",
            ),
            AuthorityAlert(
                destination_id=dest_id,
                category="crowd",
                place_id=None,
                title="Navratri crowd advisory",
                message="Expect very high footfall across Gotri grounds and the old city from Oct 11. Peak flow is predicted 6:00 PM – 10:00 PM. Authorities are readying shuttles and temporary parking.",
                severity="info",
                is_active=True,
                created_by="admin@demo.com",
            ),
            AuthorityAlert(
                destination_id=dest_id,
                category="parking",
                title="Temporary parking activated at MSU grounds",
                message="Parking available 800 m from the festival area: Maharaja Sayajirao University grounds, with shuttles every 10 minutes.",
                severity="info",
                is_active=True,
                created_by="officer@demo.com",
            ),
        ]
    )
    db.add_all(
        [
            RoadClosure(
                destination_id=dest_id,
                name="Gotri Road evening closure",
                description="Festival evening closure of Gotri Road from Ashram Chowk to the Navratri grounds.",
                road_name="Gotri Road",
                start_time="18:00",
                end_time="23:00",
                alternate_route="Use Ashram Road → Harni Road → Bhamu Bridge",
                status="active",
                lat=22.3250,
                lng=73.1380,
            ),
            RoadClosure(
                destination_id=dest_id,
                name="Mandvi old-city lane closure",
                description="Street garba lane closure around Mandvi Gate during festival nights.",
                road_name="Mandvi Gate lanes",
                start_time="18:00",
                end_time="23:30",
                alternate_route="Approach via Raopura Road; pedestrian-only after 6 PM",
                status="active",
                lat=22.2969,
                lng=73.2052,
            ),
        ]
    )
    db.flush()


# ---------------------------------------------------------------------------
# Historical footfall (simulated clearly as demo)
# ---------------------------------------------------------------------------

def _seed_history(db):
    """60 days of simulated historical footfall + current-day sample crowds."""
    rng = random.Random(42)
    places = db.query(Place).filter(Place.destination_id == dest_id).all()
    now = datetime(2026, 9, 19, 10, 0, 0)
    for day in range(60):
        d = now - timedelta(days=day)
        if d.weekday() >= 5:
            w = 1.22
        elif d.weekday() == 4:
            w = 1.06
        else:
            w = 0.92
        for p in places:
            cap = p.est_capacity or 1000
            # hourly counts sum to roughly capacity × utilisation (realistic scale)
            for hour in (9, 11, 13, 16, 18, 20):
                hfrac = {9: 0.06, 11: 0.12, 13: 0.16, 16: 0.2, 18: 0.22, 20: 0.16}[hour]
                count = int(cap * hfrac * w * (0.82 + rng.random() * 0.4))
                db.add(
                    FootfallData(
                        place_id=p.id,
                        destination_id=dest_id,
                        timestamp=d.replace(hour=hour, minute=30),
                        visitor_count=count,
                        source="simulation",
                    )
                )
            db.flush()

    # current-day crowd snapshot for instant live data
    for p in places:
        hour = 13
        r = rng.random()
        cap = p.est_capacity or 1000
        if p.id == 1:  # Laxmi Vilas Palace busy by demo design
            visitors = int(cap * (0.81 + 0.1 * r))
        elif p.id == 12:  # Tambekar Wada quiet
            visitors = int(cap * (0.12 + 0.08 * r))
        else:
            visitors = int(cap * (0.3 + 0.5 * r))
        visitors = max(20, min(visitors, cap))
        level = "low" if visitors < 0.35 * cap else ("moderate" if visitors < 0.62 * cap else ("high" if visitors < 0.85 * cap else "critical"))
        db.add(
            CrowdData(
                place_id=p.id,
                destination_id=dest_id,
                timestamp=now,
                level=level,
                visitor_count=visitors,
                capacity=cap,
                source="simulation",
            )
        )
    db.flush()

    # a couple of historical forecast rows so the analytics page is alive
    from ..models import TourismForecast

    for offset in (10, 21, 33, 46):
        d = (now - timedelta(days=offset)).strftime("%Y-%m-%d")
        base = 18000 + rng.randint(-2000, 4000)
        db.add(
            TourismForecast(
                destination_id=dest_id,
                date=d,
                event_name="Navratri pre-season",
                expected_visitors=base,
                expected_peak_start="11:00",
                expected_peak_end="19:00",
                confidence=0.7,
                high_footfall_zones=[
                    {"zone": "Zone A — Old City", "expected": round(base * 0.3)},
                    {"zone": "Zone C — Sayaji Baug", "expected": round(base * 0.4)},
                ],
                method="heuristic-baseline",
                is_demo=True,
            )
        )
    db.flush()


# ---------------------------------------------------------------------------
# Demand redistribution demo
# ---------------------------------------------------------------------------

def _seed_recommendation(db):
    palace = db.query(Place).filter(Place.name == "Laxmi Vilas Palace").first()
    museum = db.query(Place).filter(Place.name == "Baroda Museum & Picture Gallery").first()
    kansara = db.query(Place).filter(Place.name == "Kansara Bazaar").first()
    bm = db.query(Place).filter(Place.name == "Maharaja Fateh Singh Museum").first()
    if palace:
        db.add(
            AlternativeRecommendation(
                destination_id=dest_id,
                source_place_id=palace.id,
                expected_visitors=9900,
                capacity=6000,
                status="approved",
                approved_by="admin@demo.com",
                suggested_place_ids=[bm.id if bm else None, museum.id if museum else None, kansara.id if kansara else None],
            )
        )
    db.flush()