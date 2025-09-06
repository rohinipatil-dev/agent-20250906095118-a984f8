import streamlit as st
from openai import OpenAI

# Initialize OpenAI client (expects OPENAI_API_KEY in env or Streamlit secrets)
client = OpenAI()

# ----------------------------
# Config and Helpers
# ----------------------------
st.set_page_config(page_title="Future Joke Bot", page_icon="🤖", layout="centered")


def build_system_prompt(tone: str, length: str, family_friendly: bool) -> str:
    rules = [
        "You are a witty stand-up comedian AI.",
        "Your specialty is making original jokes about the FUTURE: technology, space travel, time machines, robots, AI, climate, cities, jobs, and daily life in the year 2100 and beyond.",
        "Keep jokes concise and punchy.",
        "Make the jokes easy to understand without insider jargon, unless 'Nerdy' tone is selected.",
        "Avoid hate, harassment, or harmful content.",
    ]
    if family_friendly:
        rules.append("Keep the jokes family-friendly and suitable for all ages.")
    else:
        rules.append("Mild cheekiness is okay, but do not be offensive.")

    tone_map = {
        "Classic": "Use a light, upbeat tone.",
        "Punny": "Lean into puns and wordplay.",
        "Sarcastic": "Add playful, light sarcasm without being mean.",
        "Nerdy": "Use clever sci-fi and tech references that geeks will love.",
        "Wholesome": "Keep it warm and charming."
    }
    length_map = {
        "One-liner": "Limit to one sentence.",
        "Short": "1-2 sentences max.",
        "Medium": "Up to 3 short sentences."
    }

    return (
        f"{' '.join(rules)} "
        f"Tone: {tone_map.get(tone, 'Use a light, upbeat tone.')}"
        f" Length: {length_map.get(length, '1-2 sentences max.')} "
        f"Always be original and avoid repeating the same joke structures."
    )


def get_model(selected: str) -> str:
    # Only allow supported models per requirements
    if selected not in ["gpt-4", "gpt-3.5-turbo"]:
        return "gpt-4"
    return selected


def generate_chat_completion(messages, model: str, temperature: float, max_tokens: int = 256) -> str:
    response = client.chat.completions.create(
        model=model,  # "gpt-4" or "gpt-3.5-turbo"
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = build_system_prompt("Classic", "Short", True)
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.8


# ----------------------------
# Sidebar Controls
# ----------------------------
with st.sidebar:
    st.header("Settings")
    model_choice = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo"], index=0)
    temperature = st.slider("Creativity (temperature)", 0.0, 1.5, 0.8, 0.05)
    tone = st.selectbox("Tone", ["Classic", "Punny", "Sarcastic", "Nerdy", "Wholesome"])
    length = st.selectbox("Length", ["One-liner", "Short", "Medium"])
    family_friendly = st.checkbox("Family-friendly", value=True)

    if st.button("Apply settings"):
        st.session_state.model = get_model(model_choice)
        st.session_state.temperature = temperature
        st.session_state.system_prompt = build_system_prompt(tone, length, family_friendly)
        st.success("Settings applied!")

    if st.button("Clear chat"):
        st.session_state.chat_history = []
        st.success("Chat cleared.")


# ----------------------------
# Main UI
# ----------------------------
st.title("🤖 Future Joke Bot")
st.caption("Tell me a topic and I’ll crack a joke about the future.")

init_session_state()

# Render existing chat
for m in st.session_state.chat_history:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# Chat input
user_input = st.chat_input("Ask for a future-themed joke (e.g., 'time travel', 'AI in 2100', 'smart fridges').")
if user_input:
    # Append user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare messages with system prompt
    messages = [{"role": "system", "content": st.session_state.system_prompt}]
    messages.extend(st.session_state.chat_history)

    # Get model and temperature
    model = get_model(st.session_state.model)
    temp = float(st.session_state.temperature)

    # Generate response
    try:
        assistant_reply = generate_chat_completion(messages, model=model, temperature=temp)
    except Exception as e:
        assistant_reply = "Oops, I ran into an issue generating a joke. Please try again."

    # Append assistant reply and render
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.write(assistant_reply)

# Footer hint
st.write("")
st.caption("Tip: Try prompts like 'smart homes', 'Mars colonies', 'quantum coffee machines', or 'robot pets'.")