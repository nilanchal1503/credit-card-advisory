import streamlit as st
import json
import os
from serpapi import GoogleSearch

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Credit Card Advisor 💳", layout="centered")

# Theme toggle in sidebar
mode = st.sidebar.radio("🌓 Theme", ["Light Mode", "Dark Mode"])

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = mode
elif st.session_state.theme_mode != mode:
    st.session_state.theme_mode = mode
    st.rerun()

# ---------------- THEME CSS ----------------
if st.session_state.theme_mode == "Dark Mode":
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom right, #0f111a, #1a1e2b);
            color: #ff0000;
        }
        .message-box {
            background-color: #222435;
            color: #f0f4f8;
            border-left: 5px solid #7a42f4;
            border-radius: 10px;
            margin: 6px 0;
            padding: 10px 14px;
        }
        .message-box.ai {
            background-color: #2a2c3a;
        }
        .card-box {
            background-color: #2a2b3d;
            border: 1.5px solid #5c5e70;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 20px;
            color: #f0f4f8;
        }
                /* Dark mode form input tweaks */
input, select, textarea, .stSlider, .stNumberInput, .stSelectbox, .stRadio {
    color: #ffffff !important;
    background-color: #ffffff !important;
    border-color: #ffffff !important;
}
.stRadio > div {
    color: #ffffff !important;
}


        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom right, #f3f9ff, #dbefff);
            color: #222;
        }
        .message-box {
            background-color: #ffffff;
            border-left: 5px solid #0099ff;
            border-radius: 10px;
            margin: 6px 0;
            padding: 10px 14px;
        }
        .message-box.ai {
            border-left-color: #7a42f4;
            background-color: #f4f2ff;
        }
        .card-box {
            background-color: #ffffffcc;
            border: 2px solid #dbe9ff;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 20px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
            color: #222;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------- MODEL SETUP ----------------
st.title("💳 Credit Card Advisor")

# Set the SERP API key
os.environ["SERP_API_KEY"] = "fcc806f328affde082149cf0609a6fb346003bf3da079de728e7d1588d9b06ce"

def fetch_search_results(query):
    """
    Fetch search results using the SERP API.
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP API Key not found. Set it as an environment variable.")
    
    params = {
        "q": query,
        "location": "India",
        "hl": "en",
        "gl": "in",
        "api_key": api_key
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("organic_results", [])
    except Exception as e:
        return [{"title": "Error fetching results", "link": str(e)}]

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "cards_shown_in_chat" not in st.session_state:
    st.session_state.cards_shown_in_chat = False

# ---------------- CHAT UI ----------------
st.markdown("### 💬 Talk to the Advisor")

if st.button("🔄 Reset Chat"):
    st.session_state.chat_history = []
    st.session_state.cards_shown_in_chat = False
    st.rerun()

for msg in st.session_state.chat_history:
    label = "Advisor" if msg["role"] == "ai" else "You"
    role_class = "ai" if msg["role"] == "ai" else ""
    st.markdown(f"<div class='message-box {role_class}'><strong>{label}:</strong> {msg['text']}</div>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your question and press Enter:")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    search_results = fetch_search_results(user_input)
    response = "Here are the top search results:\n"
    for result in search_results[:5]:  # Display top 5 results
        response += f"- {result['title']}: {result['link']}\n"
    
    st.session_state.chat_history.append({"role": "ai", "text": response})
    st.rerun()

# ---------------- FORM SECTION ----------------
with open("cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

st.markdown('<div class="recommend-header"><h4>📊 Get Personalized Recommendations</h4></div>', unsafe_allow_html=True)
st.markdown('<div class="recommend-form">', unsafe_allow_html=True)

income = st.number_input("👉 Monthly income (₹)", min_value=0, step=1000)
spending_area = st.selectbox("👉 Primary spend category", ["Groceries", "Fuel", "Travel", "Dining", "Shopping"])
monthly_spend = st.number_input(f"👉 Monthly spend on {spending_area}", min_value=0, step=500)
preferred_benefit = st.selectbox("👉 Preferred benefit", ["Cashback", "Lounge Access", "Amazon Vouchers", "Dining Discounts"])
credit_score_known = st.radio("👉 Do you know your credit score?", ["Yes", "No"])
credit_score = st.slider("Your credit score", 300, 900, 700) if credit_score_known == "Yes" else None

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RECOMMENDATIONS ----------------
if st.button("🎯 Show Recommendations"):
    scored_cards = []
    for card in cards:
        score = 0
        if income >= card["eligibility"]["income"]:
            score += 1
        for benefit in card["benefits"]:
            if preferred_benefit.lower() in benefit.lower():
                score += 2
        if spending_area.lower() in card["rewards"].lower():
            score += 1
        if score > 0:
            card["score"] = score
            scored_cards.append(card)

    sorted_cards = sorted(scored_cards, key=lambda x: x["score"], reverse=True)

    st.markdown("### ✨ Top Recommended Cards")
    if sorted_cards:
        for card in sorted_cards[:3]:
            annual_savings = int(monthly_spend * 12 * 0.015)
            st.markdown(f"""
                <div class="card-box">
                    <img src="{card['image_url']}" width="80" style="float:right; margin-left:10px;"/>
                    <h4>{card['name']}</h4>
                    <p><strong>Issuer:</strong> {card['issuer']}</p>
                    <p><strong>Annual Fee:</strong> ₹{card['annual_fee']}</p>
                    <p><strong>Benefits:</strong> {', '.join(card['benefits'])}</p>
                    <p><strong>🎁 Estimated Savings:</strong> ₹{annual_savings}/year</p>
                    <a href="{card['apply_link']}" class="apply-link" target="_blank">👉 Apply Now</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Sorry, no matching cards found. Try adjusting your preferences.")
