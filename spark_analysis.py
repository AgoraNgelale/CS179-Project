#!/usr/bin/env python3
"""Load the CS179 historical stock/ETF dataset into a Spark DataFrame.

Run from the repository root:
    conda activate spark_env
    python spark_analysis.py
"""
from pathlib import Path
from pyspark.sql import SparkSession, Window, functions as F, types as T

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "archive" / "Data"
SCHEMA = T.StructType([
    T.StructField("Date", T.StringType(), True),
    T.StructField("Open", T.DoubleType(), True),
    T.StructField("High", T.DoubleType(), True),
    T.StructField("Low", T.DoubleType(), True),
    T.StructField("Close", T.DoubleType(), True),
    T.StructField("Volume", T.LongType(), True),
    T.StructField("OpenInt", T.LongType(), True),
])

def main():
    for category in ("Stocks", "ETFs"):
        if not (DATA / category).is_dir():
            raise FileNotFoundError(f"Missing dataset folder: {DATA / category}")

    spark = (SparkSession.builder
             .appName("CS179-Historical-Stock-Analyzer")
             .getOrCreate())
    try:
        frames = []
        for category in ("Stocks", "ETFs"):
            # Use recursive lookup for the thousands of small ticker files.
            df = (spark.read
                  .option("header", "true")
                  .option("recursiveFileLookup", "true")
                  .schema(SCHEMA)
                  .csv(str(DATA / category))
                  .withColumn("source_file", F.input_file_name())
                  .withColumn("ticker", F.regexp_extract(
                      F.col("source_file"), r"/([^/]+)\.us\.txt$", 1))
                  .withColumn("asset_type", F.lit(category))
                  .withColumn("trade_date", F.to_date(F.col("Date"), "yyyy-MM-dd"))
                  .drop("Date"))
            frames.append(df)

        all_data = frames[0].unionByName(frames[1])
        print("\n=== Dataset row counts ===")
        all_data.groupBy("asset_type").count().orderBy("asset_type").show()
        print("TOTAL ROWS:", all_data.count())
        print("\n=== Sample records ===")
        all_data.select("ticker", "asset_type", "trade_date", "Open", "Close", "Volume").show(10, truncate=False)
        print("\n=== Performance by ticker ===")
        # Group by ticker and asset type; order the observed closes by trade date.
        # min_by/max_by select the close on the earliest/latest trading date.
        performance = (all_data
            .filter(F.col("trade_date").isNotNull() & F.col("Close").isNotNull())
            .groupBy("asset_type", "ticker")
            .agg(
                F.min("trade_date").alias("first_date"),
                F.max("trade_date").alias("last_date"),
                F.min_by(F.col("Close"), F.col("trade_date")).alias("first_close"),
                F.max_by(F.col("Close"), F.col("trade_date")).alias("last_close"),
                F.min("Low").alias("lowest_low"),
                F.max("High").alias("highest_high"),
                F.avg("Volume").alias("avg_volume"),
                F.count("*").alias("trading_records")
            )
            .withColumn("return_pct",
                F.when(F.col("first_close") > 0,
                    (F.col("last_close") / F.col("first_close") - 1) * 100))
        )
        performance.orderBy(F.desc("return_pct")).select(
            "asset_type", "ticker", "first_date", "last_date",
            "first_close", "last_close", "return_pct", "trading_records"
        ).show(20, truncate=False)
        print("TOTAL TICKERS:", performance.count())
        print("\n=== Invalid dates / missing tickers ===")
        all_data.select(
            F.sum(F.col("trade_date").isNull().cast("long")).alias("invalid_dates"),
            F.sum((F.col("ticker") == "").cast("long")).alias("missing_tickers")
        ).show()
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
