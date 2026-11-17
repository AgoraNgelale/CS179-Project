#!/usr/bin/env bash
set -Eeuo pipefail

ENV_NAME="spark_env"
MINICONDA="$HOME/miniconda3"
JAVA_HOME_TARGET="$HOME/jdk11"

log() { printf '\n[CS179] %s\n' "$*"; }
fail() { printf '\n[CS179 ERROR] %s\n' "$*" >&2; exit 1; }
trap 'fail "Setup stopped at line $LINENO. Check the error above."' ERR

log "Checking system architecture and tools"
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || fail "This setup targets the UCR Linux x86_64 server."
command -v curl >/dev/null || fail "curl is required."
command -v tar >/dev/null || fail "tar is required."

if [[ ! -x "$MINICONDA/bin/conda" ]]; then
  if command -v conda >/dev/null 2>&1; then
    CONDA_BIN="$(command -v conda)"
    log "Using existing Conda at $CONDA_BIN"
  else
    log "Installing Miniconda in $MINICONDA"
    mkdir -p "$MINICONDA"
    installer="$(mktemp "${TMPDIR:-/tmp}/cs179-miniconda.XXXXXX.sh")"
    trap 'rm -f "${installer:-}"' EXIT
    curl -fL --retry 3 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh' -o "$installer"
    bash "$installer" -b -u -p "$MINICONDA"
    rm -f "$installer"
    trap - EXIT
    CONDA_BIN="$MINICONDA/bin/conda"
  fi
else
  CONDA_BIN="$MINICONDA/bin/conda"
  log "Using Miniconda already installed at $MINICONDA"
fi

log "Checking Conda environment $ENV_NAME"
if "$CONDA_BIN" env list --json | python3 -c 'import json,sys; name=sys.argv[1]; data=json.load(sys.stdin); sys.exit(0 if any(p.rstrip("/").split("/")[-1] == name for p in data["envs"]) else 1)' "$ENV_NAME"; then
  log "Environment exists; reusing it"
else
  "$CONDA_BIN" create -y -n "$ENV_NAME" python=3.10 pip
fi

if [[ ! -x "$JAVA_HOME_TARGET/bin/java" ]]; then
  log "Installing Temurin JDK 11 in $JAVA_HOME_TARGET"
  tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/cs179-java.XXXXXX")"
  trap 'rm -rf "${tmpdir:-}"' EXIT
  curl -fL --retry 3 'https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.22%2B7/OpenJDK11U-jdk_x64_linux_hotspot_11.0.22_7.tar.gz' -o "$tmpdir/jdk.tar.gz"
  tar -xzf "$tmpdir/jdk.tar.gz" -C "$tmpdir"
  mv "$tmpdir/jdk-11.0.22+7" "$JAVA_HOME_TARGET"
  rm -rf "$tmpdir"
  trap - EXIT
else
  log "Reusing Java 11 at $JAVA_HOME_TARGET"
fi

log "Installing PySpark and supporting packages in $ENV_NAME"
"$CONDA_BIN" run -n "$ENV_NAME" python -m pip install 'pyspark[sql]==3.5.0' pandas matplotlib numpy 'mysql-connector-python' 'sqlalchemy<3' pyarrow

log "Verifying Java and Spark"
"$JAVA_HOME_TARGET/bin/java" -version
JAVA_HOME="$JAVA_HOME_TARGET" SPARK_LOCAL_IP=127.0.0.1 "$CONDA_BIN" run --no-capture-output -n "$ENV_NAME" python -c '
import pyspark
from pyspark.sql import SparkSession
print("PySpark version:", pyspark.__version__)
spark = (SparkSession.builder.master("local[2]").appName("CS179SetupTest")
         .config("spark.ui.enabled", "false").getOrCreate())
try:
    result = spark.range(10).count()
    assert result == 10, result
    print("Spark verification PASSED: counted 10 records")
finally:
    spark.stop()
'

log "Setup complete! For a new terminal session, activate with:"
printf '  source "%s/etc/profile.d/conda.sh"\n  conda activate %s\n  export JAVA_HOME="%s"\n' "$(dirname "$(dirname "$CONDA_BIN")")" "$ENV_NAME" "$JAVA_HOME_TARGET"
