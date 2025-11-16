import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Film, Sparkles } from 'lucide-react';
import { uploadVideo, generateClips } from '../services/api';

function HomePage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    // Validate file type
    const validTypes = [
      'video/mp4',
      'video/quicktime',
      'video/x-msvideo',
      'video/x-matroska',
      'video/webm',
    ];

    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid video file (MP4, MOV, AVI, MKV, WebM)');
      return;
    }

    // Validate file size (2GB max)
    const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
    if (file.size > maxSize) {
      setError('File size must be less than 2GB');
      return;
    }

    setError('');
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError('');

    try {
      // Upload video
      const uploadData = await uploadVideo(selectedFile, setUploadProgress);

      // Automatically start clip generation
      await generateClips(uploadData.job_id);

      // Navigate to job detail page
      navigate(`/jobs/${uploadData.job_id}`);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Video Clipper
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upload your long-form video and let AI automatically generate
          engaging short clips with captions for social media.
        </p>
      </div>

      {/* Upload Card */}
      <div className="max-w-2xl mx-auto">
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Upload Video</h2>

          {/* Drag and Drop Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-upload"
              className="hidden"
              accept="video/*"
              onChange={handleChange}
              disabled={uploading}
            />

            {!selectedFile ? (
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Drop your video here or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  MP4, MOV, AVI, MKV, WebM (max 2GB)
                </p>
              </label>
            ) : (
              <div className="space-y-4">
                <Film className="mx-auto h-12 w-12 text-primary-600" />
                <div>
                  <p className="text-lg font-medium text-gray-900">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>

                {uploading ? (
                  <div className="space-y-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-600">
                      Uploading... {uploadProgress}%
                    </p>
                  </div>
                ) : (
                  <div className="flex justify-center space-x-4">
                    <button
                      onClick={handleUpload}
                      className="btn btn-primary flex items-center space-x-2"
                    >
                      <Sparkles className="h-5 w-5" />
                      <span>Generate Clips</span>
                    </button>

                    <button
                      onClick={() => setSelectedFile(null)}
                      className="btn btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Sparkles className="h-6 w-6 text-primary-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">AI-Powered</h3>
            <p className="text-sm text-gray-600">
              Automatic highlight detection using AI
            </p>
          </div>

          <div className="text-center">
            <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Film className="h-6 w-6 text-primary-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">Multi-Format</h3>
            <p className="text-sm text-gray-600">
              Export in vertical and landscape formats
            </p>
          </div>

          <div className="text-center">
            <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Upload className="h-6 w-6 text-primary-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">Auto Captions</h3>
            <p className="text-sm text-gray-600">
              Generated and burned-in captions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
