import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Button from '@mui/material/Button';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SchemaIcon from '@mui/icons-material/Schema';
import axios from 'axios';

// Import MermaidDiagram component
import MermaidDiagram from '../components/MermaidDiagram';

const DocumentView = () => {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/documents/${id}`);
        setDocument(response.data);
      } catch (err) {
        setError('Failed to load document. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDocument();
  }, [id]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleCopyText = () => {
    if (document && document.text) {
      navigator.clipboard.writeText(document.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = async (format) => {
    try {
      const response = await axios.get(
        `http://localhost:5000/api/documents/${id}/export`,
        {
          params: { format },
          responseType: 'blob'
        }
      );

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `document-${id}.${format.toLowerCase()}`);
      
      // Append to html link element page
      document.body.appendChild(link);
      
      // Start download
      link.click();
      
      // Clean up and remove the link
      link.parentNode.removeChild(link);
    } catch (err) {
      console.error('Error downloading document:', err);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography color="error" align="center">{error}</Typography>
        </Box>
      </Container>
    );
  }

  // Determine if we should show the Diagrams tab
  const hasDiagrams = document?.hasDiagram || (document?.diagrams && document.diagrams.length > 0);
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {document?.filename || 'Document View'}
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mb: 2 }}>
          <Button 
            variant="outlined" 
            startIcon={<ContentCopyIcon />}
            onClick={handleCopyText}
          >
            {copied ? 'Copied!' : 'Copy Text'}
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('PDF')}
          >
            PDF
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('DOCX')}
          >
            DOCX
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('TXT')}
          >
            TXT
          </Button>
        </Box>

        <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab label="Text" />
          <Tab label="Original" />
          {document?.hasTable && <Tab label="Tables" />}
          {hasDiagrams && <Tab label="Diagrams" icon={<SchemaIcon />} iconPosition="start" />}
        </Tabs>

        {activeTab === 0 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="body1" component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
              {document?.text || 'No text content available'}
            </Typography>
          </Paper>
        )}

        {activeTab === 1 && (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            {document?.imageUrl ? (
              <img 
                src={document.imageUrl} 
                alt="Original document" 
                style={{ maxWidth: '100%' }} 
              />
            ) : (
              <Typography>Original image not available</Typography>
            )}
          </Paper>
        )}

        {activeTab === 2 && document?.hasTable && (
          <Paper sx={{ p: 3 }}>
            {document?.tables && document.tables.length > 0 ? (
              document.tables.map((table, index) => (
                <Box key={index} sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>Table {index + 1}</Typography>
                  <div dangerouslySetInnerHTML={{ __html: table.html }} />
                </Box>
              ))
            ) : (
              <Typography>No tables detected</Typography>
            )}
          </Paper>
        )}

        {activeTab === 3 && hasDiagrams && (
          <Paper sx={{ p: 3 }}>
            {document?.diagrams && document.diagrams.length > 0 ? (
              document.diagrams.map((diagram, index) => (
                <Box key={index} sx={{ mb: 4 }}>
                  <MermaidDiagram 
                    code={diagram.mermaidCode} 
                    title={`${diagram.type} Diagram ${index + 1}`} 
                  />
                </Box>
              ))
            ) : (
              <Typography>No diagrams detected</Typography>
            )}
          </Paper>
        )}
      </Box>
    </Container>
  );
};

export default DocumentView;