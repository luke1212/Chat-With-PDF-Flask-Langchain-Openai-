from flask import *
import file_server
import open_ai
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

doc_path = os.path.join(app.instance_path, 'docs')

@app.route('/')
def home():
    try:
        os.makedirs(doc_path,exist_ok=True)     
        f_names = file_server.get_pdf_names(doc_path)
        return render_template("home.html", names = f_names)    
    except Exception as e:
        print(f"Error: {str(e)}")
        abort(404)
        

@app.route('/upload', methods = ['POST'])   
def upload_files():
    try:   
        if request.method == 'POST' and 'file' in request.files:
            f = request.files['file']
            
            if f.filename == '':               
                os.makedirs(doc_path,exist_ok=True)
                f_names = file_server.get_pdf_names(doc_path)
                return render_template("home.html", names = f_names)
            
            # create the folders when setting up app
            os.makedirs(doc_path, exist_ok=True)

            # # when saving the file
            file_path = os.path.join(doc_path, secure_filename(f.filename))
            f.save(file_path)
            file_names = file_server.get_pdf_names(doc_path)
            return render_template("home.html", names = file_names)
    except Exception as e:        
        print(f"Error: {str(e)}")
        abort(404)  

@app.route('/download/<name>', methods=['GET', 'POST'])
def download(name):
    try: 
        return send_from_directory(doc_path, name, as_attachment=True)
    except Exception as e:        
        print(f"Error: {str(e)}")
        abort(404)   

@app.route('/delete/<name>', methods=['GET', 'POST'])
def delete(name):
    try: 
        path = os.path.join(doc_path, secure_filename(name))
        file_server.delete_file(path)
        f_names = file_server.get_pdf_names(doc_path)
        return render_template("home.html", names = f_names)
    except Exception as e:        
        print(f"Error: {str(e)}")
        abort(404)  
               
@app.route('/chathistory', methods=['GET', 'POST'])
def chathistory():
    try:
        return render_template('chat_history.html')
    except Exception as e:
        print(f"Error: {str(e)}")
        abort(404)   

@app.route("/get", methods=["GET", "POST"])
def get_bot_response():
    userText = request.form["msg"]
    response = open_ai.get_pdf_info(userText, request.form["file_name"]) 
    return response

@app.route('/selected_file/<name>', methods=['GET', 'POST'])
def selected_file(name):
    try:
        f_names = file_server.get_pdf_names(doc_path)
        return render_template('home.html', selected_file_name = name, names = f_names)
    except Exception as e:
        print(f"Error: {str(e)}")
        abort(404)
        
if __name__ == "__main__":
    app.run(debug=True)
