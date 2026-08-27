import { useState, useCallback, useMemo } from "react";
import { useLocalStorage } from "./useLocalStorage";
import { initialHistory } from "../data/mockData";

export function useDecisionHistory() {
  const [history, setHistory] = useLocalStorage("supplyPrescriptHistory", initialHistory);

  const stats = useMemo(() => {
    const total = history.length;
    if (total === 0) {
      return { total: 0, positive: 0, accuracy: 0, avgPred: 0, avgActual: 0 };
    }
    const positive = history.filter(x => x.outcome === "Positive").length;
    const avgPred = history.reduce((a, x) => a + (x.predicted || 0), 0) / total;
    const avgActual = history.reduce((a, x) => a + (x.actual || x.predicted || 0), 0) / total;
    const accuracy = Math.round((positive / total) * 100);
    return { total, positive, accuracy, avgPred, avgActual };
  }, [history]);

  const addDecision = useCallback((decision) => {
    const newRecord = {
      id: Date.now(),
      date: new Date().toLocaleDateString("en-US", { day: "2-digit", month: "short", year: "numeric" }),
      option: decision.title,
      predicted: decision.cost,
      actual: null,
      outcome: "Pending",
      status: "Executed"
    };
    setHistory(prev => [newRecord, ...prev]);
    return newRecord;
  }, [setHistory]);

  const updateDecision = useCallback((id, updates) => {
    setHistory(prev => prev.map(record => 
      record.id === id ? { ...record, ...updates } : record
    ));
  }, [setHistory]);

  const resetHistory = useCallback(() => {
    setHistory(initialHistory);
  }, [setHistory]);

  const getDecisionById = useCallback((id) => {
    return history.find(record => record.id === id);
  }, [history]);

  const filterHistory = useCallback((filters) => {
    return history.filter(record => {
      if (filters.outcome && filters.outcome !== "all" && record.outcome !== filters.outcome) return false;
      if (filters.status && filters.status !== "all" && record.status !== filters.status) return false;
      if (filters.dateFrom && new Date(record.date) < new Date(filters.dateFrom)) return false;
      if (filters.dateTo && new Date(record.date) > new Date(filters.dateTo)) return false;
      return true;
    });
  }, [history]);

  const sortHistory = useCallback((records, sortBy, sortOrder) => {
    return [...records].sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      if (sortBy === "date") {
        aVal = new Date(aVal).getTime();
        bVal = new Date(bVal).getTime();
      }
      if (typeof aVal === "string") {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }
      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, []);

  return {
    history,
    stats,
    addDecision,
    updateDecision,
    resetHistory,
    getDecisionById,
    filterHistory,
    sortHistory
  };
}