# 04 — Capstone: GenAI Pipeline Script

A nightly evaluation pipeline that downloads a dataset from S3, runs chunking
inference, grades results, and uploads them back to S3.

---

## Prerequisites

| Tool | Purpose |
|------|---------|
| `bash` ≥ 4 | Script runtime |
| `aws` CLI v2 | S3 sync (download + upload) |
| `terraform` ≥ 1.6 | Provision / tear down S3 bucket |
| `uv` | Run `ingest.py` (Python 3.11+) |
| `jq` | Build JSON payloads (grading + Slack alert) |
| `flock` | Concurrency lock (ships with `util-linux`; on macOS install via `brew install util-linux`) |

---

## Quick Start

```bash
make help   # list all available targets
```

### 1 — Create the Slack app and get a webhook URL

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps) and click **Create New App → From scratch**.
2. Name it (e.g. `nightly-eval-alerts`) and select your workspace.
3. In the left sidebar click **Incoming Webhooks** → toggle **On**.
4. Click **Add New Webhook to Workspace**, pick a channel, click **Allow**.
5. Copy the URL — it looks like `https://hooks.slack.com/services/T.../B.../...`.

### 2 — Configure `.env`

```bash
make setup          # copies .env.example → .env
# Edit .env: set S3_BUCKET, AWS_REGION, and SLACK_WEBHOOK_URL
```

> `SLACK_WEBHOOK_URL` is optional — alerts are silently skipped if unset.

### 3 — Provision infrastructure

```bash
make infra-up       # reads .env, runs terraform init + apply; prints bucket name
```

> Both download and upload require AWS credentials (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` or an IAM role).

---

### 4 — Run the pipeline

```bash
make run
```

The script executes four steps in order:

| Step | Name | What it does |
|------|------|-------------|
| 1 | `download` | `aws s3 sync` dataset from `s3://$S3_BUCKET/dataset/input/` |
| 2 | `inference` | Runs `ingest.py` via `uv run python` to chunk each `.txt` file |
| 3 | `grading` | Grades each file, simulates 25% failure rate, writes per-file JSON + `summary.json` |
| 4 | `upload` | `aws s3 sync` results to `s3://$S3_BUCKET/dataset/results/<date>/` (requires AWS credentials) |

Logs are written to `./logs/nightly_eval_<YYYY-MM-DD>.log`.

---

### 5 — Run ingest.py standalone (optional)

```bash
uv run python ingest.py
```

Reads all `.txt` files from the `texts/` directory and prints chunk previews.

---

### 6 — Tear down the S3 bucket

```bash
cd terraform
terraform destroy -auto-approve
```

---

## Safety Mechanisms

| Mechanism | Implementation |
|-----------|---------------|
| Strict mode | `set -euo pipefail` — any unset variable or failed command aborts the run |
| Env var validation | `: "${VAR:?}"` pattern — fails immediately with a descriptive message if a required variable is missing |
| Step tracking + cleanup | `trap cleanup EXIT` reads `$CURRENT_STEP` to report exactly which step failed, then removes the temp work dir |
| Concurrency safety | `flock -n 9` on `/tmp/nightly_eval.lock` — a second run exits immediately if one is already active |
| Structured logging | `log()` writes `[ISO-8601 timestamp] [LEVEL] [step:NAME] message` to stdout, the log file, and syslog (`logger`) |
| Slack alert on failure | `slack_alert()` POSTs a JSON payload to `$SLACK_WEBHOOK_URL` (skipped silently if the variable is not set) |

---

## Project Structure

```
04-capstone/
├── nightly_eval.sh   # Main pipeline script
├── ingest.py         # Document chunker (inference step)
├── texts/            # Sample .txt files uploaded to S3 by Terraform
│   ├── doc1.txt
│   ├── doc2.txt
│   ├── doc3.txt
│   └── doc4.txt
├── logs/             # Created at runtime — daily log files
└── terraform/
    ├── main.tf       # S3 bucket + public-read policy + file upload
    ├── variables.tf  # bucket_name, aws_region, environment
    └── outputs.tf    # bucket_name, bucket_arn, uploaded_files
```
