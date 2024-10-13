import React, { useState } from "react";
import './ImageUpload.css';

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageExplanation, setImageExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files ? e.target.files[0] : null;
    setSelectedFile(file);
    setImageExplanation(null); // Reset explanation when a new file is selected
    setError(null); // Reset error when a new file is selected
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      alert("Please upload an image first.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      // Use Fetch API to send the image to the backend
      const response = await fetch("http://localhost:8000/upload-image/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload image.");
      }

      // Extract explanation data from the response
      const result = await response.json();
      const { response: raw } = result;
      setImageExplanation(raw); // Store the explanation in state
    } catch (error) {
      setError("Failed to fetch image explanation. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="image-upload-container">
      <h2>Upload an Image to Get an Explanation</h2>
      <form onSubmit={handleSubmit} className="image-upload-form">
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload and Analyze"}
        </button>
      </form>

      {/* Display loading status */}
      {loading && <div className="loading">Processing image...</div>}

      {/* Display error if something went wrong */}
      {error && <div className="error">{error}</div>}

      {/* Display image explanation */}
      {imageExplanation && (
        <div className="image-explanation">
          <h3>Image Explanation</h3>
          <p>{imageExplanation}</p>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
