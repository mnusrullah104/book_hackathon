"""
CLI Testing Interface for RAG Agent

Provides command-line interface for testing agent behavior with:
- Single query mode
- Interactive REPL mode
- Test suite with predefined queries
"""

import sys
import asyncio
import argparse
from typing import List, Dict
from agent import create_agent, AgentResponse


# =============================================================================
# TEST QUERIES (Phase 5: T037-T039)
# =============================================================================

TEST_QUERIES = [
    {
        "query": "Explain ROS 2 fundamentals",
        "module": "Module 1 - ROS 2",
        "should_cite_sources": True,
        "should_retrieve": True,
        "description": "Single-topic query about ROS 2 basics"
    },
    {
        "query": "How does Isaac Sim work?",
        "module": "Module 3 - Isaac Sim",
        "should_cite_sources": True,
        "should_retrieve": True,
        "description": "Single-topic query about Isaac Sim"
    },
    {
        "query": "What is VLA?",
        "module": "Module 4 - VLA",
        "should_cite_sources": True,
        "should_retrieve": True,
        "description": "Single-topic query about VLA models"
    },
    {
        "query": "How do I use ROS 2 with Isaac Sim?",
        "module": "Cross-module",
        "should_cite_sources": True,
        "should_retrieve": True,
        "description": "Cross-module integration query"
    },
    {
        "query": "Explain robotics simulation basics",
        "module": "Module 2 - Simulation",
        "should_cite_sources": True,
        "should_retrieve": True,
        "description": "Single-topic query about simulation"
    },
    {
        "query": "Tell me about humanoid robots",
        "module": "Broad/Vague",
        "should_cite_sources": True,
        "should_retrieve": True,
        "description": "Broad query requiring clarification or multiple sources"
    },
    {
        "query": "What's the weather today?",
        "module": "Out of scope",
        "should_cite_sources": False,
        "should_retrieve": False,
        "description": "Out-of-scope query (not in knowledge base)"
    },
    {
        "query": "How do I train a VLA model?",
        "module": "Module 4 - VLA",
        "should_cite_sources": True,
        "should_retrieve": True,
        "description": "Specific technical question"
    },
]


# =============================================================================
# OUTPUT FORMATTING (Phase 5: T033)
# =============================================================================

def format_response(response: AgentResponse, query: str, test_case: Dict = None):
    """
    Format agent response for readable CLI output.

    Args:
        response: AgentResponse object
        query: Original user query
        test_case: Optional test case metadata
    """
    print("\n" + "="*80)
    print(f"[QUERY] {query}")

    if test_case:
        print(f"[TEST] {test_case['description']}")
        print(f"[MODULE] {test_case['module']}")

    print(f"\n[RETRIEVING] {'Yes' if response.retrieval_performed else 'No'}")

    if response.retrieved_sources:
        print(f"[SOURCES] {len(response.retrieved_sources)} sources retrieved")
        for i, url in enumerate(response.retrieved_sources[:3], 1):
            print(f"  {i}. {url}")
        if len(response.retrieved_sources) > 3:
            print(f"  ... and {len(response.retrieved_sources) - 3} more")

    print(f"\n[RESPONSE]")
    print(response.content)

    print(f"\n[METADATA]")
    print(f"- Turn: {response.turn_number}")
    print(f"- Tokens: ~{response.tokens_used}")
    print(f"- Time: {response.execution_time_seconds:.2f}s")
    print(f"- Retrieval: {'Yes' if response.retrieval_performed else 'No'}")

    if response.error:
        print(f"- Error: {response.error}")

    print("="*80)


