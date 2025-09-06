import os, io, json
from typing import Optional, Dict

import re, time, requests

import streamlit as st
from PIL import Image
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai

# ✅ MUST be the first Streamlit command:
st.set_page_config(page_title="Car Brand Identifier", page_icon="🚗")
st.markdown("""
<style>
.card {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1rem;
    background-color: #f9fafb;
}
.kv {
    display: grid;
    grid-template-columns: 160px auto;
    row-gap: 6px;
    column-gap: 12px;
}
.kv div:first-child {
    opacity: 0.7;
    font-weight: 500;
}
.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}
.chip {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    border: 1px solid #e5e7eb;
    background: #fff;
    font-size: 0.85rem;
}
.logo {
    border-radius: 8px;
    max-height: 80px;
}
</style>
""", unsafe_allow_html=True)


# --- API key handling (.env + sidebar fallback) ---
load_dotenv()                               # loads GOOGLE_API_KEY from .env if present
API_KEY = os.getenv("GOOGLE_API_KEY")


if not API_KEY:
    st.error("Add your Gemini API key in the sidebar or in a .env file, then rerun.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- Minimal brand knowledge base (extend freely) ---
BRAND_KB: Dict[str, Dict[str, str]] = {
    "toyota": {"headquarters": "Toyota City, Japan", "founded": "1937"},
    "bmw": {"headquarters": "Munich, Germany", "founded": "1916"},
    "mercedes-benz": {"headquarters": "Stuttgart, Germany", "founded": "1926"},
    "audi": {"headquarters": "Ingolstadt, Germany", "founded": "1909"},
    "volkswagen": {"headquarters": "Wolfsburg, Germany", "founded": "1937"},
    "honda": {"headquarters": "Minato, Tokyo, Japan", "founded": "1948"},
    "hyundai": {"headquarters": "Seoul, South Korea", "founded": "1967"},
    "kia": {"headquarters": "Seoul, South Korea", "founded": "1944"},
    "ford": {"headquarters": "Dearborn, Michigan, USA", "founded": "1903"},
    "chevrolet": {"headquarters": "Detroit, Michigan, USA", "founded": "1911"},
    "porsche": {"headquarters": "Stuttgart, Germany", "founded": "1931"},
    "ferrari": {"headquarters": "Maranello, Italy", "founded": "1939"},
    "lamborghini": {"headquarters": "Sant'Agata Bolognese, Italy", "founded": "1963"},
    "nissan": {"headquarters": "Yokohama, Japan", "founded": "1933"},
    "peugeot": {"headquarters": "Poissy, France", "founded": "1810"},
    "citroën": {"headquarters": "Poissy, France", "founded": "1919"},
    "renault": {"headquarters": "Boulogne-Billancourt, France", "founded": "1899"},
    "volvo": {"headquarters": "Gothenburg, Sweden", "founded": "1927"},
    "skoda": {"headquarters": "Mladá Boleslav, Czech Republic", "founded": "1895"},
    "seat": {"headquarters": "Martorell, Spain", "founded": "1950"},
    "tesla": {"headquarters": "Austin, Texas, USA", "founded": "2003"},
}

# here the extras start

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIPEDIA_SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
HEADERS = {"User-Agent": "CarBrandApp/1.0 (student project)"}

# Map of Wikidata property IDs to human meaning
WD_PROPS = {
    "P571": "founded",           # inception (date)
    "P159": "headquarters",      # HQ location (entity)
    "P112": "founder",           # founder (entity|list)
    "P749": "parent_company",    # parent org (entity)
    "P17":  "country",           # country (entity)
    "P856": "website",           # official website (literal)
    "P154": "logo",              # logo image (media filename)
}

def _clean_time(value: str) -> str:
    # Wikidata time looks like '+1937-01-01T00:00:00Z'
    m = re.match(r"^\+?(\d{4})", value or "")
    return m.group(1) if m else value

HEADERS = {"User-Agent": "CarBrandApp/1.0 (https://yourgithub.com/limpakis)"}

@st.cache_data(show_spinner=False, ttl=24*3600)
def wd_search_brand(brand: str) -> str | None:
    params = {
        "action": "wbsearchentities",
        "language": "en",
        "type": "item",
        "format": "json",
        "search": brand
    }
    r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["search"][0]["id"] if data.get("search") else None


@st.cache_data(show_spinner=False, ttl=24*3600)
def wd_get_entity(qid: str) -> dict:
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "props": "labels|claims|sitelinks",
        "languages": "en",
        "format": "json"
    }
    r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()["entities"][qid]


@st.cache_data(show_spinner=False, ttl=24*3600)
def wd_get_labels(qids: list[str]) -> dict[str, str]:
    if not qids:
        return {}
    params = {
        "action": "wbgetentities",
        "ids": "|".join(qids),
        "props": "labels",
        "languages": "en",
        "format": "json"
    }
    r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    entities = r.json().get("entities", {})
    out = {}
    for q, ent in entities.items():
        label = (ent.get("labels", {}).get("en") or {}).get("value")
        if label:
            out[q] = label
    return out


