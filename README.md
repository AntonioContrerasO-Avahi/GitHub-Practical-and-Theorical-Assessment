# AWS Bedrock Practice Workbook

This repository contains a comprehensive Jupyter notebook workbook for learning and practicing AWS Bedrock capabilities with Claude AI models.

## Overview

The workbook covers 7 practical exercises ranging from basic model invocation to advanced RAG (Retrieval-Augmented Generation) systems with multi-turn conversations and embeddings. 3 more to come

## Target Environment

**Primary Environment: AWS SageMaker Domain**

This workbook is designed to run within an AWS SageMaker Domain environment, where IAM roles and AWS credentials are automatically configured through the execution role.

## Running Locally

While the notebook is optimized for SageMaker, it can be run locally with a few modifications:

### Prerequisites

1. **AWS Credentials Configuration**

   Before running the notebook locally, you must configure your AWS credentials:

   ```bash
   aws configure
   ```

   You'll need to provide:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region name (e.g., `us-east-1`)
   - Default output format (e.g., `json`)

2. **Python Environment**

   Ensure you have Python 3.8+ installed with the required dependencies:

   ```bash
   pip install boto3 langchain-aws langgraph langchain-community pypdf langchain-text-splitters sqlite-vec gradio tqdm
   ```

### Required Code Modifications for Local Execution

When running locally, you need to modify the Gradio launch configuration in **Task 6** and **Task 7**:

**Change this (SageMaker configuration):**
```python
demo.launch(
    share=True,
    server_port=7860,
    show_error=True
)
```

**To this (Local configuration):**
```python
demo.launch(
    share=False,      # False for local execution
    server_name="127.0.0.1",  # localhost
    server_port=7860,
    show_error=True,
    inbrowser=True    # ✅ Automatically opens browser
)
```

### Running in SageMaker

If you're running in a SageMaker Domain, **leave the code as-is**. The execution role will automatically handle AWS authentication, and the Gradio interface will be accessible through SageMaker's proxy.

## Execution Instructions

### Important: Run Order

1. **First**: Execute the full notebook (`task-1-to-6.ipynb`) from start to finish
   - This sets up the environment, loads models, creates vector stores, and prepares all necessary components

2. **Then**: Execute individual task cells for Task 5, Task 6, and Task 7 if you want to interact with:
   - Task 5: Multi-turn conversation chatbot with memory
   - Task 6: RAG system with document retrieval
   - Task 7: Advanced RAG with Gradio interface

### What's Included

The notebook covers the following practices:

1. **Setup Confirmation** - Verify AWS Bedrock connectivity
2. **Practice 1: First Call to Claude** - Basic model invocation
3. **Practice 2: Model Comparison** - Compare different Claude and Nova models
4. **Practice 3: Parameter Handling** - Experiment with temperature, top_p, and top_k
5. **Practice 4: Response Streaming** - Real-time token streaming
6. **Practice 5: Multi-turn Conversations** - Chatbot with persistent memory and summarization
7. **Practice 6: Basic RAG with Embeddings** - Document ingestion and vector search
8. **Practice 7: Advanced RAG System** - Complete RAG pipeline with Gradio UI

## Troubleshooting

### Common Issues

**Issue**: `NoCredentialsError` or authentication errors
- **Solution**: Run `aws configure` and ensure your credentials are properly set

**Issue**: Gradio interface doesn't open
- **Solution**: Check that you've modified the launch configuration for local execution (see above)

**Issue**: Model not found or access denied
- **Solution**: Ensure your AWS account has access to AWS Bedrock and the specific models used in the notebook

**Issue**: Vector store creation fails
- **Solution**: Ensure you have the PDF file (`styleguide _ Style guides for Google-originated open-source projects.pdf`) in the working directory

## Architecture

- **Embeddings**: Amazon Titan Text Embeddings v1
- **LLM**: Claude 3.5 Haiku (primary), Claude 3 Haiku, Amazon Nova models
- **Vector Store**: SQLite-Vec (local vector database)
- **Framework**: LangChain + LangGraph for agent orchestration
- **UI**: Gradio for interactive interfaces

## File Structure

```
.
├── README.md                           # This file
├── task-1-to-6.ipynb                  # Main practice notebook
├── vector_store.db                    # Generated SQLite vector database (after running)
├── chatbot_memory.sqlite              # Generated conversation memory (after running)
└── styleguide _ Style guides...pdf    # Sample PDF for RAG exercises
```

## Notes

- The notebook uses streaming for real-time responses
- Conversation memory is persisted using SQLite
- Automatic summarization triggers after 10 messages to manage context length
- Vector embeddings are cached locally for faster retrieval

## Support

For issues or questions related to AWS Bedrock, refer to the [official AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/).

---

**Last Updated**: 2026-02-06
**AWS Region**: us-east-1
**Primary Model**: Claude 3.5 Haiku (us.anthropic.claude-3-5-haiku-20241022-v1:0)