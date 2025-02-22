from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
# from langgraph.errors import
from src.graph_state import AgentState, MasterPlanState
from src.utilities import mark_page


async def master_plan_node(state: AgentState):
    try:
        page = state["page"]
        screen_shot = await mark_page(page)

        system_message = """
        You are an expert a preparing a step by step plan to complete a task.
        You will be given a task provided by the user. The task might also be a question.
        You will need to prepare a plan to complete the task. In case its a question, you will need to prepare a plan to answer the question.
    
        You will be also provided the screenshot of the current web page.
        - If the current page is google home page or any other search engine, create a plan that basically searches the keyword and continues to the next step.
        - If the current page is not a some other web page, create a plan to scroll through the page and relevant collect information. 
    
        For eg if the task is "What is the lastest news on Apple's stock price?", you will need to prepare a plan to answer the question.
        You will need to prepare a plan to complete the task.
    
        For example, if the task is "What is the latest news on Apple's stock price?", your plan might look like this:
        1. Go to Google
        2. Type "Apple stock price news today" in the search bar and press enter
        3. Click on the link to the reliable financial news source (like Reuters, Bloomberg, or CNBC).
        4. Scan the article for current stock price and recent developments
        5. If you have enough information, prepare a concise summary of the latest news and price movement
        6. If you do not have enough information, go back to the previous page and try a different source and collect 
        more data until you have enough information to answer the question.
    
        Your plan should be clear, sequential, and focused on achieving the user's goal efficiently. 
    
        --Notes--
        The browser is already open. First page will always be google, so plan accordingly with a search term.
        For any question, you will need to go to google and search for the question.
        """

        human_prompt = """ This is the task that needs to be performed/question that needs to be answered: {input} \n 
        This is the screenshot of the current web page: {screenshot}"""

        input_str = state["input_str"]

        human_message = human_prompt.format(input=input_str, screenshot=screen_shot)

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message)
        ]

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        # llm = (ChatOpenAI(base_url=os.getenv("OPENROUTER_BASE_URL"), model=os.getenv("MODEL_NAME")))
        structured_llm = llm.with_structured_output(MasterPlanState)

        response = structured_llm.invoke(messages)

        return {"master_plan": [response]}
    except Exception as e:
        raise e
