# OCR Application Integration Guide

This guide provides detailed information on integrating the AI Agent OCR application with other systems and extending its functionality.

## API Reference

The OCR application exposes a REST API that can be used to integrate with other applications.

### Base URL

When running locally with Docker Compose: `http://localhost:5000`  
When using Docker Model Runner: `http://localhost:5000`

### Authentication

Currently, the API does not require authentication. For production deployment, you should implement an authentication mechanism such as JWT or API keys.

### Endpoints

#### Process Document

```
POST /api/ocr
```

**Request:**

Content-Type: multipart/form-data

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| file | File | Yes | The document or image to process |
| detectTables | Boolean | No | Enable table detection (default: true) |
| detectHandwriting | Boolean | No | Enable handwriting recognition (default: true) |
| multiLanguage | Boolean | No | Enable multi-language support (default: false) |
| preserveFormatting | Boolean | No | Preserve document formatting (default: true) |
| detectDiagrams | Boolean | No | Enable diagram detection (default: true) |

**Response:**

```json
{
  "success": true,
  "documentId": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

#### List Documents

```
GET /api/documents
```

**Response:**

```json
[
  {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "filename": "example.pdf",
    "createdAt": "2025-04-01T12:34:56.789Z",
    "hasTable": true,
    "hasDiagram": false,
    "thumbnailUrl": "/api/documents/f47ac10b-58cc-4372-a567-0e02b2c3d479/thumbnail"
  }
]
```

#### Get Document

```
GET /api/documents/{documentId}
```

**Response:**

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "filename": "example.pdf",
  "text": "Extracted document text...",
  "tables": [
    {
      "id": "table-1",
      "html": "<table>...</table>",
      "bbox": [10, 20, 300, 150]
    }
  ],
  "diagrams": [
    {
      "id": "diagram-1",
      "type": "flowchart",
      "mermaidCode": "flowchart TD\n    A[Start] --> B[Process]\n    B --> C[End]"
    }
  ],
  "hasTable": true,
  "hasDiagram": true,
  "imageUrl": "/api/documents/f47ac10b-58cc-4372-a567-0e02b2c3d479/image",
  "thumbnailUrl": "/api/documents/f47ac10b-58cc-4372-a567-0e02b2c3d479/thumbnail",
  "createdAt": "2025-04-01T12:34:56.789Z",
  "metadata": {
    "pageCount": 1,
    "languages": ["eng"],
    "confidence": 95.5
  }
}
```

#### Get Document Image

```
GET /api/documents/{documentId}/image
```

Returns the original document image.

#### Get Document Thumbnail

```
GET /api/documents/{documentId}/thumbnail
```

Returns a thumbnail image of the document.

#### Export Document

```
GET /api/documents/{documentId}/export?format={format}
```

Exports the document in the specified format (PDF, DOCX, TXT, JSON).

#### Get Diagram

```
GET /api/diagrams/{diagramId}/render
```

Returns the Mermaid.js code for a specific diagram.

#### Get/Update Settings

```
GET /api/settings
PUT /api/settings
```

Gets or updates application settings.

## Docker Integration

### Using with Docker Compose

The application includes a `docker-compose.yml` file that sets up all required services. To use it:

```bash
docker-compose up -d
```

This will start the following services:
- Frontend: React application on port 3000
- API: Flask backend on port 5000
- OCR Engine: OCR processing service on port 6000
- MongoDB: Database on port 27017

### Custom Docker Configuration

You can customize the Docker configuration by creating a `.env` file with the following variables:

```
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=secure_password
OCR_ENGINE_URL=http://ocr-engine:6000
API_URL=http://api:5000
ROOT_URL=http://localhost:3000
```

## Extending the OCR Engine

### Adding New Languages

To add support for additional languages:

1. Install the required Tesseract language packs in the OCR engine Dockerfile:
   ```dockerfile
   RUN apt-get update && apt-get install -y \
       tesseract-ocr \
       tesseract-ocr-eng \
       tesseract-ocr-fra \
       tesseract-ocr-deu \
       # Add more language packs here
   ```

2. Update the language options in the OCR engine code:
   ```python
   # Configure language
   lang = 'eng'
   if options['multi_language']:
       lang = 'eng+fra+deu+spa+ita+[new_language_code]'
   ```

### Adding New Diagram Types

To add support for additional diagram types:

1. Update the diagram patterns in the OCR engine code:
   ```python
   DIAGRAM_PATTERNS = {
       'flowchart': r'(?i)(flowchart|flow\s+chart|flow\s+diagram)',
       'sequence': r'(?i)(sequence\s+diagram|seq\s+diagram)',
       # Add new diagram type patterns here
       'newDiagramType': r'(?i)(new\s+diagram\s+pattern)'
   }
   ```

