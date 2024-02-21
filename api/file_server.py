import os
import shutil
from flask_wtf import FlaskForm
from wtforms import StringField

class FileForm(FlaskForm):
    name = StringField('File Name')
    path = StringField('File Path')


def get_pdf_names(directory):
    pdf_names = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_names.append(filename)
    return pdf_names

