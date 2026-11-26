#!/usr/bin/env python3
"""Japan Resort & Urban STR (Minpaku) + 365-Day Ryokan-gyo Ordinance Verifier & SEO Builder.

Compiles, validates, and exports regulatory profiles for 20 high-demand Japanese ski,
onsen, urban, heritage, and island jurisdictions into:
  - site/data/resort_ordinances.json
  - site/data/resort_ordinances_bundle.js (synchronous fallback for local file:// viewing)
  - site/markets/<slug>.html (20 dedicated programmatic SEO static HTML pages with FAQPage JSON-LD)
  - site/sitemap.xml (21 canonical URLs for Google Search Console indexing)
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SITE_BASE_URL = "https://chaochenxuanhua-boop.github.io/japan-resort-minpaku-map"
INTAKE_EMAIL = "chaochenxuanhua@gmail.com"
DEFAULT_FX_USD_JPY = 152.0
DEFAULT_CLOSING_PCT = 7.0
DEFAULT_MGMT_FEE_PCT = 22.0

EXPECTED_RESORTS: list[str] = [
    "Kutchan / Niseko",
    "Hakuba",
    "Kyoto City",
    "Shibuya",
    "Shinjuku",
    "Taito / Asakusa",
    "Chuo Osaka",
    "Atami",
    "Hakone",
    "Karuizawa",
    "Fujikawaguchiko",
    "Furano",
    "Nozawa Onsen",
    "Myoko",
    "Takayama",
    "Kanazawa",
    "Fukuoka City",
    "Naha",
    "Ishigaki",
    "Miyakojima",
]

VALID_CATEGORIES: set[str] = {
    "Ski & Alpine",
    "Onsen & Mountain",
    "Coastal & Island",
    "Heritage",
    "Urban & Metro",
}

VALID_MINPAKU_SEVERITIES: set[str] = {
    "Green: Standard 180d",
    "Amber: Zone/Season Restricted",
    "Red: Strict Weekday/School-Zone Ban",
}

VALID_RYOKAN_FEASIBILITY: set[str] = {
    "High - Investor Friendly",
    "Moderate - Zoning Dependent",
    "Strict - High Barrier",
}

VERIFICATION_TIMESTAMP = "2026-11-26T12:00:00Z"
MLIT_PORTAL_URL = "https://www.mlit.go.jp/kankocho/minpaku/municipality/index.html"

GOV_DOMAIN_RE = re.compile(
    r"(?:^|\.)(?:lg\.jp|go\.jp|(?:pref|city|town|vill)\.[a-z0-9.-]+\.jp)$"
)


def get_raw_ordinance_records() -> list[dict[str, Any]]:
    """Return curated regulatory profiles for the 20 target Japanese STR & Ryokan markets."""
    return [
        {
            "id": "kutchan-niseko",
            "name": "Kutchan / Niseko",
            "seo_short_name": "Niseko",
            "japanese_name": "倶知安町・ニセコ (北海道)",
            "prefecture": "Hokkaido",
            "resort_category": "Ski & Alpine",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 165,
            "minpaku_ordinance_summary": (
                "Governed by the Hokkaido Prefectural Minpaku Ordinance: unhosted Minpaku is prohibited on school days "
                "within 100m of elementary and junior high school entrances in Kutchan Town. Outside school buffers in "
                "Hirafu and Kabayama resort zones, up to 180 days apply subject to winter snow-clearing and registered "
                "local administrator (Kanri Gyosha) response rules."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Hirafu Quasi-City Planning Districts and Niseko resort parcels allow 365-day Simple Lodging (Kan'i Shukusho) "
                "subject to Kutchan Landscape & Machizukuri Ordinance height/FAR limits and neighbor briefings. Institutional "
                "chalets routinely secure full Ryokan-gyo permits to capture ultra-prime winter ADR plus green-season golf stays."
            ),
            "fire_safety_and_building_notes": (
                "Kutchan Public Health Center & Shiribeshi Fire Department enforce winter snow-protected egress, wired Jikaho "
                "automatic fire alarms, >=3.3 sqm per guest floor area, and face-to-face or compliant real-time ICT video "
                "check-in backed by 10-minute on-site emergency dispatch."
            ),
            "local_lodging_tax_notes": (
                "Kutchan Town Accommodation Tax: 3% flat rate of room charge plus Hokkaido prefectural lodging levy."
            ),
            "ordinance_jurisdiction": "Hokkaido Government & Kutchan Public Health Center (北海道経済部観光局 / 倶知安保健所)",
            "official_url": "https://www.pref.hokkaido.lg.jp/kz/kkd/minpaku/portal.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 145000000,
                "typical_renovation_capex_jpy": 12000000,
                "fire_license_upgrade_capex_jpy": 3800000,
                "peak_adr_jpy": 115000,
                "offpeak_adr_jpy": 42000,
                "peak_months": 4,
                "peak_occupancy_pct": 85,
                "offpeak_occupancy_pct": 45,
                "annual_fixed_opex_jpy": 2400000,
            },
        },
        {
            "id": "hakuba",
            "name": "Hakuba",
            "seo_short_name": "Hakuba",
            "japanese_name": "白馬村 (長野県)",
            "prefecture": "Nagano",
            "resort_category": "Ski & Alpine",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 105,
            "minpaku_ordinance_summary": (
                "Nagano Prefectural Article 18 Ordinance prohibits unhosted Minpaku statewide during all of May "
                "(May 1-31) and July 1-September 30 (green-season blackout), plus bans Monday noon through Saturday "
                "noon operation inside designated residential zones and within 100m of schools on school days."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Highly viable across Wadano, Echoland, Happo, and Goryu. Vast portions of Hakuba Village are "
                "Quasi-City Planning or unzoned alpine parcels without exclusive residential hotel bans, making 365-day "
                "Simple Lodging the standard vehicle to unlock summer MTB/hiking revenue and unlimited winter powder nights."
            ),
            "fire_safety_and_building_notes": (
                "Requires commercial automatic fire alarm system (Jikaho), emergency exit illumination, fire-retardant "
                "curtains/carpets, snow-load egress clearance, and Omachi Public Health Center inspection. Buildings "
                "exceeding 200 sqm converting from residential to lodging require Building Code change-of-use confirmation."
            ),
            "local_lodging_tax_notes": (
                "Nagano Prefecture + Hakuba Village accommodation tax framework applies (flat ¥200-¥300/person/night "
                "with low-rate exemptions)."
            ),
            "ordinance_jurisdiction": "Nagano Prefecture Tourism & Omachi Public Health Center (長野県観光スポーツ部 / 大町保健所)",
            "official_url": "https://www.pref.nagano.lg.jp/kankoki/sangyo/kanko/minpaku/jourei.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 85000000,
                "typical_renovation_capex_jpy": 8000000,
                "fire_license_upgrade_capex_jpy": 3200000,
                "peak_adr_jpy": 78000,
                "offpeak_adr_jpy": 32000,
                "peak_months": 4,
                "peak_occupancy_pct": 82,
                "offpeak_occupancy_pct": 42,
                "annual_fixed_opex_jpy": 1650000,
            },
        },
        {
            "id": "kyoto-city",
            "name": "Kyoto City",
            "seo_short_name": "Kyoto",
            "japanese_name": "京都市 (京都府)",
            "prefecture": "Kyoto",
            "resort_category": "Heritage",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 60,
            "minpaku_ordinance_summary": (
                "Japan's strictest municipal Minpaku ordinance: in Exclusive Residential zones, unhosted operation is "
                "restricted to January 15 noon through March 16 noon (~60 winter off-peak days—cherry blossom and autumn "
                "foliage are 100% prohibited), plus mandatory physical staff stationed within 800m and 10-minute arrival."
            ),
            "ryokan_365_feasibility": "Strict - High Barrier",
            "ryokan_365_zoning_notes": (
                "365-day Simple Lodging (Kyo-machiya Ichimune-gashi) is permitted ONLY in Commercial, Neighborhood "
                "Commercial, Quasi-Residential, or non-exclusive Residential zones without anti-hotel Special Use overlays, "
                "and requires Kyoto's neighborhood signage period plus an on-site or 800m/10-min staffed check-in desk."
            ),
            "fire_safety_and_building_notes": (
                "Kyoto City Medical Hygiene Center & Fire Department enforce hardwired Jikaho fire alarms, illuminated "
                "exterior emergency contact plaques, party-wall fireproofing on machiya townhouses, and face-to-face check-in."
            ),
            "local_lodging_tax_notes": (
                "Kyoto City Accommodation Tax: steeply progressive tiered rate (revised upward up to ¥1,000-¥10,000 "
                "per person/night for luxury ADR brackets)."
            ),
            "ordinance_jurisdiction": "Kyoto City Medical Hygiene Center - Lodging Desk (京都市医療衛生センター 宿泊施設適正化窓口)",
            "official_url": "https://www.city.kyoto.lg.jp/hokenfukushi/page/0000232956.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 92000000,
                "typical_renovation_capex_jpy": 11500000,
                "fire_license_upgrade_capex_jpy": 4500000,
                "peak_adr_jpy": 76000,
                "offpeak_adr_jpy": 48000,
                "peak_months": 7,
                "peak_occupancy_pct": 88,
                "offpeak_occupancy_pct": 68,
                "annual_fixed_opex_jpy": 2100000,
            },
        },
        {
            "id": "shibuya",
            "name": "Shibuya",
            "seo_short_name": "Shibuya",
            "japanese_name": "渋谷区 (東京都)",
            "prefecture": "Tokyo",
            "resort_category": "Urban & Metro",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 70,
            "minpaku_ordinance_summary": (
                "Shibuya Ward Ordinance severely restricts unhosted Minpaku in Exclusive Residential zones to school "
                "vacation windows only (roughly July 20-August 31 and late-December to early-January, ~65-70 days/yr), "
                "bans Bunkyo Educational Districts year-round, and requires prior neighbor notification."
            ),
            "ryokan_365_feasibility": "Strict - High Barrier",
            "ryokan_365_zoning_notes": (
                "365-day Ryokan-gyo (Simple Lodging or Boutique Hotel) is prohibited in Exclusive Residential pockets "
                "(Shoto, Yoyogi-Uehara residential blocks) and viable ONLY on Commercial, Neighborhood Commercial, or "
                "Class 2 Residential / Quasi-Industrial lots with full barrier-free and front-desk compliance."
            ),
            "fire_safety_and_building_notes": (
                "Shibuya Ward Public Health Center & Tokyo Fire Department enforce strict vertical fire compartmentation "
                "(Tokutei Shokaidan staircases on multi-story buildings), commercial Jikaho, 2-way egress, and staffed "
                "front-desk or ward-approved smart reception."
            ),
            "local_lodging_tax_notes": (
                "Tokyo Metropolitan Accommodation Tax applies (¥100-¥200/person/night on nightly rates >= ¥10,000)."
            ),
            "ordinance_jurisdiction": "Shibuya Ward Public Health Center Environmental Health Division (渋谷区保健所生活衛生課)",
            "official_url": "https://www.city.shibuya.tokyo.jp/kurashi/jutaku/minpaku/index.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 135000000,
                "typical_renovation_capex_jpy": 10000000,
                "fire_license_upgrade_capex_jpy": 4200000,
                "peak_adr_jpy": 68000,
                "offpeak_adr_jpy": 52000,
                "peak_months": 7,
                "peak_occupancy_pct": 89,
                "offpeak_occupancy_pct": 76,
                "annual_fixed_opex_jpy": 2300000,
            },
        },
        {
            "id": "shinjuku",
            "name": "Shinjuku",
            "seo_short_name": "Shinjuku",
            "japanese_name": "新宿区 (東京都)",
            "prefecture": "Tokyo",
            "resort_category": "Urban & Metro",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 104,
            "minpaku_ordinance_summary": (
                "Shinjuku Ward Article 18 Ordinance bans Minpaku operation in Exclusive Residential zones from Monday "
                "noon through Friday noon (allowing Friday noon to Monday noon weekends only, ~104 days/yr), alongside "
                "mandatory commercial waste collection contracts and neighbor disclosure prior to filing."
            ),
            "ryokan_365_feasibility": "Moderate - Zoning Dependent",
            "ryokan_365_zoning_notes": (
                "High-yield 365-day Simple Lodging is widely achieved across Commercial and Neighborhood Commercial "
                "corridors (Higashi-Shinjuku, Okubo, Yotsuya, Kagurazaka arterial frontages) in small multi-unit pencil "
                "buildings <200 sqm or purpose-built minpaku apartments."
            ),
            "fire_safety_and_building_notes": (
                "Shinjuku Ward Public Health Center requires strict Tokyo Fire Department Mixed-Use Building (Tokutei "
                "Ichidan) alarm compliance, emergency lighting, waste storage room separation, and video/in-person guest "
                "identity verification."
            ),
            "local_lodging_tax_notes": (
                "Tokyo Metropolitan Accommodation Tax (¥100-¥200/person/night)."
            ),
            "ordinance_jurisdiction": "Shinjuku Ward Public Health Center Sanitation Division (新宿区保健所衛生課)",
            "official_url": "https://www.city.shinjuku.lg.jp/seikatsu/ese02_002015.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 115000000,
                "typical_renovation_capex_jpy": 9000000,
                "fire_license_upgrade_capex_jpy": 3900000,
                "peak_adr_jpy": 62000,
                "offpeak_adr_jpy": 47000,
                "peak_months": 7,
                "peak_occupancy_pct": 90,
                "offpeak_occupancy_pct": 78,
                "annual_fixed_opex_jpy": 2050000,
            },
        },
        {
            "id": "taito-asakusa",
            "name": "Taito / Asakusa",
            "seo_short_name": "Asakusa",
            "japanese_name": "台東区・浅草 (東京都)",
            "prefecture": "Tokyo",
            "resort_category": "Urban & Metro",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 104,
            "minpaku_ordinance_summary": (
                "Taito Ward enforces one of Tokyo's toughest unhosted Minpaku ordinances: unless an administrator is "
                "stationed on-site (same building), operation is banned Monday noon through Saturday noon across the "
                "ward (~104 weekend nights/yr), protecting Asakusa and Ueno residential alleys."
            ),
            "ryokan_365_feasibility": "Strict - High Barrier",
            "ryokan_365_zoning_notes": (
                "Although nearly all of Asakusa and Kuramae sits in permissive Commercial zoning, Taito Ward's local "
                "Ryokan-gyo Ordinance mandates an on-site staffed front desk (Genkan Choba) with 24-hour personnel "
                "presence—blocking unmanned single-unit condos and favoring whole-building 4-to-12-suite boutique hotels."
            ),
            "fire_safety_and_building_notes": (
                "Taito Public Health Center rejects unmanned tablet-only check-in for most Simple Lodging conversions "
                "unless paired with continuous on-premises staff; Tokyo Fire Department requires interconnected Jikaho "
                "and smoke evacuation windows."
            ),
            "local_lodging_tax_notes": (
                "Tokyo Metropolitan Accommodation Tax (¥100-¥200/person/night)."
            ),
            "ordinance_jurisdiction": "Taito Ward Public Health Center Environmental Hygiene Division (台東区保健所生活衛生課)",
            "official_url": "https://www.city.taito.lg.jp/kenchiku/jutaku/minpaku/index.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 108000000,
                "typical_renovation_capex_jpy": 9500000,
                "fire_license_upgrade_capex_jpy": 4600000,
                "peak_adr_jpy": 58000,
                "offpeak_adr_jpy": 43000,
                "peak_months": 7,
                "peak_occupancy_pct": 89,
                "offpeak_occupancy_pct": 75,
                "annual_fixed_opex_jpy": 2450000,
            },
        },
        {
            "id": "chuo-osaka",
            "name": "Chuo Osaka",
            "seo_short_name": "Osaka Chuo",
            "japanese_name": "大阪市中央区・難波 (大阪府)",
            "prefecture": "Osaka",
            "resort_category": "Urban & Metro",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 165,
            "minpaku_ordinance_summary": (
                "Osaka City restricts standard 180-day Minpaku on weekdays within 100m of schools and inside strictly "
                "residential pockets. More importantly, Osaka City is Japan's primary National Strategic Special Zone "
                "(Tokku Minpaku / 特区民泊) hub allowing 365-day operation (minimum 2-night stay, >=25 sqm rooms) "
                "alongside full Simple Lodging permits—though new Tokku filings face heightened municipal scrutiny."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Chuo Ward (Shinsaibashi, Namba, Nipponbashi, Tanimachi) is overwhelmingly zoned Commercial, allowing "
                "both 1-night-minimum 365-day Simple Lodging (Kan'i Shukusho) and Special Zone 365-day apartments in "
                "buildings whose condo HOA bylaws explicitly authorize commercial hospitality."
            ),
            "fire_safety_and_building_notes": (
                "Osaka City Public Health Center & Osaka Municipal Fire Department require building-wide Jikaho "
                "automatic fire alarms (and sprinklers if lodging floor space reaches statutory multi-tenant thresholds), "
                "emergency multilingual signage, and 10-minute emergency response."
            ),
            "local_lodging_tax_notes": (
                "Osaka Prefectural Accommodation Tax (tiered ¥100-¥300/person/night; lower threshold revised to ¥5,000/night)."
            ),
            "ordinance_jurisdiction": "Osaka City Public Health Center Environmental Hygiene Group (大阪市保健所環境衛生監視課)",
            "official_url": "https://www.city.osaka.lg.jp/kenko/page/0000426656.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 68000000,
                "typical_renovation_capex_jpy": 6500000,
                "fire_license_upgrade_capex_jpy": 2900000,
                "peak_adr_jpy": 44000,
                "offpeak_adr_jpy": 32000,
                "peak_months": 7,
                "peak_occupancy_pct": 88,
                "offpeak_occupancy_pct": 74,
                "annual_fixed_opex_jpy": 1550000,
            },
        },
        {
            "id": "atami",
            "name": "Atami",
            "seo_short_name": "Atami",
            "japanese_name": "熱海市 (静岡県)",
            "prefecture": "Shizuoka",
            "resort_category": "Onsen & Mountain",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 140,
            "minpaku_ordinance_summary": (
                "Shizuoka Prefectural Minpaku Ordinance restricts weekday operation within school perimeters and "
                "designated residential/villa covenant zones. Crucially, many Atami ocean-view villas sit inside "
                "managed bessochi estates whose private HOA bylaws restrict or levy commercial lodging fees."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "365-day Simple Lodging performs strongly in Commercial, Second-Class Residential, and non-exclusive "
                "coastal hillside parcels outside anti-STR HOA covenants, backed by 45-minute Shinkansen Tokyo weekend demand."
            ),
            "fire_safety_and_building_notes": (
                "Atami Public Health Center & Fire Department inspect steep-slope cliff ordinance compliance (Gake Jorei), "
                "automatic fire alarms, and Legionella filtration/chlorination rules whenever natural onsen feeds guest tubs."
            ),
            "local_lodging_tax_notes": (
                "Atami City Accommodation Tax (¥200/person/night) plus Onsen Bath Tax (¥150/night)."
            ),
            "ordinance_jurisdiction": "Shizuoka Prefecture & Atami Public Health Center (静岡県衛生課 / 熱海保健所)",
            "official_url": "https://www.pref.shizuoka.jp/kurashi/seikatsu/eisei/1002536/1021232.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 58000000,
                "typical_renovation_capex_jpy": 6500000,
                "fire_license_upgrade_capex_jpy": 2900000,
                "peak_adr_jpy": 62000,
                "offpeak_adr_jpy": 38000,
                "peak_months": 5,
                "peak_occupancy_pct": 82,
                "offpeak_occupancy_pct": 58,
                "annual_fixed_opex_jpy": 1600000,
            },
        },
        {
            "id": "hakone",
            "name": "Hakone",
            "seo_short_name": "Hakone",
            "japanese_name": "箱根町 (神奈川県)",
            "prefecture": "Kanagawa",
            "resort_category": "Onsen & Mountain",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 95,
            "minpaku_ordinance_summary": (
                "Kanagawa Prefectural Minpaku Ordinance targets Hakone Town directly: unhosted Minpaku is heavily "
                "restricted inside Class 1 Low-Rise Residential zones overlaid with Hakone's Class 1 Tourist Villa "
                "Special Use Districts (Sengokuhara and Gora quiet zones), enforcing seasonal blackouts."
            ),
            "ryokan_365_feasibility": "Moderate - Zoning Dependent",
            "ryokan_365_zoning_notes": (
                "Parcel-level zoning verification is essential: Class 1 Tourist Villa Special Districts prohibit new "
                "commercial hotels, whereas Class 2 Tourist Villa Districts, Commercial zones (Hakone-Yumoto, Gora "
                "station front), and Second-Class Residential lots permit 365-day Simple Lodging."
            ),
            "fire_safety_and_building_notes": (
                "Odawara Public Health Center enforces Kanagawa Ryokan-gyo check-in booth + 10-minute on-site dispatch "
                "rules, Fuji-Hakone-Izu National Park exterior color rules, and sulfurous-gas resistant alarm sensors."
            ),
            "local_lodging_tax_notes": (
                "Onsen Bath Tax (¥150/adult/night) plus private thermal spring association monthly water supply fees."
            ),
            "ordinance_jurisdiction": "Kanagawa Prefecture & Odawara Public Health Center (神奈川県生活衛生課 / 小田原保健福祉事務所)",
            "official_url": "https://www.pref.kanagawa.jp/docs/e8z/cnt/f537269/index.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 72000000,
                "typical_renovation_capex_jpy": 8500000,
                "fire_license_upgrade_capex_jpy": 3300000,
                "peak_adr_jpy": 74000,
                "offpeak_adr_jpy": 44000,
                "peak_months": 6,
                "peak_occupancy_pct": 84,
                "offpeak_occupancy_pct": 60,
                "annual_fixed_opex_jpy": 1950000,
            },
        },
        {
            "id": "karuizawa",
            "name": "Karuizawa",
            "seo_short_name": "Karuizawa",
            "japanese_name": "軽井沢町 (長野県)",
            "prefecture": "Nagano",
            "resort_category": "Onsen & Mountain",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 75,
            "minpaku_ordinance_summary": (
                "Dual regulatory lock: Nagano Prefecture's Article 18 Ordinance bans May and ALL of July-September "
                "(Karuizawa's prime summer retreat season), plus Karuizawa Town's Nature Conservation Guidelines "
                "(Shizen Hogo Taisaku Yoko) require neighbor consent meetings and discourage unstaffed villa rentals."
            ),
            "ryokan_365_feasibility": "Strict - High Barrier",
            "ryokan_365_zoning_notes": (
                "Among Japan's hardest resort markets for unmanned STR. 365-day Ryokan-gyo is generally viable ONLY "
                "along Commercial corridors (Karuizawa/Naka-Karuizawa station areas) or with 24-hour on-site staff, "
                "1,000+ sqm lot minimums in sanctuary zones, and Town Committee clearance."
            ),
            "fire_safety_and_building_notes": (
                "Saku Public Health Center + Karuizawa Town Environment Division reject unmanned tablet check-in in "
                "villa forests and enforce a strict summer construction ban (July 25-August 31 zero noise/work rule)."
            ),
            "local_lodging_tax_notes": (
                "Nagano Prefecture + Karuizawa Town accommodation tax applies alongside private villa road maintenance fees."
            ),
            "ordinance_jurisdiction": "Karuizawa Town Environment Division & Saku Public Health Center (軽井沢町環境課 / 長野県佐久保健所)",
            "official_url": "https://www.town.karuizawa.lg.jp/www/contents/1525842900496/index.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 98000000,
                "typical_renovation_capex_jpy": 11000000,
                "fire_license_upgrade_capex_jpy": 5200000,
                "peak_adr_jpy": 82000,
                "offpeak_adr_jpy": 36000,
                "peak_months": 4,
                "peak_occupancy_pct": 80,
                "offpeak_occupancy_pct": 38,
                "annual_fixed_opex_jpy": 2300000,
            },
        },
        {
            "id": "fujikawaguchiko",
            "name": "Fujikawaguchiko",
            "seo_short_name": "Fujikawaguchiko",
            "japanese_name": "富士河口湖町 (山梨県)",
            "prefecture": "Yamanashi",
            "resort_category": "Onsen & Mountain",
            "minpaku_severity": "Green: Standard 180d",
            "effective_minpaku_days_typical": 180,
            "minpaku_ordinance_summary": (
                "Yamanashi Prefecture imposes no Article 18 statutory day-reduction ordinance; full 180-day operation "
                "is permitted. However, intense year-round inbound Mt. Fuji demand exhausts 180 nights in 6 months, "
                "leaving half the year idle unless upgraded to a 365-day Simple Lodging license."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "High feasibility across non-delineated (Hisenbiki) Urban Planning parcels around Lake Kawaguchi and "
                "Saiko, subject to Fujikawaguchiko Landscape Ordinance, Mt. Fuji World Heritage buffer height/color "
                "rules, and municipal prior neighbor consultation."
            ),
            "fire_safety_and_building_notes": (
                "Fuji-Tobu Public Health Center & Kawaguchiko Fire HQ inspect Jikaho alarms, propane gas interlocks, "
                "septic Johkasou upsizing (where sewer lines are absent), and freeze-protected piping."
            ),
            "local_lodging_tax_notes": (
                "Onsen bath tax applies to thermal facilities; municipal Mt. Fuji overtourism lodging tax advancing."
            ),
            "ordinance_jurisdiction": "Yamanashi Prefecture & Fuji-Tobu Public Health Center (山梨県衛生薬務課 / 富士・東部保健所)",
            "official_url": "https://www.pref.yamanashi.jp/eisei-ykm/minpaku/minpaku.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 64000000,
                "typical_renovation_capex_jpy": 7200000,
                "fire_license_upgrade_capex_jpy": 2800000,
                "peak_adr_jpy": 68000,
                "offpeak_adr_jpy": 45000,
                "peak_months": 7,
                "peak_occupancy_pct": 86,
                "offpeak_occupancy_pct": 64,
                "annual_fixed_opex_jpy": 1550000,
            },
        },
        {
            "id": "furano",
            "name": "Furano",
            "seo_short_name": "Furano",
            "japanese_name": "富良野市 (北海道)",
            "prefecture": "Hokkaido",
            "resort_category": "Ski & Alpine",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 165,
            "minpaku_ordinance_summary": (
                "Covered by Hokkaido Prefectural Article 18 Ordinance restricting weekday operation within 100m of "
                "schools. Because Furano enjoys dual peak seasons (winter ski + June-August lavender tourism), hitting "
                "the 180-day ceiling by mid-summer forces 5+ months of idle asset downtime without a Ryokan-gyo permit."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Kitanomine Resort Zone and mixed commercial/quasi-residential areas support 365-day Simple Lodging. "
                "Avoid Class 1/2 Low-Rise Exclusive Residential pockets and Agricultural Promotion Zones (Noshin Chiiki) "
                "where farmland conversion is blocked."
            ),
            "fire_safety_and_building_notes": (
                "Furano Public Health Center checks sanitary plumbing, linen storage, ICT check-in camera positioning, "
                "and Kamikawa Chubu Fire Union automatic fire alarm certification."
            ),
            "local_lodging_tax_notes": (
                "Combined Hokkaido Prefectural + Furano City tiered accommodation tax (¥200-¥500+ per guest/night)."
            ),
            "ordinance_jurisdiction": "Hokkaido Government & Furano Public Health Center (北海道 / 富良野保健所)",
            "official_url": "https://www.pref.hokkaido.lg.jp/kz/kkd/minpaku/portal.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 62000000,
                "typical_renovation_capex_jpy": 7000000,
                "fire_license_upgrade_capex_jpy": 2900000,
                "peak_adr_jpy": 64000,
                "offpeak_adr_jpy": 29000,
                "peak_months": 6,
                "peak_occupancy_pct": 80,
                "offpeak_occupancy_pct": 44,
                "annual_fixed_opex_jpy": 1450000,
            },
        },
        {
            "id": "nozawa-onsen",
            "name": "Nozawa Onsen",
            "seo_short_name": "Nozawa Onsen",
            "japanese_name": "野沢温泉村 (長野県)",
            "prefecture": "Nagano",
            "resort_category": "Ski & Alpine",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 100,
            "minpaku_ordinance_summary": (
                "Subject to Nagano Prefecture's Article 18 Ordinance banning unhosted Minpaku throughout May and "
                "July-September, alongside weekday prohibitions in residential zones and 100m school buffers."
            ),
            "ryokan_365_feasibility": "Moderate - Zoning Dependent",
            "ryokan_365_zoning_notes": (
                "365-day Simple Lodging is achievable in commercial and mixed village core parcels near Ogama and "
                "Nagasaka gondola, provided sewage capacity, narrow-road fire access, and village Yu-nakama hot-spring "
                "water rights are respected."
            ),
            "fire_safety_and_building_notes": (
                "Closely spaced timber lodges in heavy snow zones face strict Hokushin Fire Department review: wired "
                "Jikaho fire alarms, winter secondary 2nd/3rd floor escape routes, and fire-rated kitchen partitions."
            ),
            "local_lodging_tax_notes": (
                "Nozawa Onsen bath tax (Nyutozei, ¥150/night) plus Nagano prefectural accommodation tax."
            ),
            "ordinance_jurisdiction": "Nagano Prefecture & Hokushin Public Health Center (長野県 / 北信保健所)",
            "official_url": "https://www.pref.nagano.lg.jp/kankoki/sangyo/kanko/minpaku/jourei.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 68000000,
                "typical_renovation_capex_jpy": 9500000,
                "fire_license_upgrade_capex_jpy": 3400000,
                "peak_adr_jpy": 68000,
                "offpeak_adr_jpy": 26000,
                "peak_months": 4,
                "peak_occupancy_pct": 80,
                "offpeak_occupancy_pct": 34,
                "annual_fixed_opex_jpy": 1500000,
            },
        },
        {
            "id": "myoko",
            "name": "Myoko",
            "seo_short_name": "Myoko",
            "japanese_name": "妙高市 (新潟県)",
            "prefecture": "Niigata",
            "resort_category": "Ski & Alpine",
            "minpaku_severity": "Green: Standard 180d",
            "effective_minpaku_days_typical": 180,
            "minpaku_ordinance_summary": (
                "Niigata Prefecture (outside Niigata City) imposes no statutory Article 18 day-reduction or seasonal "
                "blackout ordinance on Myoko City; full 180-day Private Lodging Act allowance applies with winter snow "
                "and waste management contracts."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Akakura Onsen, Ikenotaira, and Suginohara base areas feature permissive commercial/quasi-residential "
                "or unzoned resort parcels. Converting aging pensions or chalets into 365-day Simple Lodging is highly "
                "capital-efficient."
            ),
            "fire_safety_and_building_notes": (
                "Joetsu Public Health Center oversees Ryokan-gyo licensing. Detached chalets <200 sqm avoid Building "
                "Code change-of-use confirmation while still requiring commercial fire alarms and snow-hooded exits."
            ),
            "local_lodging_tax_notes": (
                "Onsen bath tax (¥150/adult/night for properties connected to Akakura/Ikenotaira thermal springs)."
            ),
            "ordinance_jurisdiction": "Niigata Prefecture Sanitary Division & Joetsu Public Health Center (新潟県 / 上越保健所)",
            "official_url": "https://www.pref.niigata.lg.jp/sec/seikatsueisei/1356885478419.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 45000000,
                "typical_renovation_capex_jpy": 7500000,
                "fire_license_upgrade_capex_jpy": 2700000,
                "peak_adr_jpy": 56000,
                "offpeak_adr_jpy": 22000,
                "peak_months": 4,
                "peak_occupancy_pct": 78,
                "offpeak_occupancy_pct": 35,
                "annual_fixed_opex_jpy": 1350000,
            },
        },
        {
            "id": "takayama",
            "name": "Takayama",
            "seo_short_name": "Takayama",
            "japanese_name": "高山市 (岐阜県)",
            "prefecture": "Gifu",
            "resort_category": "Heritage",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 160,
            "minpaku_ordinance_summary": (
                "Gifu Prefecture requires documented prior neighborhood explanation and waste/emergency protocols on "
                "Minpaku filings. Heavy year-round European and Asian heritage tourism means whole-house machiya "
                "rentals exhaust 180 nights rapidly."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Takayama supports historic machiya conversions into whole-house Simple Lodging (Ichimune-gashi "
                "Kan'i Shukusho) across Commercial and Neighborhood Commercial streets near Sanmachi Suji and Takayama "
                "Station, subject to Historic Preservation District exterior facade rules."
            ),
            "fire_safety_and_building_notes": (
                "Hida Public Health Center & Takayama Fire Department focus on timber townhouse fire spread: "
                "interconnected Jikaho alarms, fire-rated party walls, illuminated exits, and 10-minute concierge hub."
            ),
            "local_lodging_tax_notes": (
                "Takayama City Accommodation Tax (tiered ¥100-¥300/person/night)."
            ),
            "ordinance_jurisdiction": "Gifu Prefecture & Hida Public Health Center (岐阜県生活衛生課 / 飛騨保健所)",
            "official_url": "https://www.pref.gifu.lg.jp/page/17488.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 44000000,
                "typical_renovation_capex_jpy": 8000000,
                "fire_license_upgrade_capex_jpy": 2900000,
                "peak_adr_jpy": 54000,
                "offpeak_adr_jpy": 33000,
                "peak_months": 6,
                "peak_occupancy_pct": 83,
                "offpeak_occupancy_pct": 56,
                "annual_fixed_opex_jpy": 1350000,
            },
        },
        {
            "id": "kanazawa",
            "name": "Kanazawa",
            "seo_short_name": "Kanazawa",
            "japanese_name": "金沢市 (石川県)",
            "prefecture": "Ishikawa",
            "resort_category": "Heritage",
            "minpaku_severity": "Red: Strict Weekday/School-Zone Ban",
            "effective_minpaku_days_typical": 104,
            "minpaku_ordinance_summary": (
                "Kanazawa City Minpaku Ordinance restricts weekday operation (Monday through Friday banned) inside "
                "Exclusive Residential zones and Traditional Environment Preservation areas (Higashi Chaya, Nagamachi "
                "samurai district perimeters), capping residential Minpaku to ~104 weekend/holiday days per year."
            ),
            "ryokan_365_feasibility": "Moderate - Zoning Dependent",
            "ryokan_365_zoning_notes": (
                "Whole-house Kanazawa Machiya 365-day Simple Lodging thrives in Commercial, Neighborhood Commercial, "
                "and Second-Class Residential corridors near Omicho Market, Kanazawa Station, and Korinbo—provided "
                "Landscape Ordinance lattice/roofing standards and neighborhood briefings are completed."
            ),
            "fire_safety_and_building_notes": (
                "Kanazawa City Public Health Center requires nearby check-in reception (within ~800m/10-min walk for "
                "dispersed machiya hospitality) or compliant ICT check-in, plus commercial Jikaho fire alarms."
            ),
            "local_lodging_tax_notes": (
                "Kanazawa City Accommodation Tax (¥200/person/night under ¥20,000; ¥500/person/night at >= ¥20,000)."
            ),
            "ordinance_jurisdiction": "Kanazawa City Public Health Center Hygiene Guidance Division (金沢市保健所衛生指導課)",
            "official_url": "https://www4.city.kanazawa.lg.jp/soshikikarasagasu/unei/gyomuannai/3/1/6291.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 48000000,
                "typical_renovation_capex_jpy": 8800000,
                "fire_license_upgrade_capex_jpy": 3100000,
                "peak_adr_jpy": 56000,
                "offpeak_adr_jpy": 34000,
                "peak_months": 6,
                "peak_occupancy_pct": 84,
                "offpeak_occupancy_pct": 58,
                "annual_fixed_opex_jpy": 1480000,
            },
        },
        {
            "id": "fukuoka-city",
            "name": "Fukuoka City",
            "seo_short_name": "Fukuoka",
            "japanese_name": "福岡市 (福岡県)",
            "prefecture": "Fukuoka",
            "resort_category": "Urban & Metro",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 165,
            "minpaku_ordinance_summary": (
                "Fukuoka City imposes strict neighborhood prior-notice, condo HOA written authorization proof, "
                "waste-disposal contracts, and school-zone rules on Minpaku filings rather than a citywide weekday "
                "blackout—yet high year-round Korean, Taiwanese, and domestic convention traffic makes a 180-day cap "
                "heavily restrictive."
            ),
            "ryokan_365_feasibility": "Moderate - Zoning Dependent",
            "ryokan_365_zoning_notes": (
                "365-day Ryokan-gyo (Hotel/Simple Lodging) in Hakata, Tenjin, Nakasu, and Watanabe-dori Commercial "
                "zones yields strong 80%+ annual occupancy, though Fukuoka City's strict anti-illegal-STR Ryokan "
                "Ordinance requires clear front-desk / lobby camera supervision or manned check-in hub."
            ),
            "fire_safety_and_building_notes": (
                "Fukuoka City Ward Health & Welfare Centers + Fire Prevention Bureau enforce strict building-wide "
                "fire alarm interlocks, exterior operator plates, and clear separation from long-term residential tenants."
            ),
            "local_lodging_tax_notes": (
                "Fukuoka City + Fukuoka Prefectural dual accommodation tax (¥200/night under ¥20,000; ¥500/night >= ¥20,000)."
            ),
            "ordinance_jurisdiction": "Fukuoka City Public Health & Medical Bureau - Living Hygiene Division (福岡市保健医療局生活衛生課)",
            "official_url": "https://www.city.fukuoka.lg.jp/hofuku/seikatsueisei/life/minpaku/minpaku.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 65000000,
                "typical_renovation_capex_jpy": 6800000,
                "fire_license_upgrade_capex_jpy": 3200000,
                "peak_adr_jpy": 43000,
                "offpeak_adr_jpy": 31000,
                "peak_months": 6,
                "peak_occupancy_pct": 87,
                "offpeak_occupancy_pct": 74,
                "annual_fixed_opex_jpy": 1580000,
            },
        },
        {
            "id": "naha",
            "name": "Naha",
            "seo_short_name": "Naha",
            "japanese_name": "那覇市 (沖縄県)",
            "prefecture": "Okinawa",
            "resort_category": "Coastal & Island",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 160,
            "minpaku_ordinance_summary": (
                "Naha City operates an independent municipal Public Health Center: Minpaku is restricted on school "
                "days within 100m of schools and inside designated residential pockets, with mandatory 10-minute "
                "on-island administrator response and strict typhoon/garbage compliance."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Commercial and Neighborhood Commercial districts along Kokusai-dori, Makishi, Miebashi, and "
                "Tomari ferry port (gateway to Kerama Islands) readily qualify for 365-day Simple Lodging condo-hotels "
                "and whole-floor family suites."
            ),
            "fire_safety_and_building_notes": (
                "Naha City Public Health Center & Naha Fire HQ require salt-corrosion resistant exterior fire bells, "
                "RC stairwell smoke doors, automatic fire alarms, and compliant tablet/video or staffed front desk."
            ),
            "local_lodging_tax_notes": (
                "Okinawa Prefecture + Naha City accommodation tax (~2% tiered levy rolling out)."
            ),
            "ordinance_jurisdiction": "Naha City Public Health Center Environmental Hygiene Division (那覇市保健所環境衛生課)",
            "official_url": "https://www.city.naha.okinawa.jp/nahahokenjyo/eisei/seikatueisei/minpaku.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 56000000,
                "typical_renovation_capex_jpy": 6200000,
                "fire_license_upgrade_capex_jpy": 2800000,
                "peak_adr_jpy": 46000,
                "offpeak_adr_jpy": 29000,
                "peak_months": 7,
                "peak_occupancy_pct": 85,
                "offpeak_occupancy_pct": 66,
                "annual_fixed_opex_jpy": 1450000,
            },
        },
        {
            "id": "ishigaki",
            "name": "Ishigaki",
            "seo_short_name": "Ishigaki",
            "japanese_name": "石垣市 (沖縄県)",
            "prefecture": "Okinawa",
            "resort_category": "Coastal & Island",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 165,
            "minpaku_ordinance_summary": (
                "Okinawa Prefectural Minpaku Ordinance restricts weekday operation within 100m of schools on school "
                "days. Extended March-November subtropical beach weather makes a 180-day ceiling severely "
                "yield-limiting compared to a 365-day Simple Lodging villa license."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Northern coastal villa belts (Kabira, Yonehara, Nosoko, Fusaki) lie largely outside restrictive "
                "residential zoning, enabling 365-day Simple Lodging pool villas—provided Agricultural Land Act "
                "(Nochi-ho Article 4/5 conversion) and Natural Park buffers are cleared pre-purchase."
            ),
            "fire_safety_and_building_notes": (
                "Yaeyama Public Health Center & Ishigaki Fire HQ require typhoon-rated reinforced concrete (RC) "
                "glazing, merged septic Johkasou environmental discharge approval, and commercial fire alarms."
            ),
            "local_lodging_tax_notes": (
                "Okinawa Prefecture + Ishigaki municipal accommodation tax (~2% tiered structure)."
            ),
            "ordinance_jurisdiction": "Okinawa Prefecture Hygiene Division & Yaeyama Public Health Center (沖縄県 / 八重山保健所)",
            "official_url": "https://www.pref.okinawa.jp/kurashi/kenko/eisei/1004624/1004632.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 76000000,
                "typical_renovation_capex_jpy": 7800000,
                "fire_license_upgrade_capex_jpy": 3100000,
                "peak_adr_jpy": 72000,
                "offpeak_adr_jpy": 39000,
                "peak_months": 7,
                "peak_occupancy_pct": 82,
                "offpeak_occupancy_pct": 52,
                "annual_fixed_opex_jpy": 1850000,
            },
        },
        {
            "id": "miyakojima",
            "name": "Miyakojima",
            "seo_short_name": "Miyakojima",
            "japanese_name": "宮古島市 (沖縄県)",
            "prefecture": "Okinawa",
            "resort_category": "Coastal & Island",
            "minpaku_severity": "Amber: Zone/Season Restricted",
            "effective_minpaku_days_typical": 165,
            "minpaku_ordinance_summary": (
                "Governed by Okinawa Prefectural Article 18 Ordinance (100m school perimeter weekday restrictions) "
                "plus Miyakojima groundwater conservation ordinances. Direct Shimojishima & Miyako airport flights "
                "from Tokyo, Seoul, and Hong Kong sustain 8+ months of luxury villa demand."
            ),
            "ryokan_365_feasibility": "High - Investor Friendly",
            "ryokan_365_zoning_notes": (
                "Irabu Island, Kurima, Ueno, and Gusukube coastal parcels sit predominantly in unzoned or non-exclusive "
                "areas ideal for 365-day Simple Lodging pool villas. Critical pre-purchase checks: Groundwater Source "
                "Protection Ordinance septic rules and Blue-Zone Agricultural Land exclusions."
            ),
            "fire_safety_and_building_notes": (
                "Miyako Public Health Center requires advanced nitrogen/phosphorus removal Johkasou tanks (protecting "
                "Miyakojima's coral aquifer), commercial Jikaho fire alarms, and certified 10-minute island dispatch."
            ),
            "local_lodging_tax_notes": (
                "Okinawa Prefecture + Miyakojima accommodation tax levy applies."
            ),
            "ordinance_jurisdiction": "Okinawa Prefecture Hygiene Division & Miyako Public Health Center (沖縄県 / 宮古保健所)",
            "official_url": "https://www.pref.okinawa.jp/kurashi/kenko/eisei/1004624/1004632.html",
            "secondary_mlit_url": MLIT_PORTAL_URL,
            "verified_at": VERIFICATION_TIMESTAMP,
            "benchmark_metrics": {
                "typical_price_jpy": 84000000,
                "typical_renovation_capex_jpy": 8200000,
                "fire_license_upgrade_capex_jpy": 3400000,
                "peak_adr_jpy": 84000,
                "offpeak_adr_jpy": 42000,
                "peak_months": 7,
                "peak_occupancy_pct": 83,
                "offpeak_occupancy_pct": 50,
                "annual_fixed_opex_jpy": 1950000,
            },
        },
    ]


def compute_yield_comparison(record: dict[str, Any], fx_rate: float = DEFAULT_FX_USD_JPY) -> dict[str, Any]:
    """Compute exact 180d Ordinance-Capped Minpaku vs 365d Ryokan-gyo underwriting metrics."""
    bm = record["benchmark_metrics"]
    price_jpy = int(bm["typical_price_jpy"])
    reno_jpy = int(bm["typical_renovation_capex_jpy"])
    fire_upgrade_jpy = int(bm["fire_license_upgrade_capex_jpy"])
    peak_adr = int(bm["peak_adr_jpy"])
    offpeak_adr = int(bm["offpeak_adr_jpy"])
    peak_months = int(bm["peak_months"])
    peak_occ = float(bm["peak_occupancy_pct"])
    offpeak_occ = float(bm["offpeak_occupancy_pct"])
    fixed_opex = int(bm["annual_fixed_opex_jpy"])
    minpaku_cap = int(record["effective_minpaku_days_typical"])

    peak_cal_days = round((peak_months / 12.0) * 365)
    offpeak_cal_days = 365 - peak_cal_days

    ryokan_peak_nights = round(peak_cal_days * (peak_occ / 100.0))
    ryokan_offpeak_nights = round(offpeak_cal_days * (offpeak_occ / 100.0))
    ryokan_total_nights = ryokan_peak_nights + ryokan_offpeak_nights

    max_allowed_peak_minpaku = round(minpaku_cap * 0.45) if minpaku_cap <= 95 else minpaku_cap
    minpaku_peak_nights = min(ryokan_peak_nights, max_allowed_peak_minpaku)
    rem_allowance = max(0, minpaku_cap - minpaku_peak_nights)
    minpaku_offpeak_nights = min(ryokan_offpeak_nights, rem_allowance)
    minpaku_total_nights = minpaku_peak_nights + minpaku_offpeak_nights

    minpaku_gross = minpaku_peak_nights * peak_adr + minpaku_offpeak_nights * offpeak_adr
    ryokan_gross = ryokan_peak_nights * peak_adr + ryokan_offpeak_nights * offpeak_adr

    minpaku_mgmt = round(minpaku_gross * (DEFAULT_MGMT_FEE_PCT / 100.0))
    ryokan_mgmt = round(ryokan_gross * (DEFAULT_MGMT_FEE_PCT / 100.0))

    minpaku_noi = minpaku_gross - minpaku_mgmt - fixed_opex
    ryokan_noi = ryokan_gross - ryokan_mgmt - fixed_opex

    closing_jpy = round(price_jpy * (DEFAULT_CLOSING_PCT / 100.0))
    basis_minpaku = price_jpy + closing_jpy + reno_jpy
    basis_ryokan = basis_minpaku + fire_upgrade_jpy

    yield_minpaku = (minpaku_noi / basis_minpaku) * 100.0 if basis_minpaku > 0 else 0.0
    yield_ryokan = (ryokan_noi / basis_ryokan) * 100.0 if basis_ryokan > 0 else 0.0
    noi_delta = ryokan_noi - minpaku_noi
    payback_months = round(fire_upgrade_jpy / (noi_delta / 12.0), 1) if noi_delta > 0 else 0.0

    return {
        "fx_rate": fx_rate,
        "minpaku_cap_days": minpaku_cap,
        "minpaku_peak_nights": minpaku_peak_nights,
        "minpaku_offpeak_nights": minpaku_offpeak_nights,
        "minpaku_total_nights": minpaku_total_nights,
        "ryokan_peak_nights": ryokan_peak_nights,
        "ryokan_offpeak_nights": ryokan_offpeak_nights,
        "ryokan_total_nights": ryokan_total_nights,
        "extra_nights": ryokan_total_nights - minpaku_total_nights,
        "minpaku_gross_jpy": minpaku_gross,
        "ryokan_gross_jpy": ryokan_gross,
        "minpaku_mgmt_jpy": minpaku_mgmt,
        "ryokan_mgmt_jpy": ryokan_mgmt,
        "fixed_opex_jpy": fixed_opex,
        "minpaku_noi_jpy": minpaku_noi,
        "ryokan_noi_jpy": ryokan_noi,
        "noi_delta_jpy": noi_delta,
        "basis_minpaku_jpy": basis_minpaku,
        "basis_ryokan_jpy": basis_ryokan,
        "fire_upgrade_jpy": fire_upgrade_jpy,
        "yield_minpaku_pct": round(yield_minpaku, 2),
        "yield_ryokan_pct": round(yield_ryokan, 2),
        "yield_lift_pct": round(yield_ryokan - yield_minpaku, 2),
        "payback_months": payback_months,
    }


def _fmt_jpy(val: float) -> str:
    n = round(val)
    sign = "-" if n < 0 else ""
    return f"{sign}¥{abs(n):,}"


def _fmt_usd(jpy_val: float, fx_rate: float = DEFAULT_FX_USD_JPY) -> str:
    n = round(jpy_val / fx_rate)
    sign = "-" if n < 0 else ""
    return f"{sign}${abs(n):,}"


def _fmt_dual(jpy_val: float, fx_rate: float = DEFAULT_FX_USD_JPY) -> str:
    return f"{_fmt_jpy(jpy_val)} ({_fmt_usd(jpy_val, fx_rate)})"


def _severity_classes(severity: str) -> tuple[str, str]:
    if severity.startswith("Green"):
        return "badge-green", "dot-green"
    if severity.startswith("Amber"):
        return "badge-amber", "dot-amber"
    return "badge-red", "dot-red"


def _feasibility_classes(feasibility: str) -> tuple[str, str]:
    if feasibility.startswith("High"):
        return "badge-green", "dot-green"
    if feasibility.startswith("Moderate"):
        return "badge-amber", "dot-amber"
    return "badge-red", "dot-red"


def render_market_html(record: dict[str, Any], all_records: list[dict[str, Any]]) -> str:
    """Render a clean SmartHR/Notion-compliant Programmatic SEO HTML page for a single market."""
    slug = record["id"]
    name = record["name"]
    short_name = record.get("seo_short_name", name)
    jp_name = record["japanese_name"]
    prefecture = record["prefecture"]
    category = record["resort_category"]
    canonical_url = f"{SITE_BASE_URL}/markets/{slug}.html"

    # Keep H1 strictly <= 7 words (4-6 words here)
    h1_text = f"{short_name} Airbnb & Ryokan Rules"
    assert len(h1_text.split()) <= 7, f"H1 exceeded 7 words: {h1_text}"

    uw = compute_yield_comparison(record)
    sev_badge, sev_dot = _severity_classes(record["minpaku_severity"])
    feas_badge, feas_dot = _feasibility_classes(record["ryokan_365_feasibility"])

    faq_entities = [
        {
            "q": f"Can foreigners run Airbnb 365 days in {name}?",
            "a": (
                f"Yes, foreign investors can legally purchase freehold property in {name} ({prefecture}) with zero "
                f"nationality restrictions, but operating 365 days per year requires obtaining a Hotel and Ryokan "
                f"Business Act Simple Lodging (Kan'i Shukusho / 簡易宿所) commercial permit from {record['ordinance_jurisdiction']}. "
                f"Current 365-day feasibility in {name} is rated '{record['ryokan_365_feasibility']}': {record['ryokan_365_zoning_notes']}"
            ),
        },
        {
            "q": f"What are {name} Minpaku ordinance caps and restricted seasons?",
            "a": (
                f"Under Japan's Private Lodging Business Act (Article 18 local ordinance authority), {name} is classified "
                f"as '{record['minpaku_severity']}', resulting in ~{uw['minpaku_cap_days']} effective operating days per year "
                f"(versus the 180-day national ceiling). Specifically: {record['minpaku_ordinance_summary']}"
            ),
        },
        {
            "q": f"180-day Minpaku vs 365-day Ryokan yield in {name}: what is the net return difference?",
            "a": (
                f"Based on {name} benchmark acquisition price ({_fmt_dual(record['benchmark_metrics']['typical_price_jpy'])}) "
                f"and peak ADR ({_fmt_dual(record['benchmark_metrics']['peak_adr_jpy'])}/night), an ordinance-capped Minpaku "
                f"registration yields {uw['yield_minpaku_pct']:.2f}% net cash-on-cash ({_fmt_dual(uw['minpaku_noi_jpy'])} NOI), "
                f"whereas a 365-day Simple Lodging license lifts net yield to {uw['yield_ryokan_pct']:.2f}% "
                f"({_fmt_dual(uw['ryokan_noi_jpy'])} NOI)—repaying the {_fmt_dual(uw['fire_upgrade_jpy'])} fire-code and "
                f"licensing upgrade in {uw['payback_months']:.1f} months."
            ),
        },
        {
            "q": f"What fire safety and front-desk rules apply to {name} short-term rentals?",
            "a": f"{record['fire_safety_and_building_notes']} Local tax note: {record['local_lodging_tax_notes']}",
        },
    ]

    faq_json_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["a"],
                },
            }
            for item in faq_entities
        ],
    }

    mail_subject = urllib.parse.quote(
        f"[Pre-Purchase Zoning Check] {name} ({prefecture}) - 365d Ryokan-gyo Feasibility"
    )
    mail_body = urllib.parse.quote(
        "\n".join(
            [
                f"Pre-Purchase Zoning & 365-Day Ryokan-gyo Inquiry — {name} ({jp_name})",
                "----------------------------------------------------------------------",
                f"Target Market: {name} ({prefecture})",
                f"Competent Authority: {record['ordinance_jurisdiction']}",
                f"Benchmark Basis: {_fmt_dual(uw['basis_ryokan_jpy'])} | Simulated 365d Yield: {uw['yield_ryokan_pct']:.2f}%",
                "",
                "Property Listing URL or Cadastral Chiban (地番):",
                "[Paste listing link or address here]",
                "",
                "Requested Scope:",
                "- Bilingual Gyoseishoshi Yoto Chiiki & Hokenjo 365-day Simple Lodging pre-check",
                "- Jikaho commercial fire-alarm & Building Code (>200 sqm) retrofit estimate",
                "- Local bilingual STR management & 10-min Kake-tsuke operator introduction",
            ]
        )
    )
    mailto_href = f"mailto:{INTAKE_EMAIL}?subject={mail_subject}&body={mail_body}"

    peer_links_html = "\n".join(
        f'          <a href="./{html.escape(r["id"])}.html" class="peer-market-link'
        f'{" active-peer" if r["id"] == slug else ""}">'
        f'{html.escape(r["name"])} <span>({html.escape(r["prefecture"])})</span></a>'
        for r in all_records
    )

    faq_visible_html = "\n".join(
        f'        <div class="faq-item">\n'
        f'          <h3>{html.escape(item["q"])}</h3>\n'
        f'          <p>{html.escape(item["a"])}</p>\n'
        f"        </div>"
        for item in faq_entities
    )

    meta_desc = (
        f"{name} ({prefecture}) short-term rental zoning guide: {record['minpaku_severity']} "
        f"(~{uw['minpaku_cap_days']}d/yr) vs 365-day Ryokan-gyo yield ({uw['yield_minpaku_pct']:.2f}% to "
        f"{uw['yield_ryokan_pct']:.2f}%), fire code, and bilingual Gyoseishoshi parcel check."
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-F0ZLS15LNQ"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-F0ZLS15LNQ');
    document.addEventListener('click', function(e) {{
      var el = e.target && e.target.closest ? e.target.closest('a, button') : null;
      if (!el || typeof gtag !== 'function') return;
      var label = (el.textContent || '').trim().slice(0, 60);
      var href = el.getAttribute('href') || '';
      if (el.id || (href && href.indexOf('http') === 0)) {{
        gtag('event', 'cta_engagement', {{
          element_id: el.id || 'link',
          element_text: label,
          link_url: href,
          page_path: location.pathname
        }});
      }}
    }});
  </script>
  <title>{html.escape(name)} Airbnb &amp; 365-Day Ryokan Zoning Guide ({html.escape(prefecture)}) | Japan STR Atlas</title>
  <meta name="description" content="{html.escape(meta_desc)}" />
  <link rel="canonical" href="{html.escape(canonical_url)}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Noto+Sans+JP:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap"
    rel="stylesheet"
  />
  <link rel="stylesheet" href="../style.css" />
  <script type="application/ld+json">
{json.dumps(faq_json_ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body>
  <header class="site-navbar">
    <div class="container navbar-inner">
      <a href="../index.html" class="brand-mark">Japan Resort STR Atlas</a>
      <nav class="top-nav" aria-label="Market guide navigation">
        <a href="../index.html#explorer" class="nav-link">All 20 Markets</a>
        <a href="../index.html?market={html.escape(slug)}#simulator" class="nav-link">Interactive Calculator</a>
        <a href="{html.escape(mailto_href)}" id="navMarketCheckCta" class="nav-link nav-cta">Parcel Zoning Check</a>
      </nav>
    </div>
  </header>

  <main class="container main-content">
    <section class="section-block">
      <div class="breadcrumb-row">
        <a href="../index.html">Japan STR Atlas</a>
        <span>/</span>
        <span>{html.escape(prefecture)}</span>
        <span>/</span>
        <span>{html.escape(name)} ({html.escape(jp_name)})</span>
      </div>

      <div class="hero-compact">
        <div>
          <h1>{html.escape(h1_text)}</h1>
          <p class="page-lead">
            Compare {uw['minpaku_cap_days']}-day effective Minpaku limits and 365-day Ryokan permits in {html.escape(name)}, {html.escape(prefecture)}.
          </p>
        </div>
        <div class="market-cta-group">
          <a href="../index.html?market={html.escape(slug)}#simulator" id="btnOpenInteractiveSim" class="btn-secondary">
            Customize in Calculator
          </a>
          <a href="{html.escape(mailto_href)}" id="btnMarketZoningCta" class="btn-primary">
            Request Zoning &amp; Scrivener Check
          </a>
        </div>
      </div>

      <div class="surface-card market-Yield-card">
        <div class="badge-row market-top-badges">
          <span class="badge badge-cat">{html.escape(category)} &middot; {html.escape(jp_name)}</span>
          <span class="badge {sev_badge}"><span class="status-dot {sev_dot}" aria-hidden="true"></span>Minpaku: {html.escape(record['minpaku_severity'])}</span>
          <span class="badge {feas_badge}"><span class="status-dot {feas_dot}" aria-hidden="true"></span>365d Ryokan: {html.escape(record['ryokan_365_feasibility'])}</span>
        </div>

        <div class="alpha-summary">
          <div class="alpha-metric">
            <span class="alpha-label">365d Annual NOI Gain</span>
            <strong class="alpha-value">{'+' if uw['noi_delta_jpy'] >= 0 else ''}{html.escape(_fmt_jpy(uw['noi_delta_jpy']))}</strong>
            <span class="alpha-sub">{'+' if uw['noi_delta_jpy'] >= 0 else ''}{html.escape(_fmt_usd(uw['noi_delta_jpy']))} / yr at &yen;{int(DEFAULT_FX_USD_JPY)}/$</span>
          </div>
          <div class="alpha-metric">
            <span class="alpha-label">Net Cash-on-Cash Yield</span>
            <strong class="alpha-value">{uw['yield_minpaku_pct']:.2f}% &rarr; {uw['yield_ryokan_pct']:.2f}%</strong>
            <span class="alpha-sub">+{uw['extra_nights']} bookable nights/yr unlocked</span>
          </div>
          <div class="alpha-metric">
            <span class="alpha-label">Fire-Code CapEx Payback</span>
            <strong class="alpha-value">{uw['payback_months']:.1f} mos</strong>
            <span class="alpha-sub">Upgrade cost: {html.escape(_fmt_dual(uw['fire_upgrade_jpy']))}</span>
          </div>
        </div>

        <h2 class="subtable-heading">180-Day Minpaku vs 365-Day Ryokan-gyo Benchmark Yield ({html.escape(name)})</h2>
        <div class="table-wrap flat-table-wrap">
          <table class="ledger-table">
            <thead>
              <tr>
                <th>Underwriting Line Item (FX &yen;{int(DEFAULT_FX_USD_JPY)}/USD)</th>
                <th>180d Minpaku (Local Cap)</th>
                <th>365d Ryokan-gyo (Simple Lodging)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Legal Operating Ceiling</td>
                <td>~{uw['minpaku_cap_days']} days/yr (Ordinance Cap)</td>
                <td>365 days/yr (Commercial Permit)</td>
              </tr>
              <tr>
                <td>Realized Booked Nights (Peak / Off-Peak)</td>
                <td>{uw['minpaku_total_nights']} nights ({uw['minpaku_peak_nights']}p / {uw['minpaku_offpeak_nights']}o)</td>
                <td>{uw['ryokan_total_nights']} nights ({uw['ryokan_peak_nights']}p / {uw['ryokan_offpeak_nights']}o)</td>
              </tr>
              <tr>
                <td>Benchmark ADR (Peak / Off-Peak)</td>
                <td>{html.escape(_fmt_jpy(record['benchmark_metrics']['peak_adr_jpy']))} / {html.escape(_fmt_jpy(record['benchmark_metrics']['offpeak_adr_jpy']))}</td>
                <td>{html.escape(_fmt_jpy(record['benchmark_metrics']['peak_adr_jpy']))} / {html.escape(_fmt_jpy(record['benchmark_metrics']['offpeak_adr_jpy']))}</td>
              </tr>
              <tr>
                <td>Gross Annual Booking Revenue</td>
                <td>{html.escape(_fmt_dual(uw['minpaku_gross_jpy']))}</td>
                <td>{html.escape(_fmt_dual(uw['ryokan_gross_jpy']))}</td>
              </tr>
              <tr>
                <td>STR Management &amp; OTA Fees ({int(DEFAULT_MGMT_FEE_PCT)}%)</td>
                <td>-{html.escape(_fmt_dual(uw['minpaku_mgmt_jpy']))}</td>
                <td>-{html.escape(_fmt_dual(uw['ryokan_mgmt_jpy']))}</td>
              </tr>
              <tr>
                <td>Annual Fixed OpEx &amp; Property Tax</td>
                <td>-{html.escape(_fmt_dual(uw['fixed_opex_jpy']))}</td>
                <td>-{html.escape(_fmt_dual(uw['fixed_opex_jpy']))}</td>
              </tr>
              <tr class="row-highlight">
                <td>Net Operating Income (Annual NOI)</td>
                <td>{html.escape(_fmt_dual(uw['minpaku_noi_jpy']))}</td>
                <td>{html.escape(_fmt_dual(uw['ryokan_noi_jpy']))}</td>
              </tr>
              <tr>
                <td>Total Capital Basis (Price + 7% Closing + CapEx)</td>
                <td>{html.escape(_fmt_dual(uw['basis_minpaku_jpy']))}</td>
                <td>{html.escape(_fmt_dual(uw['basis_ryokan_jpy']))} (incl. Fire/Permit)</td>
              </tr>
              <tr class="row-Total">
                <td>Net Cash-on-Cash Yield (%)</td>
                <td>{uw['yield_minpaku_pct']:.2f}%</td>
                <td>{uw['yield_ryokan_pct']:.2f}%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="calc-cta-row">
          <p>
            Model custom purchase price, renovation budget, and occupancy for your specific {html.escape(name)} property.
          </p>
          <a href="../index.html?market={html.escape(slug)}#simulator" id="btnCustomizeModelBottom" class="btn-secondary">
            Open Interactive {html.escape(short_name)} Yield Calculator
          </a>
        </div>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <h2>Statutory Zoning, Fire Code &amp; Official Ordinance Breakdown</h2>
        <p class="section-desc">
          Competent authority: {html.escape(record['ordinance_jurisdiction'])} &middot; Verified {html.escape(record['verified_at'][:10])}
        </p>
      </div>

      <div class="detail-grid-2">
        <article class="surface-card">
          <h3 class="sheet-heading">1. Private Lodging Act (180d Minpaku) &amp; Article 18 Rules</h3>
          <p>{html.escape(record['minpaku_ordinance_summary'])}</p>
        </article>

        <article class="surface-card">
          <h3 class="sheet-heading">2. 365-Day Ryokan-gyo (簡易宿所) Parcel Feasibility</h3>
          <p>{html.escape(record['ryokan_365_zoning_notes'])}</p>
        </article>

        <article class="surface-card">
          <h3 class="sheet-heading">3. Fire Service Act (Jikah&#333;) &amp; Building Standards</h3>
          <p>{html.escape(record['fire_safety_and_building_notes'])}</p>
        </article>

        <article class="surface-card">
          <h3 class="sheet-heading">4. Accommodation Tax &amp; Official Citations</h3>
          <p>{html.escape(record['local_lodging_tax_notes'])}</p>
          <p class="citation-links">
            <strong>Official Portal:</strong>
            <a href="{html.escape(record['official_url'])}" target="_blank" rel="noopener noreferrer">{html.escape(record['official_url'])}</a><br />
            <strong>MLIT National Registry:</strong>
            <a href="{html.escape(record['secondary_mlit_url'])}" target="_blank" rel="noopener noreferrer">{html.escape(record['secondary_mlit_url'])}</a>
          </p>
        </article>
      </div>
    </section>

    <section class="section-block">
      <div class="surface-card cta-banner-card">
        <div>
          <h2>Verify a {html.escape(name)} Listing Before Signing a Purchase Agreement</h2>
          <p class="section-desc">
            Send the property link or cadastral lot number (<em>Chiban</em> / 地番) to coordinate a pre-purchase Urban Planning Act
            <em>Y&#333;to Chiiki</em> check, <em>Hokenjo</em> 365-day Simple Lodging consult, and <em>Jikah&#333;</em> fire-alarm quote with a bilingual <em>Gy&#333;seishoshi</em>.
          </p>
        </div>
        <div class="cta-banner-actions">
          <a href="{html.escape(mailto_href)}" id="btnBottomScrivenerEmail" class="btn-primary">
            Email Pre-Purchase Zoning Desk ({html.escape(INTAKE_EMAIL)})
          </a>
          <a href="../index.html?market={html.escape(slug)}#zoning-desk" id="btnBottomBriefBuilder" class="btn-secondary">
            Build Custom Bilingual Sheet
          </a>
        </div>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <h2>Frequently Asked Questions: {html.escape(name)} Short-Term Rentals</h2>
      </div>
      <div class="surface-card faq-list">
{faq_visible_html}
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <h2>Explore All 20 Japan STR &amp; Ryokan Jurisdictions</h2>
      </div>
      <div class="peer-market-grid">
{peer_links_html}
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <strong class="footer-brand">Japan Resort STR Atlas</strong>
        <p class="footer-copy">
          Compiled from Prefectural &amp; Municipal Private Lodging Act (Article 18) ordinances, Public Health Center Ryokan-gyo rules, and the MLIT Minpaku Portal.
        </p>
      </div>
      <div class="footer-disclaimer">
        <strong>Legal Disclaimer:</strong> Figures and ordinance summaries are for preliminary investment research only and do not constitute legal or tax advice. Confirm parcel-level <em>Y&#333;to Chiiki</em> boundaries, road frontage, and HOA bylaws with a licensed <em>Gy&#333;seishoshi</em> prior to purchase.
      </div>
    </div>
  </footer>
</body>
</html>
"""


