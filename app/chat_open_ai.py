
import os
import openai
import datetime
import file_server
import data_retrieval
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import MessagesPlaceholder
from langchain.schema.agent import AgentFinish
from langchain.agents import AgentExecutor
import functions
import prompts


from dotenv import load_dotenv, find_dotenv

# read local .env file
_ = load_dotenv(find_dotenv()) 
openai.api_key = os.environ['OPENAI_API_KEY']

current_date = datetime.datetime.now().date()

# Define the date after which the model should be set to "gpt-3.5-turbo"
target_date = datetime.date(2024, 6, 12)

# Set the model variable based on the current date
if current_date > target_date:
    _llm_model = "gpt-3.5-turbo"
else:
    _llm_model = "gpt-3.5-turbo-0301"
 
# OpenAI Chat Completion
def get_summary(document_path):
    template_string = """summarize the following sections of the paper:\
        text: ```{text}```
        """
    prompt_template = ChatPromptTemplate.from_template(template_string)
    chat = data_retrieval.chat_open_ai_model()
    prompt = prompt_template.format_messages(text = "something here")
    return chat.invoke(prompt)

def get_completion(message):
    chat = ChatOpenAI(temperature=0.0, model=_llm_model)
    return chat.invoke(message)

def chat_with_doc(message, filename):
    vdb = file_server.embed_single_doc(filename)
    prompt = prompts.prompt_template_1(message)
    qa_chain = data_retrieval.retrieverQA(vdb,prompt)
    return qa_chain({"query": message})["result"]

def create_conversational_memory_agent(message, filename):
    memory = chat_memory()
    llm = data_retrieval.chat_open_ai_model()
    prompt = prompts.prompt_template_2(message)
    retriever = file_server.embed_single_doc(filename).as_retriever(search_type="similarity", search_kwargs={"k": 4})
    chain_type = "refine"
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory,
        chain_type=chain_type,
        condense_question_prompt=prompt,
        verbose=True
    )
    return qa({"question": message})

def get_overview_tagging(message, file):
    tagging_model = ChatOpenAI(temperature=0.0).bind(
        functions=functions.overview_tagging_function,
        function_call={"name":"Overview"}
    )
    docs = data_retrieval.data_max_marginal_relevance_search(message, file)
    tagging_chain = prompts.prompt_template_3 | tagging_model | JsonOutputFunctionsParser()
    return tagging_chain.invoke({"message": docs, "filename": file})

def initialize_agent_chain():
    functionList = [format_tool_to_openai_function(f) for f in functions.tools]
    model = ChatOpenAI(temperature=0).bind(functions=functionList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are helpful but sassy assistant"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    chain = prompt | model | OpenAIFunctionsAgentOutputParser()
    agent_chain = RunnablePassthrough.assign(
        agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | chain
    return agent_chain

def initialize_chatbot(message):
    intermediate_steps = []
    while True:
        result = initialize_agent_chain().invoke({
            "input": message, 
            "intermediate_steps": intermediate_steps
        })
        if isinstance(result, AgentFinish):
            return result
        tool = {
            "search_wikipedia": functions.search_wikipedia, 
            "get_current_temperature": functions.get_current_temperature,
        }[result.tool]
        observation = tool.run(result.tool_input)
        intermediate_steps.append((result, observation))

def chat_agent_executor(message):
    agent_executor = AgentExecutor(agent=initialize_agent_chain(), tools=functions.tools, verbose=True, memory=chat_memory())
    return agent_executor.invoke({"input": message})['output']

def chat_memory():
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    return memory
  
# For testing and debugging
if __name__ == "__main__": 
    r = chat_agent_executor("what is google?")
    print(r)

