'use client';

import { useRef, useEffect, useState } from 'react';

/**
 * Universal wrapper for D3 charts that use the Draw pattern
 * Handles loading, drawing, and provides ref access for animations
 */
export default function ChartWrapper({ 
  chartConfig,
  className = '',
  onChartReady 
}) {
  const containerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!chartConfig || !containerRef.current) return;

    const loadAndDrawChart = async () => {
      try {
        setIsLoading(true);
        
        // Load data if loader function provided
        let data = chartConfig.data;
        if (chartConfig.loadData) {
          data = await chartConfig.loadData();
        }

        // Clear container
        containerRef.current.innerHTML = '';

        // Draw chart
        const svg = chartConfig.draw(data, chartConfig.options);
        
        // Append to container
        if (svg && svg.node) {
          containerRef.current.appendChild(svg.node());
        }

        setIsLoading(false);
        
        // Notify parent that chart is ready
        if (onChartReady) {
          onChartReady(containerRef.current.querySelector('svg'));
        }
      } catch (err) {
        console.error('Error loading chart:', err);
        setError(err.message);
        setIsLoading(false);
      }
    };

    loadAndDrawChart();
  }, [chartConfig, onChartReady]);

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        Error loading chart: {error}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef} 
      className={`chart-container ${className}`}
    />
  );
}
