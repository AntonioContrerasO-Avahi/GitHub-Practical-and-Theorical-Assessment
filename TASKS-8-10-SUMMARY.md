# Tasks 8-10 Summary: Advanced LLM Practices

## 📊 Task 8: Model Evaluation and Comparison

**Objective**: Evaluate and compare multiple LLM models using automated metrics and LLM-as-judge evaluation.

**Implementation**: `task-8.ipynb`

### Key Features:
- ✅ **Multi-Model Evaluation**: Tests 3 AWS Bedrock models
  - Claude 3.5 Haiku
  - Claude 3 Haiku
  - Amazon Nova Lite
- ✅ **Automated Metrics**:
  - Response time measurement
  - Token counting (input/output)
  - Cost calculation per model
  - Statistical analysis (mean, median, std)
- ✅ **LLM-as-Judge Evaluation**:
  - Uses Claude Sonnet 4.5 as judge
  - Structured scoring (1-5 scale)
  - Qualitative feedback
  - Multi-dimensional assessment
- ✅ **Comprehensive Reporting**:
  - Performance metrics comparison
  - Cost analysis per model
  - Visual comparison charts
  - Domain-specific performance tracking

### Models Evaluated:
```python
MODELS = [
    "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    "us.anthropic.claude-3-haiku-20240307-v1:0",
    "amazon.nova-lite-v1:0"
]
JUDGE_MODEL = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### Output Files:
- `evaluation_results/eval.csv` - Complete evaluation results
- `evaluation_results/automatic_metrics.csv` - Performance metrics
- `evaluation_results/complete_comparison.png` - Visual comparison

---

## 🎯 Task 9: Fine-tuning and Customization

**Objective**: Fine-tune a small transformer model using Hugging Face on real-world financial sentiment data.

**Implementation**: `task-9.py`

### Key Features:
- ✅ **Real Dataset**: Twitter financial news sentiment (300 examples)
  - Dataset: `zeroshot/twitter-financial-news-sentiment`
  - 3 classes: Bearish (0), Bullish (1), Neutral (2)
- ✅ **Small Model**: DistilBERT (~66M parameters)
  - Fast training
  - Low resource requirements
  - Production-ready
- ✅ **Data Validation**:
  - Format checking
  - Label distribution analysis
  - Data quality verification
- ✅ **Cost Estimation**:
  - Training time prediction
  - Cost breakdown by platform (AWS, GCP, Local)
  - Step count calculation
- ✅ **A/B Testing**:
  - Base model vs fine-tuned comparison
  - Multi-class metrics (accuracy, F1, precision, recall)
  - Performance improvement tracking

### Training Configuration:
```python
MODEL_NAME = "distilbert-base-uncased"
NUM_LABELS = 3  # Bearish, Bullish, Neutral
EPOCHS = 3
BATCH_SIZE = 8
MAX_LENGTH = 128
```

### Output:
- `./fine_tuned_model/` - Fine-tuned model artifacts
- `ab_test_results_*.json` - A/B test comparison results
- Training metrics and evaluation scores

### Key Improvements:
- Multi-class classification support
- DataCollatorWithPadding for dynamic batching
- Weighted metrics for imbalanced classes
- Early stopping for efficiency

---

## 🛡️ Task 10: Guardrails System

**Objective**: Implement comprehensive security and quality controls with content moderation, rate limiting, and monitoring.

**Implementation**: `task-10.py`, `task-10-test.py`

### Key Features:

#### 1. **Content Moderation** (LLM-powered)
- Uses Claude Sonnet 4.5 for intelligent content analysis
- Detects and blocks:
  - 🚫 Toxic or harmful language
  - 🔐 Personally Identifiable Information (PII)
  - ⚖️ Instructions for illegal activities
  - 💔 Hate speech or discrimination
  - 🎭 System manipulation attempts
- Returns structured risk levels: `low`, `medium`, `high`, `critical`

#### 2. **Rate Limiting** (SQLite-based)
- Per-user request quotas:
  - **Daily limit**: 100 requests/day
  - **Hourly limit**: 20 requests/hour
- Automatic counter reset
- Persistent storage
- No authentication required (simple user ID system)

#### 3. **Alert System**
- Real-time alerts for problematic content
- Multiple severity levels
- Database persistence (`alerts.sqlite`)
- Alert types:
  - `content_violation` - Moderation blocks
  - `rate_limit_exceeded` - Quota exceeded
  - `system_error` - System failures

#### 4. **Complete Logging**
- All interactions logged with timestamps
- Separate log files per user session
- Detailed logging:
  - User messages
  - Moderation decisions
  - Rate limit checks
  - Agent responses
  - Errors and warnings

### Architecture:
```
User Request
    ↓
