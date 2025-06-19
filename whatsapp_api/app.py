import sys
import logging
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from chat_logic import recommend_cards  # Import your recommendation logic

# Ensure proper module access for imports
sys.path.append("..")

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Flask app
app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Handles incoming WhatsApp messages from Twilio."""
    incoming_msg = request.form.get("Body", "").strip()
    user_number = request.form.get("From", "").strip()

    logging.info(f"📩 Incoming Message from {user_number}: {incoming_msg}")

    if not incoming_msg:
        response_text = "🤖 Hi there! Please type your request, and I'll recommend the best credit cards for you!"
    else:
        try:
            response_text = recommend_cards(incoming_msg)  # Get AI-powered recommendations
        except Exception as e:
            logging.error(f"❌ Error processing request: {e}")
            response_text = "⚠️ Sorry, I ran into an issue processing your request. Please try again!"

    # Create Twilio response
    resp = MessagingResponse()
    msg = resp.message(response_text)

    logging.info(f"📝 Bot Response: {response_text}")

    return str(resp)

if __name__ == "__main__":
    # Ensure the app binds to the correct host and port for Render
    port = int(os.getenv("PORT", 5000))  # Read port from environment variable
    app.run(debug=True, host="0.0.0.0", port=port)