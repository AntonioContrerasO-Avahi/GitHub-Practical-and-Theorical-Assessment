# ============================================================================================================
# GRADIO UI FOR MULTI-AGENT CODE REVIEW SYSTEM
# Interactive interface for testing the DeepAgents code reviewer
# ============================================================================================================

import gradio as gr
from coordinator import review_code, split_code_into_sections
import time

# ============================================================================================================
# EXAMPLE CODES FOR TESTING
# ============================================================================================================

EXAMPLE_GOOD_CODE = """
def calculate_average(numbers: list[float]) -> float:
    \"\"\"
    Calculate the average of a list of numbers.

    Args:
        numbers: List of numeric values

    Returns:
        Average value as float
    \"\"\"
    if not numbers:
        return 0.0

    return sum(numbers) / len(numbers)


class DataProcessor:
    \"\"\"Process and analyze data collections.\"\"\"

    def __init__(self):
        self.data = []

    def add_item(self, item: dict) -> None:
        \"\"\"Add item to collection.\"\"\"
        self.data.append(item)

    def get_summary(self) -> dict:
        \"\"\"Get summary statistics.\"\"\"
        return {
            'count': len(self.data),
            'items': self.data
        }
"""

EXAMPLE_BAD_CODE = """
import os

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
"""

EXAMPLE_MIXED_CODE = """
import hashlib
from typing import List

def hash_password(password: str) -> str:
    \"\"\"Hash a password using SHA-256.\"\"\"
    return hashlib.sha256(password.encode()).hexdigest()

def processUserData(userData):
    # Missing docstring and camelCase
    result = []
    for item in userData:
        result.append(item.upper())
    return result

class UserManager:
    def __init__(self):
        self.users = {}
        self.admin_password = "secret123"  # Security issue!

    def add_user(self, name: str, email: str):
        # Could use better data structure
        for existing_name in self.users:
            if existing_name == name:
                return False
        self.users[name] = email
        return True
"""

# ============================================================================================================
# GRADIO INTERFACE FUNCTIONS
# ============================================================================================================

def analyze_code_sections(code: str) -> str:
    """Quick analysis of code sections (for preview)"""
    if not code.strip():
        return "❌ No code provided"

    try:
        sections = split_code_into_sections(code)

        summary = f"📊 **Code Structure Analysis**\n\n"
        summary += f"**Total Sections:** {len(sections)}\n\n"

        for i, section in enumerate(sections, 1):
            summary += f"{i}. **{section['type'].upper()}**: `{section['name']}` "
            summary += f"(lines {section['line_start']}-{section['line_end']})\n"

        return summary
    except Exception as e:
        return f"❌ Error analyzing code: {str(e)}"


def run_code_review(code: str, progress=gr.Progress()) -> str:
    """Run the multi-agent code review with progress tracking"""

    if not code.strip():
        return "❌ **Error:** Please provide some Python code to review."

    try:
        # Show progress
        progress(0, desc="🔍 Analyzing code structure...")
        time.sleep(0.5)

        progress(0.2, desc="🤖 Initializing agents...")
        time.sleep(0.5)

        progress(0.3, desc="🚀 Starting multi-agent review...")

        # Run the actual review (without verbose console output)
        result = review_code(code, verbose=False)

        progress(1.0, desc="✅ Review complete!")

        return result

    except Exception as e:
        return f"❌ **Error during review:**\n\n```\n{str(e)}\n```\n\nPlease check your code and try again."


# ============================================================================================================
# BUILD GRADIO INTERFACE
# ============================================================================================================

def create_ui():
    """Create the Gradio interface"""

    with gr.Blocks(
        title="🤖 Multi-Agent Code Review System"
    ) as app:

        gr.Markdown("""
        # 🤖 Multi-Agent Code Review System

        **Powered by DeepAgents & AWS Bedrock**

        This system uses 4 specialized AI agents to comprehensively review your Python code:
        - 🎨 **Style Reviewer**: PEP8, formatting, naming conventions
        - 🔒 **Security Reviewer**: Vulnerabilities, unsafe code, secrets
        - ⚡ **Performance Reviewer**: Efficiency and optimization
        - 🏗️ **Structure Reviewer**: Architecture and design patterns
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Input Code")

                code_input = gr.Code(
                    label="Python Code to Review",
                    language="python",
                    lines=20
                )

                with gr.Row():
                    review_btn = gr.Button(
                        "🚀 Start Review",
                        variant="primary",
                        size="lg"
                    )
                    clear_btn = gr.ClearButton(
                        [code_input],
                        value="🗑️ Clear",
                        size="lg"
                    )

                gr.Markdown("### 📊 Quick Analysis")
                structure_output = gr.Markdown(label="Code Structure")

                code_input.change(
                    fn=analyze_code_sections,
                    inputs=[code_input],
                    outputs=[structure_output]
                )

            with gr.Column(scale=1):
                gr.Markdown("### 📋 Review Report")

                review_output = gr.Markdown(
                    label="Comprehensive Review",
                    value="*Review results will appear here...*"
                )

        # Examples section
        gr.Markdown("---")
        gr.Markdown("### 💡 Example Codes")

        with gr.Row():
            example1_btn = gr.Button("✅ Good Code Example")
            example2_btn = gr.Button("❌ Bad Code Example")
            example3_btn = gr.Button("⚠️ Mixed Quality Example")

        # Wire up the review button
        review_btn.click(
            fn=run_code_review,
            inputs=[code_input],
            outputs=[review_output]
        )

        # Wire up example buttons
        example1_btn.click(
            lambda: EXAMPLE_GOOD_CODE,
            outputs=[code_input]
        )

        example2_btn.click(
            lambda: EXAMPLE_BAD_CODE,
            outputs=[code_input]
        )

        example3_btn.click(
            lambda: EXAMPLE_MIXED_CODE,
            outputs=[code_input]
        )

        # Footer
        gr.Markdown("""
        ---
        ### 🔧 How It Works

        1. **Code Analysis**: The system parses your code into logical sections (imports, functions, classes)
        2. **Agent Delegation**: The coordinator delegates each section to specialized review agents
        3. **Parallel Review**: Agents work simultaneously on different aspects (style, security, performance, structure)
        4. **Result Aggregation**: The coordinator synthesizes all findings into a comprehensive report

        ### ⚙️ Technology Stack
        - **Framework**: LangChain DeepAgents
        - **Models**: Claude Sonnet 4.5 (coordinator), Claude Haiku (subagents)
        - **Vector DB**: ChromaDB (for style guidelines)
        - **Platform**: AWS Bedrock

        ### ⏱️ Expected Review Time
        - Small files (<50 lines): ~15-30 seconds
        - Medium files (50-200 lines): ~30-60 seconds
        - Large files (>200 lines): ~60-90 seconds

        *Note: First review may take longer as agents initialize.*
        """)

    return app


# ============================================================================================================
# LAUNCH APPLICATION
# ============================================================================================================

if __name__ == "__main__":
    print("=" * 100)
    print("🚀 LAUNCHING MULTI-AGENT CODE REVIEW UI")
    print("=" * 100)
    print("\n📦 Loading agents and vector store...")

    # Create and launch the app
    app = create_ui()

    print("✅ Ready!")
    print("\n" + "=" * 100)
    print("🌐 Opening Gradio interface...")
    print("=" * 100)

    # app.launch(
    #     server_name="0.0.0.0",
    #     server_port=7862,
    #     share=False,
    #     show_error=True,
    #     inbrowser=True
    # )
    app.launch(
        share=False,      # False for local execution
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7854,
        show_error=True,
        inbrowser=True
    )
