"""CLI entry point for PRISM shadow-mode operation."""
import sys
import json
from pathlib import Path

# Ensure src/ is on path when run directly
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from prism.core.pipeline import PrismPipeline


def print_result(result) -> None:
    print("─" * 60)
    print(f"  Turn {result.turn_number}")
    print(f"  Temperature: {result.temperature:.2f}")
    print(f"  Factual lock: {result.intent.is_factual}")
    print("─" * 60)
    print(f"  Bias:        {result.classification.bias}")
    print(f"  Confidence:  {result.classification.confidence:.3f}")
    print(f"  Route:       {result.route.route}")
    print(f"  Reason:      {result.route.reason}")
    print(f"  Assertiveness: {result.bayesian_state.assertiveness:.3f}")
    print("─" * 60)
    if result.route.system_prompt_addition:
        print(f"  Prompt add:  {result.route.system_prompt_addition}")
    print(f"  Topic drift: {result.meta['topic_drift']:.3f}")
    print(f"  Frustrated:  {result.meta['is_frustrated']}")
    print(f"  Drift alert: {result.meta['is_topic_drift']}")
    print("─" * 60)


def run_interactive() -> None:
    print("PRISM Shadow Mode — type 'quit' or 'reset' to exit / restart")
    pipeline = PrismPipeline(project_root=_PROJECT_ROOT)

    while True:
        try:
            user_input = input("\n\u003e ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break
        if user_input.lower() == "reset":
            pipeline.reset()
            print("Pipeline state reset.")
            continue

        result = pipeline.process(user_input)
        print_result(result)


def run_single(message: str, json_out: bool = False) -> None:
    pipeline = PrismPipeline(project_root=_PROJECT_ROOT)
    result = pipeline.process(message)
    if json_out:
        out = {
            "turn": result.turn_number,
            "temperature": result.temperature,
            "bias": result.classification.bias,
            "confidence": result.classification.confidence,
            "route": result.route.route,
            "reason": result.route.reason,
            "assertiveness": result.bayesian_state.assertiveness,
            "factual": result.intent.is_factual,
            "topic_drift": result.meta["topic_drift"],
            "frustrated": result.meta["is_frustrated"],
        }
        print(json.dumps(out, indent=2))
    else:
        print_result(result)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        run_interactive()
        return

    if args[0] in ("-h", "--help"):
        print("Usage: python -m prism.cli [message] [--json]")
        print("   or: python -m prism.cli          (interactive)")
        return

    json_out = "--json" in args
    message = " ".join(a for a in args if a != "--json")
    run_single(message, json_out=json_out)


if __name__ == "__main__":
    main()
