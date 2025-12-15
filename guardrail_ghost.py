import requests
import argparse
import sys

# The "Ghost" Character (Zero Width Space)
GHOST_CHAR = "\u200b"

def ghostify(text):
    """Injects invisible characters between every letter."""
    return GHOST_CHAR.join(list(text))

def main():
    parser = argparse.ArgumentParser(description="Guardrail-Ghost: Bypass Keyword Filters")
    parser.add_argument("--target", required=True, help="URL of the target AI")
    parser.add_argument("--message", required=True, help="The malicious message to send")
    args = parser.parse_args()

    print("--- R00t3dbyFa17h: Guardrail-Ghost v1.0 ---")
    
    # 1. Try Normal (Baseline)
    print(f"\n[*] Attempting Normal Payload: '{args.message}'")
    try:
        response = requests.post(args.target, json={"message": args.message})
        print(f"    Result: {response.json()['response']}")
    except Exception as e:
        print(f"    Error: {e}")

    # 2. Ghost Mode
    ghost_payload = ghostify(args.message)
    print(f"\n[👻] ACTIVATING GHOST MODE...")
    print(f"[*] Original Length: {len(args.message)}")
    print(f"[*] Ghost Length:    {len(ghost_payload)} (Hidden bytes added)")
    
    try:
        response = requests.post(args.target, json={"message": ghost_payload})
        print(f"    Result: {response.json()['response']}")
    except Exception as e:
        print(f"    Error: {e}")

if __name__ == "__main__":
    main()
