import re
import json

def extract_preferences(chat_history):
    income = None
    spend_area = None
    benefit = None

    for message in chat_history:
        if message["role"] == "user":
            text = message["text"].lower()

            # Income extraction
            income_match = re.search(r"(?:income|salary)[^\d]*(\d{4,6})", text)
            if income_match:
                income = int(income_match.group(1))

            # Spending area
            for area in ["groceries", "fuel", "travel", "dining", "shopping"]:
                if area in text:
                    spend_area = area.capitalize()

            # Benefit preference
            for b in ["cashback", "lounge", "voucher", "discount"]:
                if b in text:
                    benefit = b

    return income, spend_area, benefit

def recommend_cards(income, spend_area, benefit, cards):
    recommendations = []

    for card in cards:
        score = 0

        if income and income >= card["eligibility"]["income"]:
            score += 1

        if benefit:
            for b in card["benefits"]:
                if benefit in b.lower():
                    score += 2

        if spend_area and spend_area.lower() in card["rewards"].lower():
            score += 1

        if score > 0:
            card["score"] = score
            recommendations.append(card)

    return sorted(recommendations, key=lambda x: x["score"], reverse=True)
