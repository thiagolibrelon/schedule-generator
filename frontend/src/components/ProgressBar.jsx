export default function ProgressBar({ steps, atual }) {
  return (
    <div className="progress-bar">
      {steps.map((s, i) => (
        <div key={i} className={`progress-step ${i === atual ? "ativo" : ""} ${i < atual ? "concluido" : ""}`}>
          <div className="progress-bolinha">{i < atual ? "✓" : i + 1}</div>
          <span className="progress-label">{s}</span>
          {i < steps.length - 1 && <div className="progress-linha" />}
        </div>
      ))}
    </div>
  )
}
