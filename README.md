# 📖 Story Teller Agent

An AI agent that writes a short story and generates an image for it.

---

## How It Works

1. You type a request like "tell me a story about a dragon"
2. The agent writes a short creative story
3. The agent generates an image for the story using deAPI.ai
4. Both the story and image appear in the chat

---

## How To Run

**1. Clone the repo**
```bash
git clone https://github.com/maramessam14/generate-story.git
cd generate-story
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Add your API keys**

Create a `.env` file:
```
GROQ_API_KEY=your_groq_key_here
DEAPI_KEY=your_deapi_key_here
```

- Groq key (free): https://console.groq.com
- deAPI key ($5 free credits): https://deapi.ai

**4. Run**
```
streamlit run app.py
```

---

## Tech Stack

- **LangGraph** — agent framework
- **Groq (LLaMA 3.3)** — story writing
- **deAPI.ai** — image generation
- **Streamlit** — UI