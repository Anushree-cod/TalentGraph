import json

from candidate_builder_profile import build_candidate_profile
from skill_canonicalizer import canonicalize_skill_entries, load_skill_aliases


INPUT_FILE = "datasets/provided_dataset/candidates.jsonl"
OUTPUT_FILE = "datasets/structured_candidates.jsonl"


def main():
    aliases = load_skill_aliases()
    count = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for line in infile:
            candidate = json.loads(line)

            canonical_skills, skills_detailed, raw_skills = canonicalize_skill_entries(
                candidate.get("skills", []),
                aliases,
            )

            profile = build_candidate_profile(
                candidate,
                canonical_skills,
                skills_detailed,
                raw_skills,
            )

            outfile.write(json.dumps(profile) + "\n")

            count += 1

            if count % 1000 == 0:
                print(f"Processed {count}")

    print("=" * 50)
    print(f"Done. Total Profiles: {count}")
    print(f"Saved: {OUTPUT_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()
