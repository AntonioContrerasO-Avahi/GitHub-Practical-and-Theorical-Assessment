"""
Practice 9: Fine-tuning and Customization
Simple fine-tuning example using Hugging Face Transformers
Model: DistilBERT (small, ~66M parameters)
Task: Sentiment Classification
"""

import json
import os
from datetime import datetime
from datasets import Dataset, load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
    DataCollatorWithPadding
)
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd

# Configuration
MODEL_NAME = "distilbert-base-uncased"  # Small model (~66M params)
OUTPUT_DIR = "./fine_tuned_model"
MAX_LENGTH = 128
BATCH_SIZE = 8
EPOCHS = 3
NUM_LABELS = 3  # Bearish, Bullish, Neutral
DATASET_NAME = "zeroshot/twitter-financial-news-sentiment"
NUM_SAMPLES = 300  # Number of examples to use


def load_financial_dataset(n_samples=300):
    """Load Twitter financial news sentiment dataset from Hugging Face

    Dataset: zeroshot/twitter-financial-news-sentiment
    Labels: 0=Bearish, 1=Bullish, 2=Neutral
    """
    print(f"Loading dataset: {DATASET_NAME}")

    # Load the full dataset
    ds = load_dataset(DATASET_NAME)

    # Print dataset info
    print(f"Available splits: {list(ds.keys())}")
    print(f"Full train dataset size: {len(ds['train'])}")

    # Take first n_samples from training set
    dataset = ds['train'].select(range(min(n_samples, len(ds['train']))))

    print(f"Selected {len(dataset)} samples")
    print(f"Label distribution: {pd.Series(dataset['label']).value_counts().sort_index()}")

    # Show sample
    print("\nSample tweet:")
    print(f"  Text: {dataset[0]['text'][:100]}...")
    print(f"  Label: {dataset[0]['label']} (0=Bearish, 1=Bullish, 2=Neutral)")

    return dataset


def validate_dataset_format(dataset):
    """Validate the dataset format and content"""
    print("\n=== Dataset Validation ===")

    # Check required fields
    required_fields = ["text", "label"]
    for field in required_fields:
        if field not in dataset.column_names:
            raise ValueError(f"Missing required field: {field}")
        print(f"✓ Field '{field}' present")

    # Check data types
    sample_text = dataset[0]['text']
    sample_label = dataset[0]['label']

    if not isinstance(sample_text, str):
        raise ValueError("Text entries must be strings")
    print("✓ Text entries are strings")

    if not isinstance(sample_label, (int, np.integer)):
        raise ValueError("Labels must be integers")
    print("✓ Labels are integers")

    # Check label values
    unique_labels = set(dataset["label"])
    label_names = {0: "Bearish", 1: "Bullish", 2: "Neutral"}
    print(f"✓ Found {len(unique_labels)} unique labels: {unique_labels}")
    for label in sorted(unique_labels):
        print(f"  {label}: {label_names.get(label, 'Unknown')}")

    # Check dataset size
    n_samples = len(dataset)
    print(f"✓ Dataset contains {n_samples} examples")

    if n_samples < 100:
        print(f"⚠ Warning: Dataset has fewer than 100 examples ({n_samples})")

    # Check balance
    label_counts = pd.Series(dataset["label"]).value_counts().sort_index()
    print(f"✓ Label distribution:")
    for label, count in label_counts.items():
        print(f"  {label_names.get(label, 'Unknown')}: {count}")

    return True


def calculate_fine_tuning_cost(dataset, epochs=EPOCHS, batch_size=BATCH_SIZE):
    """Estimate fine-tuning cost (for AWS, GCP, etc.)"""
    print("\n=== Cost Estimation ===")

    n_samples = len(dataset)
    steps_per_epoch = n_samples // batch_size
    total_steps = steps_per_epoch * epochs

    # Rough estimates (update based on your cloud provider)
    # These are example costs - adjust for your provider
    cost_per_1000_steps = {
        "AWS SageMaker (ml.g4dn.xlarge)": 0.736 / 3600 * 1000,  # ~$0.20 per 1000 steps
        "Google Colab Pro (T4 GPU)": 0.01 * 1000 / 3600,  # ~$0.003 per 1000 steps
        "Local GPU (electricity only)": 0.002,  # ~$0.002 per 1000 steps
    }

    print(f"Training steps per epoch: {steps_per_epoch}")
    print(f"Total training steps: {total_steps}")
    print(f"Estimated training time: {total_steps * 0.5 / 60:.1f} minutes\n")

    print("Estimated costs:")
    for platform, cost_per_k in cost_per_1000_steps.items():
        estimated_cost = (total_steps / 1000) * cost_per_k
        print(f"  {platform}: ${estimated_cost:.4f}")

    return total_steps


