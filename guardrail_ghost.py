import argparse
import requests
import sys
import binascii

# --- COLORS FOR TERMINAL ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- GHOST CHARACTERS ---
ZERO_WIDTH_SPACE = '\u200b'

def print_banner():
    print(Colors.HEADER + r"""
   _____                     _           _ _   
  / ____|                   | |         (_) |  
 | |  __ _   _  __ _ _ __ __| |_ __ __ _ _| |  
 | | |_ | | | |/ _` | '__/ _` | '__/ _` | | |  
 | |__| | |_| | (_| | | | (_| | | | (_| | | |  
  \_____|\__,_|\__,_|_|  \__,_|_|  \__,_|_|_|  
           G H O S T   v 3 . 0
    """ + Colors.ENDC)

def print_hex_comparison(original, payload):
    """Shows the hidden bytes visually"""
    orig_hex = binascii.hexlify(original.encode('utf-8')).decode('utf-8')
    pay_hex = binascii.hexlify(payload.encode('utf-8')).decode('utf-8')
    
    print(f"\n{Colors.BLUE}🔍 [HEX INSPECTION]{Colors.ENDC}")
    print(f"   Original ({len(original)} chars): {Colors.RED}{orig_hex}{Colors.ENDC}")
    print(f"   Ghost    ({len(payload)} chars): {Colors.GREEN}{pay_hex}{Colors.ENDC}")
    print("   " + "-" * 60)

def obfuscate_zero_width(text):
    return ZERO_WIDTH_SPACE.join(list(text))

# =========================================================================
# v3.0+ ADDITIONS BELOW  --  everything else is preserved as-is.
# Strictly ADDITIVE: the default run (--mode zero) is byte-for-byte the
# original behavior. New modes/flags are opt-in. These techniques audit the
# robustness of keyword-based AI guardrails/WAFs; a --defense-check shows which
# are defeated by proper Unicode (NFKC) normalization + zero-width stripping.
# Author: R00t3dbyFa17h / K70n0s510  (HTB, Bugcrowd, Microsoft, Intigriti, Google)
# =========================================================================

import unicodedata

VERSION = "3.0+"
QUIET = False

# Latin -> confusable look-alikes (Cyrillic/Greek). Visually similar, binary-distinct.
_HOMOGLYPHS = {
    'a': 'а', 'c': 'с', 'e': 'е', 'o': 'о', 'p': 'р', 'x': 'х', 'y': 'у',
    'A': 'А', 'B': 'В', 'C': 'С', 'E': 'Е', 'H': 'Н', 'K': 'К', 'M': 'М',
    'O': 'О', 'P': 'Р', 'T': 'Т', 'X': 'Х', 'Y': 'У', 'i': 'і', 's': 'ѕ',
    'j': 'ј', 'd': 'ԁ', 'n': 'ո',
}
_LEET = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'l': '1', 'b': '8', 'g': '9'}

def obf_homoglyph(text):
    return ''.join(_HOMOGLYPHS.get(ch, ch) for ch in text)

def obf_mixed(text):
    # Homoglyph substitution + zero-width injection for maximum obfuscation.
    return ZERO_WIDTH_SPACE.join(list(obf_homoglyph(text)))

def obf_fullwidth(text):
    # ASCII -> Unicode fullwidth forms (NFKC-decomposable back to ASCII).
    out = []
    for ch in text:
        o = ord(ch)
        if 0x21 <= o <= 0x7e:
            out.append(chr(o - 0x21 + 0xff01))
        elif ch == ' ':
            out.append('　')
        else:
            out.append(ch)
    return ''.join(out)

def obf_combining(text):
    # Insert a combining acute accent after each char (U+0301).
    return ''.join(ch + '́' for ch in text)

def obf_leet(text):
    return ''.join(_LEET.get(ch.lower(), ch) for ch in text)

def obf_case(text):
    return ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))

def obf_rtl(text):
    # Wrap with RTL override markers (U+202E ... U+202C).
    return '‮' + text + '‬'

# Mode registry: name -> (function, human label). 'zero' is the original.
MODES = {
    "zero":      (obfuscate_zero_width, "Zero-Width Space (U+200B)"),
    "homoglyph": (obf_homoglyph,        "Homoglyph (Cyrillic/Greek look-alikes)"),
    "mixed":     (obf_mixed,            "Mixed (Homoglyph + Zero-Width)"),
    "fullwidth": (obf_fullwidth,        "Fullwidth Unicode Forms"),
    "combining": (obf_combining,        "Combining Diacritical Marks (U+0301)"),
    "leet":      (obf_leet,             "Leetspeak Substitution"),
    "case":      (obf_case,             "Alternating Case"),
    "rtl":       (obf_rtl,              "Right-to-Left Override (U+202E)"),
}

def _strip_invisibles(text):
    # Remove zero-width / direction-control / combining marks.
    cleaned = []
    for ch in text:
        if ch in ('​', '‌', '‍', '﻿', '⁠', '‮', '‬', '‭'):
            continue
        if unicodedata.combining(ch):
            continue
        cleaned.append(ch)
    return ''.join(cleaned)

def nfkc_recovers(original, payload):
    """Defensive indicator: would NFKC normalization + invisible-stripping
    collapse the evasion back to the original keyword? If True, a properly
    hardened filter would still catch it."""
    norm = unicodedata.normalize('NFKC', _strip_invisibles(payload))
    return original.lower() in norm.lower()