2. Add a generator function for the new diagram type:
   ```python
   def generate_mermaid_diagram(text, diagram_type):
       # Existing code...
       
       elif diagram_type == 'newDiagramType':
           # Generate Mermaid.js code for the new diagram type
           mermaid_code = "newDiagramType\n"
           # Extract relevant elements and add to the diagram
           # ...
           return mermaid_code
   ```

### Improving OCR Accuracy

To improve OCR accuracy for specific use cases:

1. Add custom preprocessing steps in the OCR engine:
   ```python
   # Apply custom preprocessing
   # Example: Adaptive thresholding for low contrast documents
   if options.get('adaptive_threshold', False):
       thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
   ```

2. Use domain-specific post-processing:
   ```python
   # Apply domain-specific corrections
   # Example: Fix common OCR errors in medical documents
   if options.get('domain') == 'medical':
       text = fix_medical_terminology(text)
   ```

## Frontend Integration

### Embedding in Other Web Applications

You can embed the OCR application in other web applications using an iframe:

```html
<iframe 
  src="http://localhost:3000" 
  width="100%" 
  height="600px" 
  frameborder="0"
></iframe>
```

For deeper integration, you can use the API directly and build your own UI on top of it.

### Customizing the UI

The frontend is built with React and Material-UI. To customize the UI:

1. Clone the repository
2. Modify the components in the `frontend/src` directory
3. Rebuild the frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

## Integration with AI Agents

### Using with Model Context Protocol (MCP)

The OCR application supports integration with the Model Context Protocol (MCP), allowing AI agents to interact with documents and extracted content.

#### Example MCP Integration

```python
from mcp_client import MCPClient

# Initialize MCP client
mcp_client = MCPClient()

# Register OCR capabilities
mcp_client.register_capability(
    "document_ocr",
    endpoint="http://localhost:5000/api/ocr",
    input_schema={"file": "binary", "options": "object"},
    output_schema={"documentId": "string", "text": "string"}
)

# Use OCR in an agent workflow
async def process_document(document_path):
    # Process document with OCR
    ocr_result = await mcp_client.invoke_capability(
        "document_ocr",
        {"file": open(document_path, "rb"), "options": {"detectDiagrams": True}}
    )
    
    # Add to agent context
    context_id = await mcp_client.add_to_context({
        "document": {
            "id": ocr_result["documentId"],
            "text": ocr_result["text"],
            "source": document_path
        }
    })
    
    return context_id
```

### Creating Autonomous Document Processing Workflows

You can create autonomous document processing workflows by combining the OCR application with AI agents:

1. **Document Ingestion Agent**: Monitors for new documents and sends them to the OCR service
2. **Classification Agent**: Categorizes processed documents based on content
3. **Extraction Agent**: Extracts specific information based on document type
4. **Workflow Agent**: Triggers appropriate actions based on extracted information

#### Example Workflow Architecture

```
Document Source → Ingestion Agent → OCR App → Classification Agent → Extraction Agent → Workflow Agent → Business Systems
```

## Security Considerations

### Data Protection

- All uploaded documents are stored in the `uploads` directory
- Processed results are stored in MongoDB
- For sensitive documents, consider implementing:
  - Document encryption at rest
  - Secure deletion policies
  - Access controls and audit logging

### API Security

For production deployments, implement:

1. API authentication using JWT or API keys
2. Rate limiting to prevent abuse
3. Input validation to prevent injection attacks
4. HTTPS for all communication

## Performance Tuning

### Scaling the OCR Engine

To handle higher loads:

1. Deploy multiple OCR engine instances
2. Use a load balancer to distribute requests
3. Implement a task queue for asynchronous processing

### Optimizing MongoDB

1. Create appropriate indexes for frequently queried fields
2. Configure MongoDB for your specific workload
3. Implement a caching layer for frequent requests

## Troubleshooting

### Common Issues

1. **OCR Quality Problems**
   - Try different preprocessing options
   - Ensure input images have sufficient resolution and contrast
   - Check language settings match the document language

2. **Performance Issues**
   - Monitor resource usage across services
   - Check for memory leaks in long-running services
   - Optimize database queries

3. **Integration Problems**
   - Verify API endpoints and authentication
   - Check network connectivity between services
   - Validate request and response formats

## Support and Contribution

### Getting Help

- Open issues on the GitHub repository
- Check the wiki for additional documentation
- Join the community discussion forum

### Contributing

- Fork the repository
- Make your changes
- Submit a pull request with a clear description of changes
- Follow the code style and testing guidelines

### License

This project is licensed under the MIT License - see the LICENSE file for details.