import React, { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Divider from '@mui/material/Divider';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import axios from 'axios';

const Settings = () => {
  const [settings, setSettings] = useState({
    defaultLanguage: 'eng',
    enableHandwriting: true,
    enableTableDetection: true,
    preserveFormatting: true,
    maxFileSize: 10,
    defaultExportFormat: 'PDF'
  });
  
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/settings');
        setSettings(response.data);
      } catch (error) {
        console.error('Error fetching settings:', error);
        setSnackbar({
          open: true,
          message: 'Failed to load settings',
          severity: 'error'
        });
      }
    };

    fetchSettings();
  }, []);

  const handleChange = (event) => {
    const { name, value, checked } = event.target;
    setSettings({
      ...settings,
      [name]: event.target.type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await axios.put('http://localhost:5000/api/settings', settings);
      setSnackbar({
        open: true,
        message: 'Settings saved successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      setSnackbar({
        open: true,
        message: 'Failed to save settings',
        severity: 'error'
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Application Settings
        </Typography>

        <Paper sx={{ p: 3, mt: 3 }}>
          <form onSubmit={handleSubmit}>
            <Typography variant="h6" gutterBottom>OCR Settings</Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="default-language-label">Default Language</InputLabel>
              <Select
                labelId="default-language-label"
                name="defaultLanguage"
                value={settings.defaultLanguage}
                onChange={handleChange}
                label="Default Language"
              >
                <MenuItem value="eng">English</MenuItem>
                <MenuItem value="fra">French</MenuItem>
                <MenuItem value="deu">German</MenuItem>
                <MenuItem value="spa">Spanish</MenuItem>
                <MenuItem value="ita">Italian</MenuItem>
                <MenuItem value="jpn">Japanese</MenuItem>
                <MenuItem value="kor">Korean</MenuItem>
                <MenuItem value="chi_sim">Chinese (Simplified)</MenuItem>
                <MenuItem value="chi_tra">Chinese (Traditional)</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableHandwriting}
                    onChange={handleChange}
                    name="enableHandwriting"
                  />
                }
                label="Enable Handwriting Recognition"
              />
            </Box>

            <Box sx={{ mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableTableDetection}
                    onChange={handleChange}
                    name="enableTableDetection"
                  />
                }
                label="Enable Table Detection"
              />
            </Box>

            <Box sx={{ mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.preserveFormatting}
                    onChange={handleChange}
                    name="preserveFormatting"
                  />
                }
                label="Preserve Document Formatting"
              />
            </Box>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom>General Settings</Typography>

            <FormControl fullWidth margin="normal">
              <TextField
                label="Maximum File Size (MB)"
                type="number"
                name="maxFileSize"
                value={settings.maxFileSize}
                onChange={handleChange}
                inputProps={{ min: 1, max: 50 }}
              />
            </FormControl>

            <FormControl fullWidth margin="normal">
              <InputLabel id="default-export-format-label">Default Export Format</InputLabel>
              <Select
                labelId="default-export-format-label"
                name="defaultExportFormat"
                value={settings.defaultExportFormat}
                onChange={handleChange}
                label="Default Export Format"
              >
                <MenuItem value="PDF">PDF</MenuItem>
                <MenuItem value="DOCX">DOCX</MenuItem>
                <MenuItem value="TXT">TXT</MenuItem>
                <MenuItem value="JSON">JSON</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
              <Button type="submit" variant="contained" color="primary">
                Save Settings
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Settings;