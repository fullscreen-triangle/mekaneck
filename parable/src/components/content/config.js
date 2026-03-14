import * as d3 from 'd3';
import { 
  CirclePackingLoad, 
  CirclePackingDraw 
} from '@/components/charts/CirclePacking';
import { 
  SankeyChartLoad, 
  SankeyChartDraw 
} from '@/components/charts/SankeyChart';
import { 
  StackedSteamgraphLoad, 
  StackedSteamgraphDraw 
} from '@/components/charts/StackedStreamGraph';
import { 
  histogramAnimations, 
  scatterPlotAnimations,
  timelineAnimations,
  generalAnimations 
} from '@/utils/chartAnimations';

// ============================================
// EXAMPLE 1: Single Chart Story
// ============================================
export const circlePackingStory = {
  id: 'circle-packing-story',
  title: 'Understanding Hierarchical Data',
  subtitle: 'Exploring Circle Packing Visualization',
  layout: 'single-chart',
  
  charts: [
    {
      id: 'circle-pack-main',
      title: 'Circle Packing',
      loadData: CirclePackingLoad,
      draw: CirclePackingDraw,
      options: {
        width: 800,
        height: 600,
        fill: '#4f46e5',
        stroke: '#312e81',
      }
    }
  ],

  steps: [
    {
      id: 'step-1',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Introduction</h3>
          <p className="text-lg mb-4">
            Circle packing is a method of visualizing hierarchical data using 
            nested circles. Each circle represents a node in the hierarchy.
          </p>
          <p className="text-sm text-gray-600">
            Watch as the circles fade in and scale up.
          </p>
        </>
      ),
      chartId: 'circle-pack-main',
      animation: (svg) => {
        const circles = d3.select(svg).selectAll('circle');
        
        return gsap.from(circles.nodes(), {
          attr: { r: 0 },
          opacity: 0,
          duration: 1.5,
          stagger: 0.05,
          ease: 'elastic.out(1, 0.5)',
          paused: true,
        });
      }
    },
    {
      id: 'step-2',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Hierarchy Levels</h3>
          <p className="text-lg mb-4">
            The size of each circle represents its value in the hierarchy. 
            Larger circles contain smaller circles, showing parent-child relationships.
          </p>
        </>
      ),
      chartId: 'circle-pack-main',
      animation: (svg) => {
        const circles = d3.select(svg).selectAll('circle');
        
        return gsap.to(circles.nodes(), {
          attr: { 
            stroke: '#ef4444',
            'stroke-width': 3 
          },
          duration: 0.8,
          stagger: 0.03,
          ease: 'power2.inOut',
          paused: true,
        });
      }
    },
    {
      id: 'step-3',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Interactive Exploration</h3>
          <p className="text-lg mb-4">
            Circle packing allows for efficient use of space while maintaining 
            the hierarchical structure of the data.
          </p>
        </>
      ),
      chartId: 'circle-pack-main',
      animation: (svg) => {
        const text = d3.select(svg).selectAll('text');
        
        return gsap.from(text.nodes(), {
          opacity: 0,
          scale: 0,
          duration: 0.8,
          stagger: 0.05,
          ease: 'back.out(1.7)',
          paused: true,
        });
      }
    }
  ]
};

