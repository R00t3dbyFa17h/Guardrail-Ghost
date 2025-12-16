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

def send_request(target, message, label):
    try:
        response = requests.post(target, json={"message": message})
        
        if response.status_code == 200:
            print(f"[*] {label}: {Colors.GREEN}✅ BYPASS SUCCESS ({response.status_code}){Colors.ENDC}")
            print(f"    Server Reply: {response.json().get('response')}")
        elif response.status_code == 403:
            print(f"[*] {label}: {Colors.RED}⛔ BLOCKED ({response.status_code}){Colors.ENDC}")
            print(f"    Server Reply: {response.json().get('response')}")
        else:
            print(f"[*] {label}: {Colors.YELLOW}⚠️ UNKNOWN ({response.status_code}){Colors.ENDC}")
            
    except Exception as e:
        print(f"[!] Error: {e}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="WAF Evasion Tool")
    parser.add_argument('--target', required=True, help='Target URL (e.g., http://localhost:5000/chat)')
    parser.add_argument('--message', required=True, help='The malicious word to hide')
    args = parser.parse_args()

    print(f"{Colors.BOLD}--- PHASE 1: CONTROL TEST ---{Colors.ENDC}")
    print("Sending clean payload to verify WAF is active...")
    send_request(args.target, args.message, "CLEAN PAYLOAD")

    print(f"\n{Colors.BOLD}--- PHASE 2: GHOST MODE ---{Colors.ENDC}")
    ghost_payload = obfuscate_zero_width(args.message)
    print(f"Injecting Zero-Width Spaces into '{args.message}'...")
    
    # Show the Hex Dump
    print_hex_comparison(args.message, ghost_payload)
    
    # Send the Attack
    send_request(args.target, ghost_payload, "GHOST PAYLOAD")

if __name__ == "__main__":
    main()
