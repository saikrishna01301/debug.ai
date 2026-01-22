'use client';
import { useState } from 'react';
import { Solution } from './interfaces';
import { apiService } from '@/services/api';

interface SolutionCardProps {
  solution: Solution;
  index: number;
  analysisId: number;
}

const SolutionCard = ({ solution, index, analysisId }: SolutionCardProps) => {
  const [feedbackGiven, setFeedbackGiven] = useState<boolean | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFeedback = async (worked: boolean) => {
    setIsSubmitting(true);
    try {
      await apiService.submitFeedback({
        analysis_id: analysisId,
        solution_index: index,
        worked: worked,
      });
      setFeedbackGiven(worked);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      key={index}
      className="border-2 border-gray-200 rounded-lg p-5 hover:border-blue-400 transition"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-xl font-semibold text-gray-900">
          {index + 1}. {solution.title}
        </h3>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
          solution.confidence >= 0.8
            ? 'bg-green-100 text-green-800'
            : solution.confidence >= 0.6
            ? 'bg-yellow-100 text-yellow-800'
            : 'bg-orange-100 text-orange-800'
        }`}>
          {Math.round(solution.confidence * 100)}% confident
        </span>
      </div>

      <p className="text-gray-700 mb-4 leading-relaxed">
        {solution.explanation}
      </p>

      <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
        <pre className="text-sm text-gray-100 font-mono">
          <code>{solution.code}</code>
        </pre>
      </div>

      {solution.source_urls && solution.source_urls.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {solution.source_urls.map((url, urlIndex) => (
            <a
              key={urlIndex}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Source {urlIndex + 1}
            </a>
          ))}
        </div>
      )}

      {/* Feedback Section */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        {feedbackGiven === null ? (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">Did this solution help?</span>
            <button
              onClick={() => handleFeedback(true)}
              disabled={isSubmitting}
              className="px-3 py-1.5 bg-green-100 text-green-700 rounded-md hover:bg-green-200 transition disabled:opacity-50 text-sm font-medium"
            >
              Yes, it worked!
            </button>
            <button
              onClick={() => handleFeedback(false)}
              disabled={isSubmitting}
              className="px-3 py-1.5 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition disabled:opacity-50 text-sm font-medium"
            >
              No, didn&apos;t help
            </button>
          </div>
        ) : (
          <div className={`text-sm font-medium ${feedbackGiven ? 'text-green-600' : 'text-red-600'}`}>
            {feedbackGiven
              ? '✓ Thanks! Glad it helped.'
              : '✓ Thanks for the feedback. Try another solution.'}
          </div>
        )}
      </div>
    </div>
  );
};

export default SolutionCard;
