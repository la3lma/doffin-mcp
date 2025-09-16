
import asyncio
import json
from typing import Any, Dict, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from selectolax.parser import HTMLParser

from mcp.server.fastmcp import FastMCP

BASE = "https://doffin.no"
UA = "MCP-Doffin/1.0 (+contact@example.com)"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=0.8, max=2))
async def fetch(url: str) -> str:
    async with httpx.AsyncClient(headers={"User-Agent": UA}, timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text


def build_search_url(p: Dict[str, Any]) -> str:
    from urllib.parse import urlencode
    qs: Dict[str, Any] = {}
    if p.get("q"):
        qs["query"] = p["q"]
    if p.get("cpv"):
        qs["cpvCodesLabel"] = ",".join(p["cpv"])
    if p.get("buyer"):
        qs["buyer"] = p["buyer"]
    if p.get("published_from"):
        qs["publishedFrom"] = p["published_from"]
    if p.get("published_to"):
        qs["publishedTo"] = p["published_to"]
    if p.get("deadline_to"):
        qs["deadlineTo"] = p["deadline_to"]
    if p.get("county"):
        qs["county"] = p["county"]
    if p.get("procedure"):
        qs["procedure"] = p["procedure"]
    if (page := p.get("page")) and page > 1:
        qs["page"] = page
    return f"{BASE}/search?{urlencode(qs, doseq=True)}"


def parse_search(html: str) -> List[Dict[str, Any]]:
    tree = HTMLParser(html)
    items: List[Dict[str, Any]] = []
    for card in tree.css(".notice-card, .search-result, [data-test='notice-card']"):
        def txt(sel: str) -> str:
            el = card.css_first(sel)
            return el.text(strip=True) if el else ""

        title = txt(".notice-title") or txt("h2, h3")
        if not title:
            link_title = card.css_first("a[href*='/notices/']")
            if link_title:
                title = link_title.text(strip=True)

        link_el = card.css_first("a[href*='/notices/']")
        link = link_el.attributes.get("href") if link_el else None
        if link and not link.startswith("http"):
            link = BASE + link

        buyer = txt(".notice-buyer, [data-test='buyer'], dt:contains('Oppdragsgiver') + dd")
        published = card.css_first("time[datetime][data-test='published']")
        published_at = published.attributes.get("datetime") if published else txt(".notice-published, [data-test='published']")
        deadline = card.css_first("time[datetime][data-test='deadline']")
        deadline_at = deadline.attributes.get("datetime") if deadline else txt(".notice-deadline, [data-test='deadline']")

        cpv = [n.text(strip=True) for n in card.css(".notice-cpv .tag, [data-test='cpv'] .tag, .cpv .tag")]

        if link and title:
            items.append({
                "notice_id": link.rsplit("/", 1)[-1],
                "title": title,
                "buyer": buyer or None,
                "published_at": published_at or None,
                "deadline_at": deadline_at or None,
                "cpv": cpv,
                "link": link
            })
    return items


def parse_notice(html: str, url: str) -> Dict[str, Any]:
    t = HTMLParser(html)
    out: Dict[str, Any] = {"source_url": url}

    # JSON-LD if present
    for s in t.css("script[type='application/ld+json']"):
        try:
            j = json.loads(s.text())
            if isinstance(j, dict):
                out.update(j)
        except Exception:
            pass

    def txt(sel: str) -> str | None:
        el = t.css_first(sel)
        return el.text(strip=True) if el else None

    out["title"] = out.get("title") or txt("h1") or txt("[data-test='title']")
    out["buyer"] = out.get("buyer") or txt("[data-test='buyer-name'], .buyer .value, dt:contains('Oppdragsgiver') + dd")
    out["description"] = out.get("description") or txt(".notice-description, [data-test='description'], article")

    pub = t.css_first("time[datetime][data-test='published']")
    out["published_at"] = out.get("published_at") or (pub.attributes.get("datetime") if pub else txt("[data-test='published']"))

    ded = t.css_first("time[datetime][data-test='deadline']")
    out["deadline_at"] = out.get("deadline_at") or (ded.attributes.get("datetime") if ded else txt("[data-test='deadline']"))

    if "cpv" not in out or not out["cpv"]:
        out["cpv"] = [n.text(strip=True) for n in t.css("[data-test='cpv'] .tag, .cpv .tag")]

    atts: List[Dict[str, str]] = []
    for a in t.css("a[href$='.pdf'], a[href*='/Document/'], a[href*='/document/']"):
        href = a.attributes.get("href")
        if href and not href.startswith("http"):
            href = BASE + href
        name = a.text(strip=True)
        if href:
            atts.append({"name": name, "url": href})
    out["attachments"] = atts

    # Truncate raw html to keep payload small but helpful for LLM extraction
    out["raw_html"] = (t.body.text() if t.body else html)[:200000]
    return out


async def main() -> None:
    server = FastMCP("mcp-doffin", instructions="Doffin MCP server (Python)")

    @server.tool()
    async def search_notices(
        q: str = None,
        cpv: List[str] = None,
        buyer: str = None,
        published_from: str = None,
        published_to: str = None,
        deadline_to: str = None,
        county: str = None,
        procedure: str = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search public procurement notices on doffin.no"""
        args = {
            "q": q,
            "cpv": cpv,
            "buyer": buyer,
            "published_from": published_from,
            "published_to": published_to,
            "deadline_to": deadline_to,
            "county": county,
            "procedure": procedure,
            "page": page,
        }
        url = build_search_url(args)
        html = await fetch(url)
        return {"results": parse_search(html), "source_url": url}

    @server.tool()
    async def get_notice(
        notice_id: str = None,
        url: str = None,
    ) -> Dict[str, Any]:
        """Fetch and parse a single notice page from doffin.no"""
        if not notice_id and not url:
            raise ValueError("Either notice_id or url must be provided")
        
        target_url = url or f"{BASE}/notices/{notice_id}"
        html = await fetch(target_url)
        return parse_notice(html, target_url)

    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
