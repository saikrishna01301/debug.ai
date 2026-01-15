// Note: This component should be in a 'components' directory.
import { Solution } from './interfaces';
import SolutionCard from './SolutionCard';

interface SolutionsProps {
  solutions: Solution[];
  sources_used: number;
}

const Solutions = ({ solutions, sources_used }: SolutionsProps) => (
  <div className="bg-white rounded-xl shadow-lg p-6">
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-2xl font-bold text-gray-900">Solutions</h2>
      <span className="text-sm text-gray-500">
        Based on {sources_used} sources from Stack Overflow
      </span>
    </div>

    <div className="space-y-4">
      {solutions.map((solution, index) => (
        <SolutionCard key={index} solution={solution} index={index} />
      ))}
    </div>
  </div>
);

export default Solutions;
