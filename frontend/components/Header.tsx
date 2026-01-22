import Link from 'next/link';

const Header = () => (
  <div className="relative mb-8">
    <Link
      href="/analytics"
      className="absolute right-0 top-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
      </svg>
      Analytics
    </Link>
    <div className="text-center">
      <h1 className="text-5xl font-bold text-gray-900 mb-2">DebugAI</h1>
      <p className="text-xl text-gray-600">
        Intelligent Error Analysis with RAG-Powered Solutions
      </p>
      <p className="text-xs text-gray-600">
        Optimized for Python and JavaScript errors. Other languages fallback to LLM analysis.
      </p>
    </div>
  </div>
);

export default Header;
