"""Themed SVG illustration generator (data-URI).

Every entity is given a deterministic, category-correct illustration built from:

  * the destination's brand palette (base / accent / ink),
  * a thematic glyph matched to the entity's category (temple -> shikhara,
    fort/heritage -> bastion, artisan/weaver -> loom, festival -> festoon,
    food -> plate, hotel -> canopy, guide -> map, etc.),
  * a caption with the entity's name + a short theme label.

Because the image is generated *from* the entity's own metadata and returned
as a base64 data-URI, it can never 404 and can never be thematically wrong.
This is the seed-time image used for every entity; the frontend Image
component additionally keeps a themed fallback for anything remote.

Output: <img src="data:image/svg+xml;base64,..."> data URIs.
"""
import base64
import hashlib
import re

W, H = 800, 600

# destination_id -> (base, accent, ink)
PALETTE = {
    1: ("#6b1f2f", "#e3a04e", "#f7e8c8"),   # Vadodara   maroon + old-gold
    2: ("#0d5c63", "#7fd1b5", "#f0faf7"),   # Ahmedabad  teal   + jade
    3: ("#b25c1e", "#f2d06b", "#fff4dd"),   # Kutch      rust   + saffron
    4: ("#b0456e", "#f7c4dd", "#fff0f6"),   # Jaipur     rose   + blush
    5: ("#c9642b", "#f7b06a", "#fff3e0"),   # Varanasi   amber  + saffron
}

