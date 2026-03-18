from agent import ImageState, agent, routing, generate_image
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import dotenv
dotenv.load_dotenv()

workflow = StateGraph(ImageState)
workflow.add_node("agent", agent)
workflow.add_node("gen_image", ToolNode([generate_image]))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    routing,
    {"tool": "gen_image", "done": END}
)
workflow.add_edge("gen_image", "agent")
workflow = workflow.compile()

if __name__ == "__main__":
    state = ImageState(messages=[], user_input="", generation_output=None, story=None)
    user_input = input("User: ")
    while user_input.lower() != "exit":
        state["user_input"] = user_input
        state = workflow.invoke(state)
        if state.get("generation_output"):
            print(f"Story: {state.get('story')}")
            print(f"Image generated!")
            break
        user_input = input("User: ")