@st.cache_data(show_spinner=False, ttl=24*3600)
def wikipedia_summary_from_wikidata(entity: dict) -> tuple[str|None, str|None]:
    sitelinks = entity.get("sitelinks", {})
    enwiki = sitelinks.get("enwiki", {})
    title = enwiki.get("title")
    if not title:
        return None, None
    url = WIKIPEDIA_SUMMARY_API + requests.utils.quote(title)
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return title, None
    j = r.json()
    return title, j.get("extract")


def extract_from_claims(entity: dict) -> dict:
    """
    Extracts a normalized dict from Wikidata claims.
    Resolves referenced entity labels for HQ, founder, parent, country.
    """
    claims = entity.get("claims", {})

    # First collect referenced QIDs we might need to label
    qids_to_label = set()
    def collect_qids(prop):
        for snak in claims.get(prop, []):
            try:
                v = snak["mainsnak"]["datavalue"]["value"]
                if isinstance(v, dict) and v.get("entity-type") == "item":
                    qids_to_label.add(v["id"])
            except KeyError:
                pass

    for pid in ["P159", "P112", "P749", "P17"]:
        collect_qids(pid)

    labels = wd_get_labels(list(qids_to_label))

    out = {}
    # Founded year
    if "P571" in claims:
        try:
            v = claims["P571"][0]["mainsnak"]["datavalue"]["value"]["time"]
            out["founded"] = _clean_time(v)
        except Exception:
            pass

    # HQ (entity)
    if "P159" in claims:
        try:
            v = claims["P159"][0]["mainsnak"]["datavalue"]["value"]["id"]
            out["headquarters"] = labels.get(v, v)
        except Exception:
            pass

    # Founder(s)
    founders = []
    for snak in claims.get("P112", []):
        try:
            v = snak["mainsnak"]["datavalue"]["value"]["id"]
            founders.append(labels.get(v, v))
        except Exception:
            pass
    if founders:
        out["founder"] = ", ".join(sorted(set(founders)))

    # Parent company
    if "P749" in claims:
        try:
            v = claims["P749"][0]["mainsnak"]["datavalue"]["value"]["id"]
            out["parent_company"] = labels.get(v, v)
        except Exception:
            pass

    # Country
    if "P17" in claims:
        try:
            v = claims["P17"][0]["mainsnak"]["datavalue"]["value"]["id"]
            out["country"] = labels.get(v, v)
        except Exception:
            pass

    # Website (literal)
    if "P856" in claims:
        try:
            out["website"] = claims["P856"][0]["mainsnak"]["datavalue"]["value"]
        except Exception:
            pass

    # Logo image (filename → Commons URL)
    if "P154" in claims:
        try:
            fn = claims["P154"][0]["mainsnak"]["datavalue"]["value"]
            # Commons file URLs are predictable:
            out["logo_url"] = f"https://commons.wikimedia.org/wiki/Special:FilePath/{requests.utils.quote(fn)}"
        except Exception:
            pass

    return out

@st.cache_data(show_spinner=False, ttl=24*3600)
def enrich_brand_live(brand: str) -> dict:
    """
    Try Wikidata/Wikipedia first. If that fails, fall back to in-code KB.
    Returns a dict with fields we can render directly.
    """
    # 1) Try local KB first for fast fields
    base = enrich_brand(brand)

    # 2) Wikidata lookup
    try:
        qid = wd_search_brand(brand)
        if not qid:
            return base

        entity = wd_get_entity(qid)
        extra = extract_from_claims(entity)

        wp_title, wp_summary = wikipedia_summary_from_wikidata(entity)
        if wp_title:
            extra["wikipedia_title"] = wp_title
            extra["wikipedia_url"] = f"https://en.wikipedia.org/wiki/{requests.utils.quote(wp_title)}"
        if wp_summary:
            extra["summary"] = wp_summary

        # Merge: prefer live data where present
        merged = {**base, **extra}
        # Ensure brand canonical (prefer label from entity if available)
        label = (entity.get("labels", {}).get("en") or {}).get("value")
        if label:
            merged["brand"] = label

        return merged
    except Exception as e:
        # Keep UI resilient
        st.info(f"Using local KB (live enrichment unavailable: {e})")
        return base

# here finishes the extras 

class BrandPrediction(BaseModel):
    brand: str = Field(..., description="Canonical brand name (e.g., 'BMW')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0..1")
    rationale: Optional[str] = Field(None, description="Short note explaining how the brand was inferred")

SYS_INSTRUCTIONS = (
    "You are an expert visual inspector for car branding. "
    "Given an image of a car or logo, identify the CAR BRAND only (not the model). "
    "When unsure, pick the most likely brand and lower the confidence accordingly. "
    "Output strictly JSON with fields: brand (string), confidence (0..1), rationale (string). "
    "Return just the JSON string with no extra commentary."
)

