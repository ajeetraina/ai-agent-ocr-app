import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pymongo
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Database setup
client = MongoClient('mongodb://db:27017/')
db = client['ocr_app']
documents_collection = db['documents']
settings_collection = db['settings']

# Initialize default settings if not exists
if settings_collection.count_documents({}) == 0:
    default_settings = {
        'defaultLanguage': 'eng',
        'enableHandwriting': True,
        'enableTableDetection': True,
        'preserveFormatting': True,
        'maxFileSize': 10,  # MB
        'defaultExportFormat': 'PDF',
        'enableDiagramDetection': True  # Added for Mermaid.js support
    }
    settings_collection.insert_one(default_settings)

# OCR Engine service URL
OCR_ENGINE_URL = os.environ.get('OCR_ENGINE_URL', 'http://ocr-engine:6000')

@app.route('/api/ocr', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get OCR options from request
    options = {
        'detectTables': request.form.get('detectTables', 'true').lower() == 'true',
        'detectHandwriting': request.form.get('detectHandwriting', 'true').lower() == 'true',
        'multiLanguage': request.form.get('multiLanguage', 'false').lower() == 'true',
        'preserveFormatting': request.form.get('preserveFormatting', 'true').lower() == 'true',
        'detectDiagrams': request.form.get('detectDiagrams', 'true').lower() == 'true'  # Added for Mermaid.js
    }
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, f"{document_id}_{filename}")
    file.save(file_path)
    
    # Send to OCR Engine
    try:
        files = {'file': open(file_path, 'rb')}
        response = requests.post(
            f"{OCR_ENGINE_URL}/process",
            files=files,
            data=options
        )
        
        if response.status_code != 200:
            return jsonify({'error': 'OCR processing failed'}), 500
        
        ocr_result = response.json()
        
        # Save to database
        document_data = {
            'id': document_id,
            'filename': filename,
            'text': ocr_result.get('text', ''),
            'tables': ocr_result.get('tables', []),
            'diagrams': ocr_result.get('diagrams', []),  # Added for Mermaid.js
            'hasDiagram': len(ocr_result.get('diagrams', [])) > 0,  # Added for Mermaid.js
            'hasTable': len(ocr_result.get('tables', [])) > 0,
            'imageUrl': f"/api/documents/{document_id}/image",
            'thumbnailUrl': f"/api/documents/{document_id}/thumbnail",
            'createdAt': datetime.now(),
            'metadata': {
                'pageCount': ocr_result.get('pageCount', 1),
                'languages': ocr_result.get('languages', ['eng']),
                'confidence': ocr_result.get('confidence', 0)
            }
        }
        
        documents_collection.insert_one(document_data)
        
        return jsonify({
            'success': True,
            'documentId': document_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    documents = list(documents_collection.find({}, {'_id': 0}).sort('createdAt', pymongo.DESCENDING))
    # Convert datetime objects to strings for JSON serialization
    for doc in documents:
        doc['createdAt'] = doc['createdAt'].isoformat()
    return jsonify(documents)

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    document = documents_collection.find_one({'id': document_id}, {'_id': 0})
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Convert datetime objects to strings for JSON serialization
    document['createdAt'] = document['createdAt'].isoformat()
    return jsonify(document)

@app.route('/api/documents/<document_id>/image', methods=['GET'])
def get_document_image(document_id):
    document = documents_collection.find_one({'id': document_id})
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Find the original image file
    filename = document['filename']
    file_path = os.path.join(UPLOAD_FOLDER, f"{document_id}_{filename}")
    
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return jsonify({'error': 'Image file not found'}), 404

@app.route('/api/documents/<document_id>/thumbnail', methods=['GET'])
def get_document_thumbnail(document_id):
    document = documents_collection.find_one({'id': document_id})
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # For simplicity, we're returning the original image as thumbnail
    # In a production environment, you would generate and store actual thumbnails
    filename = document['filename']
    file_path = os.path.join(UPLOAD_FOLDER, f"{document_id}_{filename}")
    
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return jsonify({'error': 'Thumbnail not found'}), 404

@app.route('/api/documents/<document_id>/export', methods=['GET'])
def export_document(document_id):
    format = request.args.get('format', 'PDF')
    document = documents_collection.find_one({'id': document_id})
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # For the demo, we'll just return a simple text file with the OCR'd text
    # In a real application, you would generate proper PDF, DOCX, etc.
    text_content = document.get('text', '')
    
    temp_file_path = os.path.join(PROCESSED_FOLDER, f"{document_id}_export.txt")
    with open(temp_file_path, 'w') as f:
        f.write(text_content)
    
    return send_file(temp_file_path, as_attachment=True, download_name=f"{document['filename'].split('.')[0]}.txt")

@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = settings_collection.find_one({}, {'_id': 0})
    return jsonify(settings)

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    new_settings = request.json
    settings_collection.update_one({}, {'$set': new_settings})
    return jsonify({'success': True})

# Endpoint for diagram processing with Mermaid.js
@app.route('/api/diagrams/<diagram_id>/render', methods=['GET'])
def render_diagram(diagram_id):
    document = documents_collection.find_one({'diagrams.id': diagram_id}, {'_id': 0})
    if not document:
        return jsonify({'error': 'Diagram not found'}), 404
    
    for diagram in document.get('diagrams', []):
        if diagram.get('id') == diagram_id:
            return jsonify({
                'mermaidCode': diagram.get('mermaidCode', ''),
                'type': diagram.get('type', 'flowchart')
            })
    
    return jsonify({'error': 'Diagram not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