def validate_response(response: AgentResponse, test_case: Dict) -> Dict[str, bool]:
    """
    Validate response against test case expectations.

    Args:
        response: AgentResponse object
        test_case: Test case with expected behavior

    Returns:
        Dictionary of validation results
    """
    results = {}

    # Check retrieval performed
    results["retrieval_check"] = (
        response.retrieval_performed == test_case["should_retrieve"]
    )

    # Check sources cited
    if test_case["should_cite_sources"]:
        results["citation_check"] = len(response.retrieved_sources) > 0
    else:
        results["citation_check"] = True  # Not applicable

    # Check no error
    results["no_error"] = response.error is None

    # Check response not empty
    results["has_content"] = bool(response.content and response.content.strip())

    return results


# =============================================================================
# SINGLE QUERY MODE (Phase 5: T032)
# =============================================================================

async def run_single_query(query: str, args):
    """
    Execute a single query and display results.

    Args:
        query: User query string
        args: Parsed command-line arguments
    """
    print(f"Initializing agent with model: {args.model}")

    # Create agent
    agent = create_agent(
        model=args.model,
        verbose=args.verbose
    )

    # Execute query
    response = await agent.chat(query, top_k=args.top_k)

    # Display results
    format_response(response, query)


# =============================================================================
# INTERACTIVE MODE (Phase 5: T034)
# =============================================================================

async def run_interactive_mode(args):
    """
    Start interactive REPL mode for multi-turn conversations.

    Args:
        args: Parsed command-line arguments
    """
    print("="*80)
    print("RAG Agent - Interactive Mode")
    print("="*80)
    print(f"Model: {args.model}")
    print(f"Top-K: {args.top_k}")
    print("\nCommands:")
    print("  /exit, /quit - Exit interactive mode")
    print("  /new, /reset - Start a new session")
    print("  /session - Show current session info")
    print("  /help - Show this help message")
    print("\nType your query and press Enter.")
    print("="*80 + "\n")

    # Create agent
    agent = create_agent(
        model=args.model,
        verbose=args.verbose
    )

    turn = 0

    while True:
        try:
            # Get user input
            user_input = input(f"\n[Turn {turn + 1}] You: ").strip()

            # Handle commands
            if user_input.lower() in ["/exit", "/quit"]:
                print("\nGoodbye!")
                break

            elif user_input.lower() in ["/new", "/reset"]:
                session_id = agent.start_new_session()
                turn = 0
                print(f"\nNew session started: {session_id}")
                continue

            elif user_input.lower() == "/session":
                session = agent.get_session()
                print(f"\nSession ID: {session.session_id}")
                print(f"Turn count: {session.turn_count}")
                print(f"Retrieval count: {session.retrieval_count}")
                print(f"Total tokens: {session.total_tokens_used}")
                print(f"Created: {session.created_at}")
                continue

            elif user_input.lower() == "/help":
                print("\nCommands:")
                print("  /exit, /quit - Exit interactive mode")
                print("  /new, /reset - Start a new session")
                print("  /session - Show current session info")
                print("  /help - Show this help message")
                continue

            elif not user_input:
                continue

            # Execute query
            response = await agent.chat(user_input, top_k=args.top_k)

            # Display response
            print(f"\n[Agent]")
            print(response.content)

            if response.retrieved_sources:
                print(f"\n[Sources: {len(response.retrieved_sources)} retrieved]")

            if args.verbose:
                print(f"[Metadata: {response.tokens_used} tokens, {response.execution_time_seconds:.2f}s]")

            turn += 1

        except KeyboardInterrupt:
            print("\n\nInterrupted. Use /exit to quit.")
            continue

        except EOFError:
            print("\n\nGoodbye!")
            break

        except Exception as e:
            print(f"\nError: {e}")
            continue


# =============================================================================
# TEST SUITE MODE (Phase 5: T037-T041)
# =============================================================================

