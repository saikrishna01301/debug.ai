import { SearchResult } from './interfaces';

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  totalResults: number;
}

const SearchResults = ({ results, query, totalResults }: SearchResultsProps) => {
  // Handle case where results might be undefined or empty
  if (!results || results.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
        <div className="text-center py-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Results Found</h2>
          <p className="text-gray-600">
            No matching solutions found for your error. Try a different error message.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Search Results</h2>
        <p className="text-sm text-gray-600 mt-1">
          Found {totalResults} results for: <span className="font-semibold">{query}</span>
        </p>
      </div>

      <div className="space-y-4">
        {results.map((result, index) => (
        <div
          key={index}
          className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 transition"
        >
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {result.title}
            </h3>
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              Score: {(1 - result.distance).toFixed(3)}
            </span>
          </div>

          <p className="text-sm text-gray-700 mb-3 leading-relaxed">
            {result.content}
          </p>

          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-2">
              {result.tags.map((tag, tagIndex) => (
                <span
                  key={tagIndex}
                  className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>

            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500">
                {result.votes} votes
              </span>
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-800 underline"
              >
                View on Stack Overflow
              </a>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
  );
};

export default SearchResults;
