# ============================================================================================================
# MULTI-AGENT CODE REVIEW COORDINATOR (DeepAgents)
# Main agent orchestrates specialized review subagents for comprehensive code analysis
# ============================================================================================================

from deepagents import create_deep_agent
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool
from typing import List, Dict
import ast
import re

# ============================================================================================================
# CONFIGURATION
# ============================================================================================================
REGION = "us-east-1"
MAIN_MODEL = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"  # Sonnet for orchestration
SUBAGENT_MODEL = "us.anthropic.claude-3-5-haiku-20241022-v1:0"  # Haiku for speed
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "python_docs"

# ============================================================================================================
# LOAD VECTOR STORE FOR STYLE GUIDELINES
# ============================================================================================================
print("📦 Loading vector store...")
embeddings = BedrockEmbeddings(
    region_name=REGION,
    model_id="amazon.titan-embed-text-v1"
)

vector_db = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DB_DIR
)
print("✅ Vector store loaded\n")

# ============================================================================================================
# UTILITY: CODE SPLITTER
# ============================================================================================================
def split_code_into_sections(code: str) -> List[Dict[str, str]]:
    """
    Divide Python code into logical sections (functions, classes, imports)

    Returns:
        List of dicts with 'type', 'name', 'code', 'line_start', 'line_end'
    """
    sections = []
    lines = code.split('\n')

    try:
        tree = ast.parse(code)

        # Extract imports
        import_lines = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append((i, line))

        if import_lines:
            sections.append({
                'type': 'imports',
                'name': 'imports',
                'code': '\n'.join([l[1] for l in import_lines]),
                'line_start': import_lines[0][0],
                'line_end': import_lines[-1][0]
            })

        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno
                func_code = '\n'.join(lines[start_line:end_line])

                sections.append({
                    'type': 'function',
                    'name': node.name,
                    'code': func_code,
                    'line_start': start_line + 1,
                    'line_end': end_line
                })

            elif isinstance(node, ast.ClassDef):
                start_line = node.lineno - 1
                end_line = node.end_lineno
                class_code = '\n'.join(lines[start_line:end_line])

                sections.append({
                    'type': 'class',
                    'name': node.name,
                    'code': class_code,
                    'line_start': start_line + 1,
                    'line_end': end_line
                })

    except SyntaxError as e:
        # If parsing fails, treat entire code as one section
        sections.append({
            'type': 'raw',
            'name': 'code_block',
            'code': code,
            'line_start': 1,
            'line_end': len(lines),
            'syntax_error': str(e)
        })

    return sections


# ============================================================================================================
# TOOLS FOR SUBAGENTS
# ============================================================================================================

@tool
def search_style_guidelines(query: str) -> str:
    """
    Search Python style guidelines from the vector database (Google Python Style Guide).
    Use this when you need to check PEP8 conventions, naming rules, or formatting best practices.

    Args:
        query: What guideline to search (e.g., "function naming conventions", "docstring format")

    Returns:
        Relevant style guidelines from documentation
    """
    try:
        results = vector_db.similarity_search(query, k=2)

        if not results:
            return "No relevant style guidelines found."

        guidelines = "\n\n".join([
            f"📖 Guideline:\n{doc.page_content[:400]}"
            for doc in results
        ])

        return f"Style Guidelines Found:\n\n{guidelines}"

    except Exception as e:
        return f"Error searching guidelines: {str(e)}"


@tool
def analyze_code_structure(code: str) -> str:
    """
    Analyze Python code structure: complexity, nesting depth, metrics.

    Args:
        code: Python code to analyze

    Returns:
        Structural analysis with complexity metrics
    """
    try:
        tree = ast.parse(code)

        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        loops = len([n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))])
        conditionals = len([n for n in ast.walk(tree) if isinstance(n, ast.If)])

        lines = code.split('\n')
        non_empty = [l for l in lines if l.strip() and not l.strip().startswith('#')]

        complexity = 'High' if loops + conditionals > 5 else 'Medium' if loops + conditionals > 2 else 'Low'

        return f"""📊 Structure Analysis:
• Functions: {len(functions)} ({', '.join(functions[:3]) if functions else 'none'})
• Classes: {len(classes)} ({', '.join(classes) if classes else 'none'})
• Lines of code: {len(non_empty)}
• Loops: {loops}
• Conditionals: {conditionals}
• Cyclomatic Complexity: {complexity}"""

    except SyntaxError as e:
        return f"⚠️ Syntax Error: {str(e)}"
    except Exception as e:
        return f"❌ Analysis Error: {str(e)}"


