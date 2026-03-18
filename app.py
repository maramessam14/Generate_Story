import streamlit as st
# import base64
from main import workflow, ImageState

st.set_page_config(page_title="Story Teller 🧙", page_icon="📖", layout="centered")
st.title("📖 Story Teller Agent")
st.caption("Tell me what you want and I'll write you a story with an image! ✨")

if "state" not in st.session_state:
    st.session_state.state = ImageState(
        messages=[],
        user_input="",
        generation_output=None,
        story=None
    )

if "chat_display" not in st.session_state:
    st.session_state.chat_display = []

for entry in st.session_state.chat_display:
    with st.chat_message(entry["role"]):
        st.write(entry["content"])
        if entry.get("image") and entry["image"] != "null":
            try:
               import base64
               st.image(base64.b64decode(entry["image"]), width=512)
            except Exception:
                pass
            
user_input = st.chat_input("Ask for a story or start a conversation...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.chat_display.append({
        "role": "user",
        "content": user_input
    })

    st.session_state.state["user_input"] = user_input
    st.session_state.state["generation_output"] = None
    st.session_state.state["story"] = None

    with st.spinner("🧙 Crafting your story..."):
        st.session_state.state = workflow.invoke(st.session_state.state)

    ai_text = st.session_state.state.get("story") or ""
    image_data = st.session_state.state.get("generation_output")

    with st.chat_message("assistant"):
        if ai_text:
            st.write(ai_text)
        if image_data and image_data != "null":
            try:
                import base64
                st.image(base64.b64decode(image_data), width=512)
                st.caption("🎨 Generated image for the story")
            except Exception:
                st.info("🎨 Image is being generated...")

    st.session_state.chat_display.append({
        "role": "assistant",
        "content": ai_text,
        "image": image_data
    })