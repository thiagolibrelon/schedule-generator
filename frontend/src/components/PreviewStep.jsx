export default function PreviewStep({ imagemUrl, onVoltar, onNovo }) {
  const baixar = () => {
    const a = document.createElement("a")
    a.href = imagemUrl
    a.download = "cronograma.png"
    a.click()
  }

  return (
    <div className="step-card preview-card">
      <h2 className="step-titulo">✅ Cronograma Gerado!</h2>
      <p className="step-desc">Visualize e baixe o cronograma abaixo.</p>

      <div className="preview-acoes">
        <button className="btn-primario" onClick={baixar}>
          ⬇️ Baixar PNG
        </button>
        <button className="btn-ghost" onClick={onVoltar}>
          ← Editar
        </button>
        <button className="btn-ghost" onClick={onNovo}>
          + Novo Cronograma
        </button>
      </div>

      <div className="preview-img-wrapper">
        <img src={imagemUrl} alt="Cronograma gerado" className="preview-img" />
      </div>
    </div>
  )
}
