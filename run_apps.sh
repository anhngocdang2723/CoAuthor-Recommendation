#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$ROOT_DIR/.venv/bin/python"
METHODS_DIR="$ROOT_DIR/Methods"
LOG_DIR="$ROOT_DIR/.run_logs"

mkdir -p "$LOG_DIR"

APPS=(
  "query_code.py:5000:main"
  "train_recommend_sSFCM.py:5001:ssfcm"
  "train_recommend_sSMC_FCM.py:5002:ssmcfcm"
)

usage() {
  cat <<EOF
Usage: ./run_apps.sh <command>

Commands:
  start    Stop old processes on ports 5000-5002, then start all 3 apps
  stop     Stop any process using ports 5000, 5001, 5002
  restart  stop + start
  status   Show status of each app by port
  test     Call each app homepage and print HTTP code
  logs     Show log file locations

Examples:
  ./run_apps.sh start
  ./run_apps.sh status
  ./run_apps.sh test
EOF
}

ensure_env() {
  if [[ ! -x "$VENV_PY" ]]; then
    echo "[ERR] Không tìm thấy Python venv tại: $VENV_PY"
    echo "Hãy tạo venv trước: python3 -m venv .venv"
    exit 1
  fi
}

pids_on_port() {
  local port="$1"
  ss -ltnp "( sport = :$port )" 2>/dev/null \
    | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' \
    | sort -u
}

kill_port() {
  local port="$1"
  local pids
  pids="$(pids_on_port "$port" || true)"
  if [[ -n "$pids" ]]; then
    echo "[INFO] Stop port $port (PID: $(echo "$pids" | tr '\n' ' '))"
    echo "$pids" | xargs -r kill -9
  else
    echo "[INFO] Port $port đang trống"
  fi
}

start_one() {
  local file="$1"
  local port="$2"
  local tag="$3"
  local log_file="$LOG_DIR/${tag}.log"

  echo "[INFO] Start $file at port $port"
  nohup "$VENV_PY" "$METHODS_DIR/$file" >"$log_file" 2>&1 &
  sleep 1

  if ss -ltnp "( sport = :$port )" 2>/dev/null | grep -q ":$port"; then
    echo "[OK]   Running on port $port | log: $log_file"
  else
    echo "[ERR]  Không chạy được $file trên port $port"
    echo "----- tail $log_file -----"
    tail -n 40 "$log_file" || true
    echo "--------------------------"
    exit 1
  fi
}

status_all() {
  for app in "${APPS[@]}"; do
    IFS=":" read -r file port tag <<<"$app"
    if ss -ltnp "( sport = :$port )" 2>/dev/null | grep -q ":$port"; then
      echo "[RUNNING] $file | port $port"
    else
      echo "[STOPPED] $file | port $port"
    fi
  done
}

test_all() {
  for app in "${APPS[@]}"; do
    IFS=":" read -r file port tag <<<"$app"
    code="$(curl --max-time 3 -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$port/" || true)"
    if [[ "$code" == "200" ]]; then
      echo "[OK]   http://127.0.0.1:$port/ -> $code ($file)"
    else
      echo "[FAIL] http://127.0.0.1:$port/ -> $code ($file)"
    fi
  done
}

start_all() {
  ensure_env
  for app in "${APPS[@]}"; do
    IFS=":" read -r _ port _ <<<"$app"
    kill_port "$port"
  done
  for app in "${APPS[@]}"; do
    IFS=":" read -r file port tag <<<"$app"
    start_one "$file" "$port" "$tag"
  done
}

stop_all() {
  for app in "${APPS[@]}"; do
    IFS=":" read -r _ port _ <<<"$app"
    kill_port "$port"
  done
}

show_logs() {
  for app in "${APPS[@]}"; do
    IFS=":" read -r file _ tag <<<"$app"
    echo "$file -> $LOG_DIR/${tag}.log"
  done
}

cmd="${1:-}" 
case "$cmd" in
  start)
    start_all
    ;;
  stop)
    stop_all
    ;;
  restart)
    stop_all
    start_all
    ;;
  status)
    status_all
    ;;
  test)
    test_all
    ;;
  logs)
    show_logs
    ;;
  *)
    usage
    exit 1
    ;;
esac
