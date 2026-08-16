"""Pulls listings from external job APIs and normalizes them into
Scanline's canonical schema. Adzuna shown as the reference implementation
since it has a free tier; add more sources by writing a fetch_* function
and a matching normalize_* function, then registering both below.
"""
import os
import httpx
 
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
 
 
async def fetch_adzuna(query: str, location: str = "us", page: int = 1) -> list[dict]:
    url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": query,
        "results_per_page": 20,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [])
 
 
def normalize_adzuna(raw: dict) -> dict:
    return {
        "source": "adzuna",
        "external_id": str(raw.get("id")),
        "title": raw.get("title", "").strip(),
        "org": (raw.get("company") or {}).get("display_name", "Unknown"),
        "type": "job",  # Adzuna doesn't distinguish internships; refine via title keywords
        "location": (raw.get("location") or {}).get("display_name"),
        "description": raw.get("description", ""),
        "apply_url": raw.get("redirect_url"),
        "tags": [],  # populate via extract_tags()
        "deadline": None,  # Adzuna doesn't provide deadlines
    }
 
 
def dedupe_listings(listings: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for l in listings:
        key = (l["source"], l["external_id"])
        if key not in seen:
            seen.add(key)
            out.append(l)
    return out
 
 
async def extract_tags(description: str, anthropic_client) -> list[str]:
    """Uses Claude to pull structured skill/domain tags out of a raw
    job description. Keep the prompt tight — this runs per-listing at scale.
    """
    if not description:
        return []
    resp = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": (
                "Extract 4-8 lowercase, single/double-word skill or domain tags "
                "from this job description. Return ONLY a comma-separated list, "
                "nothing else.\n\n" + description[:2000]
            ),
        }],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    return [t.strip() for t in text.split(",") if t.strip()]
 
