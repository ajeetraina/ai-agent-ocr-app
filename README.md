# AI Agent OCR Application

An advanced OCR (Optical Character Recognition) application built collaboratively by AI agents using Docker Model Runner.

## Project Overview

This application leverages Docker Model Runner to create AI agents that collaboratively build a complete OCR system. Each agent specializes in a different aspect of the application development process.

### Key Features

- Document/image upload and processing
- Text extraction with high accuracy
- Format preservation and structure recognition
- Multi-language support
- Handwriting recognition capabilities
- Table and form extraction
- Document classification and sorting
- Searchable document repository
- Export to various formats (PDF, DOCX, TXT)

## Architecture

The application follows a modular architecture with the following components:

1. **Frontend**: Web interface for document upload and result visualization
2. **OCR Engine**: Core processing engine for text extraction
3. **Data Storage**: Document management and search functionality
4. **API Layer**: Integration between components

## AI Agent Roles

This project demonstrates collaborative development using specialized AI agents:

- **Interface Agent**: Frontend UI/UX and user experience
- **OCR Engine Agent**: Image processing and text extraction
- **Data Processing Agent**: Document storage and retrieval
- **Integration Agent**: Component coordination and API design

## Getting Started

### Prerequisites

- Docker
- Docker Model Runner plugin
- Git

### Installation

1. Clone this repository
```bash
git clone https://github.com/ajeetraina/ai-agent-ocr-app.git
cd ai-agent-ocr-app
```

2. Build and run the service containers

```
docker compose up -d --build
```


4. Access the application at http://localhost:3000

5. Try uploading a document through the API directly

```
curl -X POST http://localhost:5000/api/ocr \
  -F "file=@/Users/ajeetsraina/keyframing-01.jpg" \
  -F "detectTables=true" \
  -F "detectDiagrams=true"
```

### Result:

```
{"documentId":"18ef6f23-47fd-46c6-b74e-87be27cbe717","success":true}
```

## Development Process

This project serves as a demonstration of how AI agents can collaborate to build a complete application. Each agent contributes specific components that are then integrated into a cohesive system and containerized for deployment.

## License

MIT
