// Note: This component should be in a 'components' directory.
interface RootCauseProps {
  root_cause: string;
  reasoning: string;
}

const RootCause = ({ root_cause, reasoning }: RootCauseProps) => (
  <div className="bg-white rounded-xl shadow-lg p-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-3">Root Cause</h2>
    <p className="text-gray-700 leading-relaxed">{root_cause}</p>
    
    <div className="mt-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
      <p className="text-sm font-semibold text-blue-900 mb-2">Analysis</p>
      <p className="text-sm text-blue-800">{reasoning}</p>
    </div>
  </div>
);

export default RootCause;
