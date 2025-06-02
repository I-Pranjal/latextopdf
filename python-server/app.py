from flask import Flask, request, send_file, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Full path to pdflatex executable
PDFLATEX_PATH = r"C:\Users\12345\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    data = request.get_json()
    latex_code = data.get('latexCode')

    if not latex_code:
        return jsonify({'error': 'Missing LaTeX code'}), 400

    file_id = str(uuid.uuid4())
    tex_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.tex')
    pdf_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.pdf')

    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    try:
        subprocess.run([PDFLATEX_PATH, '-output-directory', UPLOAD_FOLDER, tex_path],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return send_file(pdf_path, as_attachment=True)
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to compile LaTeX'}), 500
    finally:
        # Cleanup auxiliary files
        for ext in ['.aux', '.log', '.tex']:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, f'{file_id}{ext}'))
            except FileNotFoundError:
                pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
