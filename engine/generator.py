"""
FinPulse AI - Multi-Persona Synthetic Ledger Generator
Generates realistic, semi-structured micro-enterprise transaction records
for three distinct real-world personas across 180 days.
"""

from typing import Dict, Any
import datetime
import random
import pandas as pd
import numpy as np


class PersonaGenerator:
    """
    Generates realistic synthetic transaction ledgers for 3 micro-business personas:
    1. Persona A (Strong / Prime): Steady Kirana store (high UPI %, predictable cadence, healthy DSCR)
    2. Persona B (Volatile / High Risk): Seasonal artisan (lumpy batches, heavy debt servicing)
    3. Persona C (Thin Margin / Growing): Street food vendor (high velocity, small tickets, tight runway)
    """

    PERSONAS = {
        "persona_a": {
            "name": "Persona A: Laxmi Kirana General Store",
            "type": "Grocery & Daily Provisions (Kirana)",
            "description": "Steady daily footfall, 82% UPI penetration, predictable vendor restocking, modest sustainable bank loan.",
            "risk_profile": "Prime Credit Candidate (Low Risk)"
        },
        "persona_b": {
            "name": "Persona B: Kalakar Handicrafts & Pottery",
            "type": "Seasonal Artisan & Craft Workshop",
            "description": "Lumpy exhibition-based revenues, high debt repayment to informal lenders, vulnerable to seasonal dry spells.",
            "risk_profile": "High Risk / Volatile"
        },
        "persona_c": {
            "name": "Persona C: Annapurna Tiffin & Street Cart",
            "type": "Quick Service Street Food & Snacks",
            "description": "Very high transaction velocity (₹30-₹150 tickets), tight net margin, negligible runway, debt-free.",
            "risk_profile": "Moderate Risk / Thin Margin Growing"
        }
    }

    @classmethod
    def generate_persona_a(cls, days: int = 180, seed: int = 42) -> pd.DataFrame:
        """
        Persona A: Steady Kirana Store
        - Inflows: Daily sales ₹3,500 - ₹9,000 (80%+ UPI, 20% Cash)
        - Outflows:
          - Twice-weekly wholesale distributor inventory payouts (₹12,000 - ₹22,000)
          - Monthly shop rent (₹12,000 on 5th of month)
          - Monthly helper wages (₹8,000 on 1st of month)
          - Monthly electricity / utility bills (₹2,500 on 10th of month)
          - Monthly formal MUDRA loan EMI (₹6,500 on 15th of month)
          - Occasional miscellaneous maintenance (₹300 - ₹1,200)
        """
        random.seed(seed)
        np.random.seed(seed)
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        records = []

        for day_offset in range(days):
            current_date = start_date + datetime.timedelta(days=day_offset)
            is_weekend = current_date.weekday() >= 5

            # Daily sales: 3 to 6 batches of daily customer collections
            num_sales_batches = random.randint(3, 6)
            base_daily_sales = random.uniform(4200, 8500) * (1.25 if is_weekend else 1.0)
            
            # Split into UPI and Cash batches
            upi_share = random.uniform(0.78, 0.88)
            cash_share = 1.0 - upi_share

            # UPI sales
            records.append({
                "Date": current_date.isoformat(),
                "Transaction_Type": "CREDIT",
                "Category": "Sales",
                "Amount": round(base_daily_sales * upi_share, 2),
                "Payment_Mode": "UPI",
                "Description": f"Counter QR collection batch ({random.randint(15, 35)} txns)"
            })

            # Cash sales
            records.append({
                "Date": current_date.isoformat(),
                "Transaction_Type": "CREDIT",
                "Category": "Sales",
                "Amount": round(base_daily_sales * cash_share, 2),
                "Payment_Mode": "Cash",
                "Description": "Over-the-counter cash sales register"
            })

            # Inventory restocking: Wednesdays and Saturdays
            if current_date.weekday() in [2, 5]:
                restock_amt = random.uniform(11000, 19000)
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Inventory",
                    "Amount": round(restock_amt, 2),
                    "Payment_Mode": "Bank Transfer",
                    "Description": f"FMCG Wholesale Distributor Invoice #{random.randint(4000, 9999)}"
                })

            # Monthly Rent on 5th
            if current_date.day == 5:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Rent",
                    "Amount": 12000.00,
                    "Payment_Mode": "Bank Transfer",
                    "Description": "Commercial Shop Rent - Monthly"
                })

            # Monthly Wages on 1st
            if current_date.day == 1:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Wages",
                    "Amount": 8500.00,
                    "Payment_Mode": "Bank Transfer",
                    "Description": "Shop Assistant Monthly Wage"
                })

            # Monthly Electricity on 10th
            if current_date.day == 10:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Utilities",
                    "Amount": round(random.uniform(2200, 3100), 2),
                    "Payment_Mode": "UPI",
                    "Description": "State Electricity Board Commercial Meter"
                })

            # Monthly MUDRA Loan EMI on 15th
            if current_date.day == 15:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Debt_Repayment",
                    "Amount": 6500.00,
                    "Payment_Mode": "Bank Transfer",
                    "Description": "Bank MUDRA Kishore Loan auto-debit EMI"
                })

            # Occasional Misc Expense
            if random.random() < 0.20:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Miscellaneous",
                    "Amount": round(random.uniform(200, 900), 2),
                    "Payment_Mode": random.choice(["Cash", "UPI"]),
                    "Description": random.choice(["Packaging pouches & polythene", "Cleaning supplies", "Tea & customer refreshments"])
                })

        df = pd.DataFrame(records)
        df["Date"] = pd.to_datetime(df["Date"])
        return df.sort_values("Date").reset_index(drop=True)

    @classmethod
    def generate_persona_b(cls, days: int = 180, seed: int = 101) -> pd.DataFrame:
        """
        Persona B: Seasonal Artisan / High Risk
        - Inflows: Irregular, lumpy payments every 2-4 weeks (festivals/exhibitions), long quiet stretches
        - High cash component (55% Cash, 45% UPI/Bank)
        - Outflows:
          - Heavy monthly debt servicing to local moneylender (₹18,500/month)
          - Bulk raw material purchase before craft melas (clay, brass, paints)
          - Studio rent & workshop wages
        """
        random.seed(seed)
        np.random.seed(seed)
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        records = []

        # Exhibition dates (lumpy sales)
        exhibition_days = set()
        for i in range(15, days, random.randint(20, 35)):
            for duration in range(random.randint(2, 4)):
                if i + duration < days:
                    exhibition_days.add(i + duration)

        for day_offset in range(days):
            current_date = start_date + datetime.timedelta(days=day_offset)

            # Inflow logic
            if day_offset in exhibition_days:
                # Big exhibition collection
                lump_sum = random.uniform(28000, 65000)
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "CREDIT",
                    "Category": "Sales",
                    "Amount": round(lump_sum * 0.45, 2),
                    "Payment_Mode": "UPI",
                    "Description": "Craft Fair / Exhibition QR payment receipts"
                })
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "CREDIT",
                    "Category": "Sales",
                    "Amount": round(lump_sum * 0.55, 2),
                    "Payment_Mode": "Cash",
                    "Description": "Direct stall cash sales"
                })
            else:
                # Regular slow day: 30% chance of a modest workshop sale
                if random.random() < 0.35:
                    sale_amt = random.uniform(800, 2600)
                    records.append({
                        "Date": current_date.isoformat(),
                        "Transaction_Type": "CREDIT",
                        "Category": "Sales",
                        "Amount": round(sale_amt, 2),
                        "Payment_Mode": random.choice(["Cash", "UPI"]),
                        "Description": "Local workshop walk-in retail purchase"
                    })

            # Bulk Raw Material purchases once a month
            if current_date.day == 8:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Inventory",
                    "Amount": round(random.uniform(16000, 24000), 2),
                    "Payment_Mode": "Cash",
                    "Description": "Bulk purchase of raw clay, brass casting, lac & paints"
                })

            # Heavy monthly Debt Servicing on 10th (High-cost moneylender loan)
            if current_date.day == 10:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Debt_Repayment",
                    "Amount": 18500.00,
                    "Payment_Mode": "Cash",
                    "Description": "Equipment & workshop finance installment (Unorganized Credit)"
                })

            # Studio Rent on 1st
            if current_date.day == 1:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Rent",
                    "Amount": 9000.00,
                    "Payment_Mode": "Bank Transfer",
                    "Description": "Artisan Shed & Studio Lease"
                })

            # Apprentice Wages on 15th
            if current_date.day == 15:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Wages",
                    "Amount": 7000.00,
                    "Payment_Mode": "Cash",
                    "Description": "Workshop Apprentice wages"
                })

            # Utilities on 20th
            if current_date.day == 20:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Utilities",
                    "Amount": round(random.uniform(1500, 2500), 2),
                    "Payment_Mode": "UPI",
                    "Description": "Kiln fuel and workshop electricity"
                })

        df = pd.DataFrame(records)
        df["Date"] = pd.to_datetime(df["Date"])
        return df.sort_values("Date").reset_index(drop=True)

    @classmethod
    def generate_persona_c(cls, days: int = 180, seed: int = 777) -> pd.DataFrame:
        """
        Persona C: Street Food Vendor / Thin Margin, High Velocity
        - Inflows: Steady daily footfall, small-ticket transactions (₹40 - ₹120)
        - 65% UPI Soundbox, 35% Cash
        - Outflows:
          - Daily fresh morning vegetable & dairy market purchases (₹1,500 - ₹2,800/day)
          - Weekly cooking gas LPG cylinder refills (₹2,200)
          - Daily municipal cart stall fee (₹100/day)
          - Monthly helper stipend (₹6,000)
          - Zero formal debt (Debt-free, but low working capital cushion: 4-8 days)
        """
        random.seed(seed)
        np.random.seed(seed)
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        records = []

        for day_offset in range(days):
            current_date = start_date + datetime.timedelta(days=day_offset)
            is_weekend = current_date.weekday() >= 5

            # Daily sales: ₹2,800 to ₹5,200
            daily_revenue = random.uniform(3000, 5200) * (1.30 if is_weekend else 1.0)
            upi_amt = daily_revenue * random.uniform(0.60, 0.72)
            cash_amt = daily_revenue - upi_amt

            records.append({
                "Date": current_date.isoformat(),
                "Transaction_Type": "CREDIT",
                "Category": "Sales",
                "Amount": round(upi_amt, 2),
                "Payment_Mode": "UPI",
                "Description": f"UPI Soundbox collection ({random.randint(35, 75)} transactions)"
            })

            records.append({
                "Date": current_date.isoformat(),
                "Transaction_Type": "CREDIT",
                "Category": "Sales",
                "Amount": round(cash_amt, 2),
                "Payment_Mode": "Cash",
                "Description": "Coin & cash drawer street sales"
            })

            # Daily raw ingredients purchase (Mandi/Vegetables/Oil/Paneer)
            daily_raw_cost = daily_revenue * random.uniform(0.58, 0.68)
            records.append({
                "Date": current_date.isoformat(),
                "Transaction_Type": "DEBIT",
                "Category": "Inventory",
                "Amount": round(daily_raw_cost, 2),
                "Payment_Mode": random.choice(["Cash", "UPI"]),
                "Description": "Daily APMC mandi vegetables, cooking oil & flour"
            })

            # Daily Cart Street Hawking Fee
            records.append({
                "Date": current_date.isoformat(),
                "Transaction_Type": "DEBIT",
                "Category": "Rent",
                "Amount": 100.00,
                "Payment_Mode": "Cash",
                "Description": "Municipal designated street vending hawker fee"
            })

            # Weekly Commercial LPG Cylinders on Tuesdays
            if current_date.weekday() == 1:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Utilities",
                    "Amount": 2150.00,
                    "Payment_Mode": "UPI",
                    "Description": "Commercial 19kg LPG Cylinder refill"
                })

            # Monthly Helper Stipend on 1st
            if current_date.day == 1:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Wages",
                    "Amount": 6000.00,
                    "Payment_Mode": "UPI",
                    "Description": "Cart Assistant / Cleaner Monthly Stipend"
                })

            # Occasional small repairs/supplies
            if random.random() < 0.15:
                records.append({
                    "Date": current_date.isoformat(),
                    "Transaction_Type": "DEBIT",
                    "Category": "Miscellaneous",
                    "Amount": round(random.uniform(150, 450), 2),
                    "Payment_Mode": "Cash",
                    "Description": "Paper plates, biodegradable cups, napkins"
                })

        df = pd.DataFrame(records)
        df["Date"] = pd.to_datetime(df["Date"])
        return df.sort_values("Date").reset_index(drop=True)

    @classmethod
    def get_persona_dataset(cls, persona_key: str, days: int = 180) -> pd.DataFrame:
        """Returns the synthetic dataframe for the given persona key."""
        if persona_key == "persona_a":
            return cls.generate_persona_a(days=days)
        elif persona_key == "persona_b":
            return cls.generate_persona_b(days=days)
        elif persona_key == "persona_c":
            return cls.generate_persona_c(days=days)
        else:
            raise ValueError(f"Unknown persona key: {persona_key}")