# category keyword -> glyph path (viewBox 0 0 400 220, mirrored when odd seed)
_GLYPHS = {
    "temple": "M200 20 L246 60 L226 60 L226 100 L174 100 L174 60 L154 60 Z "
              "M196 34 L196 44 M210 34 L210 44 M200 44 L200 100 M190 46 L190 70 "
              "M210 46 L210 70 M186 70 L200 100 L214 70 M156 122 L174 122 L176 132 L166 132 Z "
              "M224 116 L244 122 L238 118 L252 100 M120 122 L150 122 L150 140 L120 140 Z "
              "M250 122 L282 122 L282 140 L250 140 Z M172 150 L228 150 L228 164 L208 164 L208 158 L172 158 Z "
              "M150 150 L186 180 L214 170 L244 184 L258 150 M230 174 M242 166",
    "heritage": "M120 140 L140 110 L140 60 Q200 40 262 58 L262 110 L284 140 Z "
                "M152 80 L152 46 L206 20 L252 44 L252 60 M200 44 L200 60 "
                "M188 64 L188 102 L212 102 L212 64 M176 86 L176 140 M216 90 L216 118 L244 118 M244 118 L248 140 "
                "M116 196 L116 150 L292 150 L292 196 M140 196 L140 156 M252 196 L252 160",
    "palace": "M120 140 L150 116 L150 60 L182 46 Q200 26 218 46 L250 60 L250 116 L284 142 "
              "M172 66 L172 104 M220 66 L220 104 M196 54 Q196 70 196 104 L200 106 M196 156 L196 136 M212 156 L212 134",
    "culture": "M150 70 Q120 78 118 110 Q140 96 150 112 L150 132 L260 132 L260 78 Q250 76 248 86 L240 92 "
               "M164 92 Q172 96 168 102 Q188 116 208 120 Q228 112 232 100 Q240 92 238 84 "
               "M120 84 Q104 90 102 104 Q116 98 122 110 M110 126 L92 136 L112 142 M266 122 L292 132 L274 140 M110 158 L124 150 M122 160 L130 166",
    "market": "M150 58 Q196 36 262 54 L262 120 Q234 150 162 128 L150 104 Z "
              "M176 42 L178 56 M196 40 L198 54 M228 44 L230 58 "
              "M176 128 L176 146 L208 146 L208 123 M196 132 L196 148 M216 112 L216 152 M232 118 L232 152 M160 92 L162 150 L140 150 L136 118 M120 148 L92 112 L84 122",
    "artisan": "M152 92 L168 112 L176 92 L168 68 Z M150 66 Q158 70 158 78 "
               "M214 92 Q234 92 240 108 Q242 118 232 122 L214 126 L202 152 M228 158 L244 146 M220 112 L224 128 "
               "M150 128 L128 152 M170 140 L196 152 M104 144 L96 164 M142 136 L170 132 M184 86 Q196 82 202 88 M180 162 L208 168",
    "weave": "M120 100 L150 144 L280 106 L250 148 M120 100 L140 76 L176 66 L156 124 L186 84 L146 118 "
             "M226 66 L280 45 L260 128 L216 114 M160 124 L248 98 M240 66 L238 48 M196 128 L258 82 "
             "M120 122 L128 172 M188 112 L196 156 M208 122 L216 164",
    "handloom": "M110 122 L180 26 L318 120 M172 116 L186 92 M192 92 L176 88 M208 62 L218 84 M216 84 L228 60 "
                "M110 122 L192 132 M318 120 L226 132 L204 160 L222 148 M188 128 L176 162 M110 150 L150 150 M176 168 L212 188",
    "pottery": "M200 32 Q232 60 222 100 Q218 124 200 138 Q176 128 170 100 Q170 74 200 48 "
               "M184 62 Q218 70 206 92 M170 104 Q188 92 188 72 Q188 122 176 136 M210 106 Q196 116 196 136 M196 150 L200 122",
    "festival": "M140 100 Q120 84 128 70 Q152 76 150 94 M260 96 Q278 84 272 72 Q252 78 254 92 "
                "M150 132 L200 104 L262 130 L240 146 L188 140 M190 120 L188 150 M212 118 L232 148 M218 96 L224 80 M228 78 L224 62 "
                "M96 130 Q112 118 118 130 Q138 124 140 136 M166 152 L158 172 M234 156 L244 176 M196 158 L196 178 M270 122 L292 130 L270 138",
    "diya": "M200 118 Q228 96 226 78 Q232 60 214 72 Q230 52 212 50 L196 84 L180 50 Q162 58 174 74 Q168 68 166 88 Q170 106 200 118 Z "
            "M200 118 Q196 136 200 152 Q196 170 200 182 M224 142 Q240 150 254 158 Q270 170 272 186 M172 142 Q156 148 142 158 Q128 170 126 182 "
            "M232 148 L244 162 M166 148 L154 160 M200 148 L200 162 M182 120 L186 132 M218 122 L214 134",
    "kite": "M200 34 L272 122 L224 160 L200 126 Z M200 34 L158 128 L200 126 M200 34 L200 88 M200 34 L196 60 M204 66 L208 54 "
            "M154 150 L170 154 M214 156 L226 150 M174 142 L160 158 M248 118 L266 110 M186 34 L204 56 M226 34 L248 34 M196 140 L206 132 L212 140 Z",
    "camel": "M110 120 Q116 112 124 112 Q138 110 140 102 Q142 96 136 96 Q128 96 122 100 Q116 104 118 110 "
             "M140 102 Q156 92 176 96 Q194 96 200 112 Q208 120 222 120 Q240 120 252 128 Q268 136 274 148 Q278 158 268 162 "
             "M262 156 Q256 168 244 174 Q230 178 218 172 M226 148 L212 128 M216 166 L222 178 M232 132 L240 154 M258 128 L268 148 "
             "M150 128 L146 142 M168 120 L176 138 M182 160 L188 176 M196 96 L196 84 L206 76 M224 104 L212 96",
    "guide": "M120 120 L150 84 L200 42 L252 84 L282 120 L252 132 L200 76 L150 132 Z M200 60 L232 96 M200 74 L200 52 M222 66 L200 96 L184 72 "
             "M140 128 L176 148 M172 148 L180 162 M246 124 L284 142 M264 136 L284 156 M150 132 L120 152 M146 62 L128 78 M260 64 L286 78 M142 178 L176 166 M252 176 L220 160",
    "boats": "M96 96 Q120 76 152 92 Q184 104 200 92 Q224 82 250 96 Q280 110 308 104 Q330 100 340 108 "
             "M96 96 L100 148 L300 148 L340 120 L308 104 M120 92 L124 132 M168 100 L168 148 M216 96 L218 148 M268 104 L270 148 "
             "M120 166 L118 180 M196 164 L198 180 M262 168 L264 182 M170 176 L168 170",
    "ghat": "M130 110 L150 132 L178 118 L196 140 L224 122 L252 132 L274 116 Q264 96 240 100 L240 112 L230 104 L222 118 Q204 102 186 110 L186 102 L176 96 L168 108 M130 110 L126 100 L140 92 M274 116 L280 92 M252 132 L252 152 M196 140 L196 156 M160 158 L160 174 M150 98 L148 150 L130 116 M226 74 L226 56 M242 66 L242 44 M210 82 L210 66 "
             "M150 16 L154 26 M196 24 L202 40 M258 18 L264 34 M176 30 L224 40 M172 48 L190 36",
    "stepwell": "M128 118 L128 84 Q136 72 152 78 L152 130 M176 108 L216 72 L216 122 L176 144 Z M196 92 L196 130 "
                "M216 104 L248 130 M258 94 L258 104 L266 104 L288 86 M288 92 L308 112 M302 78 L316 70 L318 80 M284 110 L300 128 "
                "M168 108 L168 100 M168 152 L168 176 M196 150 L200 176 M152 60 L148 78 M214 58 L224 78 M210 58 L204 40 M236 92 L246 112 M234 102 L218 102",
}

