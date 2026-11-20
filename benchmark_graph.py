
import csv
import matplotlib.pyplot as plt

results = {}

with open("benchmark_results.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        files = int(row["files"])
        cores = int(row["cores"])
        seconds = float(row["seconds"])

        if files not in results:
            results[files] = {}

        results[files][cores] = seconds

for files in sorted(results):
    cores = sorted(results[files])
    times = [results[files][core] for core in cores]

    plt.plot(cores, times, marker="o", label=f"{files} files")

plt.xlabel("CPU Threads")
plt.ylabel("Execution Time (seconds)")
plt.title("Spark Benchmark: Execution Time vs CPU Threads")
plt.xticks([1, 2, 4])
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("benchmark_graph.png", dpi=300)
plt.show()
