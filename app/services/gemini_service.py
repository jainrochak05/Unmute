import google.generativeai as genai

def get_chat_reply(api_key, model_name, user_message):
    if not api_key:
        return ("I’m here for you. (AI unavailable: missing API key).", None)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name or "models/gemini-2.0-flash")
        response = model.generate_content(
            f"You are a supportive emotional wellness assistant.\nUser: {user_message}\nAssistant:"
        )
        text = getattr(response, "text", None) or "I'm here with you. Tell me more."
        return text, None
    except Exception as e:
        msg = str(e)
        if "ResourceExhausted" in msg or "quota" in msg.lower() or "429" in msg:
            return (
                "I’m here with you. I can still support you even though AI quota is temporarily exhausted. "
                "Try again in a minute, or continue journaling your thoughts here.",
                None,
            )
        return (None, f"Gemini error: {type(e).__name__}: {e}")
