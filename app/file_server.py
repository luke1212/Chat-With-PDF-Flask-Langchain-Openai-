import os
from flask_wtf import FlaskForm
from wtforms import StringField

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

