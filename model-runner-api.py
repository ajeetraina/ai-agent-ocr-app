#!/usr/bin/env python3

"""
Docker Model Runner API for OCR Application

This script provides a simplified API for Docker Model Runner to interact with the OCR engine.
It wraps the OCR engine functionality with a standard API interface compatible with model-runner.
"""

import os
import sys
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import numpy as np
import cv2
import re

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# In-memory database for the model runner demo
# In a real app, this would be MongoDB as in the full application
DOCUMENTS_DB = []

# Import diagram pattern detection from OCR engine
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr-engine'))
try:
    from app import detect_tables, detect_diagrams, calculate_confidence
except ImportError:
    # Fallback implementations if import fails
    def detect_tables(img, thresh):
        return []
    
    def detect_diagrams(text):
        return []
    
    def calculate_confidence(text):
        if not text:
            return 0
        alpha_numeric = sum(c.isalnum() or c.isspace() for c in text)
        total_length = len(text)
        return (alpha_numeric / total_length) * 100 if total_length > 0 else 0

@app.route('/api/ocr', methods=['POST'])
def process_document():
    """
    Docker Model Runner compatible API endpoint for OCR processing
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get OCR options from request
    options = {
        'detect_tables': request.form.get('detectTables', 'true').lower() == 'true',
        'detect_handwriting': request.form.get('detectHandwriting', 'true').lower() == 'true',
        'multi_language': request.form.get('multiLanguage', 'false').lower() == 'true',
        'preserve_formatting': request.form.get('preserveFormatting', 'true').lower() == 'true',
        'detect_diagrams': request.form.get('detectDiagrams', 'true').lower() == 'true'
    }
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, f"{document_id}_{filename}")
    file.save(file_path)
    
    # Process the image
    try:
        # Open the image
        image = Image.open(file_path)
        
        # Convert to OpenCV format for preprocessing
        img_cv = np.array(image.convert('RGB'))
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
        
        # Apply preprocessing for better OCR results
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Configure OCR parameters
        config = '--psm 1'  # Automatic page segmentation with OSD
        if options['detect_handwriting']:
            config += ' --oem 1'  # LSTM only
        
        # Determine language
        lang = 'eng'
        if options['multi_language']:
            lang = 'eng+fra+deu+spa+ita'  # Add more languages as needed
        
        # Perform OCR
        text = pytesseract.image_to_string(thresh, lang=lang, config=config)
        
        # Detect tables if required
        tables = []
        if options['detect_tables']:
            tables = detect_tables(img_cv, thresh)
        
        # Detect diagrams if required
        diagrams = []
        if options['detect_diagrams']:
            diagrams = detect_diagrams(text)
        
        # Calculate confidence
        confidence = calculate_confidence(text)
        
        # Store document in our in-memory database
        document_data = {
            'id': document_id,
            'filename': filename,
            'text': text,
            'tables': tables,
            'diagrams': diagrams,
            'hasDiagram': len(diagrams) > 0,
            'hasTable': len(tables) > 0,
            'imageUrl': f"/api/documents/{document_id}/image",
            'thumbnailUrl': f"/api/documents/{document_id}/thumbnail",
            'createdAt': datetime.now().isoformat(),
            'confidence': confidence
        }
        
        DOCUMENTS_DB.append(document_data)
        
        # Prepare the response in Docker Model Runner compatible format
        result = {
            'text': text,
            'documentId': document_id,
            'confidence': confidence,
            'hasTable': len(tables) > 0,
            'hasDiagram': len(diagrams) > 0,
            'success': True
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """
    List all processed documents
    """
    return jsonify(DOCUMENTS_DB)

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    Get a specific document by ID
    """
    for doc in DOCUMENTS_DB:
        if doc['id'] == document_id:
            return jsonify(doc)
    
    return jsonify({'error': 'Document not found'}), 404

# Command-line interface for direct script execution with image path
if __name__ == '__main__' and len(sys.argv) > 1:
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        sys.exit(1)
    
    try:
        # Process the image directly
        image = Image.open(image_path)
        img_cv = np.array(image.convert('RGB'))
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Perform OCR
        text = pytesseract.image_to_string(thresh)
        confidence = calculate_confidence(text)
        
        # Print results to stdout
        print(f"OCR Processing Results:\n")
        print(f"Confidence: {confidence:.2f}%\n")
        print(f"Extracted Text:\n{text}")
        
        # Detect diagrams
        diagrams = detect_diagrams(text)
        if diagrams:
            print(f"\nDetected {len(diagrams)} diagrams")
            for i, diagram in enumerate(diagrams):
                print(f"\nDiagram {i+1} ({diagram['type']}):\n{diagram['mermaidCode']}")
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        sys.exit(1)

# Standard web server when run without arguments
elif __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