@st.cache_data(show_spinner=False)
def to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def call_gemini(image: Image.Image) -> Optional[BrandPrediction]:
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYS_INSTRUCTIONS)
    img_bytes = to_bytes(image)
    try:
        resp = model.generate_content([
            {"mime_type": "image/png", "data": img_bytes},
            "Return JSON now."
        ])
        text = resp.candidates[0].content.parts[0].text if resp and resp.candidates else None
        if not text:
            return None

        # Try to extract JSON (model should return clean JSON per instruction)
        text = text.strip()
        # Some models return ```json blocks. Strip fences if present.
        if text.startswith("```"):
            text = text.strip("`\n ")
            if text.lower().startswith("json"):
                text = text[4:].strip()  # remove 'json' label

        data = json.loads(text)
        pred = BrandPrediction(**data)
        return pred

    except Exception as e:
        st.error(f"Gemini error: {e}")
        return None


def enrich_brand(brand: str) -> Dict[str, str]:
    key = brand.lower().strip()
    # Normalize a few common aliases
    aliases = {
        "vw": "volkswagen",
        "benz": "mercedes-benz",
        "mercedes": "mercedes-benz",
        "citroen": "citroën",
        "škoda": "skoda",
    }
    key = aliases.get(key, key)
    info = BRAND_KB.get(key)
    if info:
        return {
            "brand": brand,
            "headquarters": info.get("headquarters", "Unknown"),
            "founded": info.get("founded", "Unknown"),
        }
    return {"brand": brand, "headquarters": "Unknown", "founded": "Unknown"}

def render_brand_card(enriched: dict, confidence: float):
    left, right = st.columns([1, 2])

    with left:
        if enriched.get("logo_url"):
            st.image(enriched["logo_url"], caption="", use_container_width=False, output_format="PNG")
        else:
            st.markdown("### " + enriched.get("brand", "Unknown"))

        # confidence chip(s)
        st.markdown(
            f'<div class="chips"><span class="chip">Confidence: {confidence:.2f}</span>'
            + (f'<span class="chip">{enriched.get("country","")}</span>' if enriched.get("country") else "")
            + (f'<span class="chip">{enriched.get("parent_company","")}</span>' if enriched.get("parent_company") else "")
            + "</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="kv">', unsafe_allow_html=True)
        def row(k, v):
            if v: st.markdown(f"<div>{k}</div><div><strong>{v}</strong></div>", unsafe_allow_html=True)

        row("Brand",        enriched.get("brand"))
        row("Headquarters", enriched.get("headquarters"))
        row("Founded",      enriched.get("founded"))
        row("Country",      enriched.get("country"))
        row("Parent company", enriched.get("parent_company"))
        row("Founder(s)",   enriched.get("founder"))
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Summary panel
    if enriched.get("summary") or enriched.get("wikipedia_url"):
        with st.expander("About this brand"):
            if enriched.get("summary"):
                st.write(enriched["summary"])
            if enriched.get("wikipedia_url"):
                st.markdown(f"**Wikipedia:** [{enriched.get('wikipedia_title','Open')}]({enriched['wikipedia_url']})")

# --- UI ---
st.title("🚗 Car Brand Identifier (Gemini + Streamlit)")
st.caption("Upload a car photo or logo. I’ll guess the brand and show HQ + founding year.")

with st.sidebar:
    st.header("Settings")

    if not API_KEY:
        st.warning("No GOOGLE_API_KEY found in your environment (.env or system).")
        API_KEY = st.text_input("Paste your Gemini API key", type="password")

    # model selector
    model_choice = st.selectbox(
        "Model", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0,
        help="Use 'pro' for harder images; 'flash' is cheaper/faster."
    )
    MODEL_NAME = model_choice  # always use the latest choice

    # confidence slider
    min_conf = st.slider("Min confidence to accept", 0.0, 1.0, 0.5, 0.05)

uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])


if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded image", use_container_width=True)

    with st.spinner("Identifying brand..."):
        pred = call_gemini(image)

    if not pred:
        st.warning("I couldn't parse a prediction. Try a clearer logo or switch to the 'pro' model.")
        st.stop()
   
   
    st.subheader("Details")
    enriched = enrich_brand_live(pred.brand)
    
    render_brand_card(enriched, pred.confidence)

    if enriched.get("website"):
        st.markdown(f"**Website:** [{enriched['website']}]({enriched['website']})")

    if enriched.get("wikipedia_url"):
        st.markdown(f"**Wikipedia:** [{enriched['wikipedia_title']}]({enriched['wikipedia_url']})")


    if enriched.get("logo_url"):
        st.image(enriched["logo_url"], caption="Brand logo (Wikimedia)", use_container_width=False)

    st.divider()
    st.caption("Tip: Extend BRAND_KB or plug in a live source (Wikipedia/Wikidata) for more brands.")
else:
    st.info("Upload a car photo (logo or front/back view). High-contrast logos work best.")
    