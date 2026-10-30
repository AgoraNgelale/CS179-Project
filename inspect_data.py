"""Inspect the downloaded historical stock market dataset.

Run from the repository root:
    python3 inspect_data.py

Place extracted stock data in the archive/ folder. The archive data should
remain excluded from Git using .gitignore.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "archive"


def main():
    if not DATA_DIR.is_dir():
        raise SystemExit(
            f"Data directory not found: {DATA_DIR}\n"
            "Extract the dataset into an 'archive' folder next to this script."
        )

    csv_files = sorted(p for p in DATA_DIR.rglob("*") if p.is_file() and p.suffix.lower() in {".csv", ".txt"})
    if not csv_files:
        raise SystemExit(f"No .csv or .txt files found inside {DATA_DIR}")

    total_rows = 0
    total_bytes = 0
    sample_rows = []
    headers_seen = set()
    errors = []

    for path in csv_files:
        total_bytes += path.stat().st_size
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames:
                    errors.append(f"{path.relative_to(DATA_DIR)}: missing header")
                    continue
                headers_seen.add(tuple(reader.fieldnames))
                for row in reader:
                    total_rows += 1
                    if len(sample_rows) < 5:
                        sample_rows.append((str(path.relative_to(DATA_DIR)), row))
        except (OSError, UnicodeError, csv.Error) as exc:
            errors.append(f"{path.relative_to(DATA_DIR)}: {exc}")

    print("DATASET SUMMARY")
    print("------------------------------")
    print(f"Data files: {len(csv_files):,}")
    print(f"Data size (MiB): {total_bytes / (1024 ** 2):,.2f}")
    print(f"Data size (MB): {total_bytes / 1_000_000:,.2f}")
    print(f"Records read: {total_rows:,}")
    print(f"Distinct column layouts: {len(headers_seen)}")
    for headers in sorted(headers_seen):
        print(f"Columns ({len(headers)}): {', '.join(headers)}")

    print("\nSAMPLE RECORDS")
    for filename, row in sample_rows:
        print(f"{filename}: {row}")

    if errors:
        print(f"\nWARNING: {len(errors)} files had reading issues:")
        for message in errors[:10]:
            print(f"  {message}")
        if len(errors) > 10:
            print(f"  ...and {len(errors) - 10} more")


if __name__ == "__main__":
    main()
