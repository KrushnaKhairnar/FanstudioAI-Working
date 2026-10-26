import React, { useState } from 'react';
import { Camera, X, Upload, CheckCircle2, Link as LinkIcon } from 'lucide-react';
import { useUploadMediaMutation } from './queries.js';

export const MediaUploadModal = ({
  isOpen,
  onClose,
  targetProduct,
  onPhotoUploaded,
}) => {
  const [uploadPreview, setUploadPreview] = useState('');
  const [uploadFileName, setUploadFileName] = useState('');
  const [uploadUrlInput, setUploadUrlInput] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const uploadMediaMutation = useUploadMediaMutation();

  if (!isOpen || !targetProduct) return null;

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadFileName(file.name);
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result) {
          setUploadPreview(reader.result);
          setUploadUrlInput('');
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveProductImage = async () => {
    const imageData = uploadPreview || uploadUrlInput;
    if (!imageData) return;

    setErrorMsg('');
    setSuccessMsg('');

    try {
      const payload = {
        image_base64: uploadPreview.startsWith('data:image') ? uploadPreview : undefined,
        image_url: !uploadPreview.startsWith('data:image') ? uploadUrlInput : undefined,
        filename: uploadFileName || `${targetProduct.product_code || targetProduct.fanCode}.jpg`,
        product_id: targetProduct.product_id,
        is_primary: true,
      };

      const res = await uploadMediaMutation.mutateAsync(payload);
      setSuccessMsg('Product photo updated successfully!');
      if (onPhotoUploaded) {
        onPhotoUploaded(targetProduct.product_id, res.url || res.image_url);
      }
      setTimeout(() => {
        onClose();
        setUploadPreview('');
        setUploadUrlInput('');
        setUploadFileName('');
        setSuccessMsg('');
      }, 1000);
    } catch (err) {
      console.error('Upload error:', err);
      setErrorMsg(err.message || 'Failed to upload image');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Camera className="w-5 h-5 text-amber-600" />
            <div>
              <h3 className="text-sm font-extrabold text-slate-900">
                Upload Fan Photo: {targetProduct.name || targetProduct.fanName}
              </h3>
              <p className="text-[11px] text-slate-400 font-mono">
                {targetProduct.product_code || targetProduct.fanCode}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-4 text-xs">
          {successMsg && (
            <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 font-semibold">
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5">
              Select Image File (Local disk)
            </label>
            <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-200 hover:border-amber-500 rounded-2xl cursor-pointer bg-slate-50/50 hover:bg-amber-50/20 transition-all">
              <Upload className="w-5 h-5 text-slate-400 mb-1" />
              <span className="text-[11px] font-bold text-slate-700">Click to upload photo</span>
              <span className="text-[10px] text-slate-400">PNG, JPG, WEBP up to 10MB</span>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <LinkIcon className="w-3.5 h-3.5" />
              <span>Or provide public Image URL</span>
            </label>
            <input
              type="url"
              value={uploadUrlInput}
              onChange={(e) => {
                setUploadUrlInput(e.target.value);
                setUploadPreview('');
              }}
              placeholder="https://example.com/ceiling-fan.jpg"
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>

          {(uploadPreview || uploadUrlInput) && (
            <div className="p-3 bg-slate-100 rounded-2xl flex flex-col items-center">
              <span className="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-wider">
                Photo Preview
              </span>
              <div className="w-36 h-36 rounded-xl bg-white border border-slate-200 overflow-hidden flex items-center justify-center p-2 shadow-2xs">
                <img
                  src={uploadPreview || uploadUrlInput}
                  alt="Preview"
                  className="max-w-full max-h-full object-contain"
                />
              </div>
            </div>
          )}

          <div className="pt-2 flex items-center justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSaveProductImage}
              disabled={uploadMediaMutation.isPending || (!uploadPreview && !uploadUrlInput)}
              className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs shadow-xs transition-colors cursor-pointer disabled:opacity-50"
            >
              {uploadMediaMutation.isPending ? 'Uploading...' : 'Save Fan Photo'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
