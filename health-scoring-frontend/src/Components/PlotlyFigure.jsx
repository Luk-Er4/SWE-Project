import { useEffect, useRef, useState } from "react";

const PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js";

let plotlyPromise = null;

function loadPlotly() {
  if (window.Plotly) {
    return Promise.resolve(window.Plotly);
  }

  if (!plotlyPromise) {
    plotlyPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = PLOTLY_CDN;
      script.async = true;
      script.onload = () => resolve(window.Plotly);
      script.onerror = () => reject(new Error("Unable to load Plotly."));
      document.head.appendChild(script);
    });
  }

  return plotlyPromise;
}

export default function PlotlyFigure({ figure }) {
  const containerRef = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    let resizeObserver = null;

    async function renderFigure() {
      if (!figure || !containerRef.current) {
        return;
      }

      try {
        setError("");
        const Plotly = await loadPlotly();

        if (ignore || !containerRef.current) {
          return;
        }

        await Plotly.react(
          containerRef.current,
          figure.data || [],
          {
            autosize: true,
            height: figure.layout?.height || 380,
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(12, 18, 28, 0.55)",
            font: {
              color: "#d7e1eb",
              family: "Segoe UI Variable, Aptos, sans-serif",
            },
            margin: { t: 48, r: 28, b: 56, l: 56 },
            ...figure.layout,
          },
          {
            displayModeBar: false,
            responsive: true,
            ...figure.config,
          }
        );

        resizeObserver = new ResizeObserver(() => {
          if (window.Plotly && containerRef.current) {
            window.Plotly.Plots.resize(containerRef.current);
          }
        });

        resizeObserver.observe(containerRef.current);
      } catch (plotError) {
        if (!ignore) {
          setError(plotError.message || "Unable to render dashboard figure.");
        }
      }
    }

    renderFigure();

    return () => {
      ignore = true;

      if (resizeObserver) {
        resizeObserver.disconnect();
      }

      if (window.Plotly && containerRef.current) {
        window.Plotly.purge(containerRef.current);
      }
    };
  }, [figure]);

  if (!figure) {
    return null;
  }

  if (error) {
    return <p className="muted">{error}</p>;
  }

  return <div ref={containerRef} className="plotly-chart" />;
}
