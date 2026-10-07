# FinPulse AI: Micro-Enterprise Financial Health & Credit Readiness Engine

> **Built for the IBM Bharat Cares Internship**  
> A production-ready, deterministic financial analytics and credit underwriting platform for Indian micro-enterprises.

---

## 📌 Executive Summary
Micro-enterprises (Kirana stores, artisanal handicraft workshops, street food vendors, local service providers) form the backbone of the Indian economy. However, traditional banks and NBFCs struggle to underwrite them due to **informal bookkeeping, lack of audited balance sheets, and irregular cash flow streams**.

**FinPulse AI** bridges this credit gap by taking raw, semi-structured transaction ledgers (CSV, XLSX) or UPI collections, computing deterministic financial health indicators, displaying an executive interactive dashboard, and synthesizing an automated, underwriting-ready **Credit Readiness Scorecard** (aligned with **PM MUDRA Yojana**, **PM SVANidhi**, and formal NBFC micro-lending criteria).

---

## 🏗️ System Architecture & Directory Layout

```text
finpulse-ai/
├── app.py                      # Main Streamlit executive dashboard & UI orchestration
├── requirements.txt            # Pinned dependencies
├── create_sample_data.py       # Pre-populates sample_data/ with offline test ledgers
├── verify_engine.py            # Standalone test suite for deterministic mathematical logic
├── sample_data/                # Realistic multi-persona ledgers (180 days)
│   ├── persona_a_kirana.csv    # Steady Kirana store (Prime credit candidate)
│   ├── persona_b_artisan.csv   # Seasonal artisan (Volatile / high risk)
│   └── persona_c_streetfood.csv# Street food cart (High velocity, thin margin)
├── engine/
│   ├── __init__.py             # Engine package exports
│   ├── analyzer.py             # Deterministic financial indicators, DSCR, CV & 4-pillar score
│   ├── generator.py            # Realistic 180-day micro-business synthetic data generator
│   └── visualizer.py           # Plotly interactive chart factory (Waterfall, Radar, Timelines)
└── README.md                   # Complete documentation & metric formulas
```

---

## 🧮 Mathematical Formulas & Deterministic Scoring Engine

### 1. Net Operating Cash Flow
$$\text{Net Cash Flow} = \sum \text{Inflows (CREDIT)} - \sum \text{Outflows (DEBIT)}$$

### 2. Debt Service Coverage Ratio (DSCR)
$$DSCR = \frac{\text{Net Operating Income}}{\text{Total Debt Service Obligations (Principal + Interest EMI)}}$$
- **Benchmark**: $\ge 1.50\times$ (Healthy / Prime), $1.00 - 1.49\times$ (Tight cushion), $< 1.00\times$ (Default risk).

### 3. Cash Flow Volatility Index ($CV$)
$$CV = \frac{\sigma_{\text{weekly net}}}{\mu_{\text{weekly net}}}$$
- Measures dispersion of weekly net balances. Lower $CV$ indicates high predictability.

### 4. Working Capital Runway (Days)
$$\text{Runway (Days)} = \frac{\text{Cumulative Net Retained Reserves}}{\text{Average Daily Operational Burn Rate}}$$

### 5. Digital Penetration Ratio
$$\text{Digital Penetration} = \frac{\sum \text{Turnover}_{\text{UPI + Bank}}}{\sum \text{Turnover}_{\text{Total}}} \times 100$$
- Verifiable digital trail required for automated bank statement and account aggregator credit underwriting.

---

## 🏆 4-Pillar Composite Credit Readiness Score (0 to 100)

| Pillar | Weight | Key Metrics Evaluated |
| :--- | :---: | :--- |
| **1. Cash Flow Stability** | **30%** | Weekly Net Flow $CV$, negative balance dip frequency, liquidity cushion |
| **2. Margin Adequacy** | **25%** | Net profit margin %, gross revenue trajectory, pricing power |
| **3. Debt Repayment Discipline** | **25%** | DSCR ratio, debt-to-inflow percentage ($\le 25\%$), EMI reliability |
| **4. Digital Record Verifiability** | **20%** | UPI QR code adoption %, bank account transaction density |

### Credit Risk Tiers:
- 🟢 **Prime Credit Readiness (75 - 100 pts)**: Ready for immediate formal bank credit / MUDRA Kishore/Tarun loan (up to ₹10 Lakhs).
- 🟡 **Moderate Risk / Conditional (50 - 74 pts)**: Eligible for micro-credit schemes such as PM SVANidhi (₹10,000 - ₹50,000) or MUDRA Shishu.
- 🔴 **High Risk / Sub-Prime (< 50 pts)**: Requires 60-day ledger hygiene, debt restructuring, and cash buffer improvements before applying.

---

## 👥 Built-in Micro-Business Personas

1. **Persona A: Laxmi Kirana General Store (Prime Candidate)**
   - Daily turnover: ₹4,000 - ₹8,500
   - 82% UPI payments via counter QR
   - Monthly MUDRA EMI: ₹6,500; DSCR > 2.0x; Runway > 45 days.
2. **Persona B: Kalakar Handicrafts & Pottery (Volatile / High Risk)**
   - Lumpy exhibition revenue every 3-4 weeks with dry spells
   - High informal moneylender debt service (₹18,500/month); DSCR < 1.0x during lean periods; $CV > 1.2$.
3. **Persona C: Annapurna Tiffin & Street Cart (Thin Margin / Growing)**
   - High transaction velocity (30-80 micro-tickets daily of ₹40 - ₹120)
   - 65% UPI Soundbox; Debt-free; Tight runway (4-10 days); eligible for PM SVANidhi working capital loans.

---

## 🚀 Quickstart & Setup Guide

### 1. Installation
Ensure Python 3.10+ is installed:
```bash
cd finpulse-ai
pip install -r requirements.txt
```

### 2. Run Verification Tests
```bash
python verify_engine.py
```

### 3. Generate Offline Sample CSVs (Optional)
```bash
python create_sample_data.py
```

### 4. Launch the Executive Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Dashboard Capabilities
- **Executive Metric Cards**: Real-time Gross Turnover, Operational Burn, Net Margin %, DSCR, Runway Days, and Composite Credit Score badge.
- **Visuals**:
  - Dual-axis monthly inflow vs outflow with cumulative balance reserve.
  - Revenue-to-Surplus Waterfall breakdown.
  - 4-Pillar Credit Radar / Spider chart.
  - Expense breakdown donut chart (Operational vs Debt Servicing).
  - Weekly net cash flow volatility timeline with 3-week rolling average.
- **Automated Underwriting & Red-Flag Audit**: Identifies critical leverage traps, negative cash dips, and generates tailored micro-loan recommendations.
- **Export**: Full JSON underwriting audit package download + printable markdown report.
