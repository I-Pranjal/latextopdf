from flask import Flask, request, send_file, jsonify, after_this_request
import subprocess
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PDFLATEX_PATH = 'pdflatex'  # Make sure it's in your PATH or provide full path

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    data = request.get_json()
    latex_code = data.get('latexCode')

    if not latex_code:
        return jsonify({'error': 'Missing LaTeX code'}), 400

    file_id = str(uuid.uuid4())
    tex_filename = f'{file_id}.tex'
    tex_path = os.path.join(UPLOAD_FOLDER, tex_filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.pdf')

    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_code)

    try:
        result = subprocess.run(
            [PDFLATEX_PATH, '-interaction=nonstopmode', tex_filename],
            cwd=UPLOAD_FOLDER,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return jsonify({
                'error': 'Failed to compile LaTeX',
                'stdout': result.stdout,
                'stderr': result.stderr
            }), 500

        @after_this_request
        def cleanup(response):
            try:
                for filename in os.listdir(UPLOAD_FOLDER):
                    if filename.startswith(file_id):
                        os.remove(os.path.join(UPLOAD_FOLDER, filename))
            except Exception:
                pass
            return response

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
