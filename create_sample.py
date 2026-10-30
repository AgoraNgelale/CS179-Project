"""Create a 1–2 MB sample CSV from the historical stock market dataset.

Run: python3 create_sample.py
Reads archive/ recursively; writes sample_data/stock_market_sample.csv.
Only the sample output should be submitted, not the full archive.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "archive"
OUTPUT = ROOT / "sample_data" / "stock_market_sample.csv"
TARGET_BYTES = 1_500_000
MAX_BYTES = 2_000_000
COLUMNS = ["Ticker", "Category", "Date", "Open", "High", "Low", "Close", "Volume", "OpenInt"]


def main():
    files = sorted(p for p in SOURCE.rglob("*")
                   if p.is_file() and p.suffix.lower() in {".txt", ".csv"})
    if not files:
        raise SystemExit(f"No .txt or .csv data files found in {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    used = 0
    with OUTPUT.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS)
        writer.writeheader()
        for path in files:
            ticker = path.name.split(".")[0].upper()
            category = path.parent.name
            try:
                with path.open("r", encoding="utf-8-sig", newline="") as source:
                    reader = csv.DictReader(source)
                    if not reader.fieldnames or not set(COLUMNS[2:]).issubset(reader.fieldnames):
                        continue
                    for row in reader:
                        if not row.get("Date"):
                            continue
                        output_row = {"Ticker": ticker, "Category": category}
                        output_row.update({col: row[col] for col in COLUMNS[2:]})
                        writer.writerow(output_row)
                        count += 1
                        if out.tell() >= TARGET_BYTES:
                            break
            except (OSError, UnicodeError, csv.Error) as exc:
                print(f"Skipped {path.name}: {exc}")
            if out.tell() >= TARGET_BYTES:
                used += 1
                break
            used += 1

    size = OUTPUT.stat().st_size
    print(f"Created: {OUTPUT}")
    print(f"Size: {size:,} bytes ({size / 1_000_000:.2f} MB)")
    print(f"Records: {count:,}")
    print(f"Source files visited: {used:,}")
    if not (1_000_000 <= size <= MAX_BYTES):
        print("WARNING: Sample is outside the required 1–2 MB range.")


if __name__ == "__main__":
    main()
