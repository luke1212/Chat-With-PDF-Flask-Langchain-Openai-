from flask import *
from api import file_server
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

doc_path = os.path.join(app.instance_path, 'docs')

@app.route('/')
def home():
    try:
        f_names = file_server.get_pdf_names(doc_path)
        return render_template("home.html", names = f_names)
    except Exception as e:
        print(f"Error: {str(e)}")
        abort(404)
        

@app.route('/upload', methods = ['POST'])   
def upload():   
    if request.method == 'POST' and 'file' in request.files:
        f = request.files['file']
        if f.filename == '':
            return render_template("home.html", name = "No file selected")
        # create the folders when setting up app
        os.makedirs(os.path.join(app.instance_path, 'docs'), exist_ok=True)

        # # when saving the file
        file_path = os.path.join(doc_path, secure_filename(f.filename))
        f.save(file_path)
        file_names = file_server.get_pdf_names(doc_path)
        
        return render_template("home.html", names = file_names)

@app.route('/download/<name>', methods=['GET', 'POST'])
def download(name):
    try: 
        path = os.path.join(doc_path, secure_filename(name))
        return send_from_directory('pdfs', name, as_attachment=True)
    except Exception as e:        
        print(f"Error: {str(e)}")
        abort(404)   
                
@app.route('/config', methods=['GET', 'POST'])
def config():
    try:
        return render_template('config.html')
    except Exception as e:
        print(f"Error: {str(e)}")
        abort(404)   
        
if __name__ == "__main__":
    app.run(debug=True)