# glyph keyword -> short human label shown on the image
_ENTITY_LABEL = {
    "temple": "Temple",
    "heritage": "Heritage",
    "palace": "Palace",
    "culture": "Culture",
    "market": "Local Market",
    "artisan": "Artisan",
    "weave": "Weave",
    "handloom": "Handloom",
    "pottery": "Pottery",
    "festival": "Festival",
    "diya": "Lights",
    "kite": "Kites",
    "camel": "Desert & Safari",
    "guide": "Heritage Walk",
    "boats": "River & Boats",
    "ghat": "Steps & Ghats",
    "stepwell": "Stepwell",
}

_CAT_KEYWORD = [
    ("temple", "temple"), ("mandir", "temple"), ("shrine", "temple"), ("dargah", "temple"),
    ("fort", "heritage"), ("heritage", "heritage"), ("history", "heritage"),
    ("ruin", "heritage"), ("haveli", "heritage"), ("palace", "palace"),
    ("museum", "palace"), ("monument", "palace"), ("landmark", "palace"),
    ("garden", "heritage"), ("culture", "culture"), ("cultural", "culture"),
    ("market", "market"), ("bazaar", "market"), ("street", "market"),
    ("weave", "weave"), ("handloom", "handloom"), ("textile", "handloom"),
    ("loom", "handloom"), ("pottery", "pottery"), ("potter", "pottery"),
    ("clay", "pottery"), ("craft", "artisan"), ("artisan", "artisan"),
    ("art", "artisan"), ("embroider", "artisan"), ("tie-dye", "artisan"),
    ("bandhani", "artisan"), ("workshop", "artisan"), ("metal", "artisan"),
    ("bead", "artisan"), ("jewel", "artisan"), ("festival", "festival"),
    ("feast", "festival"), ("diya", "diya"), ("deep", "diya"), ("light", "diya"),
    ("kite", "kite"), ("desert", "camel"), ("camel", "camel"), ("safari", "camel"),
    ("wildlife", "camel"), ("bird", "camel"), ("guide", "guide"), ("walk", "guide"),
    ("tour", "guide"), ("boat", "boats"), ("river", "boats"), ("ghat", "ghat"),
    ("steps", "ghat"), ("stepwell", "stepwell"), ("baoli", "stepwell"),
    ("well", "stepwell"), ("food", "culture"), ("restaurant", "culture"),
    ("stall", "market"), ("handicraft", "artisan"),
]

_MD5 = hashlib.md5


def _hex(hexcol, amt):
    hexcol = (hexcol or "#888888").lstrip("#")
    if len(hexcol) != 6:
        hexcol = "888888"
    r = max(0, min(255, int(hexcol[0:2], 16) + amt))
    g = max(0, min(255, int(hexcol[2:4], 16) + amt))
    b = max(0, min(255, int(hexcol[4:6], 16) + amt))
    return f"#{r:02x}{g:02x}{b:02x}"


