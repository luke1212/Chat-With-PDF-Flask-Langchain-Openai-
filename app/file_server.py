import os
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader


def get_doc_path(directory):
    docs_path = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            docs_path.append(os.path.join(directory, filename))
    return docs_path

def load_pdf(file_path):
    if file_path.endswith(".pdf"):
        return PyPDFLoader(file_path).load()
    elif file_path.endswith(".md"):
        return UnstructuredMarkdownLoader(file_path).load()

def text_splitter(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1500,
        chunk_overlap = 150
    )
    return text_splitter.split_documents(docs)

def embed_doc(path):
    embedding = OpenAIEmbeddings()
    persist_directory = "instance/chroma"
    docs = []
    for path in get_doc_path(path):
        docs.extend(load_pdf(path))
    splits = text_splitter(docs)
    
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding, 
        persist_directory=persist_directory    
        )
    vectordb.persist()
    return vectordb

def get_pdf_names(directory):
    pdf_names = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_names.append(filename)
    return pdf_names

def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")

# if __name__ == "__main__": 
#     v = embed_doc(r"instance/docs")
#     filename = "TaskWaver.pdf"
#     source = os.path.join("instance/docs", filename)
#     # print(v._collection.count())
#     question = "who is the author of this paper?"
#     docs = v.similarity_search(
#         question,
#         k=3,
#         filter = {"source": source}
#         )
#     print(docs[0].page_content)
#     print(docs.metadata)
    