def render_sitemap_xml(records: list[dict[str, Any]]) -> str:
    """Build valid XML sitemap covering index.html + all 20 market static pages (21 URLs)."""
    lastmod = VERIFICATION_TIMESTAMP[:10]
    urls = [
        (f"{SITE_BASE_URL}/", "1.0", "weekly"),
        *(
            (f"{SITE_BASE_URL}/markets/{r['id']}.html", "0.8", "weekly")
            for r in records
        ),
    ]
    entries = "\n".join(
        f"  <url>\n"
        f"    <loc>{html.escape(loc)}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"    <priority>{prio}</priority>\n"
        f"  </url>"
        for loc, prio, freq in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )


def validate_url(url: str, field_name: str, resort_name: str) -> list[str]:
    """Ensure citation URLs use HTTPS and resolve to official Japanese government domains."""
    errors: list[str] = []
    parsed = urlparse(url)
    if parsed.scheme != "https":
        errors.append(f"{resort_name}: {field_name} must use https:// scheme (got {url!r})")
    host = (parsed.netloc or "").lower()
    if not host or not GOV_DOMAIN_RE.search(host):
        errors.append(
            f"{resort_name}: {field_name} must point to an official Japanese government domain (got {url!r})"
        )
    return errors


def validate_record(record: dict[str, Any]) -> list[str]:
    """Validate structural, legal, and financial fields on a single municipality record."""
    errors: list[str] = []
    name = str(record.get("name", "<missing>"))

    required_str_fields = [
        "id",
        "name",
        "japanese_name",
        "prefecture",
        "resort_category",
        "minpaku_severity",
        "minpaku_ordinance_summary",
        "ryokan_365_feasibility",
        "ryokan_365_zoning_notes",
        "fire_safety_and_building_notes",
        "local_lodging_tax_notes",
        "ordinance_jurisdiction",
        "official_url",
        "secondary_mlit_url",
        "verified_at",
    ]
    for field in required_str_fields:
        val = record.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"{name}: missing or empty string field '{field}'")

    if record.get("resort_category") not in VALID_CATEGORIES:
        errors.append(f"{name}: invalid resort_category {record.get('resort_category')!r}")

    if record.get("minpaku_severity") not in VALID_MINPAKU_SEVERITIES:
        errors.append(f"{name}: invalid minpaku_severity {record.get('minpaku_severity')!r}")

    if record.get("ryokan_365_feasibility") not in VALID_RYOKAN_FEASIBILITY:
        errors.append(f"{name}: invalid ryokan_365_feasibility {record.get('ryokan_365_feasibility')!r}")

    eff_days = record.get("effective_minpaku_days_typical")
    if not isinstance(eff_days, int) or not (1 <= eff_days <= 180):
        errors.append(f"{name}: effective_minpaku_days_typical must be int in 1..180 (got {eff_days!r})")

    if isinstance(record.get("official_url"), str):
        errors.extend(validate_url(record["official_url"], "official_url", name))
    if isinstance(record.get("secondary_mlit_url"), str):
        errors.extend(validate_url(record["secondary_mlit_url"], "secondary_mlit_url", name))

    verified_at = record.get("verified_at", "")
    try:
        datetime.fromisoformat(str(verified_at).replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{name}: verified_at is not valid ISO-8601 ({verified_at!r})")

    metrics = record.get("benchmark_metrics")
    if not isinstance(metrics, dict):
        errors.append(f"{name}: benchmark_metrics must be a dict")
    else:
        required_metric_bounds = {
            "typical_price_jpy": (10_000_000, 500_000_000),
            "typical_renovation_capex_jpy": (1_000_000, 100_000_000),
            "fire_license_upgrade_capex_jpy": (500_000, 30_000_000),
            "peak_adr_jpy": (10_000, 500_000),
            "offpeak_adr_jpy": (5_000, 300_000),
            "peak_months": (1, 11),
            "peak_occupancy_pct": (20, 98),
            "offpeak_occupancy_pct": (10, 95),
            "annual_fixed_opex_jpy": (300_000, 20_000_000),
        }
        for m_key, (low, high) in required_metric_bounds.items():
            m_val = metrics.get(m_key)
            if not isinstance(m_val, (int, float)) or not (low <= m_val <= high):
                errors.append(f"{name}: benchmark_metrics.{m_key}={m_val!r} outside [{low}, {high}]")

    return errors


def build_dataset() -> dict[str, Any]:
    """Assemble full validated dataset payload with summary metadata."""
    records = get_raw_ordinance_records()
    severity_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for rec in records:
        sev = rec["minpaku_severity"]
        cat = rec["resort_category"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_minpaku_cap = round(
        sum(r["effective_minpaku_days_typical"] for r in records) / len(records), 1
    )

    return {
        "schema_version": "1.1.0",
        "generated_at": VERIFICATION_TIMESTAMP,
        "national_statute_reference": {
            "minpaku_act": "Private Lodging Business Act (住宅宿泊事業法, Act No. 65 of 2017, Article 18 Local Ordinance Authority)",
            "ryokan_act": "Hotel and Ryokan Business Act (旅館業法, Act No. 138 of 1948, Simple Lodging / 簡易宿所営業)",
            "mlit_portal_url": MLIT_PORTAL_URL,
        },
        "summary": {
            "total_resorts": len(records),
            "average_effective_minpaku_cap_days": avg_minpaku_cap,
            "ryokan_standard_operating_days": 365,
            "by_severity": severity_counts,
            "by_category": category_counts,
        },
        "resorts": records,
    }


def validate_dataset(dataset: dict[str, Any]) -> list[str]:
    """Run full cross-dataset integrity and citation verification."""
    errors: list[str] = []
    resorts = dataset.get("resorts")
    if not isinstance(resorts, list):
        return ["Dataset missing 'resorts' list"]

    found_names = [r.get("name") for r in resorts]
    if found_names != EXPECTED_RESORTS:
        missing = [n for n in EXPECTED_RESORTS if n not in found_names]
        extra = [n for n in found_names if n not in EXPECTED_RESORTS]
        errors.append(
            f"Resort coverage mismatch: count={len(found_names)}, missing={missing}, extra={extra}"
        )

    seen_ids: set[str] = set()
    for rec in resorts:
        rec_id = rec.get("id", "")
        if rec_id in seen_ids:
            errors.append(f"Duplicate resort id: {rec_id!r}")
        seen_ids.add(rec_id)
        errors.extend(validate_record(rec))

    return errors


def compile_ordinances(
    output_json_path: Path,
    output_bundle_js_path: Path | None = None,
) -> dict[str, Any]:
    """Validate and write resort_ordinances.json (and optional JS fallback bundle)."""
    dataset = build_dataset()
    errors = validate_dataset(dataset)
    if errors:
        raise ValueError("Ordinance verification failed:\n  - " + "\n  - ".join(errors))

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(dataset, ensure_ascii=False, indent=2) + "\n"
    output_json_path.write_text(serialized, encoding="utf-8")

    if output_bundle_js_path is not None:
        output_bundle_js_path.parent.mkdir(parents=True, exist_ok=True)
        bundle_content = (
            "// Auto-generated by pipeline/ordinance_verifier.py - Do not edit manually.\n"
            f"window.__RESORT_ORDINANCES_DATA__ = {json.dumps(dataset, ensure_ascii=False, indent=2)};\n"
        )
        output_bundle_js_path.write_text(bundle_content, encoding="utf-8")

    return dataset


def generate_seo_pages_and_sitemap(dataset: dict[str, Any], site_dir: Path) -> list[Path]:
    """Generate 20 static market HTML pages under site/markets/ and site/sitemap.xml."""
    resorts = dataset["resorts"]
    markets_dir = site_dir / "markets"
    markets_dir.mkdir(parents=True, exist_ok=True)

    expected_filenames = {f"{r['id']}.html" for r in resorts}
    for stale in markets_dir.glob("*.html"):
        if stale.name not in expected_filenames:
            stale.unlink()

    written_pages: list[Path] = []
    for rec in resorts:
        page_path = markets_dir / f"{rec['id']}.html"
        page_html = render_market_html(rec, resorts)
        page_path.write_text(page_html, encoding="utf-8")
        written_pages.append(page_path)

    sitemap_path = site_dir / "sitemap.xml"
    sitemap_path.write_text(render_sitemap_xml(resorts), encoding="utf-8")
    return written_pages


def validate_seo_artifacts(dataset: dict[str, Any], site_dir: Path) -> list[str]:
    """Verify all 20 static market pages, FAQPage JSON-LD, GA4 tag, and 21-URL sitemap.xml."""
    errors: list[str] = []
    markets_dir = site_dir / "markets"
    sitemap_path = site_dir / "sitemap.xml"

    if not sitemap_path.is_file():
        errors.append(f"Missing sitemap.xml at {sitemap_path}")
    else:
        sm_text = sitemap_path.read_text(encoding="utf-8")
        loc_count = sm_text.count("<loc>")
        if loc_count != len(dataset["resorts"]) + 1:
            errors.append(f"Expected {len(dataset['resorts']) + 1} <loc> entries in sitemap.xml, got {loc_count}")

    for rec in dataset["resorts"]:
        slug = rec["id"]
        p = markets_dir / f"{slug}.html"
        if not p.is_file():
            errors.append(f"Missing market SEO page: {p}")
            continue
        txt = p.read_text(encoding="utf-8")
        for marker in (
            "G-F0ZLS15LNQ",
            "cta_engagement",
            '"@type": "FAQPage"',
            f"mailto:{INTAKE_EMAIL}",
            f"../index.html?market={slug}",
            f"{SITE_BASE_URL}/markets/{slug}.html",
        ):
            if marker not in txt:
                errors.append(f"{p.name}: missing required SEO/analytics marker {marker!r}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify and compile Japan Resort Minpaku & 365-Day Ryokan-gyo ordinances + 20 SEO pages."
    )
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--output",
        type=Path,
        default=default_root / "site" / "data" / "resort_ordinances.json",
        help="Destination path for compiled resort_ordinances.json",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate existing JSON output, 20 market HTML pages, and sitemap.xml on disk",
    )
    args = parser.parse_args(argv)

    site_dir = args.output.resolve().parent.parent

    if args.check:
        if not args.output.exists():
            print(f"[ERROR] File not found: {args.output}", file=sys.stderr)
            return 1
        disk_data = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate_dataset(disk_data)
        if (site_dir / "index.html").is_file():
            errors.extend(validate_seo_artifacts(disk_data, site_dir))
        if errors:
            for err in errors:
                print(f"[ERROR] {err}", file=sys.stderr)
            return 1
        print(
            f"[OK] Verified {len(disk_data['resorts'])} resort ordinance records, "
            f"20 market pages, and sitemap.xml in {site_dir}"
        )
        return 0

    bundle_js = args.output.parent / "resort_ordinances_bundle.js"
    dataset = compile_ordinances(args.output, bundle_js)
    written_pages = generate_seo_pages_and_sitemap(dataset, site_dir)
    seo_errors = validate_seo_artifacts(dataset, site_dir)
    if seo_errors:
        raise ValueError("SEO page verification failed:\n  - " + "\n  - ".join(seo_errors))

    summary = dataset["summary"]
    print(
        f"[OK] Compiled {summary['total_resorts']} resorts -> {args.output}, "
        f"generated {len(written_pages)} market HTML pages + sitemap.xml "
        f"(Avg effective Minpaku cap: {summary['average_effective_minpaku_cap_days']}d vs 365d Ryokan-gyo)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
