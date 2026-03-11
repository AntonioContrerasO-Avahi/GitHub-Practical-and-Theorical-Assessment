#!/usr/bin/env bash
# nightly_eval.sh — 4-step RAG evaluation pipeline
# Steps: download dataset → run inference (chunk) → grade results → upload back to S3
set -euo pipefail

# =============================================================================
# 1. ENV VAR VALIDATION — fail immediately if anything is missing
# =============================================================================
: "${S3_BUCKET:?S3_BUCKET is required — set it in .env}"
: "${AWS_REGION:?AWS_REGION is required — set it in .env}"
: "${SLACK_WEBHOOK_URL:=}"  # optional — alert only fires when set
: "${PIPELINE_ENV:=dev}"   # optional with default

# =============================================================================
# 2. CONFIG
# =============================================================================
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
LOG_FILE="$LOG_DIR/nightly_eval_$(date +%Y-%m-%d).log"
LOCK_FILE="/tmp/nightly_eval.lock"
WORK_DIR="$(mktemp -d /tmp/nightly_eval_XXXXXX)"
S3_INPUT_PREFIX="dataset/input"
S3_OUTPUT_PREFIX="dataset/results/$(date +%Y-%m-%d)"
CURRENT_STEP="init"

mkdir -p "$LOG_DIR"

# =============================================================================
# 3. STRUCTURED LOGGING — timestamped, writes to file AND syslog
# =============================================================================
log() {
  local level="${1:-INFO}"
  local msg="${2:-}"
  local ts
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local line="[$ts] [$level] [step:$CURRENT_STEP] $msg"

  echo "$line" | tee -a "$LOG_FILE"           # stdout + log file
  logger -t "nightly_eval" "$line" 2>/dev/null || true   # syslog (journalctl on Linux)
}

# =============================================================================
# 4. SLACK ALERT ON FAILURE
# =============================================================================
slack_alert() {
  local msg="$1"
  [[ -z "$SLACK_WEBHOOK_URL" ]] && return 0  # skip if not configured

  local payload
  payload=$(jq -n \
    --arg text "🚨 *nightly_eval.sh failed* on \`$(hostname)\`\n*Step:* \`$CURRENT_STEP\`\n*Env:* \`$PIPELINE_ENV\`\n*Error:* $msg\n*Log:* \`$LOG_FILE\`" \
    '{text: $text}')

  curl -sf -X POST "$SLACK_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    && log "INFO" "Slack alert sent" \
    || log "WARN" "Slack alert failed to deliver"
}

# =============================================================================
# 5. TRAP — cleanup + alert on any exit
# =============================================================================
cleanup() {
  local exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    log "ERROR" "Pipeline failed at step '$CURRENT_STEP' (exit code: $exit_code)"
    slack_alert "Exited with code $exit_code at step \`$CURRENT_STEP\`"
  else
    log "INFO" "Pipeline completed successfully"
  fi

  log "INFO" "Cleaning up work dir: $WORK_DIR"
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

# =============================================================================
# 6. CONCURRENCY SAFETY — flock prevents overlapping runs
# =============================================================================
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  log "ERROR" "Another nightly_eval run is already active (lock: $LOCK_FILE). Exiting."
  exit 1
fi

# =============================================================================
# PIPELINE STEPS
# =============================================================================

# --- STEP 1: Download dataset from S3 ---
CURRENT_STEP="download"
log "INFO" "Downloading dataset from s3://$S3_BUCKET/$S3_INPUT_PREFIX/"

aws s3 sync \
  "s3://$S3_BUCKET/$S3_INPUT_PREFIX/" \
  "$WORK_DIR/input/" \
  --region "$AWS_REGION" \
  --quiet

file_count=$(find "$WORK_DIR/input/" -name "*.txt" | wc -l | tr -d ' ')
log "INFO" "Downloaded $file_count file(s) to $WORK_DIR/input/"

if [[ $file_count -eq 0 ]]; then
  log "ERROR" "No .txt files found in s3://$S3_BUCKET/$S3_INPUT_PREFIX/"
  exit 1
fi

# --- STEP 2: Run inference — chunk each document ---
CURRENT_STEP="inference"
log "INFO" "Running chunking inference on $file_count file(s)"

mkdir -p "$WORK_DIR/chunks"

for txt_file in "$WORK_DIR/input/"*.txt; do
  filename=$(basename "$txt_file")
  log "INFO" "  Chunking: $filename"
  uv run python "$PROJECT_DIR/ingest.py" 2>>"$LOG_FILE"
done

log "INFO" "Inference complete"

# --- STEP 3: Grade results — 25% simulated failure rate ---
CURRENT_STEP="grading"
log "INFO" "Grading chunked results"

mkdir -p "$WORK_DIR/results"
passed=0
failed=0

for txt_file in "$WORK_DIR/input/"*.txt; do
  filename=$(basename "$txt_file" .txt)
  result_file="$WORK_DIR/results/${filename}_result.json"

  # Simulate 25% failure probability
  roll=$((RANDOM % 100))
  if [[ $roll -lt 25 ]]; then
    status="FAILED"
    reason="simulated_read_error"
    (( failed++ )) || true
    log "WARN" "  FAILED: $filename (simulated error)"
  else
    status="PASSED"
    reason="ok"
    (( passed++ )) || true
    log "INFO" "  PASSED: $filename"
  fi

  jq -n \
    --arg file "$filename" \
    --arg status "$status" \
    --arg reason "$reason" \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    '{file: $file, status: $status, reason: $reason, graded_at: $ts}' \
    > "$result_file"
done

log "INFO" "Grading complete — passed: $passed, failed: $failed"

# Write summary
jq -n \
  --argjson passed "$passed" \
  --argjson failed "$failed" \
  --arg env "$PIPELINE_ENV" \
  --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  '{passed: $passed, failed: $failed, environment: $env, completed_at: $ts}' \
  > "$WORK_DIR/results/summary.json"

# --- STEP 4: Upload results back to S3 ---
CURRENT_STEP="upload"
log "INFO" "Uploading results to s3://$S3_BUCKET/$S3_OUTPUT_PREFIX/"

aws s3 sync \
  "$WORK_DIR/results/" \
  "s3://$S3_BUCKET/$S3_OUTPUT_PREFIX/" \
  --region "$AWS_REGION" \
  --quiet

log "INFO" "Uploaded results to s3://$S3_BUCKET/$S3_OUTPUT_PREFIX/"
log "INFO" "Pipeline finished — passed: $passed, failed: $failed"