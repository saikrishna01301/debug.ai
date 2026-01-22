// Note: This component should be in a 'components' directory.
import { AnalysisResult } from './interfaces';
import ErrorSummary from './ErrorSummary';
import RootCause from './RootCause';
import Solutions from './Solutions';

interface ResultsSectionProps {
  result: AnalysisResult;
}

const ResultsSection = ({ result }: ResultsSectionProps) => (
  <div className="space-y-6">
    <ErrorSummary
      language={result.language}
      error_type={result.error_type}
      file_path={result.file_path}
      line_number={result.line_number}
      error_message={result.error_message}
    />
    <RootCause
      root_cause={result.root_cause}
      reasoning={result.reasoning}
    />
    <Solutions
      solutions={result.solutions}
      sources_used={result.sources_used}
      analysisId={result.analysis_id}
    />
  </div>
);

export default ResultsSection;
