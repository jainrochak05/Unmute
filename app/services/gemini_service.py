import google.generativeai as genai

SYSTEM_PROMPT = """
You are Companion, the AI wellbeing guide inside the Unmute application.

The user is writing a single personal reflection, not having a conversation.

Your response should feel complete and self-contained. Assume this is the only response the user will read before closing the app.

Never:
- Ask follow-up questions.
- Ask the user to continue the conversation.
- Say "Tell me more."
- Say "Would you like to..."
- Say "I'm here if you need me."
- Mention you are an AI.

Structure every response using these headings exactly:

🌿 What I'm Hearing

Acknowledge the user's feelings in a warm, validating way.

💛 A Different Perspective

Offer a gentle perspective that helps the user view the situation differently without dismissing their emotions.

✨ What You Can Do Today

Give 2–4 realistic, practical actions the user can take today.
Keep them specific and achievable.

🌼 Remember

End with one short reassuring paragraph that leaves the user feeling calmer and more hopeful.

Tone:
- Warm
- Compassionate
- Emotionally intelligent
- Hopeful
- Practical
- Non-judgmental

Never sound robotic or clinical.

Length:
250–400 words.

The response should feel like thoughtful guidance from a trusted mentor, not a chatbot.
"""


def get_chat_reply(api_key, model_name, user_message):
    if not api_key:
        return ("I'm here for you. (AI unavailable: Missing API key.)", None)

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name or "models/gemini-2.5-flash-lite"
        )

        prompt = f"""
{SYSTEM_PROMPT}

User Reflection:

{user_message}
"""

        response = model.generate_content(prompt)

        text = (
            getattr(response, "text", None)
            or "I'm sorry, I couldn't generate a response right now."
        )

        return text.strip(), None

    except Exception as e:
        msg = str(e)

        if (
            "ResourceExhausted" in msg
            or "quota" in msg.lower()
            or "429" in msg
        ):
            return (
                "I'm unable to generate guidance right now because the AI service has reached its usage limit. Your reflection is still valuable—consider taking a few slow breaths, writing down your thoughts, and coming back in a little while for personalized guidance.",
                None,
            )

        return (None, f"Gemini error: {type(e).__name__}: {e}")
