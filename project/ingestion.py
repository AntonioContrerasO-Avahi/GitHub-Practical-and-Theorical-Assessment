# ============================================================================================================
# RAG SYSTEM - DOCUMENT INGESTION (ChromaDB Version)
# Ingesta de documentos PDF a vector store con embeddings de AWS Bedrock
# ============================================================================================================

import boto3
import os
from pathlib import Path
from langchain_aws import BedrockEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# ============================================================================================================
# CONFIGURATION
# ============================================================================================================
REGION = "us-east-1"
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "python_docs"
PDF_FILE = "../styleguide _ Style guides for Google-originated open-source projects.pdf"

print("=" * 100)
print("🚀 STARTING RAG INGESTION PIPELINE (ChromaDB)")
print("=" * 100)

# ============================================================================================================
# STEP 1: LOAD EMBEDDINGS
# ============================================================================================================
print("\n📦 Step 1: Loading embedding model...")
embeddings = BedrockEmbeddings(
    region_name=REGION,
    model_id="amazon.titan-embed-text-v1"
)
print("✅ Embeddings loaded\n")

# ============================================================================================================
# STEP 2: LOAD PDF DOCUMENT
# ============================================================================================================
print("📄 Step 2: Loading PDF document...")
if not os.path.exists(PDF_FILE):
    raise FileNotFoundError(f"File not found: {PDF_FILE}")

loader = PyPDFLoader(file_path=PDF_FILE)
documents = loader.load()
print(f"✅ Loaded {len(documents)} pages\n")

# ============================================================================================================
# STEP 3: SPLIT INTO CHUNKS
# ============================================================================================================
print("✂️  Step 3: Splitting document into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)
chunks = text_splitter.split_documents(documents)
print(f"✅ Created {len(chunks)} chunks\n")

# Show sample chunk
print("📝 Sample chunk:")
print("-" * 100)
print(chunks[0].page_content[:300] + "...")
print(f"Metadata: {chunks[0].metadata}")
print("-" * 100 + "\n")

# ============================================================================================================
# STEP 4: CREATE VECTOR STORE WITH CHROMADB
# ============================================================================================================
print("🗄️  Step 4: Creating ChromaDB vector store (this may take a few minutes)...")

# Create Chroma DB from documents
db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_DB_DIR
)

print(f"✅ Vector store created with {len(chunks)} documents")
print(f"📁 Database location: {CHROMA_DB_DIR}\n")

# ============================================================================================================
# STEP 5: TEST SIMILARITY SEARCH
# ============================================================================================================
print("🔍 Step 5: Testing semantic search...")

test_queries = [
    "What are the main Python style guidelines?",
    "How should I format Python code?",
    "What are the naming conventions?"
]

for query in test_queries:
    print(f"\n🔎 Query: '{query}'")
    print("-" * 100)

    results = db.similarity_search(query, k=2)

    for i, doc in enumerate(results, 1):
        print(f"\n📄 Result {i} (relevance score):")
        print(f"{doc.page_content[:200]}...")
        print(f"Source: Page {doc.metadata.get('page', 'N/A')}")

    print("-" * 100)

# ============================================================================================================
# STEP 6: TEST SIMILARITY SEARCH WITH SCORES
# ============================================================================================================
print("\n📊 Step 6: Testing similarity search with scores...")
query = "Python naming conventions"
results_with_scores = db.similarity_search_with_score(query, k=3)

print(f"\n🔎 Query: '{query}'")
print("-" * 100)
for i, (doc, score) in enumerate(results_with_scores, 1):
    print(f"\n📄 Result {i} - Score: {score:.4f}")
    print(f"{doc.page_content[:150]}...")
    print(f"Page: {doc.metadata.get('page', 'N/A')}")
print("-" * 100)

# ============================================================================================================
# SUMMARY
# ============================================================================================================
print("\n" + "=" * 100)
print("✅ INGESTION COMPLETED SUCCESSFULLY")
print("=" * 100)
print(f"📁 Database directory: {CHROMA_DB_DIR}")
print(f"📦 Collection name: {COLLECTION_NAME}")
print(f"📊 Total chunks: {len(chunks)}")
print(f"📄 Original pages: {len(documents)}")
print(f"🔢 Embedding dimension: {len(embeddings.embed_query('test'))}")
print("=" * 100)

# ============================================================================================================
# SAVE REFERENCE FOR LATER USE
# ============================================================================================================
print("\n💾 Vector store 'db' available for queries")
print("💡 Usage examples:")
print("   - db.similarity_search('your query', k=3)")
print("   - db.similarity_search_with_score('your query', k=3)")
print("   - db.as_retriever(search_kwargs={'k': 5})")
print("\n✨ You can now use this in your multi-agent system!")
