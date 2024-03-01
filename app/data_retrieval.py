import file_server
import os
from langchain_openai import OpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

doc_path = os.path.join("instance", "docs")

def data_similarity_search(message, filename):
    v, question, source = get_file_info(message, filename)
    docs = v.similarity_search(
        question,
        k=3,
        filter={"source": source}
    )
    return docs[0].page_content

def data_max_marginal_relevance_search(message, filename):
    v, question, source = get_file_info(message, filename)
    docs = v.max_marginal_relevance_search(
        question,
        k=3,
        filter = {"source": source}
        )
    return docs[0].page_content

def data_self_query_retriever(message, filename):
    vectordb, question, source = get_file_info(message, filename)
    metadata_field_info = [
        AttributeInfo(
            name="source",
            description="The lecture the chunk is from, should be {}".format(source),
            type="string",
        ),
        AttributeInfo(
            name="page",
            description="The page from the pdf",
            type="integer",
        ),
    ]
    document_content_description = "The content of the document."
    llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0)
    retriever = SelfQueryRetriever.from_llm(
        llm,
        vectordb,
        document_content_description,
        metadata_field_info,
        verbose=True,
    )
    return retriever.get_relevant_documents(question)

# Define the target information
def get_file_info(message, filename):
    v = file_server.embed_doc(doc_path)
    question = message
    source = os.path.join(doc_path, filename)
    return v, question, source

# if __name__ == "__main__": 
# #     r = get_completion("hi what is your name")
# #     print(r.content)
#     v = file_server.embed_doc(doc_path)
#     filename = "TaskWaver.pdf"
#     source = os.path.join("instance/docs", filename)
#     # print(v._collection.count())
#     question = "what is the conclusion of this paper?"
    # docs = v.similarity_search(
    #     question,
    #     k=3,
    #     filter = {"source": source}
    #     )
    # docs = data_self_query_retriever(question, filename)
    # docs = data_max_marginal_relevance_search(question, filename)
    # for doc in docs:
    #     print(doc.metadata)
    # print(docs)