@tool
def check_security_vulnerabilities(code: str) -> str:
    """
    Scan for common security vulnerabilities: injection, unsafe functions, hardcoded secrets.

    Args:
        code: Python code to scan

    Returns:
        Security issues found with severity levels
    """
    issues = []

    # Dangerous functions
    dangerous_patterns = [
        (r'\beval\s*\(', 'CRITICAL', 'Use of eval() - code injection risk'),
        (r'\bexec\s*\(', 'CRITICAL', 'Use of exec() - code execution risk'),
        (r'pickle\.loads?\s*\(', 'HIGH', 'Unsafe pickle deserialization'),
        (r'os\.system\s*\(', 'HIGH', 'Command injection via os.system()'),
        (r'subprocess\.[^(]*\([^)]*shell\s*=\s*True', 'HIGH', 'subprocess with shell=True'),
        (r'__import__\s*\(', 'MEDIUM', 'Dynamic imports - potential security risk'),
    ]

    for pattern, severity, message in dangerous_patterns:
        if re.search(pattern, code):
            issues.append(f"{severity}: {message}")

    # Hardcoded secrets
    secret_patterns = [
        (r'(password|pwd|passwd)\s*=\s*[\'"][^\'"]{3,}[\'"]', 'CRITICAL', 'Hardcoded password detected'),
        (r'(api_key|apikey|api-key)\s*=\s*[\'"][^\'"]{10,}[\'"]', 'HIGH', 'Hardcoded API key'),
        (r'(secret|token)\s*=\s*[\'"][^\'"]{10,}[\'"]', 'HIGH', 'Hardcoded secret/token'),
        (r'(aws_access_key|aws_secret)', 'CRITICAL', 'AWS credentials in code'),
    ]

    for pattern, severity, message in secret_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"{severity}: {message}")

    # SQL injection patterns
    if re.search(r'execute\s*\(\s*[\'"].*%s.*[\'"]', code):
        issues.append("HIGH: Potential SQL injection - use parameterized queries")

    if not issues:
        return "✅ No obvious security vulnerabilities detected."

    return "🔐 Security Issues:\n" + "\n".join([f"• {issue}" for issue in issues])


@tool
def check_pep8_compliance(code: str) -> str:
    """
    Check PEP8 compliance: naming, spacing, line length, formatting.

    Args:
        code: Python code to check

    Returns:
        PEP8 violations found
    """
    issues = []

    lines = code.split('\n')

    # Check line length
    for i, line in enumerate(lines, 1):
        if len(line) > 79 and not line.strip().startswith('#'):
            issues.append(f"Line {i}: Exceeds 79 characters ({len(line)} chars)")

    # Check function naming (should be snake_case)
    func_pattern = r'def\s+([A-Z][a-zA-Z0-9]*)\s*\('
    for match in re.finditer(func_pattern, code):
        issues.append(f"Function '{match.group(1)}' should use snake_case (PEP8)")

    # Check class naming (should be PascalCase)
    class_pattern = r'class\s+([a-z_][a-z0-9_]*)\s*[:(]'
    for match in re.finditer(class_pattern, code):
        issues.append(f"Class '{match.group(1)}' should use PascalCase (PEP8)")

    # Check spacing around operators
    if re.search(r'\w=\w', code):
        issues.append("Missing spaces around assignment operator '='")

    # Check multiple statements on one line
    for i, line in enumerate(lines, 1):
        if line.strip() and line.count(';') > 0:
            issues.append(f"Line {i}: Multiple statements on one line (use separate lines)")

    if not issues:
        return "✅ No PEP8 violations detected."

    return "📏 PEP8 Issues:\n" + "\n".join([f"• {issue}" for issue in issues[:10]])  # Limit to 10


# ============================================================================================================
# DEFINE SPECIALIZED SUBAGENTS
# ============================================================================================================

# Style Review Subagent
style_reviewer_subagent = {
    "name": "style-reviewer",
    "description": "Reviews Python code for style compliance, PEP8 violations, naming conventions, and formatting. Uses official Python style guidelines from vector database.",
    "system_prompt": """You are a Python code style expert specializing in PEP8 and Google Python Style Guide compliance.

Your job:
1. Use search_style_guidelines() to check official conventions
2. Use check_pep8_compliance() to detect violations
3. Review naming (functions: snake_case, classes: PascalCase, constants: UPPER_CASE)
4. Check docstrings, comments, and code readability
5. Verify proper spacing, indentation, and line length

Output format:
## Style Review
**Rating:** X/10
**Issues Found:** [count]

### PEP8 Compliance
[List violations]

### Naming Conventions
[Check names against guidelines]

### Documentation
[Check docstrings and comments]

### Recommendations
[Specific improvements]

Keep response under 400 words. Be specific about line numbers and violations.""",
    "tools": [search_style_guidelines, check_pep8_compliance],
}