async def run_test_suite(args):
    """
    Run predefined test suite and validate results.

    Args:
        args: Parsed command-line arguments
    """
    print("="*80)
    print("RAG Agent - Test Suite")
    print("="*80)
    print(f"Model: {args.model}")
    print(f"Top-K: {args.top_k}")
    print(f"Total tests: {len(TEST_QUERIES)}")
    print("="*80 + "\n")

    # Create agent
    agent = create_agent(
        model=args.model,
        verbose=args.verbose
    )

    results = []
    total_time = 0.0

    # Run all test queries
    for i, test_case in enumerate(TEST_QUERIES, 1):
        print(f"\n[Test {i}/{len(TEST_QUERIES)}] {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")

        try:
            # Execute query
            response = await agent.chat(test_case["query"], top_k=args.top_k)

            # Validate response
            validation = validate_response(response, test_case)

            results.append({
                "test_case": test_case,
                "response": response,
                "validation": validation,
                "passed": all(validation.values())
            })

            total_time += response.execution_time_seconds

            # Display brief result
            status = "✓ PASS" if all(validation.values()) else "✗ FAIL"
            print(f"Status: {status}")
            print(f"Retrieval: {response.retrieval_performed}, Sources: {len(response.retrieved_sources)}, Time: {response.execution_time_seconds:.2f}s")

            if not all(validation.values()):
                print(f"Failed checks: {[k for k, v in validation.items() if not v]}")

        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({
                "test_case": test_case,
                "response": None,
                "validation": {},
                "passed": False,
                "error": str(e)
            })

    # Summary statistics
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)

    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count
    success_rate = (passed_count / len(results)) * 100 if results else 0

    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per query: {total_time / len(results):.2f}s" if results else "N/A")

    # Retrieval statistics
    retrieval_count = sum(1 for r in results if r["response"] and r["response"].retrieval_performed)
    retrieval_percentage = (retrieval_count / len(results)) * 100 if results else 0
    print(f"Retrieval performed: {retrieval_count}/{len(results)} ({retrieval_percentage:.1f}%)")

    # Success criteria validation (from spec.md)
    print("\n" + "="*80)
    print("SUCCESS CRITERIA VALIDATION")
    print("="*80)

    print(f"SC-001 (95% success): {'✓ PASS' if success_rate >= 95 else '✗ FAIL'} ({success_rate:.1f}%)")

    avg_time = total_time / len(results) if results else 0
    print(f"SC-005 (<5s avg response): {'✓ PASS' if avg_time < 5.0 else '✗ FAIL'} ({avg_time:.2f}s)")

    # Source citation check
    citations_count = sum(1 for r in results if r["response"] and len(r["response"].retrieved_sources) > 0)
    print(f"SC-002 (source citations): {citations_count}/{len(results)} responses have citations")

    print("="*80)


# =============================================================================
# MAIN CLI ENTRY POINT (Phase 5: T031, T036)
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Agent CLI Testing Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single query
  python test_agent.py "What is ROS 2?"

  # Interactive mode
  python test_agent.py --interactive

  # Test suite
  python test_agent.py --test-suite

  # Custom model
  python test_agent.py "Explain Isaac Sim" --model gpt-3.5-turbo

  # Verbose logging
  python test_agent.py "VLA fundamentals" --verbose

  # Use OpenRouter with free model
  python test_agent.py "What is ROS 2?" --model mistralai/devstral-2-2512:free
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query (for single query mode)"
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive REPL mode"
    )

    parser.add_argument(
        "--test-suite",
        "-t",
        action="store_true",
        help="Run predefined test suite"
    )

    parser.add_argument(
        "--model",
        "-m",
        default="meta-llama/llama-3.2-3b-instruct:free",
        help="Model to use (default: meta-llama/llama-3.2-3b-instruct:free for OpenRouter)"
    )

    parser.add_argument(
        "--top-k",
        "-k",
        type=int,
        default=5,
        help="Number of chunks to retrieve (default: 5)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed logging"
    )

    parser.add_argument(
        "--new-session",
        action="store_true",
        help="Start fresh session (discard history)"
    )

    args = parser.parse_args()

    # Determine mode
    if args.interactive:
        asyncio.run(run_interactive_mode(args))

    elif args.test_suite:
        asyncio.run(run_test_suite(args))

    elif args.query:
        asyncio.run(run_single_query(args.query, args))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
