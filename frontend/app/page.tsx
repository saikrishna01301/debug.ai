'use client';
import { useState } from 'react';
import { AnalysisResult } from '@/components/interfaces';
import Header from '@/components/Header';
import InputSection from '@/components/InputSection';
import ResultsSection from '@/components/ResultsSection';
import { apiService } from '@/services/api';

export default function Home() {
  const [errorLog, setErrorLog] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);

    try {
      console.log('Sending analysis request with:', errorLog);
      const data = await apiService.analyze(errorLog, 5);
      console.log('Received response:', data);
      setResult(data);
    } catch (error: any) {
      console.error('Full error object:', error);
      const errorMessage = error?.message || 'Failed to analyze error. Please try again.';
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <Header />
        <InputSection
          errorLog={errorLog}
          setErrorLog={setErrorLog}
          handleAnalyze={handleAnalyze}
          loading={loading}
        />
        {result && <ResultsSection result={result} />}
      </div>
    </main>
  );
}