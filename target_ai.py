from flask import Flask, request, jsonify

app = Flask(__name__)

# The "Guardrail" - A list of forbidden words
BLACKLIST = ["exploit", "hack", "root"]

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message", "")
    
    # 1. The Guardrail Check
    for bad_word in BLACKLIST:
        if bad_word in user_input:
            return jsonify({"response": f"🛑 BLOCKED: The word '{bad_word}' is not allowed!"}), 403

    # 2. The AI Processing
    return jsonify({"response": f"✅ SUCCESS: I am processing your request: {user_input}"})

if __name__ == '__main__':
    print("🤖 Dummy AI running on port 5000...")
    print("🛡️ Guardrails are ACTIVE (Blocking: 'exploit', 'hack', 'root')")
    app.run(port=5000)
