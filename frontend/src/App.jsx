import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const EXAMPLES = [
  "What are the top 3 products by sales?",
  "What is the total revenue from all orders?",
  "Which city has the most customers?",
];

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const handleAnalyze = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setCopied(false);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Analysis failed.");
      }

      setResult(data);
    } catch (error) {
      console.error("Analysis error:", error);

      setError(
        error.message ||
          "Unable to analyze the question. Please make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleExample = (example) => {
    setQuestion(example);
    setError("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleAnalyze();
    }
  };

  const copySQL = async () => {
    if (!result?.sql) return;

    try {
      await navigator.clipboard.writeText(result.sql);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (error) {
      console.error("Copy failed:", error);
    }
  };

  const formatValue = (value, key = "") => {
    if (value === null || value === undefined) {
      return "—";
    }

    if (
      typeof value === "number" &&
      (key.toLowerCase().includes("sales") ||
        key.toLowerCase().includes("revenue") ||
        key.toLowerCase().includes("amount") ||
        key.toLowerCase().includes("price"))
    ) {
      return `$${value.toLocaleString()}`;
    }

    if (typeof value === "number") {
      return value.toLocaleString();
    }

    return String(value);
  };

  const getColumnName = (key) => {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  return (
    <div className="app">
      {/* ================= HEADER ================= */}
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-mark">
              <span>✦</span>
            </div>

            <div>
              <div className="brand-name">AI Data Intelligence</div>
              <div className="brand-subtitle">
                Natural language analytics for your business data
              </div>
            </div>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            <span>AI Online</span>
          </div>
        </div>
      </header>

      {/* ================= MAIN ================= */}
      <main className="main">
        {/* HERO */}
        <section className="hero">
          <div className="hero-badge">AI-POWERED ANALYTICS</div>

          <h1>
            Ask your data.
            <br />
            <span>Get answers instantly.</span>
          </h1>

          <p>
            Ask questions in plain English and let AI generate SQL, query
            PostgreSQL, and turn your data into actionable insights.
          </p>
        </section>

        {/* QUERY CARD */}
        <section className="query-card">
          <div className="query-header">
            <div>
              <div className="section-label">ASK YOUR DATA</div>

              <h2>What would you like to know?</h2>

              <p>
                Describe your business question naturally. No SQL required.
              </p>
            </div>
          </div>

          <div className="query-input-wrapper">
            <input
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Example: What are the top 3 products by sales?"
              disabled={loading}
            />

            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                <>
                  Analyze
                  <span className="button-arrow">→</span>
                </>
              )}
            </button>
          </div>

          <div className="examples">
            <span className="examples-label">Try an example</span>

            <div className="example-buttons">
              {EXAMPLES.map((example) => (
                <button
                  key={example}
                  onClick={() => handleExample(example)}
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* ERROR */}
        {error && (
          <section className="error-card">
            <div className="error-icon">!</div>

            <div>
              <h3>Analysis failed</h3>
              <p>{error}</p>
            </div>
          </section>
        )}

        {/* LOADING */}
        {loading && (
          <section className="loading-card">
            <div className="loading-animation">
              <div className="loading-spinner"></div>
            </div>

            <div>
              <h3>Analyzing your data</h3>
              <p>
                AI is generating SQL and querying your PostgreSQL database.
              </p>
            </div>
          </section>
        )}

        {/* RESULTS */}
        {result && !loading && (
          <div className="results-container">
            {/* ================= INSIGHT ================= */}
            {result.insight && (
              <section className="insight-card">
                <div className="insight-icon">✦</div>

                <div className="insight-content">
                  <div className="section-label">AI BUSINESS INSIGHT</div>

                  <h2>What the data tells you</h2>

                  <p>{result.insight}</p>
                </div>
              </section>
            )}

            {/* ================= RESULTS TABLE ================= */}
            {Array.isArray(result.results) && result.results.length > 0 && (
              <section className="results-card">
                <div className="card-header">
                  <div>
                    <div className="section-label">QUERY RESULTS</div>

                    <h2>Analysis results</h2>
                  </div>

                  <div className="result-count">
                    {result.results.length}{" "}
                    {result.results.length === 1 ? "result" : "results"}
                  </div>
                </div>

                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(result.results[0]).map((key) => (
                          <th key={key}>{getColumnName(key)}</th>
                        ))}
                      </tr>
                    </thead>

                    <tbody>
                      {result.results.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {Object.entries(row).map(([key, value]) => (
                            <td key={key}>{formatValue(value, key)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {/* ================= SQL ================= */}
            {result.sql && (
              <section className="sql-card">
                <div className="card-header">
                  <div>
                    <div className="section-label">GENERATED SQL</div>

                    <h2>Query executed against PostgreSQL</h2>
                  </div>

                  <button className="copy-button" onClick={copySQL}>
                    {copied ? "✓ Copied" : "Copy SQL"}
                  </button>
                </div>

                <div className="sql-container">
                  <pre>
                    <code>{result.sql}</code>
                  </pre>
                </div>
              </section>
            )}

            {/* ================= QUERY DETAILS ================= */}
            <section className="details-card">
              <div className="detail-item">
                <span className="detail-label">QUESTION</span>
                <span className="detail-value">
                  {result.question || question}
                </span>
              </div>

              <div className="detail-item">
                <span className="detail-label">DATABASE</span>
                <span className="detail-value">PostgreSQL</span>
              </div>

              <div className="detail-item">
                <span className="detail-label">AI ENGINE</span>
                <span className="detail-value">Ollama</span>
              </div>

              <div className="detail-item">
                <span className="detail-label">STATUS</span>
                <span className="detail-value success">
                  <span className="mini-dot"></span>
                  Query successful
                </span>
              </div>
            </section>
          </div>
        )}

        {/* EMPTY STATE */}
        {!result && !loading && !error && (
          <section className="empty-state">
            <div className="empty-icon">✦</div>

            <h2>Your data is ready to explore</h2>

            <p>
              Start with a question above and AI will transform your natural
              language into a database analysis.
            </p>

            <div className="workflow">
              <div className="workflow-item">
                <span>01</span>
                <strong>Natural language</strong>
              </div>

              <div className="workflow-line"></div>

              <div className="workflow-item">
                <span>02</span>
                <strong>AI-generated SQL</strong>
              </div>

              <div className="workflow-line"></div>

              <div className="workflow-item">
                <span>03</span>
                <strong>Business insights</strong>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* ================= FOOTER ================= */}
      <footer className="footer">
        <div className="footer-brand">AI Data Intelligence</div>

        <div className="footer-tech">
          FastAPI · PostgreSQL · Ollama · React
        </div>

        <div className="footer-text">
          Intelligent analytics powered by your data
        </div>
      </footer>
    </div>
  );
}

export default App;