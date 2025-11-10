'use client';

import React, { useState, useCallback } from 'react';
import { Upload, X, AlertCircle, Image as ImageIcon } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ImageUploadCardProps {
  onUpload: (files: File[]) => void;
  maxImages?: number;
  acceptedFormats?: string[];
}

export function ImageUploadCard({
  onUpload,
  maxImages = 10,
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp', 'image/heic']
}: ImageUploadCardProps) {
  const [images, setImages] = useState<{ file: File; preview: string }[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;

    setError(null);
    const fileArray = Array.from(files);

    // Validate file types
    const invalidFiles = fileArray.filter(file => !acceptedFormats.includes(file.type));
    if (invalidFiles.length > 0) {
      setError(`Invalid file type. Please upload ${acceptedFormats.join(', ')}`);
      return;
    }

    // Check max images
    if (images.length + fileArray.length > maxImages) {
      setError(`Maximum ${maxImages} images allowed`);
      return;
    }

    // Create previews
    const newImages = fileArray.map(file => ({
      file,
      preview: URL.createObjectURL(file)
    }));

    setImages(prev => [...prev, ...newImages]);
  }, [images.length, maxImages, acceptedFormats]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  }, [handleFiles]);

  const removeImage = useCallback((index: number) => {
    setImages(prev => {
      const updated = [...prev];
      URL.revokeObjectURL(updated[index].preview);
      updated.splice(index, 1);
      return updated;
    });
  }, []);

  const handleSubmit = useCallback(() => {
    if (images.length === 0) {
      setError('Please upload at least one image');
      return;
    }

    onUpload(images.map(img => img.file));
  }, [images, onUpload]);

  return (
    <Card className="glass-effect border-warmgold/20">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-darktext flex items-center gap-2">
          <ImageIcon className="w-6 h-6 text-warmgold" />
          Upload Product Images
        </CardTitle>
        <CardDescription className="text-darktext/60">
          Take clear photos from ALL angles for the best AI analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Important Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900">
            <p className="font-semibold mb-1">For Best Results:</p>
            <ul className="list-disc list-inside space-y-1 text-blue-800">
              <li>Include photos from all angles (front, back, sides, top, bottom)</li>
              <li>Show any defects, wear, or damage clearly</li>
              <li>Include original box and accessories if available</li>
              <li>Use good lighting and clear focus</li>
              <li>Include brand labels, tags, or serial numbers</li>
            </ul>
          </div>
        </div>

        {/* Upload Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200",
            isDragging ? "border-warmgold bg-warmgold/5 scale-105" : "border-gray-300 hover:border-warmgold/50",
            images.length >= maxImages && "opacity-50 cursor-not-allowed"
          )}
        >
          <Upload className={cn(
            "mx-auto h-12 w-12 mb-4 transition-colors",
            isDragging ? "text-warmgold" : "text-gray-400"
          )} />
          <div className="space-y-2">
            <p className="text-darktext font-medium">
              {isDragging ? "Drop images here" : "Drag & drop images here"}
            </p>
            <p className="text-sm text-darktext/60">or</p>
            <label htmlFor="file-upload">
              <Button
                type="button"
                variant="outline"
                className="cursor-pointer"
                onClick={() => document.getElementById('file-upload')?.click()}
                disabled={images.length >= maxImages}
              >
                Browse Files
              </Button>
              <input
                id="file-upload"
                type="file"
                className="hidden"
                multiple
                accept={acceptedFormats.join(',')}
                onChange={handleFileInput}
                disabled={images.length >= maxImages}
              />
            </label>
          </div>
          <p className="text-xs text-darktext/40 mt-4">
            {images.length} / {maxImages} images • JPG, PNG, WebP, HEIC
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2 text-red-800 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Image Previews */}
        {images.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-darktext mb-3">
              Selected Images ({images.length})
            </h3>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-4">
              {images.map((img, index) => (
                <div
                  key={index}
                  className="relative group aspect-square rounded-lg overflow-hidden border border-gray-200 hover:border-warmgold transition-colors"
                >
                  <img
                    src={img.preview}
                    alt={`Product ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-1 text-center opacity-0 group-hover:opacity-100 transition-opacity">
                    {img.file.name}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="pt-4">
          <Button
            onClick={handleSubmit}
            disabled={images.length === 0}
            className="w-full bg-gradient-gold text-carbon font-semibold hover:opacity-90 disabled:opacity-50"
            size="lg"
          >
            Start AI Analysis ({images.length} image{images.length !== 1 ? 's' : ''})
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

