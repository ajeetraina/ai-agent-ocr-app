#!/usr/bin/env node

/**
 * Docker Model Runner Script for OCR Application
 * 
 * This script demonstrates how to use Docker Model Runner to interact with the OCR application.
 * It provides a command-line interface for processing images and documents via the containerized app.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Parse command-line arguments
const args = process.argv.slice(2);
const command = args[0];

// Define the Docker container details
const containerName = 'ocr-app';
const containerVersion = 'latest';

// Help message
function showHelp() {
  console.log(`
  OCR Application - Docker Model Runner Integration
  ================================================

  Commands:
    --help                Show this help message
    --process-image PATH  Process an image or document at the specified path
    --list-documents      List all processed documents
    --get-document ID     View a specific document by ID
    --settings            View or modify application settings

  Examples:
    node model-runner.js --process-image ./sample.jpg
    node model-runner.js --list-documents
    node model-runner.js --get-document d8f7e3c1-5b62-4a8e-9e3d-8f7e3c1d8f7e
  `);
}

// Process an image using the OCR container
async function processImage(imagePath) {
  try {
    console.log(`Processing image: ${imagePath}`);
    
    // Check if file exists
    if (!fs.existsSync(imagePath)) {
      console.error(`Error: File not found at ${imagePath}`);
      process.exit(1);
    }
    
    // Get absolute path
    const absolutePath = path.resolve(imagePath);
    
    // Execute Docker Model Runner command
    console.log('Sending to OCR engine...');
    const output = execSync(`docker run -v "${absolutePath}:/app/image" ${containerName}:${containerVersion} python /app/ocr-engine/app.py /app/image`);
    
    console.log('\nProcessing complete!\n');
    console.log(output.toString());
  } catch (error) {
    console.error('Error processing image:', error.message);
    process.exit(1);
  }
}

// Main function
async function main() {
  if (args.length === 0 || command === '--help') {
    showHelp();
    return;
  }

  switch (command) {
    case '--process-image':
      const imagePath = args[1];
      if (!imagePath) {
        console.error('Error: Please provide a path to an image');
        process.exit(1);
      }
      await processImage(imagePath);
      break;
      
    case '--list-documents':
      console.log('Listing all processed documents...');
      // This would be implemented to connect to the running container and fetch document list
      console.log('Feature not implemented in this demo script.');
      break;
      
    case '--get-document':
      const documentId = args[1];
      if (!documentId) {
        console.error('Error: Please provide a document ID');
        process.exit(1);
      }
      console.log(`Fetching document with ID: ${documentId}`);
      // This would be implemented to connect to the running container and fetch a specific document
      console.log('Feature not implemented in this demo script.');
      break;
      
    case '--settings':
      console.log('Application settings:');
      // This would be implemented to view or modify settings
      console.log('Feature not implemented in this demo script.');
      break;
      
    default:
      console.error(`Unknown command: ${command}`);
      showHelp();
      process.exit(1);
  }
}

// Execute the main function
main();