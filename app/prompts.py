from langchain.prompts import ChatPromptTemplate,PromptTemplate, SystemMessagePromptTemplate

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

def prompt_template_3(message):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract the relevant information, if not explicitly provided do not guess. Extract partial info"),
        ("human", "{message}")
    ])
    return prompt