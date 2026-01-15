// Note: This component should be in a 'components' directory.
'use client';

interface InputSectionProps {
  errorLog: string;
  setErrorLog: (value: string) => void;
  handleAnalyze: () => void;
  loading: boolean;
}

const InputSection = ({ errorLog, setErrorLog, handleAnalyze, loading }: InputSectionProps) => (
  <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
    <label className="block text-sm font-semibold text-gray-700 mb-2">
      Paste Your Error Log
    </label>
    <textarea 
      value={errorLog}
      onChange={(e) => setErrorLog(e.target.value)}
      className="w-full h-48 border-2 border-gray-300 rounded-lg p-4 font-mono text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition"
      placeholder="Traceback (most recent call last):&#10;  File &quot;app.py&quot;, line 42, in process_data&#10;    result = data['key']&#10;KeyError: 'key'"
    />
    
    <button 
      onClick={handleAnalyze}
      disabled={loading || !errorLog.trim()}
      className="mt-4 w-full gradient-button text-white px-6 py-3 rounded-lg font-semibold transition shadow-md disabled:from-gray-400 disabled:to-gray-500"
    >
      {loading ? (
        <span className="flex items-center justify-center">
          <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          Analyzing...
        </span>
      ) : (
        'Analyze Error'
      )}
    </button>
  </div>
);

export default InputSection;
