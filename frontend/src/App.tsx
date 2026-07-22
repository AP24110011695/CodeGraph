import React from 'react';

function App(): React.JSX.Element {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">CodeGraph</h1>
        <p className="text-xl text-gray-600 mb-8">
          The AI Software Architect for Every Codebase
        </p>
        <button
          type="button"
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          Coming Soon
        </button>
      </div>
    </div>
  );
}

export default App;
