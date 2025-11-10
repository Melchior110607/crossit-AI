'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Stepper, Step } from '@/components/ui/stepper';
import { ImageUploadCard } from '@/components/product/image-upload-card';
import { AnalysisProgress } from '@/components/product/analysis-progress';
import { ListingReviewCard } from '@/components/product/listing-review-card';
import { PublishSuccessCard } from '@/components/product/publish-success-card';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { ArrowLeft, AlertCircle } from 'lucide-react';

type WorkflowStep = 'upload' | 'analyzing' | 'research' | 'generate' | 'review' | 'publish' | 'success';

export default function SmartProductCreation() {
  const router = useRouter();
  
  // Workflow state
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('upload');
  const [progress, setProgress] = useState(0);
  
  // Data state
  const [uploadedImages, setUploadedImages] = useState<string[]>([]);
  const [analysisId, setAnalysisId] = useState<string>('');
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [priceData, setPriceData] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [listings, setListings] = useState<Record<string, any>>({});
  const [publishResult, setPublishResult] = useState<any>(null);
  
  // Error state
  const [error, setError] = useState<string | null>(null);

  // Stepper configuration
  const steps: Step[] = [
    {
      id: 'upload',
      label: 'Upload',
      description: 'Add photos',
      status: currentStep === 'upload' ? 'in-progress' : 
              ['analyzing', 'research', 'generate', 'review', 'publish', 'success'].includes(currentStep) ? 'completed' : 'pending'
    },
    {
      id: 'analyzing',
      label: 'Analyze',
      description: 'AI analysis',
      status: currentStep === 'analyzing' ? 'in-progress' : 
              ['research', 'generate', 'review', 'publish', 'success'].includes(currentStep) ? 'completed' : 'pending'
    },
    {
      id: 'research',
      label: 'Research',
      description: 'Find prices',
      status: currentStep === 'research' ? 'in-progress' : 
              ['generate', 'review', 'publish', 'success'].includes(currentStep) ? 'completed' : 'pending'
    },
    {
      id: 'generate',
      label: 'Generate',
      description: 'Create listings',
      status: currentStep === 'generate' ? 'in-progress' : 
              ['review', 'publish', 'success'].includes(currentStep) ? 'completed' : 'pending'
    },
    {
      id: 'review',
      label: 'Review',
      description: 'Approve & publish',
      status: currentStep === 'review' ? 'in-progress' : 
              ['publish', 'success'].includes(currentStep) ? 'completed' : 'pending'
    },
  ];

  const handleImageUpload = useCallback(async (files: File[]) => {
    try {
      setError(null);
      setCurrentStep('analyzing');
      setProgress(10);

      // Upload images to S3/Supabase Storage
      const uploadResult = await apiClient.uploadImages(files);
      const imageUrls = uploadResult.uploaded_images;
      setUploadedImages(imageUrls);
      setProgress(15);

      // Step 1: Analyze product images
      const analysis = await apiClient.analyzeProduct(imageUrls);
      setAnalysisId(analysis.analysis_id);
      setAnalysisData(analysis.product_info);
      setProgress(25);

      // Check for missing info
      if (analysis.missing_info && analysis.missing_info.length > 0) {
        // TODO: Show dialog to collect missing information
        console.warn('Missing information:', analysis.missing_info);
      }

      // Move to price research
      setCurrentStep('research');
      setProgress(30);

      // Step 2: Research prices
      const prices = await apiClient.researchPrices(analysis.analysis_id, analysis.product_info);
      setPriceData(prices);
      setRecommendations(prices.marketplace_recommendations);
      setProgress(50);

      // Move to content generation
      setCurrentStep('generate');
      setProgress(55);

      // Step 3: Generate listings for recommended marketplaces
      const recommendedMarketplaces = prices.marketplace_recommendations.recommended
        .filter((m: any) => m.connected && m.score >= 0.5)
        .map((m: any) => m.marketplace);

      // If no connected marketplaces, use top 3 recommendations
      const marketplacesToGenerate = recommendedMarketplaces.length > 0 
        ? recommendedMarketplaces 
        : prices.marketplace_recommendations.recommended
            .slice(0, 3)
            .map((m: any) => m.marketplace);

      const generatedListings = await apiClient.generateListings(
        analysis.analysis_id,
        analysis.product_info,
        prices,
        marketplacesToGenerate
      );
      
      setListings(generatedListings.listings);
      setProgress(75);

      // Move to review step
      setCurrentStep('review');
      setProgress(80);

    } catch (err: any) {
      console.error('Error in product automation:', err);
      setError(err.response?.data?.detail || err.message || 'An error occurred during processing');
      setCurrentStep('upload'); // Reset to upload on error
      setProgress(0);
    }
  }, []);

  const handleListingEdit = useCallback((marketplace: string, data: Partial<any>) => {
    setListings(prev => ({
      ...prev,
      [marketplace]: {
        ...prev[marketplace],
        ...data
      }
    }));
  }, []);

  const handlePublish = useCallback(async (approvedListings: Record<string, any>) => {
    try {
      setError(null);
      setCurrentStep('publish');
      setProgress(85);

      const result = await apiClient.publishListings(analysisId, approvedListings);
      setPublishResult(result);
      setProgress(100);

      // Move to success step
      setCurrentStep('success');

    } catch (err: any) {
      console.error('Error publishing listings:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to publish listings');
      setCurrentStep('review'); // Go back to review on error
    }
  }, [analysisId]);

  const handleStartOver = useCallback(() => {
    setCurrentStep('upload');
    setProgress(0);
    setUploadedImages([]);
    setAnalysisId('');
    setAnalysisData(null);
    setPriceData(null);
    setRecommendations(null);
    setListings({});
    setPublishResult(null);
    setError(null);
  }, []);

  return (
    <div className="min-h-screen bg-lightgray pb-12">
      <div className="max-w-6xl mx-auto p-4 sm:p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-darktext mb-2">
              Smart Product Creation
            </h1>
            <p className="text-darktext/60">
              AI-powered product listing across multiple marketplaces
            </p>
          </div>
          
          {currentStep !== 'success' && (
            <Button
              variant="ghost"
              onClick={() => router.back()}
              className="text-darktext/60 hover:text-darktext"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          )}
        </div>

        {/* Stepper */}
        {currentStep !== 'success' && (
          <Stepper steps={steps} currentStepId={currentStep} />
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900">Error</p>
              <p className="text-sm text-red-800 mt-1">{error}</p>
              <Button
                onClick={handleStartOver}
                variant="outline"
                size="sm"
                className="mt-3 border-red-300 text-red-700 hover:bg-red-50"
              >
                Start Over
              </Button>
            </div>
          </div>
        )}

        {/* Step Content */}
        {currentStep === 'upload' && (
          <ImageUploadCard onUpload={handleImageUpload} />
        )}

        {(currentStep === 'analyzing' || currentStep === 'research' || currentStep === 'generate') && (
          <AnalysisProgress
            currentStep={currentStep}
            progress={progress}
            analysisData={analysisData}
            priceData={priceData}
          />
        )}

        {currentStep === 'review' && (
          <ListingReviewCard
            listings={listings}
            onApprove={handlePublish}
            onEdit={handleListingEdit}
          />
        )}

        {currentStep === 'publish' && (
          <AnalysisProgress
            currentStep="generate"
            progress={progress}
            analysisData={analysisData}
            priceData={priceData}
          />
        )}

        {currentStep === 'success' && publishResult && (
          <PublishSuccessCard
            publishedMarketplaces={publishResult.published || []}
            productId={publishResult.product_id}
          />
        )}
      </div>
    </div>
  );
}
