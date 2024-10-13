import React, { useState, ChangeEvent, FormEvent } from "react";
import axios from "axios";
import './ImageUpload.css';

interface NutritionData {
  calories: number;
  fat: number;
  saturatedFat: number;
  carbohydrate: number;
  sugar: number;
  dietaryFiber: number;
  protein: number;
  cholesterol: number;
  sodium: number;
}

interface UploadResponse {
  data: NutritionData;
}

const ImageUpload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files ? e.target.files[0] : null;
    setSelectedFile(file);
    setNutritionData(null); // Reset data when a new file is selected
    setError(null); // Reset error when a new file is selected
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
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
      // Send the image to the backend API
      const response = await axios.post<UploadResponse>("http://localhost:8000/upload-image/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Extract the nutrition data from the response
      const { data } = response.data;
      setNutritionData(data);
    } catch (error) {
      setError("Failed to fetch nutritional information. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (nutritionData) {
      const { name, value } = e.target;
      setNutritionData({
        ...nutritionData,
        [name]: Number(value), // Update the nutrition data state
      });
    }
  };

  const handleSave = () => {
    setIsEditing(false);
    console.log("Updated Nutrition Data:", nutritionData); // You can send this to the backend if needed
  };

  return (
    <div className="image-upload-container">
      <h2>Upload an Image to Get Nutritional Information</h2>
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

      {/* Display nutrition data */}
      {nutritionData && (
        <div className="nutrition-label">
          <h3>Nutrition Facts</h3>
          <form className="nutrition-form">
            {Object.entries(nutritionData).map(([key, value]) => (
              <div className="nutrition-item" key={key}>
                <label>{key.charAt(0).toUpperCase() + key.slice(1)}:</label>
                <input
                  type="number"
                  name={key}
                  value={value}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                />
              </div>
            ))}
          </form>

          <button onClick={() => setIsEditing(!isEditing)}>
            {isEditing ? "Cancel Edit" : "Edit"}
          </button>

          {isEditing && <button onClick={handleSave}>Save</button>}
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
