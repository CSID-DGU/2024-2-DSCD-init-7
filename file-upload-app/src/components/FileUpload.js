import React, { useState } from 'react';
import './FileUpload.css';
import uploadIcon from '../image/upload_file.png'; // 드래그 앤 드롭 아이콘 이미지 경로
import lockIcon from '../image/lock_icon.png'; // 자물쇠 아이콘 이미지 경로
import fileIcon from '../image/word_icon.png'; // Word 파일 아이콘 이미지 경로
import cancelIcon from '../image/cancel_icon.png'; // 취소 버튼 아이콘 이미지 경로

function FileUpload() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(47); // 임시 진행률 설정

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setProgress(47); // 파일 선택 시 임의로 진행률 설정
  };

  const handleUpload = () => {
    console.log("Uploading:", file);
  };

  const handleCancel = () => {
    setFile(null);
    setProgress(0);
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
          <input
            type="text"
            id="title"
            placeholder="input title"
          />
        </div>
        <div className="upload-section">
          <label htmlFor="attached-document" className="section-label">Attached Document</label>
          <div className="upload-dropzone">
            <img src={uploadIcon} alt="Upload Icon" className="upload-icon" /> {/* 드래그 앤 드롭 아이콘 */}
            <p className="dropzone-title">Drag & Drop</p>
            <p className="dropzone-instruction">your files here or browse.</p>
            <input type="file" onChange={handleFileChange} />
          </div>
          <div className="accepted-file-types-section">
            <p className="accepted-file-types">Accepted File Type: pdf, docx, hwp only</p>
            <div className="security-section">
              <img src={lockIcon} alt="Lock Icon" className="lock-icon" /> {/* 자물쇠 아이콘 */}
              <span>Secure</span>
            </div>
          </div>
        </div>
        {file && (
          <div className="uploaded-file-box">
            <img src={fileIcon} alt="File Icon" className="file-icon" /> {/* 파일 아이콘 */}
            <div className="file-name">{file.name}</div>
            <div className="upload-progress">
              <div className="progress-bar" style={{ width: `${progress}%` }}></div>
              <span className="progress-text">{progress}%</span> {/* 진행률 텍스트 */}
            </div>
            <img src={cancelIcon} alt="Cancel Icon" className="cancel-icon" onClick={handleCancel} /> {/* 취소 아이콘 */}
          </div>
        )}
        <button className="upload-button" onClick={handleUpload}>Upload</button>
      </div>
    </div>
  );
}

export default FileUpload;