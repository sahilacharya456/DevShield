import React, { useState } from 'react';
import { Shield, Code, Cpu, Activity } from 'lucide-react';
import { securityApi } from '../api';

const Dashboard: React.FC = () => {
  const [code, setCode] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    setLoading(true);
    try {
      const data = await securityApi.scanCode(code, 'python');
      setResults(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="flex items-center space-x-3 mb-8">
        <Shield className="w-10 h-10 text-emerald-400" />
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-blue-500">
          DevShield Enterprise
        </h1>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* IDE Section */}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 shadow-2xl">
          <div className="flex items-center space-x-2 text-gray-400 mb-4 pb-2 border-b border-gray-700">
            <Code className="w-5 h-5" />
            <span>Code Input</span>
          </div>
          
          <textarea
            className="w-full h-96 bg-[#1e1e1e] text-emerald-300 font-mono p-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            placeholder="Paste code here to trigger multi-engine analysis..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />

          <button 
            onClick={handleScan}
            disabled={loading || !code}
            className="mt-4 w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold py-3 px-4 rounded transition-all flex items-center justify-center space-x-2"
          >
            <Activity className="w-5 h-5" />
            <span>{loading ? 'Running AI & AST Scan...' : 'Analyze Code'}</span>
          </button>
        </div>

        {/* Results Section */}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 shadow-2xl overflow-y-auto max-h-[600px]">
           <div className="flex items-center space-x-2 text-gray-400 mb-4 pb-2 border-b border-gray-700">
            <Cpu className="w-5 h-5" />
            <span>Security Pipeline Engine</span>
          </div>

          {results ? (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-gray-700/50 flex justify-between items-center border border-gray-600">
                <span className="text-xl font-semibold">Vulnerabilities Found</span>
                <span className="text-3xl font-bold text-red-400">{results.total_issues || 0}</span>
              </div>
              
              {results.vulnerabilities?.map((vuln: any, idx: number) => (
                <div key={idx} className="bg-red-900/20 border border-red-500/30 p-4 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-red-400">{vuln.name}</h3>
                    <span className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">Line {vuln.line}</span>
                  </div>
                  <p className="text-gray-300 text-sm mb-3">{vuln.description}</p>
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>Source: {vuln.source}</span>
                    <button className="text-emerald-400 hover:text-emerald-300 flex items-center space-x-1">
                      <Cpu className="w-3 h-3" />
                      <span>Auto-Fix</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
             <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4 py-20">
               <Shield className="w-16 h-16 opacity-20" />
               <p>Awaiting code payload...</p>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
