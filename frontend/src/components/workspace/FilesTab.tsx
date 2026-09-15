import React, { useState, useRef } from 'react';
import type { FileMetadata } from '../../types/workspace';
import { workspaceService } from '../../api/services/workspace.service';
import { storage } from '../../config/firebase';
import { ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage';
import { Upload, FileIcon, Loader2, Download, FileText, Image as ImageIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface FilesTabProps {
  projectId: string;
  initialFiles: FileMetadata[];
  onFileAdded: (file: FileMetadata) => void;
}

export default function FilesTab({ projectId, initialFiles, onFileAdded }: FilesTabProps) {
  const { user } = useAuth();
  const [files, setFiles] = useState<FileMetadata[]>(initialFiles);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;
    
    await uploadFile(selectedFiles[0]);
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const uploadFile = async (file: File) => {
    if (!user) return;
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const storageKey = `projects/${projectId}/files/${Date.now()}_${file.name}`;
      const storageRef = ref(storage, storageKey);
      const uploadTask = uploadBytesResumable(storageRef, file);

      uploadTask.on('state_changed', 
        (snapshot) => {
          const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
          setUploadProgress(progress);
        }, 
        (error) => {
          console.error("Upload failed", error);
          setIsUploading(false);
        }, 
        async () => {
          const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
          
          // Save metadata to backend
          const res = await workspaceService.addFile(projectId, {
            filename: file.name,
            storageKey: storageKey,
            fileUrl: downloadURL,
            mimeType: file.type,
            fileSize: file.size
          });

          setFiles(prev => [...prev, res.data]);
          onFileAdded(res.data);
          setIsUploading(false);
          setUploadProgress(0);
        }
      );
    } catch (err) {
      console.error("Failed to upload file", err);
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return 'Unknown size';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (mimeType: string | null) => {
    if (!mimeType) return <FileIcon className="h-8 w-8 text-[#9A9AA3]" />;
    if (mimeType.startsWith('image/')) return <ImageIcon className="h-8 w-8 text-blue-400" />;
    if (mimeType.includes('pdf') || mimeType.includes('document') || mimeType.includes('text')) return <FileText className="h-8 w-8 text-red-400" />;
    return <FileIcon className="h-8 w-8 text-[#9A9AA3]" />;
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div 
        className="border-2 border-dashed border-[#2A2A32] rounded-2xl p-10 text-center hover:border-accent hover:bg-[#15151A]/50 transition-colors cursor-pointer relative"
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          onChange={handleFileSelect}
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="h-10 w-10 text-accent animate-spin mb-4" />
            <p className="text-[#F5F5F5] font-medium mb-2">Uploading File...</p>
            <div className="w-64 h-2 bg-[#2A2A32] rounded-full overflow-hidden">
              <div 
                className="h-full bg-accent transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-xs text-[#9A9AA3] mt-2">{Math.round(uploadProgress)}%</p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center">
            <div className="h-16 w-16 bg-[#2A2A32] rounded-full flex items-center justify-center mb-4 text-[#9A9AA3]">
              <Upload className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-bold text-[#F5F5F5] mb-1">Click to Upload</h3>
            <p className="text-sm text-[#9A9AA3]">or drag and drop your files here</p>
            <p className="text-xs text-[#9A9AA3] mt-4 max-w-sm">
              Upload design briefs, brand assets, references, and final deliverables.
            </p>
          </div>
        )}
      </div>

      {/* File List */}
      <div>
        <h3 className="text-xl font-display font-black uppercase mb-6">Workspace Files</h3>
        {files.length === 0 ? (
          <div className="bg-[#15151A] border border-[#2A2A32] rounded-2xl p-10 text-center">
            <p className="text-[#9A9AA3]">No files uploaded yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {files.map(file => (
              <div key={file.id} className="bg-[#15151A] border border-[#2A2A32] rounded-xl p-4 flex items-start gap-4 hover:border-[#9A9AA3] transition-colors group">
                <div className="p-3 bg-[#0D0D0F] rounded-lg">
                  {getFileIcon(file.mimeType)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[#F5F5F5] truncate mb-1" title={file.filename}>
                    {file.filename}
                  </p>
                  <p className="text-xs text-[#9A9AA3]">
                    {formatFileSize(file.fileSize)} • {new Date(file.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <a 
                    href={file.fileUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="p-2 text-[#9A9AA3] hover:text-accent hover:bg-accent/10 rounded-lg transition-colors"
                  >
                    <Download className="h-4 w-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