# Security Review Subagent
security_reviewer_subagent = {
    "name": "security-reviewer",
    "description": "Analyzes Python code for security vulnerabilities, unsafe functions, injection risks, and hardcoded credentials. Specializes in OWASP top 10 and Python-specific security issues.",
    "system_prompt": """You are a Python security expert specializing in vulnerability detection.

Your job:
1. Use check_security_vulnerabilities() to scan for common issues
2. Look for: eval/exec, SQL injection, command injection, XSS
3. Check for hardcoded secrets (API keys, passwords, tokens)
4. Identify unsafe deserialization (pickle)
5. Review input validation and sanitization

Output format:
## Security Review
**Security Rating:** X/10 (10 = most secure)
**Critical Issues:** [count]
**High Priority:** [count]

### Vulnerabilities Found
[List by severity: CRITICAL, HIGH, MEDIUM, LOW]

### Recommendations
[Specific fixes with code examples if needed]

Keep response under 400 words. Prioritize by severity.""",
    "tools": [check_security_vulnerabilities],
}

# Performance Review Subagent
performance_reviewer_subagent = {
    "name": "performance-reviewer",
    "description": "Analyzes Python code for performance issues, algorithmic efficiency, memory usage, and optimization opportunities. Identifies inefficient patterns and suggests improvements.",
    "system_prompt": """You are a Python performance optimization expert.

Your job:
1. Use analyze_code_structure() to understand complexity
2. Identify inefficient algorithms (nested loops, redundant operations)
3. Check for better data structures (list vs set, dict lookups)
4. Look for Python-specific optimizations (list comprehensions, generators)
5. Assess memory usage patterns

Output format:
## Performance Review
**Performance Rating:** X/10
**Complexity:** [Low/Medium/High]

### Efficiency Issues
[List inefficiencies with time/space complexity]

### Optimization Opportunities
[Specific suggestions with better alternatives]

### Code Examples
[Show optimized versions if applicable]

Keep response under 400 words. Focus on actionable improvements.""",
    "tools": [analyze_code_structure],
}

# Structure/Architecture Subagent
structure_reviewer_subagent = {
    "name": "structure-reviewer",
    "description": "Reviews code architecture, organization, modularity, and design patterns. Evaluates function/class structure and overall code organization.",
    "system_prompt": """You are a Python architecture and design expert.

Your job:
1. Use analyze_code_structure() to examine organization
2. Evaluate function size and single responsibility principle
3. Check class design and inheritance patterns
4. Assess modularity and coupling
5. Review code organization and imports

Output format:
## Architecture Review
**Structure Rating:** X/10
**Modularity:** [Good/Fair/Poor]

### Organization
[Comment on code structure]

### Design Patterns
[Identify patterns or anti-patterns]

### Improvements
[Suggest refactoring or restructuring]

Keep response under 400 words. Focus on maintainability.""",
    "tools": [analyze_code_structure],
}


# ============================================================================================================
# CREATE MAIN COORDINATOR AGENT
# ============================================================================================================

def create_code_review_coordinator():
    """
    Main coordinator agent that orchestrates specialized review subagents
    """
    llm = ChatBedrock(
        model_id=MAIN_MODEL,
        region_name=REGION,
    )

    # Configure all subagents
    subagents = [
        style_reviewer_subagent,
        security_reviewer_subagent,
        performance_reviewer_subagent,
        structure_reviewer_subagent
    ]

    agent = create_deep_agent(
        model=llm,
        name="code-review-coordinator",
        subagents=subagents,
        system_prompt="""You are the Code Review Coordinator. You orchestrate comprehensive Python code reviews using specialized subagents.

WORKFLOW:
1. Receive Python code from user
2. Analyze and identify code sections (functions, classes, imports)
3. Delegate reviews to specialized subagents:
   - style-reviewer: PEP8, formatting, naming conventions
   - security-reviewer: Vulnerabilities, unsafe code, secrets
   - performance-reviewer: Efficiency, optimization opportunities
   - structure-reviewer: Architecture, design patterns, organization

4. Wait for all subagent reviews to complete
5. Synthesize findings into a comprehensive report

DELEGATION STRATEGY:
- For each code section, call relevant subagents
- Run reviews in parallel when possible
- Collect all findings before final report

OUTPUT FORMAT:
```
=== COMPREHENSIVE CODE REVIEW ===

## Code Overview
[Brief summary: purpose, sections found, overall assessment]

## Detailed Reviews

### Style & Formatting
[Synthesize style-reviewer findings]

### Security Analysis
[Synthesize security-reviewer findings]

### Performance & Efficiency
[Synthesize performance-reviewer findings]

### Architecture & Design
[Synthesize structure-reviewer findings]

## Priority Action Items
1. [Most critical issues first]
2. [...]

## Summary
Overall Code Quality: X/10
[Brief final assessment]
```

IMPORTANT:
- Delegate to ALL 4 subagents for complete coverage
- Keep your final report under 800 words
- Prioritize critical issues (security > performance > style)
- Be specific about improvements"""
    )

    return agent


