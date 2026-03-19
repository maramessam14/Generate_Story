from typing_extensions import List, Optional, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage, AIMessage
from langchain_groq import ChatGroq
import requests, base64, os, random, time
import dotenv
dotenv.load_dotenv()


class ImageState(TypedDict):
    user_input: Optional[str]
    messages: List[AnyMessage]
    generation_output: Optional[str]
    story: Optional[str]


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)


# ── Node 1: Orchestra ─────────────────────────────────────────
def orchestra(state: ImageState) -> ImageState:
    """Decides what to do based on user input."""
    print("🎼 Orchestra: deciding next step...")
    return state


def orchestra_routing(state: ImageState) -> str:
    user_input = state.get("user_input", "").lower()
    story_keywords = ["story", "tell", "write", "once", "tale"]
    if any(word in user_input for word in story_keywords):
        return "story_writer"
    return "story_writer"  # default


# ── Node 2: Story Writer ──────────────────────────────────────
def story_writer(state: ImageState) -> ImageState:
    """Writes a short creative story."""
    print("✍️ Story Writer: writing story...")
    sys_msg = """
    You are a creative story teller.
    Write a short creative story (3-5 sentences) based on the user request.
    Only write the story, nothing else.
    """
    messages = [
        SystemMessage(content=sys_msg),
        HumanMessage(content=state["user_input"])
    ]
    response = llm.invoke(messages)
    response.pretty_print()

    story = ""
    if isinstance(response.content, str):
        story = response.content.strip()
    elif isinstance(response.content, list):
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                story = block.get("text", "").strip()
                break

    state["story"] = story
    state["messages"] = messages + [response]
    return state


# ── Node 3: Image Generation ──────────────────────────────────
def image_gen(state: ImageState) -> ImageState:
    """Generates an image based on the story."""
    print("🎨 Image Gen: generating image...")

    # Ask LLM to create image prompt from story
    prompt_msg = [
        HumanMessage(content=f"Create a short vivid image prompt (max 20 words) for this story: {state['story']}")
    ]
    prompt_response = llm.invoke(prompt_msg)
    image_prompt = prompt_response.content.strip()
    print(f"Image prompt: {image_prompt}")

    # Call deAPI
    response = requests.post(
        "https://api.deapi.ai/api/v1/client/txt2img",
        headers={
            "Authorization": f"Bearer {os.getenv('DEAPI_KEY')}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json={
            "prompt": image_prompt,
            "model": "Flux1schnell",
            "width": 512,
            "height": 512,
            "steps": 4,
            "seed": random.randint(1, 99999)
        }
    )
    print(f"deAPI Response: {response.json()}")
    request_id = response.json().get("data", {}).get("request_id")

    if not request_id:
        return state

    for attempt in range(15):
        time.sleep(4)
        result = requests.get(
            f"https://api.deapi.ai/api/v1/client/request-status/{request_id}",
            headers={
                "Authorization": f"Bearer {os.getenv('DEAPI_KEY')}",
                "Accept": "application/json"
            }
        )
        print(f"Attempt {attempt+1}: {result.json()}")
        data = result.json().get("data", {})
        image_url = data.get("result_url") or data.get("url") or data.get("image_url")

        if image_url:
            print(f"✅ Image URL: {image_url}")
            img_response = requests.get(image_url, timeout=30)
            state["generation_output"] = base64.b64encode(img_response.content).decode("utf-8")
            return state

    return state