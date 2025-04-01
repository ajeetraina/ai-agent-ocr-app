import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import Grid from '@mui/material/Grid';
import { useDropzone } from 'react-dropzone';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const Upload = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [options, setOptions] = useState({
    detectTables: true,
    detectHandwriting: true,
    multiLanguage: false,
    preserveFormatting: true
  });
  const navigate = useNavigate();

  const onDrop = (acceptedFiles) => {
    setFiles(acceptedFiles.map(file => Object.assign(file, {
      preview: URL.createObjectURL(file)
    })));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', files[0]);
    Object.keys(options).forEach(key => {
      formData.append(key, options[key]);
    });

    try {
      // Replace with your actual API endpoint
      const response = await axios.post('http://localhost:5000/api/ocr', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Navigate to document view with the document ID
      navigate(`/documents/${response.data.documentId}`);
    } catch (error) {
      console.error('Error uploading file:', error);
      // Handle error state
    } finally {
      setUploading(false);
    }
  };

  const handleOptionChange = (event) => {
    setOptions({
      ...options,
      [event.target.name]: event.target.checked
    });
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Upload Documents for OCR
        </Typography>

        <Paper
          {...getRootProps()}
          sx={{
            p: 3,
            mt: 3,
            textAlign: 'center',
            backgroundColor: isDragActive ? '#e3f2fd' : 'white',
            border: '2px dashed #1976d2',
            cursor: 'pointer'
          }}
        >
          <input {...getInputProps()} />
          <CloudUploadIcon sx={{ fontSize: 60, color: '#1976d2', mb: 2 }} />
          {isDragActive ? (
            <Typography>Drop the files here...</Typography>
          ) : (
            <Typography>Drag & drop files here, or click to select files</Typography>
          )}
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Supported formats: PDF, JPEG, PNG
          </Typography>
        </Paper>

        {files.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Selected File:</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              {files[0].type.includes('image') ? (
                <img
                  src={files[0].preview}
                  alt="Preview"
                  style={{ maxWidth: '100px', maxHeight: '100px', marginRight: '10px' }}
                />
              ) : (
                <Box
                  sx={{ 
                    width: '100px', 
                    height: '100px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    backgroundColor: '#f5f5f5',
                    marginRight: '10px'
                  }}
                >
                  PDF
                </Box>
              )}
              <Typography>{files[0].name}</Typography>
            </Box>
          </Box>
        )}

        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>OCR Options:</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={options.detectTables}
                    onChange={handleOptionChange}
                    name="detectTables"
                  />
                }
                label="Detect Tables"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={options.detectHandwriting}
                    onChange={handleOptionChange}
                    name="detectHandwriting"
                  />
                }
                label="Detect Handwriting"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={options.multiLanguage}
                    onChange={handleOptionChange}
                    name="multiLanguage"
                  />
                }
                label="Multi-language Support"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={options.preserveFormatting}
                    onChange={handleOptionChange}
                    name="preserveFormatting"
                  />
                }
                label="Preserve Formatting"
              />
            </Grid>
          </Grid>
        </Box>

        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            startIcon={uploading ? <CircularProgress size={24} /> : null}
          >
            {uploading ? 'Processing...' : 'Process Document'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Upload;