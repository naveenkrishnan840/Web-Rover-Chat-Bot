from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.src.graph_state import AgentState
import os


async def answer_node(state: AgentState):
    system_message_answer = """ You are an assistant who is expert at answering the user input based on the notes.
    You will be given:
    Notes: {notes}

    Breakdown the Answer in to two sections:
    1. Steps: A list of steps were taken to surf the web and provide answer to the user input.
    2. Final Answer: Should only contain the final answer that directly provides answer to the user input.

    Provide the answer in proper markdown format. Use proper markdown formatting for the steps and final answer.
    """

    prompt_answer = ChatPromptTemplate(
        messages=[
            ("system", system_message_answer),
            ("human", "User Input: {input}")
        ],
        input_variables=["notes", "input"],
    )

    notes = state["notes"]
    input_str = state["input_str"]

    prompt_value_answer = prompt_answer.invoke({"notes": notes, "input": input_str})
    # llm = ChatOllama(model="deepseek-coder:33b", base_url="http://localhost:11434")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    response_answer = llm.invoke(prompt_value_answer)
    answer = response_answer.content

    return {"answer": answer}
