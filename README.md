# 👻 Guardrail-Ghost v2.0

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Security-Red%20Team-red?style=for-the-badge&logo=kalilinux)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Maintained-orange?style=for-the-badge)

> *"For nothing is secret that will not be revealed, nor anything hidden that will not be known and come to light."* — **Luke 8:17**

## 💀 Overview
**Guardrail-Ghost** is an advanced adversarial evasion tool designed to audit the robustness of AI Guardrails and Web Application Firewalls (WAFs). 

It functions as a **Polyglot Injector**, leveraging Unicode manipulation to bypass keyword-based filtering systems. By transforming malicious payloads into "visually identical" but "digitally distinct" strings, it demonstrates the failure of sanitization layers that rely on standard ASCII matching.

## 🚀 Key Features (v2.0)
The tool now supports multiple evasion strategies to defeat different types of filters:

* **👻 Zero-Width Mode (`--mode zero`)**
    * Injects `U+200B` (Zero Width Space) between every character.
    * *Effect:* Breaks regex matching while remaining readable.
* **🎭 Homoglyph Mode (`--mode homoglyph`)**
    * Replaces Latin characters (a, c, e, o, p, x, y) with their Cyrillic look-alikes.
    * *Effect:* Changes the binary representation of the string entirely.
* **🧪 Mixed Mode (`--mode mixed`)**
    * Combines both strategies for maximum obfuscation.
    * *Effect:* Extremely difficult for static analysis to detect.

## 📦 Installation

```bash
# 1. Clone the repository
git clone [https://github.com/R00t3dbyFa17h/Guardrail-Ghost.git](https://github.com/R00t3dbyFa17h/Guardrail-Ghost.git)

# 2. Enter the directory
cd Guardrail-Ghost

# 3. Install dependencies
pip install -r requirements.txt
```
⚔️ Usage
Basic Syntax
Bash

`python3 guardrail_ghost.py --target <URL> --message "<PAYLOAD>" --mode <MODE>`

Attack Examples

1. The "Ghost" Attack (Zero-Width) Use this to bypass standard "Bad Word" lists.
Bash

`python3 guardrail_ghost.py --target http://localhost:5000/chat --message "exploit" --mode zero`

2. The "Doppelgänger" Attack (Homoglyph) Use this to bypass systems that strip non-printable characters but allow UTF-8.
Bash

`python3 guardrail_ghost.py --target http://localhost:5000/chat --message "admin" --mode homoglyph`

3. The "Chaos" Attack (Mixed) Use this for hardened targets.
Bash

`python3 guardrail_ghost.py --target http://localhost:5000/chat --message "root access" --mode mixed`

🛡️ Mitigation Strategies

To defend against Guardrail-Ghost, developers should implement Unicode Normalization (specifically NFKC) before processing input.
Python

import unicodedata
normalized_text = unicodedata.normalize('NFKC', user_input)

---

## 🆕 v3.0+ Additions (Strictly Additive)

The evasion engine is now fully implemented and expanded. The **default run is unchanged** (`--mode zero` reproduces the original zero-width behavior); everything below is opt-in.

### 🎛️ `--mode` — 8 evasion techniques (+ `all`)
| Mode | Technique |
| :--- | :--- |
| `zero` *(default)* | Zero-Width Space (U+200B) injection |
| `homoglyph` | Cyrillic/Greek look-alike substitution |
| `mixed` | Homoglyph + Zero-Width combined |
| `fullwidth` | ASCII → Unicode fullwidth forms |
| `combining` | Combining diacritical marks (U+0301) |
| `leet` | Leetspeak substitution |
| `case` | Alternating case |
| `rtl` | Right-to-Left override (U+202E) |
| `all` | Run every technique and print a summary table |

```bash
python3 guardrail_ghost.py --target http://localhost:5000/chat --message root --mode all
```

### 🛡️ `--defense-check` (Blue-Team value)
For each payload, reports whether **NFKC normalization + invisible-character stripping** would collapse it back to the original keyword — i.e. whether a properly hardened filter would still catch it. Turns the tool into a guardrail-hardening validator, not just a bypass generator.

### 🧰 More controls
| Flag | Description |
| :--- | :--- |
| `--list-modes` | List all evasion modes and exit |
| `--json FILE` | Write full results (per-mode status, codes, defense verdicts) to JSON |
| `--proxy URL` | Route through a proxy (Burp/ZAP) |
| `--timeout SECS` | Request timeout |
| `-H/--header 'Name: Value'` | Custom headers (repeatable) for authenticated endpoints |
| `--insecure` | Disable TLS verification |
| `--version` / `-q, --quiet` | Version string / quieter output |

> All additions use only the Python standard library (`unicodedata`, `json`) — no new dependencies. Maintained by **R00t3dbyFa17h / K70n0s510**.

---

⚠️ Disclaimer

For Educational Use Only. This tool is intended for authorized security testing and Red Team engagements. The author (R00t3dbyFa17h) is not responsible for unauthorized use.

Forged by R00t3dbyFa17h / K70n0s510
