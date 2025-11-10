import React from 'react';
import { Check, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export type StepStatus = 'pending' | 'in-progress' | 'completed' | 'error';

export interface Step {
  id: string;
  label: string;
  description?: string;
  status: StepStatus;
}

interface StepperProps {
  steps: Step[];
  currentStepId: string;
  className?: string;
}

export function Stepper({ steps, currentStepId, className }: StepperProps) {
  const currentIndex = steps.findIndex(step => step.id === currentStepId);

  return (
    <div className={cn("w-full", className)}>
      <nav aria-label="Progress">
        <ol role="list" className="flex items-center justify-between">
          {steps.map((step, index) => {
            const isCompleted = step.status === 'completed';
            const isInProgress = step.status === 'in-progress';
            const isError = step.status === 'error';
            const isPending = step.status === 'pending';
            const isLast = index === steps.length - 1;

            return (
              <li
                key={step.id}
                className={cn(
                  "relative flex-1",
                  !isLast && "pr-8 sm:pr-20"
                )}
              >
                {/* Connector Line */}
                {!isLast && (
                  <div
                    className="absolute left-0 top-4 ml-8 h-0.5 w-full"
                    aria-hidden="true"
                  >
                    <div
                      className={cn(
                        "h-full transition-all duration-500",
                        isCompleted
                          ? "bg-warmgold"
                          : "bg-gray-200"
                      )}
                    />
                  </div>
                )}

                {/* Step Content */}
                <div className="group relative flex flex-col items-center">
                  {/* Step Circle */}
                  <span
                    className={cn(
                      "relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all duration-300",
                      isCompleted && "border-warmgold bg-warmgold text-white",
                      isInProgress && "border-warmgold bg-white text-warmgold animate-pulse",
                      isError && "border-red-500 bg-red-500 text-white",
                      isPending && "border-gray-300 bg-white text-gray-500"
                    )}
                  >
                    {isCompleted && (
                      <Check className="h-5 w-5" aria-hidden="true" />
                    )}
                    {isInProgress && (
                      <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
                    )}
                    {isError && (
                      <span className="text-lg font-bold">!</span>
                    )}
                    {isPending && (
                      <span className="text-sm font-medium">{index + 1}</span>
                    )}
                  </span>

                  {/* Step Label */}
                  <span
                    className={cn(
                      "mt-2 text-xs font-medium transition-colors duration-300",
                      isCompleted && "text-warmgold",
                      isInProgress && "text-darktext",
                      isError && "text-red-500",
                      isPending && "text-gray-500"
                    )}
                  >
                    {step.label}
                  </span>

                  {/* Step Description (optional) */}
                  {step.description && (
                    <span className="mt-1 text-xs text-gray-400 text-center max-w-[100px] hidden sm:block">
                      {step.description}
                    </span>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
}

