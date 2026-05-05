#!/usr/bin/env python3
"""
TRANSCODE Daily Japan Market Report Generator

Fetches data from the TRANSCODE API and generates a structured
Markdown + JSON report for agent consumption and SEO indexing.

Environment variables:
  TRANSCODE_API_KEY  - API key for authentication
  TRANSCODE_API_URL  - Base URL (default: https://japan-intelligence-api.onrender.com)
  OUTPUT_DIR         - Output directory (default: ./daily)
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

API_URL = os.getenv("TRANSCODE_API_URL", "https://japan-intelligence-api.onrender.com")
API_KEY = os.getenv("TRANSCODE_API_KEY", "")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./daily")

JST = timezone(timedelta(hours=9))
TODAY = datetime.now(JST).strftime("%Y-%m-%d")


def api_get(path: str) -> dict:
    """Make an authenticated GET request to the TRANSCODE API."""
    url = f"{API_URL}{path}"
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  ⚠ HTTP {e.code} for {path}")
        return {"error": str(e), "status_code": e.code}
    except Exception as e:
        print(f"  ⚠ Error for {path}: {e}")
        return {"error": str(e)}


def generate_report():
    """Generate the daily market report."""
    print(f"=== TRANSCODE Daily Report: {TODAY} ===\n")

    report_data = {
        "date": TODAY,
        "generated_at": datetime.now(JST).isoformat(),
        "source": "TRANSCODE Intelligence Platform",
        "api": API_URL,
        "sections": {}
    }

    # 1. Japan Briefing (all-in-one)
    print("Fetching: japan_briefing...")
    briefing = api_get("/api/v1/japan/briefing")
    if "error" not in briefing:
        report_data["sections"]["briefing"] = briefing
        print("  ✅ Briefing OK")
    else:
        print(f"  ⚠ Briefing failed: {briefing.get('error', 'unknown')}")

    # 2. Market Summary
    print("Fetching: market_summary...")
    market = api_get("/api/v1/market/summary")
    if "error" not in market:
        report_data["sections"]["market"] = market
        print("  ✅ Market OK")

    # 3. TDnet Disclosures
    print("Fetching: tdnet...")
    tdnet = api_get("/api/v1/tdnet/today")
    if "error" not in tdnet:
        report_data["sections"]["tdnet"] = tdnet
        disclosures = tdnet.get("data", {}).get("disclosures", [])
        print(f"  ✅ TDnet OK ({len(disclosures)} disclosures)")

    # 4. JPX Investor Flows
    print("Fetching: jpx_investor...")
    jpx = api_get("/api/v1/jpx/investor-flows")
    if "error" not in jpx:
        report_data["sections"]["jpx_investor"] = jpx
        print("  ✅ JPX Investor OK")

    # 5. Economic Calendar
    print("Fetching: economic_calendar...")
    calendar = api_get("/api/v1/economic/calendar")
    if "error" not in calendar:
        report_data["sections"]["economic_calendar"] = calendar
        print("  ✅ Calendar OK")

    # Output
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # JSON output
    json_path = os.path.join(OUTPUT_DIR, f"{TODAY}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON: {json_path}")

    # Markdown output
    md_path = os.path.join(OUTPUT_DIR, f"{TODAY}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# TRANSCODE Daily Japan Market Report\n\n")
        f.write(f"**Date**: {TODAY}  \n")
        f.write(f"**Generated**: {datetime.now(JST).strftime('%Y-%m-%d %H:%M JST')}  \n")
        f.write(f"**Source**: [TRANSCODE API]({API_URL})  \n\n")
        f.write(f"---\n\n")

        # Briefing summary
        if "briefing" in report_data["sections"]:
            b = report_data["sections"]["briefing"]
            f.write(f"## 📊 Japan Briefing\n\n")
            if isinstance(b.get("data"), dict):
                for key, val in b["data"].items():
                    if isinstance(val, dict) and "summary" in val:
                        f.write(f"### {key}\n{val['summary']}\n\n")
                    elif isinstance(val, str):
                        f.write(f"### {key}\n{val}\n\n")

        # TDnet
        if "tdnet" in report_data["sections"]:
            disclosures = report_data["sections"]["tdnet"].get("data", {}).get("disclosures", [])
            f.write(f"## 📰 TDnet Disclosures ({len(disclosures)} items)\n\n")
            for d in disclosures[:20]:
                title = d.get("title", "N/A")
                company = d.get("company_name", "N/A")
                f.write(f"- **{company}**: {title}\n")
            if len(disclosures) > 20:
                f.write(f"- ... and {len(disclosures) - 20} more\n")
            f.write("\n")

        # Market
        if "market" in report_data["sections"]:
            f.write(f"## 📈 Market Summary\n\n")
            f.write(f"```json\n{json.dumps(report_data['sections']['market'].get('data', {}), ensure_ascii=False, indent=2)[:2000]}\n```\n\n")

        f.write(f"---\n\n")
        f.write(f"*Auto-generated by TRANSCODE Bot. Data sourced from {API_URL}*\n")

    print(f"✅ Markdown: {md_path}")

    # Update latest symlink / index
    index_path = os.path.join(OUTPUT_DIR, "latest.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"latest": TODAY, "url": f"{TODAY}.json"}, f)
    print(f"✅ Index: {index_path}")

    print(f"\n=== Report generation complete ===")


if __name__ == "__main__":
    generate_report()
