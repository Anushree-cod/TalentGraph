
import pandas as pd
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parents[3]

# Add resume_parser to path
sys.path.append(str(ROOT / "backend" / "resume_parser"))

from skill_extractor import extract_skills


# ---------------- LOAD DATASET ---------------- #

csv_path = ROOT / "datasets" / "Resume.csv"

# utf-8-sig removes hidden BOM characters
df = pd.read_csv(csv_path, encoding="utf-8-sig")

# Clean column names
df.columns = (
    df.columns
      .str.strip()
      .str.replace("\ufeff", "", regex=False)
)

print("\nAvailable Columns:")
print(df.columns.tolist())

# Safety check
required_cols = ["Category", "Resume_str"]

missing = [col for col in required_cols if col not in df.columns]

if missing:
    raise ValueError(
        f"Missing columns in CSV: {missing}"
    )


# ---------------- SAMPLING ---------------- #

SEED = 42
NUM_CATEGORIES = 10
RESUMES_PER_CATEGORY = 1

# Randomly choose 10 categories
selected_categories = (
    df["Category"]
      .drop_duplicates()
      .sample(
          n=min(NUM_CATEGORIES,
                df["Category"].nunique()),
          random_state=SEED
      )
)

print("\nSelected Categories:")
print(selected_categories.tolist())

# Take 1 resume from each selected category
sampled_df = (
    df[df["Category"].isin(selected_categories)]
      .groupby("Category", group_keys=False)
      .apply(
          lambda x: x.sample(
              n=min(len(x), RESUMES_PER_CATEGORY),
              random_state=SEED
          )
      )
      .reset_index(drop=True)
)
# ---------------- EVALUATION ---------------- #

results = []

for idx, row in sampled_df.iterrows():

    print(f"Processing Resume {idx + 1}/{len(sampled_df)}")

    category = str(row.get("Category", "Unknown"))
    resume_text = str(row.get("Resume_str", ""))

    skills = extract_skills(
        resume_text,
        str(ROOT / "datasets" / "skills_master.csv")
    )

    if skills:

        for skill in skills:

            results.append({

                "Resume_ID": idx + 1,
                "Category": category,
                "Skill": skill["skill"],
                "Frequency": skill.get("frequency", 1),
                "Sections": ", ".join(skill.get("sections", [])),
                "Evidence": " | ".join(skill.get("evidence", []))

            })

    else:

        results.append({

            "Resume_ID": idx + 1,
            "Category": category,
            "Skill": "No Skills Found",
            "Frequency": 0,
            "Sections": "",
            "Evidence": ""

        })


# ---------------- SAVE RESULTS ---------------- #

output_df = pd.DataFrame(results)

output_path = ROOT / "datasets" / "skill_extraction_results.csv"

output_df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\nResults saved to:")
print(output_path)