from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from src.graph_state import AgentState
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
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, max_retries=3)
    # llm = (ChatOpenAI(base_url=os.getenv("OPENROUTER_BASE_URL"), model=os.getenv("MODEL_NAME"),
    #                   api_key="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",
    #                   temperature=0.7, max_retries=3, timeout=None))
    response_answer = llm.invoke(prompt_value_answer)
    answer = response_answer.content

    return {"answer": answer}
