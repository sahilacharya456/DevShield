import asyncio
import json
import logging
from engine.security.pipeline import SecurityPipeline

# Setup basic logging to see the output
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

async def test_end_to_end():
    print("\n" + "="*50)
    print("DEVSHIELD ENTERPRISE: End-to-End Test")
    print("="*50)
    
    # Read the vulnerable file
    try:
        with open("vulnerable_dummy.py", "r") as f:
            code = f.read()
    except FileNotFoundError:
        print("Run this from the /enterprise/backend directory.")
        return

    print("1. Read vulnerable_dummy.py containing intentional flaws.")
    print("2. Starting Multi-Engine Orchestrator (Semgrep + AST + AsyncGroq/Gemini)...\n")
    
    # Trigger the pipeline
    report = await SecurityPipeline.analyze(code=code, language="python")
    
    # Use ML Pipeline to filter false positives (Optional but shows the flow)
    from engine.ml.feedback_loop import MLFeedbackPipeline
    filtered_report = MLFeedbackPipeline.filter_false_positives(report)

    # Print the final structured JSON results
    print("ANALYSIS COMPLETE. RESULTS:\n")
    print(json.dumps(filtered_report, indent=2))
    
    print("\n" + "="*50)
    print(f"Total Issues Detected: {filtered_report['total_issues']}")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
