// Note: This component should be in a 'components' directory.
import { Solution } from './interfaces';

interface SolutionCardProps {
  solution: Solution;
  index: number;
}

const SolutionCard = ({ solution, index }: SolutionCardProps) => (
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
  </div>
);

export default SolutionCard;
