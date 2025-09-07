# ---- Add near the top with other imports ----
from typing import Dict, List, Optional
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ==== TIME TOOL (offline) =====================================================
from datetime import datetime
from zoneinfo import ZoneInfo
import re



# === PERSISTENT MEMORY (JSON) ===
import json, os, atexit
MEM_PATH = "memory.json"

def _load_memory():
    global SESSIONS, FACTS
    if os.path.isfile(MEM_PATH):
        try:
            data = json.load(open(MEM_PATH, "r"))
            SESSIONS.update(data.get("sessions", {}))
            FACTS.update(data.get("facts", {}))
        except Exception:
            pass

def _save_memory():
    try:
        json.dump({"sessions": SESSIONS, "facts": FACTS}, open(MEM_PATH, "w"))
    except Exception:
        pass

_load_memory()
atexit.register(_save_memory)  # save on clean shutdown


app = FastAPI(title="Offline Ollama Assistant")

# Minimal maps (extend anytime). Cities first (more precise), then countries ↦ primary zone(s).
CITY_TZ = {
    # Europe
    "athens": "Europe/Athens", "paris": "Europe/Paris", "berlin": "Europe/Berlin",
    "rome": "Europe/Rome", "madrid": "Europe/Madrid", "lisbon": "Europe/Lisbon",
    "london": "Europe/London", "dublin": "Europe/Dublin", "amsterdam": "Europe/Amsterdam",
    "vienna": "Europe/Vienna", "prague": "Europe/Prague", "warsaw": "Europe/Warsaw",
    "zurich": "Europe/Zurich", "oslo": "Europe/Oslo", "stockholm": "Europe/Stockholm",
    "helsinki": "Europe/Helsinki",
    # Middle East & Africa
    "istanbul": "Europe/Istanbul", "tel aviv": "Asia/Jerusalem", "cairo": "Africa/Cairo",
    "johannesburg": "Africa/Johannesburg", "nairobi": "Africa/Nairobi",
    # Asia
    "dubai": "Asia/Dubai", "riyadh": "Asia/Riyadh", "tehran": "Asia/Tehran",
    "delhi": "Asia/Kolkata", "mumbai": "Asia/Kolkata", "karachi": "Asia/Karachi",
    "dhaka": "Asia/Dhaka", "bangkok": "Asia/Bangkok", "jakarta": "Asia/Jakarta",
    "singapore": "Asia/Singapore", "kuala lumpur": "Asia/Kuala_Lumpur",
    "hong kong": "Asia/Hong_Kong", "shanghai": "Asia/Shanghai", "beijing": "Asia/Shanghai",
    "seoul": "Asia/Seoul", "tokyo": "Asia/Tokyo", "taipei": "Asia/Taipei",
    # Oceania
    "sydney": "Australia/Sydney", "melbourne": "Australia/Melbourne", "perth": "Australia/Perth",
    "auckland": "Pacific/Auckland",
    # Americas
    "new york": "America/New_York", "boston": "America/New_York", "miami": "America/New_York",
    "chicago": "America/Chicago", "denver": "America/Denver", "phoenix": "America/Phoenix",
    "los angeles": "America/Los_Angeles", "seattle": "America/Los_Angeles",
    "toronto": "America/Toronto", "vancouver": "America/Vancouver",
    "mexico city": "America/Mexico_City", "bogota": "America/Bogota",
    "lima": "America/Lima", "sao paulo": "America/Sao_Paulo", "buenos aires": "America/Argentina/Buenos_Aires",
}

