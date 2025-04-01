import os
import uuid
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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Diagram patterns for detection
DIAGRAM_PATTERNS = {
    'flowchart': r'(?i)(flowchart|flow\s+chart|flow\s+diagram)',
    'sequence': r'(?i)(sequence\s+diagram|seq\s+diagram)',
    'classDiagram': r'(?i)(class\s+diagram)',
    'stateDiagram': r'(?i)(state\s+diagram|state\s+machine)',
    'entityRelationship': r'(?i)(entity\s+relationship|er\s+diagram)',
    'gantt': r'(?i)(gantt\s+chart|timeline)',
    'pieChart': r'(?i)(pie\s+chart)'     
}

@app.route('/process', methods=['POST'])
def process_image():
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
    
    # Save uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
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
        
        # Prepare the response
        result = {
            'text': text,
            'tables': tables,
            'diagrams': diagrams,
            'pageCount': 1,  # For multi-page documents, this would be calculated
            'languages': [lang.split('+')[0]],  # Primary language
            'confidence': calculate_confidence(text)
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def detect_tables(img, thresh):
    """Detect tables in the image and return structured data"""
    # This is a simplified table detection algorithm
    # In a real application, you would use more advanced techniques
    
    # Find contours in the thresholded image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    tables = []
    for i, contour in enumerate(contours):
        # Filter contours based on area and aspect ratio
        area = cv2.contourArea(contour)
        if area < 10000:  # Minimum area threshold
            continue
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        
        # Tables usually have an aspect ratio close to 1 or wider
        if 0.5 <= aspect_ratio <= 5:
            # Extract the potential table region
            table_region = thresh[y:y+h, x:x+w]
            
            # Apply OCR with table structure detection
            table_data = pytesseract.image_to_data(table_region, output_type=pytesseract.Output.DICT)
            
            # Process table data and convert to HTML format
            table_html = convert_table_data_to_html(table_data)
            
            if table_html:  # If a valid table was detected
                table_id = str(uuid.uuid4())
                tables.append({
                    'id': table_id,
                    'html': table_html,
                    'bbox': [x, y, w, h]
                })
    
    return tables

def convert_table_data_to_html(table_data):
    """Convert OCR table data to HTML format"""
    # This is a simplified version - in a real app, you'd implement more robust table structure detection
    
    # Group text by lines
    lines = {}
    for i in range(len(table_data['text'])):
        if int(table_data['conf'][i]) > 0:  # Filter out low confidence results
            line_num = table_data['block_num'][i]
            if line_num not in lines:
                lines[line_num] = []
            lines[line_num].append(table_data['text'][i])
    
    # If we have at least 2 lines, assume it's a table
    if len(lines) >= 2:
        html = '<table border="1" cellpadding="3" cellspacing="0">'
        
        # First line is header
        html += '<thead><tr>'
        for cell in lines[min(lines.keys())]:
            html += f'<th>{cell}</th>'
        html += '</tr></thead>'
        
        # Remaining lines are data
        html += '<tbody>'
        for line_num in sorted(lines.keys())[1:]:
            html += '<tr>'
            for cell in lines[line_num]:
                html += f'<td>{cell}</td>'
            html += '</tr>'
        html += '</tbody>'
        
        html += '</table>'
        return html
    
    return None

def detect_diagrams(text):
    """Detect potential diagrams in the text and generate Mermaid.js code"""
    diagrams = []
    
    # Check for diagram patterns in the text
    for diagram_type, pattern in DIAGRAM_PATTERNS.items():
        if re.search(pattern, text):
            # Generate a simple Mermaid.js diagram based on detected type
            mermaid_code = generate_mermaid_diagram(text, diagram_type)
            if mermaid_code:
                diagram_id = str(uuid.uuid4())
                diagrams.append({
                    'id': diagram_id,
                    'type': diagram_type,
                    'mermaidCode': mermaid_code
                })
    
    return diagrams

def generate_mermaid_diagram(text, diagram_type):
    """Generate Mermaid.js code based on detected text and diagram type"""
    # This is a simplified implementation that generates basic diagrams
    # In a real application, you would use more advanced NLP to parse the diagram structure
    
    if diagram_type == 'flowchart':
        # Extract potential nodes and connections from text
        nodes = re.findall(r'\b([A-Z][\w\s]*?)\b', text)
        nodes = list(set([node.strip() for node in nodes if len(node) > 3]))[:5]  # Limit to 5 nodes
        
        if len(nodes) >= 2:
            mermaid_code = "flowchart TD\n"
            # Add nodes
            for i, node in enumerate(nodes):
                mermaid_code += f"    A{i}[{node}]\n"
            
            # Add connections
            for i in range(len(nodes) - 1):
                mermaid_code += f"    A{i} --> A{i+1}\n"
            
            return mermaid_code
    
    elif diagram_type == 'sequence':
        # Extract potential actors from text
        actors = re.findall(r'\b([A-Z][\w\s]*?)\b', text)
        actors = list(set([actor.strip() for actor in actors if len(actor) > 3]))[:3]  # Limit to 3 actors
        
        if len(actors) >= 2:
            mermaid_code = "sequenceDiagram\n"
            # Add actors
            for actor in actors:
                mermaid_code += f"    participant {actor}\n"
            
            # Add some basic interactions
            for i in range(len(actors) - 1):
                mermaid_code += f"    {actors[i]}->>+{actors[i+1]}: Request\n"
                mermaid_code += f"    {actors[i+1]}-->>-{actors[i]}: Response\n"
            
            return mermaid_code
    
    elif diagram_type == 'classDiagram':
        # Extract potential class names from text
        classes = re.findall(r'\b([A-Z][\w]*?)\b', text)
        classes = list(set([cls for cls in classes if len(cls) > 2]))[:3]  # Limit to 3 classes
        
        if len(classes) >= 2:
            mermaid_code = "classDiagram\n"
            # Add classes and relationships
            for cls in classes:
                mermaid_code += f"    class {cls}\n"
            
            # Add inheritance or composition relationship
            mermaid_code += f"    {classes[0]} <|-- {classes[1]}\n"
            
            return mermaid_code
    
    # Add other diagram types as needed
    
    return None

def calculate_confidence(text):
    """Calculate a simple confidence score for the OCR result"""
    if not text:
        return 0
    
    # Calculate the ratio of alphanumeric characters to total length
    alpha_numeric = sum(c.isalnum() or c.isspace() for c in text)
    total_length = len(text)
    
    if total_length == 0:
        return 0
    
    return (alpha_numeric / total_length) * 100

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
