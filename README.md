# Japan Resort STR & 365-Day Ryokan Zoning Atlas (`05_minpaku_english_map`)

An interactive English regulatory intelligence portal and **180-Day Minpaku vs. 365-Day Simple Lodging (簡易宿所) Net Yield & Fire-Code CapEx Calculator** built for cross-border real estate investors evaluating Japanese ski, onsen, coastal island, and heritage resort properties.

---

## Why This Moat Exists

Foreign buyers acquiring chalets in **Hakuba**, **Niseko**, **Furano**, **Myoko**, or villas in **Atami**, **Hakone**, **Fujikawaguchiko**, **Ishigaki**, and **Miyakojima** face a massive Japanese regulatory blind spot:

1. **Fragmented Japanese-Only PDF Ordinances**: While Japan's national Private Lodging Business Act (*Jūtaku Shukuhaku Jigyō-hō*) sets a 180-day ceiling, Article 18 empowers prefectures and municipalities to enact strict local *Uwano-se* ordinances (e.g., Nagano banning May and July–September statewide; Kyoto residential zones restricting rentals to ~60 winter days; Otaru banning weekdays in residential zones).
2. **The 365-Day *Kan'i Shukusho* Arbitrage**: Securing a full **Hotel & Ryokan Business Act (Simple Lodging / 簡易宿所営業)** license from the local Public Health Center (*Hokenjo*) removes the 180-day ceiling and unlocks 365-day commercial operation—provided parcel zoning (*Yōto Chiiki*), commercial fire alarms (*Jikahō*), and check-in rules are verified **before** signing a Purchase & Sale Agreement.
3. **High-Ticket B2B Referral Monetization (Zero Checkout / Zero 特商法 Needed)**: Because the portal collects no upfront payments from visitors and refers high-intent foreign buyers to licensed bilingual **Administrative Scriveners (*Gyōseishoshi* / 行政書士)**, fire-equipment contractors, and local STR management operators, it operates as a pure professional lead-generation asset.

---

## Directory Structure

```text
05_minpaku_english_map/
├── .github/
│   └── workflows/
│       └── deploy.yml                  # Automated Python dataset + SEO pages check + GitHub Pages deploy
├── pipeline/
│   └── ordinance_verifier.py           # Compiles 20 market records, 20 static SEO pages & sitemap.xml
├── site/
│   ├── data/
│   │   ├── resort_ordinances.json      # Structured 20-municipality regulatory & benchmark dataset
│   │   └── resort_ordinances_bundle.js # Auto-generated synchronous fallback for offline file:// preview
│   ├── markets/
│   │   └── <slug>.html                 # 20 Programmatic SEO pages with FAQPage JSON-LD & yield tables
│   ├── sitemap.xml                     # 21 canonical URLs (portal + 20 market guides)
│   ├── index.html                      # English Investor Portal, Explorer, Yield Simulator & Zoning Desk
│   ├── style.css                       # Minimalist responsive UI stylesheet
│   └── app.js                          # Filter engine, ?market= deep-link, JPY/USD yield math & brief builder
└── README.md
```

---

## Covered 20 Resort & Urban Jurisdictions

| Category | Municipalities |
| :--- | :--- |
| **Ski & Alpine (5)** | `Kutchan / Niseko`, `Hakuba`, `Furano`, `Nozawa Onsen`, `Myoko` |
| **Urban & Metro (5)** | `Shibuya`, `Shinjuku`, `Taito / Asakusa`, `Chuo Osaka`, `Fukuoka City` |
| **Onsen & Mountain (4)** | `Atami`, `Hakone`, `Karuizawa`, `Fujikawaguchiko` |
| **Coastal & Island (3)** | `Naha`, `Ishigaki`, `Miyakojima` |
| **Heritage (3)** | `Kyoto City`, `Takayama`, `Kanazawa` |

---

## Quick Start & Verification

### 1. Run the Ordinance Compiler & Citation Verifier

```bash
python -m py_compile pipeline/ordinance_verifier.py
python pipeline/ordinance_verifier.py
python pipeline/ordinance_verifier.py --check
```

### 2. Local Browser Preview

Serve `./site` over HTTP (or open `site/index.html` directly):

```bash
python -m http.server 8090 --directory site
```

Then open `http://localhost:8090` in your browser.

### 3. Connecting a Partner *Gyōseishoshi* or STR Operator (`site/app.js`)

Edit `PARTNER_CONFIG` at the top of `site/app.js` to route pre-purchase zoning inquiries to your partner office via email, Formspree/Make webhook, or direct scheduling link:

```javascript
const PARTNER_CONFIG = {
  deskDisplayName: "Your Partner Bilingual Gyoseishoshi Office",
  intakeEmail: "intake@your-partner-scrivener.jp",
  webhookEndpointUrl: "https://formspree.io/f/your-endpoint",
  partnerBookingUrl: ""
};
```
