
import csv
import sys
import time
from pathlib import Path

from pyspark.sql import SparkSession, functions as F, types as T

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "archive" / "Data" / "Stocks"

SCHEMA = T.StructType([
    T.StructField("Date", T.StringType()),
    T.StructField("Open", T.DoubleType()),
    T.StructField("High", T.DoubleType()),
    T.StructField("Low", T.DoubleType()),
    T.StructField("Close", T.DoubleType()),
    T.StructField("Volume", T.LongType()),
    T.StructField("OpenInt", T.LongType())
])


def main():
    cores = int(sys.argv[1])
    files = sorted(DATA.glob("*.us.txt"))[:int(sys.argv[2])]

    if not files:
        raise RuntimeError("No stock files found")

    spark = (
        SparkSession.builder
        .appName("CS179-Benchmark")
        .master(f"local[{cores}]")
        .getOrCreate()
    )

    try:
        start = time.perf_counter()

        df = (
            spark.read
            .option("header", "true")
            .schema(SCHEMA)
            .csv([str(f) for f in files])
        )

        result = (
            df.groupBy("Date")
            .agg(
                F.avg("Close").alias("avg_close"),
                F.sum("Volume").alias("total_volume")
            )
        )

        rows = result.count()
        elapsed = time.perf_counter() - start

        print(f"CPU threads: {cores}")
        print(f"Files processed: {len(files)}")
        print(f"Result rows: {rows}")
        print(f"Execution time: {elapsed:.2f} seconds")

        output = ROOT / "benchmark_results.csv"
        new_file = not output.exists()

        with output.open("a", newline="") as f:
            writer = csv.writer(f)

            if new_file:
                writer.writerow([
                    "cores", "files", "result_rows", "seconds"
                ])

            writer.writerow([
                cores, len(files), rows, round(elapsed, 2)
            ])

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
