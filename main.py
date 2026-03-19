from agent import ImageState, orchestra, orchestra_routing, story_writer, image_gen
from langgraph.graph import StateGraph, START, END
import dotenv
dotenv.load_dotenv()

workflow = StateGraph(ImageState)

# 3 Nodes
workflow.add_node("orchestra", orchestra)
workflow.add_node("story_writer", story_writer)
workflow.add_node("image_gen", image_gen)

# Edges
workflow.add_edge(START, "orchestra")
workflow.add_conditional_edges(
    "orchestra",
    orchestra_routing,
    {"story_writer": "story_writer"}
)
workflow.add_edge("story_writer", "image_gen")
workflow.add_edge("image_gen", END)

workflow = workflow.compile()

if __name__ == "__main__":
    state = ImageState(messages=[], user_input="", generation_output=None, story=None)
    user_input = input("User: ")
    while user_input.lower() != "exit":
        state["user_input"] = user_input
        state = workflow.invoke(state)
        print(f"\nStory: {state.get('story')}")
        if state.get("generation_output"):
            print("Image generated!")
        user_input = input("User: ")