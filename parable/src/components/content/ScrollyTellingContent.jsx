'use client';

import { useRef, useState, useEffect } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useLenisGSAP } from '@/hooks/useLenisGSAP';
import ChartWrapper from './ChartWrapper';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

/**
 * Enhanced ScrollytellingSection Component
 * Supports multiple charts and flexible content configuration
 * 
 * @param {Object} props
 * @param {Array} props.charts - Array of chart configurations
 * @param {Array} props.steps - Array of step objects with content and animations
 * @param {Object} props.layout - Layout configuration (single-chart, multi-chart, etc.)
 * @param {boolean} props.showMarkers - Show ScrollTrigger markers for debugging
 */
export default function ScrollytellingContent({
  charts = [],
  steps = [],
  layout = 'single-chart', // 'single-chart', 'multi-chart', 'stacked'
  showMarkers = false,
  chartWrapperClassName = '',
  stepWrapperClassName = ''
}) {
  const chartWrapperRef = useRef(null);
  const scrollStepsRef = useRef(null);
  const [chartRefs, setChartRefs] = useState({});

  // Sync Lenis with GSAP
  useLenisGSAP();

  // Store chart SVG references
  const handleChartReady = (chartId, svg) => {
    setChartRefs(prev => ({
      ...prev,
      [chartId]: svg
    }));
  };

  // Pin chart and setup scroll animations
  useGSAP(() => {
    if (!chartWrapperRef.current || !scrollStepsRef.current) return;
    if (Object.keys(chartRefs).length === 0) return;

    const ctx = gsap.context(() => {
      // Pin the chart wrapper
      ScrollTrigger.create({
        trigger: chartWrapperRef.current,
        endTrigger: scrollStepsRef.current,
        start: 'center center',
        end: () => {
          const height = window.innerHeight;
          const chartHeight = chartWrapperRef.current.offsetHeight;
          return `bottom ${chartHeight + (height - chartHeight) / 2}px`;
        },
        pin: true,
        pinSpacing: false,
        markers: showMarkers,
        id: 'pin-chart',
      });

      // Setup animations for each step
      steps.forEach((step, index) => {
        const stepElement = document.getElementById(step.id);
        if (!stepElement) return;

        if (step.animations && Array.isArray(step.animations)) {
          // Multiple animations for this step
          step.animations.forEach((animConfig) => {
            const targetChart = chartRefs[animConfig.chartId];
            if (!targetChart || !animConfig.animation) return;

            const animation = animConfig.animation(targetChart, animConfig.data);
            
            ScrollTrigger.create({
              trigger: stepElement,
              start: animConfig.start || 'center center',
              end: animConfig.end || 'bottom center',
              onEnter: () => {
                if (animation && animation.play) animation.play();
              },
              onLeaveBack: () => {
                if (animation && animation.reverse) animation.reverse();
              },
              markers: showMarkers,
              id: `step-${index}-anim-${animConfig.chartId}`,
            });
          });
        } else if (step.animation) {
          // Single animation (backward compatibility)
          const targetChart = chartRefs[step.chartId || charts[0]?.id];
          if (!targetChart) return;

          const animation = step.animation(targetChart, step.animationData);
          
          ScrollTrigger.create({
            trigger: stepElement,
            start: 'center center',
            end: 'bottom center',
            onEnter: () => {
              if (animation && animation.play) animation.play();
            },
            onLeaveBack: () => {
              if (animation && animation.reverse) animation.reverse();
            },
            markers: showMarkers,
            id: `step-${index}`,
          });
        }
      });
    });

    return () => ctx.revert();
  }, [steps, chartRefs, showMarkers]);

  // Render charts based on layout
  const renderCharts = () => {
    if (layout === 'single-chart' && charts.length > 0) {
      return (
        <ChartWrapper
          chartConfig={charts[0]}
          onChartReady={(svg) => handleChartReady(charts[0].id, svg)}
        />
      );
    }

    if (layout === 'multi-chart') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {charts.map((chart) => (
            <div key={chart.id} className="chart-item">
              {chart.title && (
                <h3 className="text-lg font-semibold mb-4 text-center">
                  {chart.title}
                </h3>
              )}
              <ChartWrapper
                chartConfig={chart}
                onChartReady={(svg) => handleChartReady(chart.id, svg)}
              />
            </div>
          ))}
        </div>
      );
    }

    if (layout === 'stacked') {
      return (
        <div className="space-y-8">
          {charts.map((chart) => (
            <div key={chart.id} className="chart-item">
              {chart.title && (
                <h3 className="text-lg font-semibold mb-4 text-center">
                  {chart.title}
                </h3>
              )}
              <ChartWrapper
                chartConfig={chart}
                onChartReady={(svg) => handleChartReady(chart.id, svg)}
              />
            </div>
          ))}
        </div>
      );
    }

    return null;
  };

  return (
    <>
      <div 
        id="chart-wrapper" 
        ref={chartWrapperRef}
        className={`w-full flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-lg shadow-lg p-8 ${chartWrapperClassName}`}
      >
        {renderCharts()}
      </div>

      <article id="scroll-steps" ref={scrollStepsRef} className="relative">
        {steps.map((step) => (
          <section
            key={step.id}
            id={step.id}
            className={`step min-h-screen flex items-center justify-end pr-8 md:pr-16 ${stepWrapperClassName}`}
          >
            <div className="max-w-md bg-white/90 backdrop-blur-sm p-8 rounded-lg shadow-lg">
              {step.content}
            </div>
          </section>
        ))}
      </article>
    </>
  );
}
