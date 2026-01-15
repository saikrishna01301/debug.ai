// Note: This component should be in a 'components' directory.
interface ErrorSummaryProps {
  language: string;
  error_type: string;
  file_path: string;
  line_number: number;
  error_message: string;
}

const ErrorSummary = ({ language, error_type, file_path, line_number, error_message }: ErrorSummaryProps) => (
  <div className="bg-white rounded-xl shadow-lg p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-4">Error Summary</h2>
    
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
      <div>
        <p className="text-sm text-gray-500">Language</p>
        <p className="font-semibold text-lg">{language}</p>
      </div>
      
      <div>
        <p className="text-sm text-gray-500">Error Type</p>
        <p className="font-semibold text-lg text-red-600">{error_type}</p>
      </div>
      
      <div>
        <p className="text-sm text-gray-500">File</p>
        <p className="font-semibold text-lg">{file_path}</p>
      </div>
      
      <div>
        <p className="text-sm text-gray-500">Line</p>
        <p className="font-semibold text-lg">{line_number}</p>
      </div>
    </div>

    <div className="border-t pt-4">
      <p className="text-sm text-gray-500 mb-1">Error Message</p>
      <p className="font-mono text-sm bg-red-50 p-3 rounded border-l-4 border-red-500">
        {error_message}
      </p>
    </div>
  </div>
);

export default ErrorSummary;
