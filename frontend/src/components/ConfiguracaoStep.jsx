export default function ConfiguracaoStep({ config, onChange, onAvancar }) {
  const set = (k, v) => onChange(prev => ({ ...prev, [k]: v }))

  const valido = config.titulo.trim().length > 0

  return (
    <div className="step-card">
      <h2 className="step-titulo">Configuração do Cronograma</h2>
      <p className="step-desc">Defina as configurações gerais antes de começar.</p>

      <div className="form-grupo">
        <label>Título do Projeto *</label>
        <input
          type="text"
          value={config.titulo}
          onChange={e => set("titulo", e.target.value)}
          placeholder="Ex: J1U - PROJETO X"
          className="input"
        />
      </div>

      <div className="form-linha">
        <div className="form-grupo">
          <label>Largura das Semanas</label>
          <select value={config.largura_semana} onChange={e => set("largura_semana", parseFloat(e.target.value))} className="input">
            <option value={1}>Padrão</option>
            <option value={1.5}>50% maior</option>
            <option value={2}>Dobro</option>
          </select>
        </div>

        <div className="form-grupo">
          <label>Fonte dos Milestones</label>
          <input
            type="number"
            min={8} max={20}
            value={config.tamanho_fonte_milestone}
            onChange={e => set("tamanho_fonte_milestone", parseInt(e.target.value))}
            className="input"
          />
        </div>
      </div>

      <div className="form-grupo">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={config.gerar_legenda}
            onChange={e => set("gerar_legenda", e.target.checked)}
          />
          <span>Gerar legenda (Components + Milestones)</span>
        </label>
      </div>

      <div className="step-acoes">
        <button className="btn-primario" onClick={onAvancar} disabled={!valido}>
          Próximo →
        </button>
      </div>
    </div>
  )
}