COUNTRY_TZ = {
    # Single/main time zone countries
    "greece": ["Europe/Athens"], "france": ["Europe/Paris"], "germany": ["Europe/Berlin"],
    "italy": ["Europe/Rome"], "spain": ["Europe/Madrid"], "portugal": ["Europe/Lisbon"],
    "uk": ["Europe/London"], "united kingdom": ["Europe/London"], "ireland": ["Europe/Dublin"],
    "netherlands": ["Europe/Amsterdam"], "austria": ["Europe/Vienna"], "poland": ["Europe/Warsaw"],
    "switzerland": ["Europe/Zurich"], "norway": ["Europe/Oslo"], "sweden": ["Europe/Stockholm"],
    "finland": ["Europe/Helsinki"], "turkey": ["Europe/Istanbul"], "israel": ["Asia/Jerusalem"],
    "egypt": ["Africa/Cairo"], "south africa": ["Africa/Johannesburg"], "kenya": ["Africa/Nairobi"],
    "saudi arabia": ["Asia/Riyadh"], "uae": ["Asia/Dubai"], "iran": ["Asia/Tehran"],
    "india": ["Asia/Kolkata"], "pakistan": ["Asia/Karachi"], "bangladesh": ["Asia/Dhaka"],
    "thailand": ["Asia/Bangkok"], "indonesia": ["Asia/Jakarta"], "singapore": ["Asia/Singapore"],
    "malaysia": ["Asia/Kuala_Lumpur"], "china": ["Asia/Shanghai"], "south korea": ["Asia/Seoul"],
    "japan": ["Asia/Tokyo"], "taiwan": ["Asia/Taipei"], "australia": ["Australia/Sydney","Australia/Perth"],
    "new zealand": ["Pacific/Auckland"], "mexico": ["America/Mexico_City"], "colombia": ["America/Bogota"],
    "peru": ["America/Lima"], "brazil": ["America/Sao_Paulo", "America/Manaus", "America/Fortaleza"],
    "argentina": ["America/Argentina/Buenos_Aires"], "chile": ["America/Santiago"], "uruguay": ["America/Montevideo"],
    # USA/Canada are multi-zone: show several majors
    "usa": ["America/New_York","America/Chicago","America/Denver","America/Los_Angeles","America/Phoenix","America/Anchorage","Pacific/Honolulu"],
    "united states": ["America/New_York","America/Chicago","America/Denver","America/Los_Angeles","America/Phoenix","America/Anchorage","Pacific/Honolulu"],
    "canada": ["America/St_Johns","America/Halifax","America/Toronto","America/Winnipeg","America/Edmonton","America/Vancouver"],
}

UTC_OFFSET_RE = re.compile(r"(utc|gmt)\\s*([+−-]\\s*\\d{1,2})(?::?(\\d{2}))?", re.I)

def _fmt_time(dt: datetime) -> str:
    # %-I works on Unix; if on Windows, use %#I
    return dt.strftime("%-I:%M %p")

def local_times_for(query: str):
    """Return list[(label, time_string)] or None if not a time query."""
    q = query.lower().strip()

    # detect intent
    if not any(kw in q for kw in ["time", "date", "now", "current time", "what time"]):
        return None

    # UTC/GMT offset like "UTC+2" or "GMT -08:00"
    m = UTC_OFFSET_RE.search(q.replace(" ", ""))
    if m:
        sign = 1 if "+" in m.group(2) or "−" in m.group(2) else -1
        hours = int(re.sub(r"[+−-]", "", m.group(2)))
        mins = int(m.group(3) or 0)
        offset = sign * (hours * 60 + mins)
        # Compute from UTC then add offset
        now_utc = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        dt = now_utc
        from datetime import timedelta
        dt = dt + timedelta(minutes=offset)
        return [(f"UTC{m.group(2)}" + (f":{mins:02d}" if mins else ""), f"{_fmt_time(dt)} • {dt.strftime('%A, %d %B %Y')}")]

    # try city match
    for city, tz in CITY_TZ.items():
        if city in q:
            now = datetime.now(ZoneInfo(tz))
            return [(city.title(), f"{_fmt_time(now)} • {now.strftime('%A, %d %B %Y')}")]

    # try country match
    for country, zones in COUNTRY_TZ.items():
        if country in q:
            rows = []
            for z in zones[:6]:  # cap to avoid spam
                now = datetime.now(ZoneInfo(z))
                label = z.split("/")[-1].replace("_", " ")
                rows.append((f"{country.title()} — {label}", f"{_fmt_time(now)} • {now.strftime('%A, %d %B %Y')}"))
            return rows

    # no explicit location → assume they want system time
    now_local = datetime.now().astimezone()
    tzname = now_local.tzinfo.key if hasattr(now_local.tzinfo, "key") else str(now_local.tzinfo)
    return [("Your system time (" + tzname + ")", f"{_fmt_time(now_local)} • {now_local.strftime('%A, %d %B %Y')}")]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Make Gemma 3:1b the default
DEFAULT_MODEL = "gemma3:1b"

SESSIONS: Dict[str, List[dict]] = {}   # chat history per session
FACTS: Dict[str, List[str]] = {}       # sticky memory per session

# Ollama endpoints
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_GEN_URL  = "http://localhost:11434/api/generate"

# Optional RAG hookup (auto-on if chroma_db exists)
RAG_READY = False
try:
    from langchain_ollama import OllamaEmbeddings
    from langchain_community.vectorstores import Chroma
    if os.path.isdir("chroma_db"):
        _emb = OllamaEmbeddings(model="nomic-embed-text")
        _vdb = Chroma(collection_name="kb", persist_directory="chroma_db", embedding_function=_emb)
        RAG_READY = True
