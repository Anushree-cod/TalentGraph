import { createContext, useCallback, useContext, useMemo, useState } from 'react';

const STORAGE_KEY = 'talentgraph-analysis-result';

const AnalysisContext = createContext(null);

function readStoredResult() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AnalysisProvider({ children }) {
  const [pendingAnalysis, setPendingAnalysis] = useState(null);
  const [analysisResult, setAnalysisResultState] = useState(() => readStoredResult());

  const setAnalysisResult = useCallback((result) => {
    setAnalysisResultState(result);
    if (result) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(result));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const clearPendingAnalysis = useCallback(() => {
    setPendingAnalysis(null);
  }, []);

  const value = useMemo(
    () => ({
      pendingAnalysis,
      setPendingAnalysis,
      analysisResult,
      setAnalysisResult,
      clearPendingAnalysis,
    }),
    [pendingAnalysis, analysisResult, setAnalysisResult, clearPendingAnalysis],
  );

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>;
}

export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error('useAnalysis must be used within AnalysisProvider');
  }
  return context;
}
