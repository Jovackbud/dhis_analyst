/**
 * Dashboard component — renders Plotly charts from chart_config SSE events.
 * Uses plotly.js-dist-min for the actual rendering.
 */
import { useEffect, useRef } from 'preact/hooks';
import Plotly from 'plotly.js-dist-min';

export default function Dashboard({ charts }) {
  return (
    <div class="chart-grid">
      {charts.map((chart) => (
        <ChartPanel key={chart.id} chart={chart} />
      ))}
    </div>
  );
}

function ChartPanel({ chart }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const traces = buildTraces(chart);
    const layout = {
      ...(chart.layout || {}),
      autosize: true,
      height: 360,
    };
    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    };

    Plotly.react(containerRef.current, traces, layout, config);

    return () => {
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [chart]);

  return (
    <div
      class="chart-container"
      ref={containerRef}
      id={`chart-${chart.id}`}
    />
  );
}

function buildTraces(chart) {
  const series = chart.series || [];
  const type = chart.type || 'bar';

  return series.map((s) => {
    if (type === 'pie') {
      return {
        type: 'pie',
        labels: s.labels || [],
        values: s.values || [],
        hole: 0.35,
        marker: {
          colors: [
            '#38bdf8', '#34d399', '#fbbf24', '#f87171',
            '#a78bfa', '#fb923c', '#22d3ee', '#e879f9',
          ],
        },
        textfont: { color: '#f1f5f9', size: 12 },
      };
    }

    if (type === 'table') {
      return {
        type: 'table',
        header: {
          values: s.header || [],
          fill: { color: '#0f2028' },
          font: { color: '#f1f5f9', size: 12 },
          align: 'left',
        },
        cells: {
          values: s.cells || [],
          fill: { color: ['#0b171d', '#0d1d25'] },
          font: { color: '#94a3b8', size: 11 },
          align: 'left',
        },
      };
    }

    // bar, line, scatter
    const trace = {
      type: type === 'line' ? 'scatter' : type,
      mode: type === 'line' ? 'lines+markers' : (s.mode || undefined),
      x: s.x || [],
      y: s.y || [],
      name: s.name || '',
    };

    if (type === 'bar') {
      trace.marker = {
        color: 'rgba(56, 189, 248, 0.7)',
        line: { color: '#38bdf8', width: 1 },
      };
    }

    if (type === 'line') {
      trace.line = { color: '#34d399', width: 2.5 };
      trace.marker = { color: '#34d399', size: 6 };
    }

    return trace;
  });
}