[1] Rate Limiting Check ────→ Block if exceeded
    ↓ (allowed)
[2] Content Moderation ─────→ Block if inappropriate
    ↓ (approved)
[3] Logging (pre-processing)
    ↓
[4] Agent Processing (from Task-7)
    ↓
[5] Logging (post-processing)
    ↓
Response to User
```

### Database Schema:

**Rate Limits** (`rate_limits.sqlite`):
- `users` - User quotas and statistics
- `request_log` - All moderation decisions

**Alerts** (`alerts.sqlite`):
- `alerts` - Security incidents and violations

### Configuration:
```python
MODEL_ID = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
MAX_REQUESTS_PER_DAY = 100
MAX_REQUESTS_PER_HOUR = 20
```

### Output:
- `rate_limits.sqlite` - Rate limiting database
- `alerts.sqlite` - Alert history
- `logs/session_{user_id}_{timestamp}.log` - Interaction logs
- Gradio UI on port 7860

### Testing:
Run `task-10-test.py` to test:
- ✅ Rate limiting functionality
- ✅ Content moderation with various inputs
- ✅ Alert creation and retrieval
- ✅ Database operations

---

## 🔄 Integration & Dependencies

### Task Flow:
1. **Task 8** → Model selection and evaluation
2. **Task 9** → Model customization and fine-tuning
3. **Task 10** → Production-ready deployment with guardrails

### Common Technologies:
- **AWS Bedrock**: Claude models, Nova models
- **Hugging Face**: Transformers, Datasets
- **LangChain**: Agent framework, tools
- **SQLite**: Persistence layer
- **Gradio**: Web interfaces
- **Pydantic**: Data validation

### File Structure:
```
├── task-8.ipynb                    # Model evaluation notebook
├── task-9.py                       # Fine-tuning script
├── task-10.py                      # Guardrails system
├── task-10-test.py                 # Guardrails testing
├── evaluation_results/             # Task 8 outputs
├── fine_tuned_model/               # Task 9 outputs
├── rate_limits.sqlite              # Task 10 DB
├── alerts.sqlite                   # Task 10 DB
└── logs/                           # Task 10 logs
```

---

## 🎓 Learning Outcomes

After completing these tasks, you will understand:

✅ **Model Evaluation**:
- Automated metrics collection
- LLM-as-judge methodology
- Cost-performance trade-offs
- Multi-model comparison

✅ **Fine-tuning**:
- Dataset preparation and validation
- Transfer learning with small models
- A/B testing methodology
- Cost estimation

✅ **Production Guardrails**:
- Content moderation strategies
- Rate limiting implementation
- Security monitoring
- Logging best practices
- Multi-layered defense

---

## 🚀 Quick Start

### Task 8 - Evaluation
```bash
jupyter notebook task-8.ipynb
# Run all cells
```

### Task 9 - Fine-tuning
```bash
pip install -r task-9-requirements.txt
python task-9.py
```

### Task 10 - Guardrails
```bash
# Test mode
python task-10-test.py

# UI mode
python task-10.py
# Access: http://localhost:7860
```

---

## 📊 Key Metrics & Results

### Task 8 Results (Example):
- **Fastest Model**: Claude 3.5 Haiku (~0.8s avg)
- **Most Cost-Effective**: Amazon Nova Lite
- **Best Quality**: Claude 3.5 Haiku (judge score)

### Task 9 Results (Example):
- **Training Time**: ~3-5 minutes (3 epochs)
- **Accuracy Improvement**: +33% over base model
- **F1 Score**: ~0.95 on test set

### Task 10 Performance:
- **Moderation Latency**: ~1-2s per request
- **Rate Limit Checks**: <10ms
- **False Positive Rate**: Configurable via prompt tuning

---

## 🔧 Configuration & Customization

All tasks are highly configurable:

- **Task 8**: Edit model list, add custom prompts
- **Task 9**: Adjust epochs, batch size, dataset size
- **Task 10**: Modify rate limits, moderation criteria

---

## 📚 Best Practices Demonstrated

1. ✅ **Structured evaluation** before deployment
2. ✅ **Cost-aware** model selection
3. ✅ **Data validation** in ML pipelines
4. ✅ **A/B testing** for model improvements
5. ✅ **Multi-layered security** for production
6. ✅ **Comprehensive logging** for debugging
7. ✅ **User quotas** to prevent abuse
8. ✅ **Alert systems** for monitoring

---

**Status**: ✅ All tasks completed and tested
**Date**: February 10, 2026