except Exception:
    RAG_READY = False

from pydantic import BaseModel

class ChatBody(BaseModel):
    session_id: str
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 512
    use_rag: Optional[bool] = True

import re

def detect_intent(text: str) -> str:
    q = text.lower().strip()
    if any(k in q for k in ["time", "current time", "gmt", "utc"]): return "time"
    if re.match(r"\b(who|what|when|where|which|how many)\b", q):    return "factual"
    if any(k in q for k in ["convert", "km", "kg", "mph", "+", "-", "*", "/", "^"]): return "math"
    if any(k in q for k in ["poem", "story", "brainstorm"]):        return "creative"
    return "general"

TEMP_FOR = {
  "factual": 0.15,
  "general": 0.3,
  "creative": 0.9,
  "math": 0.2,
  "time": 0.1,
}


def _ask_ollama(model: str, messages: List[dict], temperature: float, num_predict: int) -> str:
    import requests

    SAFE_OPTS = {
    "temperature": 0.2,     # 0.1–0.4 for facts
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "num_predict": 320,
    # "mirostat": 0,        # leave off for now
    }


    # Try new /api/chat first
    try:
        r = requests.post(
            OLLAMA_CHAT_URL,
            json={"model": model, "messages": messages, "stream": False,
                  "options": {"temperature": temperature, "num_predict": num_predict}},
            timeout=600,
        )
        if r.status_code != 404:
            r.raise_for_status()
            return r.json()["message"]["content"]
    except Exception:
        pass
    # Fallback: /api/generate (flatten messages)
    prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    r = requests.post(
        OLLAMA_GEN_URL,
        json={"model": model, "prompt": prompt, "stream": False,
              "options": {"temperature": temperature, "num_predict": num_predict}},
        timeout=600,
    )
    r.raise_for_status()
    return r.json().get("response", "")


from fastapi.responses import StreamingResponse

@app.post("/chat_stream")
def chat_stream(body: ChatBody):
    sid = body.session_id
    # (reuse your same routing / rag / messages building)
    # but call Ollama with stream=True and yield chunks
    import requests, json

    def gen():
        r = requests.post(
            OLLAMA_CHAT_URL,
            json={"model": body.model or DEFAULT_MODEL, "messages": messages, "stream": True,
                  "options": {"temperature": temp, "num_predict": body.max_tokens or 512}},
            stream=True, timeout=600,
        )
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line: continue
            try:
                obj = json.loads(line)
                if "message" in obj and "content" in obj["message"]:
                    yield obj["message"]["content"]
            except Exception:
                pass
        yield ""  # end

    return StreamingResponse(gen(), media_type="text/plain")


