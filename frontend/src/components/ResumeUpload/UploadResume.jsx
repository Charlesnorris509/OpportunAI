import React, { useState } from "react";
import { Box, Typography, Button, LinearProgress, TextField } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

const UploadResume = () => {
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const allowedExtensions = ["pdf", "doc", "docx"];
      const fileExtension = selectedFile.name.split(".").pop().toLowerCase();
      if (allowedExtensions.includes(fileExtension)) {
        setFile(selectedFile);
        setError("");
      } else {
        setError("Only PDF, DOC, and DOCX files are allowed.");
      }
    }
  };

  const handleUpload = () => {
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    // Simulated upload progress
    const uploadInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(uploadInterval);
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };

  return (
    <Box
      sx={{
        maxWidth: 600,
        margin: "auto",
        textAlign: "center",
        padding: 4,
        boxShadow: 3,
        borderRadius: 2,
        backgroundColor: "#ffffff",
      }}
    >
      <Typography variant="h5" sx={{ mb: 2 }}>
        Upload Your Resume
      </Typography>
      <input
        accept=".pdf,.doc,.docx"
        style={{ display: "none" }}
        id="upload-button"
        type="file"
        onChange={handleFileChange}
      />
      <label htmlFor="upload-button">
        <Button
          variant="outlined"
          component="span"
          startIcon={<CloudUploadIcon />}
          sx={{ mb: 2 }}
        >
          Select Resume
        </Button>
      </label>
      {file && (
        <Typography variant="body1" sx={{ mb: 2 }}>
          Selected File: {file.name}
        </Typography>
      )}
      {error && (
        <Typography variant="body2" color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      <Button
        variant="contained"
        color="primary"
        disabled={uploadProgress > 0 && uploadProgress < 100}
        onClick={handleUpload}
      >
        Upload
      </Button>
      {uploadProgress > 0 && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={uploadProgress} />
          <Typography variant="body2" sx={{ mt: 1 }}>
            Upload Progress: {uploadProgress}%
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default UploadResume;
