# CS179 — Historical Stock Market Performance Analyzer

University of California, Riverside · CS179 Big Data Analytics Using Spark

This repository contains our PySpark code for analyzing historical US stock and ETF data. **The dataset is not committed to GitHub.**

## 1. Log in to the UCR Spark server

Open a terminal on your own computer and connect to the UCR login server (**Bolt**) using your **own UCR account**:

```bash
ssh YOUR_NETID@bolt.cs.ucr.edu
```

Once on Bolt, run the course-provided group login command:

```bash
cs179g_login
```

This connects to the assigned group Spark machine. Our group machine has appeared as `cs179g@class-148`; the login command chooses the configured destination automatically. **Do not try to SSH directly to `class-148` using ordinary credentials**—the course login command uses a special SSH configuration.

You can recognize where you are from the shell prompt:

- `YOUR_NETID@bolt` — UCR login server
- `cs179g@class-148` — group Spark server

To return from the Spark server to Bolt, type `exit`; type `exit` again to leave Bolt.

> **Access note:** The example `cs179g_login` command is the one configured for our group. Teammates must have the course-granted group access and may need to use the login command assigned to their own accounts.

## 2. Open and update the project

On the **Spark server**, the repository is already cloned at:

```bash
cd ~/CS179-Project
git pull origin main
```

If you're setting up a new working copy on an authorized machine:

```bash
git clone https://github.com/AgoraNgelale/CS179-Project.git
cd CS179-Project
```

## 3. Activate the Python / Spark environment

The group server has a Miniconda environment called `spark_env`. After a fresh SSH login, `conda` might not be on the shell path. Initialize it explicitly:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate spark_env
```

Your prompt should begin with `(spark_env)`. Then check:

```bash
python --version
python -c "import pyspark; print(pyspark.__version__)"
```

If the environment is missing on a **new** server, inspect `setup_cs179.sh` before running it; it installs the project's dependencies.

## 4. Dataset location

The historical dataset has already been copied to the group server:

```text
~/CS179-Project/
├── archive/
│   ├── Data/
│   │   ├── Stocks/   # *.us.txt files
│   │   └── ETFs/     # *.us.txt files
│   ├── Stocks/       # additional copy; not used by the loader
│   └── ETFs/         # additional copy; not used by the loader
├── setup_cs179.sh
└── spark_analysis.py
```

The loader reads **only** `archive/Data/Stocks` and `archive/Data/ETFs`, to avoid double-counting the additional copies. Check the dataset with:

```bash
du -sh archive/Data
find archive/Data -type f | head
```

The data is ignored by Git, so cloning this repository alone **does not download the dataset**.

## 5. Run the Spark analysis

From `~/CS179-Project`, with `spark_env` activated:

```bash
python spark_analysis.py
```

The script loads stock and ETF history, extracts ticker symbols, checks dates and ticker coverage, counts records, and computes per-ticker historical performance statistics.

**Last verified loader counts (Nov 17, 2026):**

| Category | Rows |
| --- | ---: |
| Stocks | 14,887,665 |
| ETFs | 2,565,578 |
| **Total** | **17,453,243** |

The most recent validation showed **0 invalid dates** and **0 missing ticker symbols**. The newer performance calculations still need to be verified on the server.

## 6. Contribute code through GitHub

First, ask the repository owner to invite you as a collaborator, and accept the GitHub invitation. Then, on the Spark server:

```bash
cd ~/CS179-Project
git pull origin main
```

For development, **prefer working on your own computer or a separate branch** rather than having multiple teammates edit the same shared working directory on `class-148`.

A typical branch workflow:

```bash
git switch -c feature/your-change
# edit files
git add YOUR_CHANGED_FILES
git commit -m "Describe your change"
git push -u origin feature/your-change
```

Open a pull request on GitHub, have a teammate review it, and merge it into `main`. Then update the shared Spark server checkout:

```bash
cd ~/CS179-Project
git pull origin main
```

Do not commit the `archive/` dataset, passwords, access keys, or environment directories.

## Troubleshooting

- **`conda: command not found`** — run `source ~/miniconda3/etc/profile.d/conda.sh`, then `conda activate spark_env`.
- **`python: command not found`** — activate `spark_env` first.
- **`Permission denied (publickey)` connecting to the Spark server** — log into Bolt and use `cs179g_login`, not direct `ssh cs179g@class-148`.
- **Missing dataset path** — confirm you're on the group Spark server and that `~/CS179-Project/archive/Data` exists.
- **Spark memory warnings** — the dataset contains thousands of small files. Avoid caching the entire raw dataset unnecessarily; inspect the actual error if a job fails.