# ============================================================================================================
# MAIN REVIEW FUNCTION
# ============================================================================================================

def review_code(code: str, verbose: bool = True) -> str:
    """
    Orchestrate comprehensive code review using multi-agent system

    Args:
        code: Python code to review
        verbose: Print progress updates

    Returns:
        Comprehensive review report
    """
    if verbose:
        print("=" * 100)
        print("🚀 MULTI-AGENT CODE REVIEW SYSTEM")
        print("=" * 100)

    # Analyze code structure
    if verbose:
        print("\n📂 Analyzing code structure...")

    sections = split_code_into_sections(code)

    if verbose:
        print(f"✅ Found {len(sections)} sections:")
        for i, section in enumerate(sections, 1):
            print(f"   {i}. {section['type']}: {section['name']} (lines {section['line_start']}-{section['line_end']})")

    # Create coordinator
    if verbose:
        print("\n🤖 Initializing coordinator and subagents...")
        print("   • Style Reviewer")
        print("   • Security Reviewer")
        print("   • Performance Reviewer")
        print("   • Structure Reviewer")

    coordinator = create_code_review_coordinator()

    if verbose:
        print("✅ All agents ready")
        print("\n🔄 Starting review (coordinator will delegate to subagents)...")
        print("   This may take 30-60 seconds as subagents work in parallel...\n")

    # Prepare review request
    sections_summary = "\n".join([
        f"{i+1}. {s['type'].upper()}: '{s['name']}' (lines {s['line_start']}-{s['line_end']})"
        for i, s in enumerate(sections)
    ])

    review_request = f"""Please perform a comprehensive review of this Python code:

```python
{code}
```

CODE SECTIONS IDENTIFIED:
{sections_summary}

INSTRUCTIONS:
1. Delegate to ALL 4 specialized subagents for complete coverage
2. Ensure style-reviewer, security-reviewer, performance-reviewer, and structure-reviewer all analyze the code
3. Synthesize their findings into your final report
4. Prioritize critical security issues, then performance, then style"""

    # Invoke coordinator
    result = coordinator.invoke(
        {"messages": [{"role": "user", "content": review_request}]}
    )

    # Extract response
    if isinstance(result, dict) and "messages" in result:
        response = result["messages"][-1].content if result["messages"] else "No response generated"
    elif isinstance(result, str):
        response = result
    else:
        response = str(result)

    if verbose:
        print("=" * 100)
        print("✅ REVIEW COMPLETED")
        print("=" * 100)

    return response


# ============================================================================================================
# EXAMPLE USAGE
# ============================================================================================================

if __name__ == "__main__":
    # Test code with intentional issues
    test_code = """
import os
import sys

def calculateSum(a,b):
    return a+b

class dataProcessor:
    def __init__(self):
        self.api_key = "sk-1234567890abcdef"
        self.password = "admin123"

    def process(self, user_input):
        result = eval(user_input)
        return result

    def save_file(self,filename,content):
        os.system(f"echo {content} > {filename}")

def find_item(items, target):
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == target:
                return i
    return -1

def long_function_with_many_operations_that_could_be_split():
    x = 0; y = 0; z = 0
    for i in range(100):
        x += i
        y += i * 2
        z += i * 3
    return x, y, z
"""

    print("📝 Test Code:")
    print("-" * 100)
    print(test_code)
    print("-" * 100 + "\n")

    review = review_code(test_code, verbose=True)

    print("\n" + "=" * 100)
    print("📋 FINAL REVIEW REPORT")
    print("=" * 100)
    print(review)
    print("=" * 100)
