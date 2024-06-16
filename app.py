from flask import Flask, request, jsonify, render_template, send_file
from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
import subprocess

app = Flask(__name__)
summarizer = pipeline('summarization')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize')
def summarizer_page():
    return render_template('summarize.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data['text']
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
    summarized_text = summary[0]['summary_text']
    return jsonify({"summary": summarized_text})

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    summarized_text = data['summarized_text']
    signature = data['signature']
    
    # Create a PDF in memory
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    width, height = letter
    text_object = c.beginText(1 * inch, height - 1 * inch)
    text_object.setFont("Helvetica", 12)
    text_object.textLine("Summary:")
    text_object.moveCursor(0, 14)
    
    for line in summarized_text.split('\n'):
        text_object.textLine(line)
    
    text_object.moveCursor(0, 14)
    text_object.textLine("Signature:")
    text_object.moveCursor(0, 14)
    text_object.textLine(signature)
    
    c.drawText(text_object)
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='summary.pdf', mimetype='application/pdf')

def upload_file_with_zerog(file_path, rpc_url, flow_contract_address, private_key, tag_bytes):
    cmd = ["node", "-e", f"require('./zerog_helper.js').upload_file('{file_path}', '{rpc_url}', '{flow_contract_address}', '{private_key}', '{tag_bytes}')"]
    subprocess.run(cmd, check=True, shell=True)

@app.route('/upload', methods=['POST'])
def upload():
    # Retrieve file path, RPC URL, contract address, private key, and tag bytes from the form
    file_path = request.form['file_path']
    rpc_url = request.form['rpc_url']
    flow_contract_address = request.form['flow_contract_address']
    private_key = request.form['private_key']
    tag_bytes = request.form['tag_bytes']

    # Call the function to upload the file with ZeroGravity
    upload_file_with_zerog(file_path, rpc_url, flow_contract_address, private_key, tag_bytes)

    return 'File uploaded successfully!'



if __name__ == '__main__':
    app.run(debug=True)