# ---- One unified chat endpoint ----
@app.post("/chat")
def chat(body: ChatBody):
    sid = body.session_id
    model = body.model or DEFAULT_MODEL

    # init state
    SESSIONS.setdefault(sid, [{"role": "system", "content": "You are a helpful, concise assistant."}])
    FACTS.setdefault(sid, [])

    text = body.message.strip()

    # 1) Detect intent
    intent = detect_intent(text)  # requires detect_intent() + TEMP_FOR dict

    # 2) Route to local tools FIRST (deterministic answers)

    # -- time tool (works for any city/country/UTC offset if you added local_times_for)
    hits_time = None
    try:
        hits_time = local_times_for(text)
    except NameError:
        hits_time = None

    if hits_time:
        if len(hits_time) == 1:
            label, tstr = hits_time[0]
            ans = f"{tstr} in {label}."
        else:
            bullet = "\n".join(f"• {lbl}: {tstr}" for lbl, tstr in hits_time)
            ans = f"Here are the current local times:\n{bullet}"
        SESSIONS[sid].append({"role": "assistant", "content": ans})
        return {"answer": ans}

    # -- calculator / unit conversion tool (if you added maybe_calc)
    hit_math = None
    try:
        hit_math = maybe_calc(text)
    except NameError:
        hit_math = None

    if hit_math:
        SESSIONS[sid].append({"role": "assistant", "content": hit_math})
        return {"answer": hit_math}

    # 3) Pick a safe temperature automatically unless the user set one
    temp = (body.temperature if body.temperature is not None
            else TEMP_FOR.get(intent, 0.3))

    # 4) Decide whether to use RAG (auto ON for factual questions)
    use_rag = body.use_rag if body.use_rag is not None else (intent == "factual")

    # 5) Optional RAG retrieval + citations
    rag_note = ""
    rag_evidence = False
    if use_rag and RAG_READY:
        try:
            hits = _vdb.similarity_search(text, k=8)
            if hits:
                rag_evidence = True

                # (optional) rerank to top 3 if you created a CrossEncoder named RERANK
                try:
                    if 'RERANK' in globals() and RERANK:
                        pairs = [(text, d.page_content) for d in hits]
                        scores = RERANK.predict(pairs)
                        hits = [d for _, d in sorted(zip(scores, hits), key=lambda t: t[0], reverse=True)[:3]]
                    else:
                        hits = hits[:3]
                except Exception:
                    hits = hits[:3]

                ctx = "\n\n".join(d.page_content for d in hits)
                sources = []
                for d in hits:
                    meta = getattr(d, "metadata", {}) or {}
                    src = meta.get("source") or meta.get("file_path") or "unknown"
                    sources.append(src)

                rag_note = (
                    "Use ONLY the following CONTEXT for factual claims. "
                    "If information is missing, say you don't have enough info.\n"
                    f"CONTEXT:\n{ctx}\n\n"
                    "When answering, include a line that begins with 'Sources: ' listing filenames.\n"
                    f"Sources: {', '.join(sorted(set(sources)))}"
                )
        except Exception:
            pass

    # 6) For factual questions with NO evidence, don't hallucinate
    if intent == "factual" and use_rag and not rag_evidence:
        msg = ("I can’t verify that offline from your local documents. "
            "Add files to ./docs and rebuild the index, or tell me to remember a fact.")
        SESSIONS[sid].append({"role": "assistant", "content": msg})
        return {"answer": msg}

    # 7) Build the final message stack and call the LLM
    SYSTEM_BASE = (
        "You are an offline assistant. Prefer short, correct answers. "
        "If you cannot verify a factual claim from provided context or tools, say you can’t verify. "
        "When RAG context is present, treat it as the source of truth."
    )

    # persist facts
    sticky = "\n".join(f"- {f}" for f in FACTS[sid])
    preface = (f"User-provided facts to remember across turns:\nFACTS:\n{sticky}\n") if sticky else ""

    SESSIONS[sid].append({"role": "user", "content": text})
    history = SESSIONS[sid][-10:]  # keep the last 10 messages

    messages: list[dict] = [{"role": "system", "content": SYSTEM_BASE}]
    if preface:
        messages.append({"role": "system", "content": preface})
    if rag_note:
        messages.append({"role": "system", "content": rag_note})
    messages.extend(history)

    answer = _ask_ollama(
        model or DEFAULT_MODEL,
        messages,
        temp,
        body.max_tokens or 512
    )
    SESSIONS[sid].append({"role": "assistant", "content": answer})
    return {"answer": answer}


# ---- Local tools (time/date/etc.) ----
    hits = local_times_for(text)
    if hits:
        if len(hits) == 1:
            label, tstr = hits[0]
            ans = f"{tstr} in {label}."
        else:
            bullet = "\n".join(f"• {lbl}: {tstr}" for lbl, tstr in hits)
            ans = f"Here are the current local times:\n{bullet}"
        # save to history so conversation flows
        SESSIONS[sid].append({"role":"assistant","content": ans})
        return {"answer": ans}

    # simple memory write: "remember: "
    if text.lower().startswith("remember:"):
        fact = text.split(":", 1)[1].strip()
        if fact:
            FACTS[sid].append(fact)
            return {"answer": f"Got it. I will remember: {fact}"}

    # stick facts into a system preface
    sticky = "\n".join(f"- {f}" for f in FACTS[sid])
    preface = (f"User facts to remember and use verbatim when asked:\nFACTS:\n{sticky}\n") if sticky else ""

    # optional RAG retrieval (if index exists and toggle is on)
    rag_note = ""
    if body.use_rag and RAG_READY:
        try:
            hits = _vdb.similarity_search(text, k=5)
            ctx = "\n\n".join(d.page_content for d in hits)
            if ctx:
                rag_note = ("Use ONLY the following CONTEXT for factual claims. "
                            "If info is missing, say you don't have enough info.\n"
                            f"CONTEXT:\n{ctx}\n")
        except Exception:
            pass

    # short rolling history
    SESSIONS[sid].append({"role": "user", "content": text})
    history = SESSIONS[sid][-10:]

    messages: List[dict] = []
    if preface:
        messages.append({"role": "system", "content": preface})
    if rag_note:
        messages.append({"role": "system", "content": rag_note})
    messages.extend(history)

    answer = _ask_ollama(model, messages, body.temperature or 0.2, body.max_tokens or 512)
    SESSIONS[sid].append({"role": "assistant", "content": answer})
    return {"answer": answer}
