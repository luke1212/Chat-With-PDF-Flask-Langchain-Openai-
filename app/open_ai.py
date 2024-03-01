
import os
import openai
import datetime
import re
import file_server
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PDFMinerPDFasHTMLLoader, UnstructuredMarkdownLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from nltk.tokenize import sent_tokenize
from werkzeug.utils import secure_filename

from dotenv import load_dotenv, find_dotenv

doc_path = os.path.join("instance", "docs")
md_path = os.path.join("instance", "md")

# read local .env file
_ = load_dotenv(find_dotenv()) 
openai.api_key = os.environ['OPENAI_API_KEY']

current_date = datetime.datetime.now().date()

# Define the date after which the model should be set to "gpt-3.5-turbo"
target_date = datetime.date(2024, 6, 12)

# Set the model variable based on the current date
if current_date > target_date:
    llm_model = "gpt-3.5-turbo"
else:
    llm_model = "gpt-3.5-turbo-0301"

#Load the PDF
def loadpdf_miner_html(str):
    pdf_loader = PDFMinerPDFasHTMLLoader(str)
    data = pdf_loader.load()
    return data

#Parse the HTML to snippets
def parse_html_to_snippnets(data):

    soup = BeautifulSoup(data[0].page_content, 'html.parser')
    content = soup.find_all('div')

    cur_fs = None
    cur_text = ''
    snippets = []  # first collect all snippets that have the same font size
    for c in content:
        sp = c.find('span')
        if not sp:
            continue
        st = sp.get('style')
        if not st:
            continue
        fs = re.findall(r'font-size:(\d+)px', st)
        if not fs:
            continue
        fs = int(fs[0])
        if not cur_fs:
            cur_fs = fs
        if fs == cur_fs:
            cur_text += c.text
        else:
            snippets.append((cur_text, cur_fs))
            cur_fs = fs
            cur_text = c.text
    snippets.append((cur_text, cur_fs))
    return snippets

 # count the cur_fs times and total str len
def calculate_font_statistics(snippets):
    font_dict = {}
    for snippet in snippets:
        if snippet[1] not in font_dict:
            font_dict[snippet[1]] = [0, 0]
        font_dict[snippet[1]][0] += 1
        font_dict[snippet[1]][1] += len(snippet[0])

    return font_dict

#Find the section font size
def find_section_font_size(sorted_font_dict):
    section_font_size = 0
    for key in sorted_font_dict:
        if sorted_font_dict[key][0] > 6 and sorted_font_dict[key][2] > 8 and sorted_font_dict[key][2] < 300:
            section_font_size = key
            break
    return section_font_size

#Merge the snippets
def merge_snippets(snippets, section_font_size):
    section_text = {'title': ""}
    section_title = 'title'
    title_font_size = 0
    for snippet in snippets:
        if section_title == 'title':
            # find max font_size snippet as title
            title_text = ''
            if snippet[1] > title_font_size:
                title_font_size = snippet[1]
                title_text = snippet[0]

        if snippet[1] == section_font_size:
            section_title = snippet[0]
            if section_title not in section_text:
                section_text[section_title] = ''
        else:
            section_text[section_title] += snippet[0]
    
    return section_text


#Generate the markdown from the PDF
def generate_markdown_from_pdf(filename): 

    data = loadpdf_miner_html(os.path.join(doc_path, secure_filename(filename)))
    snippets = parse_html_to_snippnets(data)
    font_dict = calculate_font_statistics(snippets)

    # count avg len
    for key in font_dict:
        font_dict[key].append(font_dict[key][1]/font_dict[key][0])
    
    # reverse sort font dict
    sorted_font_dict = {key: font_dict[key] for key in sorted(font_dict.keys(), reverse=True)}

    section_font_size = find_section_font_size(sorted_font_dict)
    section_text = merge_snippets(snippets, section_font_size)
   
    # Tokenize the text into sentences for each section
    for key in section_text:
        sentences = sent_tokenize(section_text[key])
        section_text[key] = {'sentences': sentences, 'text': section_text[key]}
        # remove meaningless \n in each sentence
        for i in range(len(sentences)):
            sentences[i] = sentences[i].replace('\n', ' ')

    # save the text into a markdown file
    filename_md = os.path.splitext(filename)[0] + ".md"
    
    # create the markdown folder if not exists
    if not os.path.exists(md_path):
        os.makedirs(md_path)
        
    with open(os.path.join(md_path, secure_filename(filename_md)), "w", encoding='utf-8') as f:
        for key in section_text:
            f.write(f"# {key}\n")
            for sentence in section_text[key]['sentences']:
                f.write(f"{sentence}\n")
            f.write("\n")

#Load the markdown file
def load_markdown_file(file_path):
    loader = UnstructuredMarkdownLoader(file_path, mode="elements")
    docs = loader.load()
    return docs
    
# OpenAI Chat Completion
def get_summary(document_path):
    docs = load_markdown_file(document_path)
    template_string = """summarize the following sections of the paper:\
        text: ```{text}```
        """
    prompt_template = ChatPromptTemplate.from_template(template_string)
    chat = ChatOpenAI(temperature=0.0, model=llm_model)
    prompt = prompt_template.format_messages(text = docs[3].page_content)
    return chat.invoke(prompt)

def get_completion(message):
    chat = ChatOpenAI(temperature=0.0, model=llm_model)
    return chat.invoke(message)
  
#For testing and debugging
# if __name__ == "__main__": 
#     r = get_completion("hi what is your name")
#     print(r.content)

