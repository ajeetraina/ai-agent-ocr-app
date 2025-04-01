# OCR Application Usage Guide

This guide provides detailed instructions on how to use the AI Agent OCR application.

## Getting Started

### Installation

#### Option 1: Using Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/ajeetraina/ai-agent-ocr-app.git
   cd ai-agent-ocr-app
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the web interface at http://localhost:3000

#### Option 2: Using Docker Model Runner

1. Install Docker Model Runner plugin:
   ```bash
   docker plugin install docker/model-runner
   ```

2. Pull the OCR model:
   ```bash
   docker model pull ajeetraina/ocr-app:latest
   ```

3. Run the model:
   ```bash
   docker model run --api ajeetraina/ocr-app
   ```

4. Access the API at http://localhost:5000

## Web Interface Guide

### Home Page

The home page provides an overview of the application's capabilities and quick access to key features:

- **Upload Button**: Start the document upload process
- **Gallery**: View previously processed documents
- **Settings**: Configure application preferences

### Uploading Documents

1. Click on the "Upload" button in the navigation bar or the "Get Started" button on the home page
2. Drag and drop your document onto the upload area or click to select a file
3. Configure OCR options:
   - **Detect Tables**: Enable table structure recognition
   - **Detect Handwriting**: Enable handwriting recognition
   - **Multi-language Support**: Enable support for multiple languages
   - **Preserve Formatting**: Maintain document layout
   - **Detect Diagrams**: Enable diagram detection and Mermaid.js conversion
4. Click "Process Document" to start OCR processing

### Viewing Documents

After processing, you'll be redirected to the document view page, which has several tabs:

#### Text Tab

Displays the extracted text with the original formatting preserved (if selected).

**Actions**:
- Copy text to clipboard
- Download as PDF, DOCX, or TXT

#### Original Tab

Shows the original document image for comparison with the extracted text.

#### Tables Tab

Displays any tables detected in the document. Each table is shown in HTML format, preserving the structure.

#### Diagrams Tab

Shows any diagrams detected in the document, rendered using Mermaid.js. Each diagram is interactive and can be:
- Zoomed in/out
- Exported as SVG or PNG
- Copied as Mermaid.js code

### Document Gallery

The gallery shows all previously processed documents, allowing you to:

- Search for documents by filename or content
- Sort by date, name, or document type
- Preview document thumbnails
- Click on a document to view its details

### Settings

Configure application preferences:

#### OCR Settings

- **Default Language**: Set the primary language for OCR (English, French, German, etc.)
- **Enable Handwriting Recognition**: Toggle handwriting recognition
- **Enable Table Detection**: Toggle table structure detection
- **Preserve Document Formatting**: Toggle layout preservation
- **Enable Diagram Detection**: Toggle diagram detection and conversion

#### General Settings

- **Maximum File Size**: Set the maximum file size for uploads (in MB)
- **Default Export Format**: Set the preferred export format (PDF, DOCX, TXT, JSON)

## Command Line Usage

### Using the Model Runner CLI

The application includes a command-line interface for batch processing:

```bash
node model-runner.js --process-image path/to/your/image.jpg
```

#### Available Commands

- `--help`: Show help message
- `--process-image PATH`: Process an image or document
- `--list-documents`: List all processed documents
- `--get-document ID`: View a specific document
- `--settings`: View or modify application settings

## API Usage

### Basic API Requests

#### Process a Document

```bash
curl -X POST http://localhost:5000/api/ocr \
  -F "file=@/path/to/document.jpg" \
  -F "detectTables=true" \
  -F "detectHandwriting=true" \
  -F "detectDiagrams=true"
```

#### List Documents

```bash
curl -X GET http://localhost:5000/api/documents
```

#### Get Document Details

```bash
curl -X GET http://localhost:5000/api/documents/{documentId}
```

## Working with Diagrams

The OCR application can detect various types of diagrams in documents and convert them to Mermaid.js format.

### Supported Diagram Types

- **Flowcharts**: Process flows, decision trees, etc.
- **Sequence Diagrams**: Interaction sequences between components
- **Class Diagrams**: Object-oriented class structures
- **State Diagrams**: State machines and transitions
- **Entity Relationship Diagrams**: Database schema representations
- **Gantt Charts**: Project timelines and schedules
- **Pie Charts**: Statistical distributions

### Tips for Diagram Recognition

To improve diagram detection:

1. Ensure diagrams have clear, high-contrast lines and text
2. Include diagram type labels (e.g., "Flowchart:", "Sequence Diagram:") near the diagram
3. Use standard shapes and connections in your diagrams
4. For handwritten diagrams, write text clearly and draw straight lines

### Editing Detected Diagrams

You can edit the Mermaid.js code for detected diagrams:

1. Click on the diagram in the Diagrams tab
2. Select "Edit Diagram" from the context menu
3. Modify the Mermaid.js code in the editor
4. Click "Update" to apply changes

## Best Practices

### Optimizing Document Quality

For best OCR results:

1. **Use high-resolution images**: At least 300 DPI for printed documents
2. **Ensure good contrast**: Black text on white background works best
3. **Correct alignment**: Straighten skewed documents before uploading
4. **Remove noise**: Clean up speckles, dots, or stains
5. **Use proper lighting**: When photographing documents, ensure even lighting

### Processing Large Documents

When working with large documents:

1. Split very large documents into smaller sections
2. Process sections individually for better performance
3. Use the batch processing feature for multiple files
4. Consider adjusting OCR settings for optimal speed vs. accuracy

### Handling Different Languages

When processing multilingual documents:

1. Enable "Multi-language Support" in the OCR options
2. Set the dominant language in Settings to improve accuracy
3. For languages with special characters, ensure proper encoding

## Troubleshooting

### Common Issues

#### Upload Failures

- **File too large**: Check the maximum file size setting
- **Unsupported format**: Ensure you're using JPEG, PNG, or PDF
- **Server error**: Check server logs for details

#### Poor OCR Quality

- **Low resolution**: Use higher quality images
- **Wrong language**: Check language settings
- **Complex formatting**: Try disabling "Preserve Formatting" for simpler output

#### Diagram Detection Issues

- **Diagrams not detected**: Ensure diagrams have clear structures and labels
- **Incorrect diagram type**: Add explicit type labels near your diagrams
- **Incorrect connections**: Make connection lines clearer and more distinct

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs for error messages
2. Consult the [Integration Guide](INTEGRATION_GUIDE.md) for advanced configuration
3. Open an issue on the GitHub repository
4. Check the community forum for similar issues and solutions