import { useState, useRef } from 'react';
import { Upload, X, ImageIcon } from 'lucide-react';

const ImageUpload = ({ onImageSelect, required = false }) => {
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
      onImageSelect(file);
    } else {
      alert('Please select a valid image file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleRemove = () => {
    setPreview(null);
    onImageSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-300 mb-2">
        Upload Image {required && <span className="text-red-400">*</span>}
      </label>

      {!preview ? (
        <div
          className={`border-2 border-dashed rounded-lg p-6 md:p-8 text-center transition-all cursor-pointer min-h-[200px] md:min-h-[250px] flex flex-col items-center justify-center ${
            isDragging
              ? 'border-cyan-500 bg-cyan-500/10 glass'
              : 'border-gray-500/30 hover:border-cyan-500/50 glass hover:bg-cyan-500/5'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileInputChange}
            className="hidden"
          />
          <Upload className="mx-auto h-12 w-12 text-cyan-400 mb-4" />
          <p className="text-sm text-gray-300 mb-2">
            Drag and drop an image here, or click to select
          </p>
          <p className="text-xs text-gray-400">
            PNG, JPG, GIF up to 10MB
          </p>
        </div>
      ) : (
        <div className="relative glass border-2 border-green-500/30 rounded-lg p-4">
          <button
            type="button"
            onClick={handleRemove}
            className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors shadow-lg"
          >
            <X className="h-5 w-5" />
          </button>
          <img
            src={preview}
            alt="Preview"
            className="w-full h-48 object-cover rounded"
          />
          <div className="mt-2 flex items-center text-sm text-green-400">
            <ImageIcon className="h-4 w-4 mr-2" />
            <span>Image uploaded successfully</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