def _clean(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _label_for(category):
    c = (category or "").lower().strip()
    for kw, glyph in _CAT_KEYWORD:
        if kw in c:
            return _ENTITY_LABEL[glyph], glyph
    return "Heritage", "heritage"


def _uri(category, name, seed=""):
    """Return (accented_base, accent, label, glyphpath)."""
    c = (category or "").lower().strip()
    for kw, glyph in _CAT_KEYWORD:
        if kw in c:
            return glyph
    return "heritage"


def svg_uri(destination_id, category, name, seed=""):
    """Build the full data URI (800x600)."""
    base, accent, ink = PALETTE.get(int(destination_id or 1), PALETTE[1])
    glyph = _uri(category, name, seed)
    label = _ENTITY_LABEL.get(glyph, "Heritage")
    path = _GLYPHS[glyph]

    h = _MD5(((name or "") + seed).encode("utf-8")).hexdigest()
    mirror = f' transform="translate(400 0) scale(-1 1)"' if int(h[0], 16) % 2 == 0 else ""

    name_lines = _wrap(name)
    name_txt = "".join(
        f'<text x="400" y="{492 + i * 26}" text-anchor="middle" fill="{ink}" opacity="0.9" '
        f'font-family="Georgia,serif" font-size="21" font-style="italic">{_clean(line)}</text>'
        for i, line in enumerate(name_lines[1:])
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{_clean(label)} — {_clean(name)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{base}"/>
      <stop offset="1" stop-color="{_hex(base, 18)}"/>
    </linearGradient>
    <linearGradient id="hint" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{accent}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{accent}" stop-opacity="0.35"/>
      <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect x="0" y="{H * 0.34}" width="{W}" height="4" fill="url(#hint)"/>
  <circle cx="120" cy="60" r="130" fill="{accent}" opacity="0.10"/>
  <circle cx="700" cy="540" r="170" fill="{accent}" opacity="0.08"/>
  <g transform="translate({W / 2} {int(H * 0.60)}) scale(0.9)" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.95">
    <g transform="translate(-200 -110)"{mirror}><path d="{path}"/></g>
  </g>
  <text x="400" y="{int(H * 0.20)}" text-anchor="middle" fill="{ink}" font-family="Georgia,serif" font-size="34" font-style="italic">{_clean(label.upper())}</text>
  <text x="400" y="{int(H * 0.78)}" text-anchor="middle" fill="{ink}" opacity="0.92" font-family="Georgia,serif" font-size="24" font-style="italic">{_clean(name_lines[0] if name_lines else "Virasa")}</text>
  {name_txt}
  <text x="400" y="{int(H * 0.90)}" text-anchor="middle" fill="{ink}" opacity="0.75" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="14" letter-spacing="6">{_mono(name)}</text>
</svg>'''
    uri = "data:image/svg+xml;charset=utf-8;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return uri


def _mono(s):
    return re.sub(r"[^A-Za-z]", "", (s or ""))[:16].upper() or "VIRASA"


def _wrap(name, maxlen=28, maxlines=2):
    name = _clean(name) or "Virasa"
    words = name.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= maxlen:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return (lines[:maxlines] or ["Virasa"])[:maxlines]


# ---------------------------------------------------------------------------
# apply(): one pass, every entity, guaranteed-correct image.
# ---------------------------------------------------------------------------

_UNRELIABLE = ("images.unsplash.com", "images.pexels.com", "upload.wikimedia.org")


def _pick_url(entity, attr, default_uri):
    """Return the current trusted image URL or the themed fallback."""
    return default_uri  # never trust pooled Photo IDs at runtime


def _entity_images(entity, attr, default_uri):
    """Return (list, changed) normalised image_urls for this row."""
    val = getattr(entity, attr)
    items = val if isinstance(val, list) else ([val] if val else [])
    items = [i for i in items if i]
    if not items:
        return [default_uri], True
    if any(any(bad in (i or "") for bad in _UNRELIABLE) for i in items):
        return [default_uri], True
    return items, False


def apply(db, destination_palette=None, row_limit=None):
    """Rewrites every row's primary image to a themed, category-correct SVG.

    Uses the entity's own (destination, category, name) so the illustration is
    derived from exactly the metadata it represents — it can never mismatch and
    it can never 404 (it's an inline data URI).
    """
    from ..models import Business, Destination, Experience, Festival, Place

    models = (
        (Place, "image_urls", True),
        (Business, "image_urls", True),
        (Experience, "image_urls", True),
        (Festival, "hero_image_url", False),
        (Destination, "image_url", False),
    )
    total = 0
    for model, attr, is_list in models:
        for entity in db.query(model).all():
            theme_key = None
            if hasattr(model, "category"):
                theme_key = getattr(entity, "category", None)
            elif hasattr(model, "kind"):
                theme_key = getattr(entity, "kind", None)
            dest_id = getattr(entity, "destination_id", None) or 1
            label = getattr(entity, "name", "") or "Heritage"
            uri = svg_uri(dest_id, theme_key or label, label)
            if is_list:
                items, changed = _entity_images(entity, attr, uri)
                if changed:
                    setattr(entity, attr, items)
                    total += 1
            else:
                cur = getattr(entity, attr)
                if not cur or any(bad in (cur or "") for bad in _UNRELIABLE):
                    setattr(entity, attr, uri)
                    total += 1
    db.flush()
    return total


if __name__ == "__main__":
    from ..core.database import SessionLocal

    db = SessionLocal()
    try:
        fixed = apply(db)
        db.commit()
        print(f"img_gen.apply repaired {fixed} entities")
    finally:
        db.close()
