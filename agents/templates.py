"""
Prompt templates for CV extraction chatbot.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# System prompt for CV extraction
CV_EXTRACTION_SYSTEM_PROMPT = """You are an expert CV/Resume analyzer. Your task is to extract structured information from CVs and provide helpful insights.

When analyzing a CV, you should:
1. Extract key information like contact details, work experience, education, skills, and certifications
2. Provide a summary of the candidate's qualifications
3. Identify strengths and areas of expertise
4. Answer specific questions about the candidate's background
5. Be objective and professional in your analysis

The CV text will be provided in the conversation. Always base your responses on the actual content of the CV."""

# Main chat template
cv_chat_template = ChatPromptTemplate.from_messages([
    ("system", CV_EXTRACTION_SYSTEM_PROMPT),
    ("system", "Here is the CV to analyze:\n\n{cv_text}"),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
])

# Quick extraction template (for structured data extraction)
CV_QUICK_EXTRACT_PROMPT = """You are an expert CV/Resume analyzer. Extract structured information from the following CV text and format it as JSON following the provided schema.

CV Text:
{cv_text}

Extract all available information and structure it according to the CV schema. If certain information is not available, omit those fields or use null values as appropriate.

Provide your response as valid JSON."""

quick_extract_template = ChatPromptTemplate.from_messages([
    ("system", CV_QUICK_EXTRACT_PROMPT),
])

# Summary template
CV_SUMMARY_PROMPT = """Analyze the following CV and provide a concise professional summary (3-5 sentences) highlighting:
- Years of experience and seniority level
- Key technical skills and expertise areas
- Notable achievements or strengths
- Overall profile fit

CV Text:
{cv_text}

Professional Summary:"""

summary_template = ChatPromptTemplate.from_messages([
    ("system", CV_SUMMARY_PROMPT),
])
