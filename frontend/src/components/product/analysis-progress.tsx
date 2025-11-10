'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Search, 
  DollarSign, 
  FileText, 
  CheckCircle2,
  Loader2 
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface AnalysisProgressProps {
  currentStep: 'analyzing' | 'research' | 'generate';
  progress: number; // 0-100
  analysisData?: any;
  priceData?: any;
}

interface ProgressStepProps {
  icon: React.ReactNode;
  label: string;
  description: string;
  status: 'pending' | 'active' | 'completed';
  data?: any;
}

function ProgressStep({ icon, label, description, status, data }: ProgressStepProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "flex items-start gap-4 p-4 rounded-lg transition-all duration-300",
        status === 'active' && "bg-warmgold/5 border-l-4 border-warmgold",
        status === 'completed' && "bg-green-50 border-l-4 border-green-500",
        status === 'pending' && "opacity-50"
      )}
    >
      {/* Icon */}
      <div className={cn(
        "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-colors",
        status === 'active' && "bg-warmgold text-white animate-pulse",
        status === 'completed' && "bg-green-500 text-white",
        status === 'pending' && "bg-gray-200 text-gray-400"
      )}>
        {status === 'active' && <Loader2 className="w-5 h-5 animate-spin" />}
        {status === 'completed' && <CheckCircle2 className="w-5 h-5" />}
        {status === 'pending' && icon}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <h3 className={cn(
          "font-semibold text-sm mb-1 transition-colors",
          status === 'active' && "text-darktext",
          status === 'completed' && "text-green-700",
          status === 'pending' && "text-gray-400"
        )}>
          {label}
        </h3>
        <p className="text-xs text-darktext/60 mb-2">{description}</p>

        {/* Data Display (if available) */}
        {status === 'completed' && data && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
            className="mt-2 p-2 bg-white rounded border border-gray-200 text-xs"
          >
            {data}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

export function AnalysisProgress({
  currentStep,
  progress,
  analysisData,
  priceData
}: AnalysisProgressProps) {
  const steps = [
    {
      key: 'analyzing',
      icon: <Sparkles className="w-5 h-5" />,
      label: 'Analyzing Images',
      description: 'AI is examining your product photos...',
      status: currentStep === 'analyzing' ? 'active' : 'completed',
      data: analysisData && (
        <div className="space-y-1">
          <p><strong>Product:</strong> {analysisData.product_name}</p>
          <p><strong>Brand:</strong> {analysisData.brand || 'Unknown'}</p>
          <p><strong>Category:</strong> {analysisData.category}</p>
          <p><strong>Condition:</strong> {analysisData.condition}</p>
          <p><strong>Confidence:</strong> {(analysisData.confidence * 100).toFixed(0)}%</p>
        </div>
      )
    },
    {
      key: 'research',
      icon: <Search className="w-5 h-5" />,
      label: 'Researching Prices',
      description: 'Searching across all marketplaces...',
      status: currentStep === 'analyzing' ? 'pending' : currentStep === 'research' ? 'active' : 'completed',
      data: priceData && (
        <div className="space-y-1">
          <p><strong>Recommended Price:</strong> ${priceData.recommended_price?.toFixed(2)}</p>
          <p><strong>Confidence:</strong> {priceData.confidence}</p>
          <p><strong>Marketplaces Searched:</strong> {priceData.search_summary?.marketplaces_searched?.length || 0}</p>
          <p><strong>Results Found:</strong> {priceData.search_summary?.total_results || 0}</p>
        </div>
      )
    },
    {
      key: 'generate',
      icon: <FileText className="w-5 h-5" />,
      label: 'Generating Content',
      description: 'Creating marketplace-optimized listings...',
      status: currentStep === 'generate' ? 'active' : currentStep === 'analyzing' || currentStep === 'research' ? 'pending' : 'completed',
    }
  ];

  return (
    <Card className="glass-effect border-warmgold/20">
      <CardContent className="p-6 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-darktext">Processing Your Product</h2>
          <p className="text-sm text-darktext/60">
            Please wait while our AI analyzes your product...
          </p>
        </div>

        {/* Progress Bar */}
        <div className="relative">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-warmgold to-gold"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
          <p className="text-center text-xs text-darktext/60 mt-2">
            {progress}% Complete
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-4">
          {steps.map((step) => (
            <ProgressStep
              key={step.key}
              icon={step.icon}
              label={step.label}
              description={step.description}
              status={step.status as any}
              data={step.data}
            />
          ))}
        </div>

        {/* Animation Effect */}
        <div className="flex justify-center">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <Sparkles className="w-8 h-8 text-warmgold" />
          </motion.div>
        </div>
      </CardContent>
    </Card>
  );
}

