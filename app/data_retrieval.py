import file_server
import os
from langchain_openai import OpenAI,ChatOpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chains import RetrievalQA

_doc_path = os.path.join("instance", "docs")
_llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0)

# Define the target information
def get_file_info(message, filename):
    v = file_server.embed_doc(_doc_path)
    question = message
    source = os.path.join(_doc_path, filename)
    return v, question, source

def pretty_print_docs(docs):
    return f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])

def data_similarity_search(message, filename):
    v, question, source = get_file_info(message, filename)
    docs = v.similarity_search(
        question,
        k=3,
        filter={"source": source}
    )
    return docs

def data_max_marginal_relevance_search(message, filename):
    v, question, source = get_file_info(message, filename)
    docs = v.max_marginal_relevance_search(
        question,
        k=3,
        filter = {"source": source}
        )
    return docs

def data_self_query_retriever(filename):
    vectordb, question, source = get_file_info("", filename)
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
    retriever = SelfQueryRetriever.from_llm(
        _llm,
        vectordb,
        document_content_description,
        metadata_field_info,
    )
    return retriever

def data_contextual_compression_retriever(filename):
    retriever = file_server.embed_single_doc(filename)
    compressor = LLMChainExtractor.from_llm(_llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=retriever.as_retriever()
    )
    return compression_retriever
   
def retrieverQA(vectordb, prompt):
    qa_chain = RetrievalQA.from_chain_type(
        chat_open_ai_model(),
        retriever=vectordb.as_retriever(),
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

def chat_open_ai_model():
    llm = ChatOpenAI(temperature=0.0)
    return llm

if __name__ == "__main__": 
    v = file_server.embed_doc(_doc_path)
    filename = "TaskWaver.pdf"
    source = os.path.join("instance/docs", filename)
    # print(v._collection.count())
    question = "who is the author of this paper?"
    # docs = v.similarity_search(
    #     question,
    #     k=3,
    #     filter = {"source": source}
    #     )
    # docs = data_self_query_retriever(question, filename)
    # docs = data_max_marginal_relevance_search(question, filename)
    # docs = data_contextual_compression_retriever(filename)
    docs = data_similarity_search(question, filename)
    # for doc in docs:
    #     print(doc.metadata)
    print(docs)