// ============================================
// EXAMPLE 2: Multiple Charts Story
// ============================================
export const multiChartStory = {
  id: 'multi-chart-story',
  title: 'Comparing Data Flows',
  subtitle: 'Sankey and Streamgraph Analysis',
  layout: 'multi-chart',
  
  charts: [
    {
      id: 'sankey-chart',
      title: 'Energy Flow (Sankey)',
      loadData: SankeyChartLoad,
      draw: SankeyChartDraw,
      options: {
        width: 600,
        height: 500,
      }
    },
    {
      id: 'streamgraph-chart',
      title: 'Trends Over Time (Streamgraph)',
      loadData: StackedSteamgraphLoad,
      draw: StackedSteamgraphDraw,
      options: {
        width: 600,
        height: 500,
      }
    }
  ],

  steps: [
    {
      id: 'step-1',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Two Perspectives</h3>
          <p className="text-lg mb-4">
            We are comparing two different ways to visualize flow and change:
            Sankey diagrams and Streamgraphs.
          </p>
        </>
      ),
      animations: [
        {
          chartId: 'sankey-chart',
          animation: (svg) => {
            const links = d3.select(svg).selectAll('path.link');
            return gsap.from(links.nodes(), {
              opacity: 0,
              duration: 1.5,
              stagger: 0.1,
              ease: 'power2.out',
              paused: true,
            });
          }
        },
        {
          chartId: 'streamgraph-chart',
          animation: (svg) => {
            const paths = d3.select(svg).selectAll('path');
            return gsap.from(paths.nodes(), {
              opacity: 0,
              duration: 1.5,
              stagger: 0.1,
              ease: 'power2.out',
              paused: true,
            });
          }
        }
      ]
    },
    {
      id: 'step-2',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Flow Analysis</h3>
          <p className="text-lg mb-4">
            The Sankey diagram shows how energy flows between different sources 
            and uses, with the width representing quantity.
          </p>
        </>
      ),
      animations: [
        {
          chartId: 'sankey-chart',
          animation: (svg) => {
            const nodes = d3.select(svg).selectAll('rect');
            return gsap.to(nodes.nodes(), {
              attr: { fill: '#22c55e' },
              duration: 0.8,
              stagger: 0.05,
              ease: 'power2.inOut',
              paused: true,
            });
          }
        }
      ]
    },
    {
      id: 'step-3',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Temporal Patterns</h3>
          <p className="text-lg mb-4">
            The Streamgraph reveals patterns over time, showing how different 
            categories ebb and flow.
          </p>
        </>
      ),
      animations: [
        {
          chartId: 'streamgraph-chart',
          animation: (svg) => {
            const paths = d3.select(svg).selectAll('path');
            return gsap.to(paths.nodes(), {
              attr: { 'fill-opacity': 0.9 },
              duration: 0.8,
              stagger: 0.05,
              ease: 'power2.inOut',
              paused: true,
            });
          }
        }
      ]
    }
  ]
};

// ============================================
// EXAMPLE 3: Stacked Charts Story
// ============================================
export const stackedChartsStory = {
  id: 'stacked-charts-story',
  title: 'Data Journey',
  subtitle: 'From Hierarchy to Flow',
  layout: 'stacked',
  
  charts: [
    {
      id: 'circle-pack',
      title: 'Step 1: Hierarchical Structure',
      loadData: CirclePackingLoad,
      draw: CirclePackingDraw,
      options: {
        width: 700,
        height: 400,
      }
    },
    {
      id: 'sankey',
      title: 'Step 2: Flow Relationships',
      loadData: SankeyChartLoad,
      draw: SankeyChartDraw,
      options: {
        width: 700,
        height: 400,
      }
    },
    {
      id: 'streamgraph',
      title: 'Step 3: Temporal Evolution',
      loadData: StackedSteamgraphLoad,
      draw: StackedSteamgraphDraw,
      options: {
        width: 700,
        height: 400,
      }
    }
  ],

  steps: [
    {
      id: 'step-1',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Starting Point</h3>
          <p className="text-lg mb-4">
            We begin with understanding the hierarchical structure of our data.
          </p>
        </>
      ),
      animations: [
        {
          chartId: 'circle-pack',
          animation: (svg) => generalAnimations.scaleUp(svg)
        }
      ]
    },
    {
      id: 'step-2',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Understanding Flows</h3>
          <p className="text-lg mb-4">
            Next, we examine how data flows between different entities.
          </p>
        </>
      ),
      animations: [
        {
          chartId: 'sankey',
          animation: (svg) => generalAnimations.fadeIn(svg)
        }
      ]
    },
    {
      id: 'step-3',
      content: (
        <>
          <h3 className="text-2xl font-bold mb-4">Temporal Perspective</h3>
          <p className="text-lg mb-4">
            Finally, we see how these patterns evolve over time.
          </p>
        </>
      ),
      animations: [
        {
          chartId: 'streamgraph',
          animation: (svg) => generalAnimations.fadeIn(svg)
        }
      ]
    }
  ]
};

// ============================================
// Export all stories
// ============================================
export const allStories = {
  circlePackingStory,
  multiChartStory,
  stackedChartsStory,
};