def compute_metrics(pred):
    """Compute metrics for evaluation (multi-class classification)"""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)

    # Use weighted average for multi-class
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted'
    )
    acc = accuracy_score(labels, preds)

    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


def run_ab_experiment(base_model_name, fine_tuned_model_path, test_dataset):
    """Run A/B test comparing base model vs fine-tuned model"""
    print("\n=== A/B Experiment ===")

    # Load both models
    print("Loading base model...")
    base_tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    base_model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name, num_labels=NUM_LABELS
    )

    print("Loading fine-tuned model...")
    ft_tokenizer = AutoTokenizer.from_pretrained(fine_tuned_model_path)
    ft_model = AutoModelForSequenceClassification.from_pretrained(fine_tuned_model_path)

    # Create data collators and trainers for evaluation
    base_collator = DataCollatorWithPadding(tokenizer=base_tokenizer)
    ft_collator = DataCollatorWithPadding(tokenizer=ft_tokenizer)

    base_trainer = Trainer(model=base_model, data_collator=base_collator)
    ft_trainer = Trainer(model=ft_model, data_collator=ft_collator)

    # Evaluate both
    print("\nEvaluating base model...")
    base_results = base_trainer.predict(test_dataset)
    base_metrics = compute_metrics(base_results)

    print("\nEvaluating fine-tuned model...")
    ft_results = ft_trainer.predict(test_dataset)
    ft_metrics = compute_metrics(ft_results)

    # Compare results
    print("\n=== A/B Test Results ===")
    comparison = pd.DataFrame({
        'Base Model': base_metrics,
        'Fine-tuned Model': ft_metrics,
        'Improvement': {k: ft_metrics[k] - base_metrics[k] for k in base_metrics}
    })
    print(comparison)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"ab_test_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'base_model': base_metrics,
            'fine_tuned_model': ft_metrics,
            'timestamp': timestamp
        }, f, indent=2)

    print(f"\nResults saved to {results_file}")

    return comparison


def main():
    print("=" * 60)
    print("Practice 9: Fine-tuning and Customization")
    print("=" * 60)

    # Step 1: Load dataset
    print(f"\n[1/6] Loading financial sentiment dataset ({NUM_SAMPLES} samples)...")
    dataset = load_financial_dataset(n_samples=NUM_SAMPLES)

    # Step 2: Validate dataset
    print("\n[2/6] Validating dataset format...")
    validate_dataset_format(dataset)

    # Step 3: Calculate cost
    print("\n[3/6] Calculating estimated costs...")
    total_steps = calculate_fine_tuning_cost(dataset)

    # Step 4: Prepare data for training
    print("\n[4/6] Preparing data for training...")

    # Split into train/test (80/20)
    split_dataset = dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = split_dataset['train']
    test_dataset = split_dataset['test']

    print(f"Training samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")

    # Load tokenizer and model
    print(f"\nLoading tokenizer and model: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS
    )

    # Tokenize datasets
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH
        )

    train_dataset = train_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)

    # Step 5: Fine-tune the model
    print("\n[5/6] Starting fine-tuning...")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        push_to_hub=False,
        logging_dir='./logs',
        logging_steps=10,
        save_total_limit=2,
    )

    # Create data collator for dynamic padding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    # Train
    train_result = trainer.train()

    # Save the fine-tuned model
    print("\nSaving fine-tuned model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # Print training metrics
    print("\n=== Training Results ===")
    print(f"Training loss: {train_result.training_loss:.4f}")
    print(f"Training steps: {train_result.global_step}")

    # Step 6: Run A/B experiment
    print("\n[6/6] Running A/B experiment...")
    try:
        ab_results = run_ab_experiment(MODEL_NAME, OUTPUT_DIR, test_dataset)
    except Exception as e:
        print(f"A/B experiment failed: {e}")
        print("Evaluating fine-tuned model only...")
        eval_results = trainer.evaluate()
        print("\n=== Final Evaluation ===")
        for key, value in eval_results.items():
            print(f"{key}: {value:.4f}")

    print("\n" + "=" * 60)
    print("Fine-tuning completed successfully!")
    print(f"Model saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
