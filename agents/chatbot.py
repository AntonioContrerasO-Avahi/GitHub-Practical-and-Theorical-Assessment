"""
Simple CV Chatbot using LangChain and AWS Bedrock.

This chatbot reads CV text from the examples folder and allows users
to ask questions about the CV or request analysis.
"""

import os
from pathlib import Path
from agents.agent import CVExtractionAgent


def load_cv_from_file(filename: str) -> str:
    """
    Load CV text from the examples folder.

    Args:
        filename: Name of the CV file in the examples folder

    Returns:
        CV text content

    Raises:
        FileNotFoundError: If the CV file doesn't exist
    """
    examples_dir = Path(__file__).parent.parent / "examples"
    cv_path = examples_dir / filename

    if not cv_path.exists():
        raise FileNotFoundError(f"CV file not found: {cv_path}")

    with open(cv_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """
    Main chatbot interface.
    """
    print("=" * 60)
    print("CV Analysis Chatbot - Powered by AWS Bedrock")
    print("=" * 60)

    # Load CV
    try:
        cv_filename = input("\nEnter CV filename (default: sample_cv.txt): ").strip()
        if not cv_filename:
            cv_filename = "sample_cv.txt"

        cv_text = load_cv_from_file(cv_filename)
        print(f"\n✅ Loaded CV: {cv_filename}")
        print(f"   Length: {len(cv_text)} characters\n")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return
    except Exception as e:
        print(f"\n❌ Error loading CV: {e}")
        return

    # Initialize agent
    try:
        print("🤖 Initializing CV Analysis Agent...")
        agent = CVExtractionAgent(cv_text)
        print("✅ Agent ready!\n")

    except Exception as e:
        print(f"\n❌ Error initializing agent: {e}")
        print("   Make sure AWS credentials are configured properly.")
        return

    # Generate initial summary
    print("📋 Generating CV summary...\n")
    try:
        summary = agent.generate_summary()
        print("Summary:")
        print("-" * 60)
        print(summary)
        print("-" * 60)
        print()

    except Exception as e:
        print(f"⚠️  Could not generate summary: {e}\n")

    # Chat loop
    print("💬 Chat Mode - Ask questions about the CV")
    print("   Commands: 'summary' (new summary), 'clear' (clear history), 'quit' (exit)\n")

    session_id = "main_session"

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            elif user_input.lower() == 'clear':
                agent.clear_history(session_id)
                print("🗑️  Chat history cleared.\n")
                continue

            elif user_input.lower() == 'summary':
                print("\n📋 Generating new summary...\n")
                summary = agent.generate_summary()
                print("Summary:")
                print("-" * 60)
                print(summary)
                print("-" * 60)
                print()
                continue

            # Get agent response
            print("\n🤖 Agent: ", end="", flush=True)
            response = agent.chat(user_input, session_id)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()