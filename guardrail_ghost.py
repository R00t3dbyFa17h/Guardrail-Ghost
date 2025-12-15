import requests
import argparse
import random
import sys

# --- Dictionaries & Constants ---
ZERO_WIDTH = '\u200b'
HOMOGLYPHS = {
    'a': 'а', 'c': 'с', 'e': 'е', 'i': 'і', 
    'o': 'о', 'p': 'р', 'x': 'х', 'y': 'у'
}

def inject_zero_width(text):
    return ZERO_WIDTH.join(list(text))

def inject_homoglyphs(text):
    result = ''
    for char in text:
        # 50% chance to swap if a homoglyph exists
        if char in HOMOGLYPHS and random.random() > 0.5:
            result += HOMOGLYPHS[char]
        else:
            result += char
    return result

def main():
    parser = argparse.ArgumentParser(description='Guardrail-Ghost v2.0: Polyglot Evasion Tool')
    parser.add_argument('--target', required=True, help='Target API URL')
    parser.add_argument('--message', required=True, help='Malicious payload')
    parser.add_argument('--mode', choices=['zero', 'homoglyph', 'mixed'], default='zero', help='Evasion mode')
    args = parser.parse_args()

    print(f'--- Guardrail-Ghost v2.0 ({args.mode} mode) ---')

    payload = args.message
    if args.mode == 'zero':
        payload = inject_zero_width(args.message)
    elif args.mode == 'homoglyph':
        payload = inject_homoglyphs(args.message)
    elif args.mode == 'mixed':
        payload = inject_zero_width(inject_homoglyphs(args.message))

    print(f'[*] Original: {args.message}')
    print(f'[*] Payload:  {payload} (Length: {len(payload)})')

    try:
        response = requests.post(args.target, json={'message': payload})
        print(f'[*] Response: {response.json()}')
    except Exception as e:
        print(f'[!] Error: {e}')

if __name__ == '__main__':
    main()