def send_request(target, message, label, timeout=None, proxies=None, headers=None, verify=True):
    # Optional transport params default to the original behavior (no timeout,
    # no proxy, default headers, verify on). Returns a result dict (additive;
    # existing callers simply ignore the return value).
    result = {"label": label, "status": "error", "code": None, "reply": None}
    try:
        response = requests.post(target, json={"message": message},
                                 timeout=timeout, proxies=proxies, headers=headers, verify=verify)
        result["code"] = response.status_code
        try:
            result["reply"] = response.json().get('response')
        except Exception:
            result["reply"] = None

        if response.status_code == 200:
            result["status"] = "bypass"
            print(f"[*] {label}: {Colors.GREEN}✅ BYPASS SUCCESS ({response.status_code}){Colors.ENDC}")
            print(f"    Server Reply: {response.json().get('response')}")
        elif response.status_code == 403:
            result["status"] = "blocked"
            print(f"[*] {label}: {Colors.RED}⛔ BLOCKED ({response.status_code}){Colors.ENDC}")
            print(f"    Server Reply: {response.json().get('response')}")
        else:
            result["status"] = "unknown"
            print(f"[*] {label}: {Colors.YELLOW}⚠️ UNKNOWN ({response.status_code}){Colors.ENDC}")

    except Exception as e:
        print(f"[!] Error: {e}")
    return result

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Guardrail-Ghost - AI Guardrail / WAF robustness auditor")
    parser.add_argument('--target', required=True, help='Target URL (e.g., http://localhost:5000/chat)')
    parser.add_argument('--message', required=True, help='The malicious word to hide')

    # --- v3.0+ additive flags (all opt-in, safe defaults) ---
    parser.add_argument('--version', action='version',
                        version=f"Guardrail-Ghost v{VERSION} - R00t3dbyFa17h / K70n0s510")
    parser.add_argument('--mode', choices=list(MODES.keys()) + ['all'], default='zero',
                        help="Evasion technique (default: zero = original behavior). 'all' tries every mode.")
    parser.add_argument('--list-modes', action='store_true', help='List available evasion modes and exit')
    parser.add_argument('--defense-check', action='store_true',
                        help='Report whether NFKC normalization + invisible-stripping would defeat each payload (defensive)')
    parser.add_argument('--json', dest='json_out', metavar='FILE', help='Write results to a JSON file')
    parser.add_argument('--proxy', help='Proxy URL (e.g., http://127.0.0.1:8080)')
    parser.add_argument('--timeout', type=float, default=None, help='Request timeout in seconds')
    parser.add_argument('-H', '--header', action='append', metavar="'Name: Value'",
                        help='Add a custom request header (repeatable)')
    parser.add_argument('--insecure', action='store_true', help='Disable TLS verification')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress extra output')
    args = parser.parse_args()

    if args.list_modes:
        print(f"{Colors.BOLD}Available evasion modes:{Colors.ENDC}")
        for name, (_, label) in MODES.items():
            print(f"  {Colors.GREEN}{name:<10}{Colors.ENDC} {label}")
        print(f"  {Colors.GREEN}{'all':<10}{Colors.ENDC} Run every mode and summarize")
        return

    global QUIET
    QUIET = args.quiet

    # Build optional transport (defaults preserve original behavior).
    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    headers = None
    if args.header:
        headers = {}
        for raw in args.header:
            if ':' in raw:
                n, _, v = raw.partition(':')
                headers[n.strip()] = v.strip()
    verify = not args.insecure
    tx = dict(timeout=args.timeout, proxies=proxies, headers=headers, verify=verify)

    print(f"{Colors.BOLD}--- PHASE 1: CONTROL TEST ---{Colors.ENDC}")
    print("Sending clean payload to verify WAF is active...")
    control = send_request(args.target, args.message, "CLEAN PAYLOAD", **tx)

    results = [control]

    # Determine which modes to run.
    run_modes = list(MODES.keys()) if args.mode == 'all' else [args.mode]

    if args.mode == 'all':
        print(f"\n{Colors.BOLD}--- PHASE 2: GHOST MODE (ALL TECHNIQUES) ---{Colors.ENDC}")
    else:
        print(f"\n{Colors.BOLD}--- PHASE 2: GHOST MODE ---{Colors.ENDC}")

    for mode in run_modes:
        obf_fn, label = MODES[mode]
        payload = obf_fn(args.message)
        print(f"\n{Colors.BLUE}[{mode}]{Colors.ENDC} {label} — obfuscating '{args.message}'...")
        print_hex_comparison(args.message, payload)
        res = send_request(args.target, payload, f"GHOST PAYLOAD [{mode}]", **tx)
        res["mode"] = mode
        res["payload"] = payload
        if args.defense_check:
            caught = nfkc_recovers(args.message, payload)
            if caught:
                print(f"    {Colors.YELLOW}🛡️ DEFENSE: NFKC normalization WOULD neutralize this (filter should normalize input).{Colors.ENDC}")
            else:
                print(f"    {Colors.RED}🛡️ DEFENSE: survives NFKC normalization — needs confusable/semantic detection.{Colors.ENDC}")
            res["nfkc_defeated"] = caught
        results.append(res)

    # Summary table for --mode all.
    if args.mode == 'all':
        print(f"\n{Colors.BOLD}--- SUMMARY ---{Colors.ENDC}")
        for r in results:
            if r.get("mode"):
                icon = {"bypass": "✅", "blocked": "⛔", "unknown": "⚠️", "error": "❗"}.get(r["status"], "?")
                print(f"  {icon} {r['mode']:<10} -> {r['status']} ({r.get('code')})")

    # Optional JSON report.
    if args.json_out:
        import json
        report = {
            "tool": "Guardrail-Ghost",
            "version": VERSION,
            "target": args.target,
            "message": args.message,
            "results": results,
        }
        try:
            with open(args.json_out, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n{Colors.GREEN}[+] JSON results written: {args.json_out}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}[!] Error writing JSON: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()
