"""
FinPulse AI - Pre-generated Sample Data Export Script
Creates Persona A, B, and C sample CSV files in sample_data/ for offline review or instant upload.
"""

import os
from engine.generator import PersonaGenerator

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
    os.makedirs(out_dir, exist_ok=True)

    print("Generating Persona A: Kirana Store (Steady)...")
    df_a = PersonaGenerator.generate_persona_a(days=180)
    df_a.to_csv(os.path.join(out_dir, "persona_a_kirana.csv"), index=False)

    print("Generating Persona B: Seasonal Artisan (High Risk)...")
    df_b = PersonaGenerator.generate_persona_b(days=180)
    df_b.to_csv(os.path.join(out_dir, "persona_b_artisan.csv"), index=False)

    print("Generating Persona C: Street Food Vendor (Thin Margin)...")
    df_c = PersonaGenerator.generate_persona_c(days=180)
    df_c.to_csv(os.path.join(out_dir, "persona_c_streetfood.csv"), index=False)

    print(f"Successfully exported all 3 personas to {out_dir}")

if __name__ == "__main__":
    main()
