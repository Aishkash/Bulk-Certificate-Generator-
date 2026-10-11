import { useState, useEffect, useMemo, useRef, useCallback } from "react";
import Form from "./Form";
import Dashboard from "./Dashboard";

const WORDS = ["stunning", "polished", "effortless", "unforgettable"];
const GLOWS = ["soft", "neon", "ultra"];
const CONFETTI_COLORS = ["#ff2d95", "#ff6ec7", "#ffb3d9", "#ffe4f1", "#ffffff", "#ffd166"];

export default function App() {
  const [job, setJob] = useState(null); // response of POST /jobs
  const [glow, setGlow] = useState("neon");
  const [sparkles, setSparkles] = useState(true);
  const [wordIndex, setWordIndex] = useState(0);
  const [bursts, setBursts] = useState([]);
  const [toast, setToast] = useState("");
  const idRef = useRef(0);
  const toastTimer = useRef(null);

  /* ---------- glow intensity: drives CSS via data-glow ---------- */
  useEffect(() => {
    document.documentElement.dataset.glow = glow;
  }, [glow]);

  /* ---------- rotating word in the hero ---------- */
  useEffect(() => {
    const t = setInterval(() => setWordIndex((i) => (i + 1) % WORDS.length), 2200);
    return () => clearInterval(t);
  }, []);

  /* ---------- confetti ---------- */
  const burst = useCallback((x, y) => {
    const id = ++idRef.current;
    const pieces = Array.from({ length: 30 }, (_, i) => {
      const angle = Math.random() * Math.PI * 2;
      const dist = 70 + Math.random() * 150;
      return {
        i,
        dx: Math.cos(angle) * dist,
        dy: Math.sin(angle) * dist - 50,
        rot: Math.random() * 720 - 360,
        size: 6 + Math.random() * 6,
        color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
      };
    });
    setBursts((b) => [...b, { id, x, y, pieces }]);
    setTimeout(() => setBursts((b) => b.filter((p) => p.id !== id)), 1400);
  }, []);

  const showToast = useCallback((msg) => {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(""), 3200);
  }, []);

  const handleCreated = (data) => {
    setJob(data);
    burst(window.innerWidth / 2, window.innerHeight / 3);
    showToast("Job created. Your certificates are on the way.");
  };

  /* ---------- global effects: spotlight, card tilt, button ripple ---------- */
  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const root = document.documentElement;
    let raf = 0;

    const onMove = (e) => {
      if (reduced) return;
      const { clientX, clientY } = e;
      const card = e.target.closest?.(".card");
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        root.style.setProperty("--mx", clientX + "px");
        root.style.setProperty("--my", clientY + "px");
        if (card) {
          const r = card.getBoundingClientRect();
          const px = (clientX - r.left) / r.width;
          const py = (clientY - r.top) / r.height;
          card.style.setProperty("--ry", (px - 0.5) * 6 + "deg");
          card.style.setProperty("--rx", (0.5 - py) * 6 + "deg");
          card.style.setProperty("--cx", px * 100 + "%");
          card.style.setProperty("--cy", py * 100 + "%");
        }
      });
    };

    const onOut = (e) => {
      const card = e.target.closest?.(".card");
      if (card && !card.contains(e.relatedTarget)) {
        card.style.setProperty("--rx", "0deg");
        card.style.setProperty("--ry", "0deg");
      }
    };

    const onClick = (e) => {
      const btn = e.target.closest?.("button");
      if (!btn || btn.disabled) return;
      const r = btn.getBoundingClientRect();
      const size = Math.max(r.width, r.height);
      const dot = document.createElement("span");
      dot.className = "ripple";
      dot.style.width = dot.style.height = size + "px";
      dot.style.left = e.clientX - r.left - size / 2 + "px";
      dot.style.top = e.clientY - r.top - size / 2 + "px";
      btn.appendChild(dot);
      setTimeout(() => dot.remove(), 650);
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseout", onOut);
    window.addEventListener("click", onClick);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseout", onOut);
      window.removeEventListener("click", onClick);
    };
  }, []);

  /* ---------- floating sparkles (generated once) ---------- */
  const sparkleItems = useMemo(
    () =>
      Array.from({ length: 16 }, (_, i) => ({
        i,
        left: Math.random() * 100,
        top: Math.random() * 100,
        size: 10 + Math.random() * 16,
        delay: Math.random() * 6,
        dur: 5 + Math.random() * 6,
        ch: i % 3 === 0 ? "✧" : "✦",
      })),
    []
  );

  return (
    <>
      <div className="spotlight" aria-hidden="true" />

      {sparkles && (
        <div className="sparkles" aria-hidden="true">
          {sparkleItems.map((s) => (
            <span
              key={s.i}
              style={{
                left: s.left + "%",
                top: s.top + "%",
                fontSize: s.size,
                animationDelay: s.delay + "s",
                animationDuration: s.dur + "s",
              }}
            >
              {s.ch}
            </span>
          ))}
        </div>
      )}

      <div className="app">
        <header>
          <h1
            className="logo"
            title="Click me!"
            onClick={(e) => burst(e.clientX, e.clientY)}
          >
            Certificate Generator
          </h1>

          <div className="toolbar">
            <div className="seg" role="group" aria-label="Glow intensity">
              {GLOWS.map((g) => (
                <button
                  key={g}
                  type="button"
                  className={"seg-btn" + (glow === g ? " active" : "")}
                  aria-pressed={glow === g}
                  onClick={() => setGlow(g)}
                >
                  {g}
                </button>
              ))}
            </div>

            <button
              type="button"
              className={"seg-btn toggle" + (sparkles ? " active" : "")}
              aria-pressed={sparkles}
              onClick={() => setSparkles((s) => !s)}
              title="Toggle sparkles"
            >
              ✦
            </button>

            {job && (
              <button className="ghost" onClick={() => setJob(null)}>
                + New job
              </button>
            )}
          </div>
        </header>

        {job ? (
          <Dashboard job={job} />
        ) : (
          <>
            <section className="hero">
              <h2 className="hero-title">
                Make certificates that look{" "}
                <span className="rotator" key={WORDS[wordIndex]}>
                  {WORDS[wordIndex]}
                </span>
              </h2>
              <p className="hero-sub">
                Fill in the details below and watch your job run live.
              </p>
            </section>
            <Form onCreated={handleCreated} />
          </>
        )}
      </div>

      {/* confetti layer */}
      {bursts.map((b) => (
        <div key={b.id} className="confetti" style={{ left: b.x, top: b.y }} aria-hidden="true">
          {b.pieces.map((p) => (
            <span
              key={p.i}
              style={{
                "--dx": p.dx + "px",
                "--dy": p.dy + "px",
                "--rot": p.rot + "deg",
                width: p.size,
                height: p.size * 0.5,
                background: p.color,
              }}
            />
          ))}
        </div>
      ))}

      {/* toast */}
      {toast && (
        <div className="toast" role="status">
          {toast}
        </div>
      )}
    </>
  );
}