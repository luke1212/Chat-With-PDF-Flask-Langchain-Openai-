
import os
import openai
import datetime
import file_server
import data_retrieval
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate,PromptTemplate, SystemMessagePromptTemplate
from langchain.chains import RetrievalQA,ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


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
    chat = chat_open_ai_model()
    prompt = prompt_template.format_messages(text = "something here")
    return chat.invoke(prompt)

def get_completion(message):
    chat = ChatOpenAI(temperature=0.0, model=_llm_model)
    return chat.invoke(message)

def chat_with_doc(message, filename):
    vdb = file_server.embed_single_doc(filename)
    prompt = prompt_template_1(message)
    qa_chain = retrieverQA(vdb,prompt)
    return qa_chain({"query": message})["result"]

def retrieverQA(vectordb, prompt):
    qa_chain = RetrievalQA.from_chain_type(
        chat_open_ai_model(),
        retriever=vectordb.as_retriever(),
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

def create_conversational_memory_agent(message, filename):
    memory = chat_memory()
    llm = chat_open_ai_model()
    prompt = prompt_template_2(message)
    retriever = file_server.embed_single_doc(filename).as_retriever(search_type="similarity", search_kwargs={"k": 4})
    chain_type = "refine"
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory,
        chain_type=chain_type,
        condense_question_prompt=prompt,
    )
    return qa({"question": message})


def chat_open_ai_model():
    llm = ChatOpenAI(temperature=0.0, model=_llm_model)
    return llm

def chat_memory():
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    return memory

def prompt_template_1(question):
    template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Answer the question in Chinese. Keep the answer as concise as possible. 
    {context}
    Question: {question}
    Helpful Answer:"""
    prompt = PromptTemplate(input_variables=["context", "question"],template=template)
    return prompt

def prompt_template_2(question):
    template = """
        Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible.
        
        CONTEXT:
        {context}
        
        QUESTION: 
        {question}

        CHAT HISTORY: 
        {chat_history}
        
        ANSWER:
        """
    prompt=PromptTemplate.from_template(template)
    return prompt
  
# For testing and debugging
if __name__ == "__main__": 
    r = create_conversational_memory_agent("what is the conclusion for this paper?", "TaskWaver.pdf")
    print(r['answer'])

