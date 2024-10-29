import React, { useState } from 'react';
import './FileUpload.css';
import uploadIcon from '../image/upload_file.png';
import lockIcon from '../image/lock_icon.png';
import fileIcon from '../image/word_icon.png';
import cancelIcon from '../image/cancel_icon.png';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(47);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setProgress(47);
  };

  const handleUpload = () => {
    console.log("Uploading:", file);
  };

  const handleCancel = () => {
    setFile(null);
    setProgress(0);
  };

  const triggerFileInput = () => {
    document.getElementById('fileInput').click();
  };

  return (
    <div className="upload-container">
      <aside className="sidebar">
        <button className="sidebar-button">Upload</button>
      </aside>
      <div className="upload-content">
        <h2>Upload Files</h2>
        <div className="upload-title">
          <label htmlFor="title">Title</label>
          <input type="text" id="title" placeholder="input title" />
        </div>
        <div className="upload-section">
          <label htmlFor="attached-document" className="section-label">Attached Document</label>
          <div className="upload-dropzone" onClick={triggerFileInput}>
            <img src={uploadIcon} alt="Upload Icon" className="upload-icon" />
            <p className="dropzone-title">Drag & Drop</p>
            <p className="dropzone-instruction">your files here or browser.</p>
            <input type="file" id="fileInput" onChange={handleFileChange} style={{ display: 'none' }} />
          </div>
          <div className="accepted-file-types-section">
            <p className="accepted-file-types">Accepted File Type: pdf, docx, hwp only</p>
            <div className="security-section">
              <img src={lockIcon} alt="Lock Icon" className="lock-icon" />
              <span>Secure</span>
            </div>
          </div>
        </div>
        {file && (
          <div className="uploaded-file-box">
            <img src={fileIcon} alt="File Icon" className="file-icon" />
            <div className="file-name">{file.name}</div>
            <div className="upload-progress-container">
              <div className="upload-progress">
                <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              </div>
              <span className="progress-text">{progress}%</span>
            </div>
            <img src={cancelIcon} alt="Cancel Icon" className="cancel-icon" onClick={handleCancel} />
          </div>
        )}
        <button className="upload-button" onClick={handleUpload}>Upload</button>
      </div>
    </div>
  );
}

export default FileUpload;
