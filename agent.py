from typing_extensions import List, Optional, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage
from langchain_groq import ChatGroq
import requests, base64, os
import dotenv
dotenv.load_dotenv()


def generate_image(prompt: str) -> str:
    """Generates an image using deAPI.ai"""
    import random, time

    # Step 1: ابعت الطلب
    response = requests.post(
        "https://api.deapi.ai/api/v1/client/txt2img",
        headers={
            "Authorization": f"Bearer {os.getenv('DEAPI_KEY')}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json={
            "prompt": prompt,
            "model": "Flux1schnell",
            "width": 512,
            "height": 512,
            "steps": 4,
            "seed": random.randint(1, 99999)
        }
    )
    print(f"deAPI Response: {response.json()}")
    request_id = response.json().get("data", {}).get("request_id")
    print(f"Request ID: {request_id}")

    if not request_id:
        return None

    # Step 2: استنى وجيب النتيجة بالـ endpoint الصح
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
            return base64.b64encode(img_response.content).decode("utf-8")

    return None



# llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
llm = llm.bind_tools([generate_image])


class ImageState(TypedDict):
    user_input: Optional[str]
    messages: List[AnyMessage]
    generation_output: Optional[str]
    story: Optional[str]


sys_msg = """
You are a creative story teller agent.
When the user asks for a story:
- Write a short creative story (3-5 sentences).
- Then call the "generate_image" tool with a vivid prompt
  that captures the key scene of the story.
If the user is just chatting, respond normally without calling any tools.
"""


def agent(state: ImageState) -> ImageState:
    if not state.get("messages"):
        state["messages"] = [
            SystemMessage(content=sys_msg),
            HumanMessage(content=state["user_input"])
        ]
    elif state.get("messages")[-1].name == "generate_image":
        state["generation_output"] = state["messages"][-1].content
        return state
    else:
        state["messages"] = state["messages"] + [
            HumanMessage(content=state["user_input"])
        ]

    response = llm.invoke(state["messages"])
    response.pretty_print()
    state["messages"] = state["messages"] + [response]

    if isinstance(response.content, str) and response.content.strip():
        state["story"] = response.content.strip()
    elif isinstance(response.content, list):
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "").strip()
                if text:
                    state["story"] = text
                    break

    return state


def routing(state: ImageState):
    if hasattr(state["messages"][-1], "tool_calls") and \
       len(state["messages"][-1].tool_calls) > 0:
        return "tool"
    return "done"