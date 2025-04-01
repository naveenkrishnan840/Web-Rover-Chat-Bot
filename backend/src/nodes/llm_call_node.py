from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from src.graph_state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI


async def llm_call_node(state: AgentState):
    try:
        template = """Imagine you are a robot browsing the web, just like humans. Now you need to complete a task. In each iteration,
        you will receive an Observation that includes a screenshot of a webpage and some texts. 
        Carefully analyze the bounding box information and the web page contents to identify the Numerical Label corresponding 
        to the Web Element that requires interaction, then follow
        the guidelines and choose one of the following actions:
    
        1. Click a Web Element.
        2. Delete existing content in a textbox and then type content.
        3. Scroll up or down.
        4. Wait 
        5. Go back
        7. Return to google to start over.
        8. Respond with the final answer
    
        Correspondingly, Action should STRICTLY follow the format:
    
        - Click [Numerical_Label] 
        - Type [Numerical_Label]; [Content] 
        - Scroll [Numerical_Label or WINDOW]; [up or down] 
        - Wait 
        - GoBack
        - Google
        - Respond 
    
        Key Guidelines You MUST follow:
    
        * Action guidelines *
        1) Execute only one action per iteration.
        2) Always click close on the popups.
        3) When clicking or typing, ensure to select the correct bounding box.
        4) Numeric labels lie in the top-left corner of their corresponding bounding boxes and are colored the same.
        5) Try to scroll down if a pdf or a document is opeened to read the entire document., if you dont find the information you need, go back to the previous page and try a different source and collect more data until you have enough information to answer the question.
    
        * Web Browsing Guidelines *
        1) Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages
        2) Select strategically to minimize time wasted.
    
        Your reply should strictly follow the format:
        Thought: {{Your brief thoughts (briefly summarize the info that will help ANSWER)}}
        Action: {{One Action format you choose}} (Make sure to enclose the bbox id in [] , for eg  Click [1], Type [5], Scroll [10] or Scroll [WINDOW])
    
        Then the User will provide:
        Observation: {{A labeled bounding boxes and contents given by User}}"
        Actions Taken: {{A list of actions taken so far}} (Could be empty, if it is the first iteration)
        Master Plan: {{A set of steps that you can use as a reference to complete the task}}
    
        Observation including a screenshot of a webpage with bounding boxes and the text related to it: {{result}}"""

        prompt = ChatPromptTemplate(
            messages=[
                ("system", template),
                ("human", "Input: {input}"),
                ("human", "Actions Taken So far: {actions_taken}"),
                ("human", "Observation: Screenshot: {image}"),
                ("human", "Observation: Bounding Boxes: {bboxes}"),

            ],
            input_variables=["image", "bboxes", "input"],
            partial_variables={"actions_taken": []},
            optional_variables=["actions_taken"]
        )

        actions_taken = state.get("actions_taken", [])
        image = state["image"]
        bboxes = state["bboxes"]
        input_str = state["input_str"]
        master_plan = state["master_plan"]

        prompt_value = prompt.invoke(
            {"actions_taken": actions_taken, "image": image, "bboxes": bboxes, "input": input_str,
             "master_plan": master_plan})

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, max_retries=3)
        # llm = (ChatOpenAI(base_url=os.getenv("OPENROUTER_BASE_URL"), model=os.getenv("MODEL_NAME"),
        #                   api_key="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",
        #                   temperature=0.7, max_retries=3, timeout=None))
        response = llm.invoke(prompt_value)

        action = response.content

        return {"action": action}
    except Exception as e:
        raise e
