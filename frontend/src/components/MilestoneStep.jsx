import { useState } from "react"

const TIPOS = ["Main Milestone", "Milestone", "Phase"]
const CORES = [
  { valor: 1, label: "Azul Escuro" },
  { valor: 2, label: "Amarelo" },
  { valor: 3, label: "Laranja" },
]

const VAZIA_ML = { descricao: "", tipo: "Main Milestone", data_inicial: "", data_final: "", nivel: 0, cor: 1 }
const VAZIA_LIVRE = { nome: "", tipo: "Attention Point", data: "", componente: "", nivel: 0, posicao: 0 }

const STATUS_LIVRE = ["Attention Point", "Concluded", "Concluded Delay", "Delayed", "Ontime"]

export default function MilestoneStep({
  milestones, milestonesLivres,
  onChangeMilestones, onChangeLivres,
  onGerar, onVoltar, carregando, erro
}) {
  const [formML, setFormML] = useState(VAZIA_ML)
  const [formLivre, setFormLivre] = useState(VAZIA_LIVRE)
  const [aba, setAba] = useState("milestones")

  const setML = (k, v) => setFormML(p => ({ ...p, [k]: v }))
  const setLivre = (k, v) => setFormLivre(p => ({ ...p, [k]: v }))

  const adicionarML = () => {
    if (!formML.descricao || !formML.data_inicial) return
    onChangeMilestones(p => [...p, formML])
    setFormML(VAZIA_ML)
  }

  const adicionarLivre = () => {
    if (!formLivre.nome || !formLivre.data || !formLivre.componente) return
    onChangeLivres(p => [...p, formLivre])
    setFormLivre(VAZIA_LIVRE)
  }

  return (
    <div className="step-card">
      <h2 className="step-titulo">Milestones</h2>
      <p className="step-desc">Opcional — adicione marcos e milestones livres.</p>

      <div className="abas">
        <button className={`aba ${aba === "milestones" ? "ativa" : ""}`} onClick={() => setAba("milestones")}>
          Milestones do Cabeçalho ({milestones.length})
        </button>
        <button className={`aba ${aba === "livres" ? "ativa" : ""}`} onClick={() => setAba("livres")}>
          Milestones Livres ({milestonesLivres.length})
        </button>
      </div>

      {aba === "milestones" && (
        <div>
          <div className="form-grid">
            <div className="form-grupo span2">
              <label>Descrição *</label>
              <input value={formML.descricao} onChange={e => setML("descricao", e.target.value)} className="input" placeholder="Ex: N3/T3" />
            </div>
            <div className="form-grupo">
              <label>Tipo</label>
              <select value={formML.tipo} onChange={e => setML("tipo", e.target.value)} className="input">
                {TIPOS.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-grupo">
              <label>Cor</label>
              <select value={formML.cor} onChange={e => setML("cor", parseInt(e.target.value))} className="input">
                {CORES.map(c => <option key={c.valor} value={c.valor}>{c.label}</option>)}
              </select>
            </div>
            <div className="form-grupo">
              <label>Data Inicial *</label>
              <input type="date" value={formML.data_inicial} onChange={e => setML("data_inicial", e.target.value)} className="input" />
            </div>
            <div className="form-grupo">
              <label>Data Final (Phase)</label>
              <input type="date" value={formML.data_final} onChange={e => setML("data_final", e.target.value)} className="input" />
            </div>
            <div className="form-grupo">
              <label>Nível (0 ou 1)</label>
              <input type="number" min={0} max={1} value={formML.nivel} onChange={e => setML("nivel", parseInt(e.target.value))} className="input" />
            </div>
          </div>

          <button className="btn-secundario" onClick={adicionarML}>+ Adicionar Milestone</button>

          {milestones.length > 0 && (
            <div className="tabela-wrapper">
              <table className="tabela">
                <thead><tr><th>Descrição</th><th>Tipo</th><th>Data</th><th>Nível</th><th></th></tr></thead>
                <tbody>
                  {milestones.map((m, i) => (
                    <tr key={i}>
                      <td>{m.descricao}</td>
                      <td>{m.tipo}</td>
                      <td>{m.data_inicial}</td>
                      <td>{m.nivel}</td>
                      <td><button onClick={() => onChangeMilestones(p => p.filter((_, j) => j !== i))} className="btn-icon">🗑️</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {aba === "livres" && (
        <div>
          <div className="form-grid">
            <div className="form-grupo">
              <label>Nome *</label>
              <input value={formLivre.nome} onChange={e => setLivre("nome", e.target.value)} className="input" placeholder="Ex: Teste 5" />
            </div>
            <div className="form-grupo">
              <label>Tipo</label>
              <select value={formLivre.tipo} onChange={e => setLivre("tipo", e.target.value)} className="input">
                {STATUS_LIVRE.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-grupo">
              <label>Data *</label>
              <input type="date" value={formLivre.data} onChange={e => setLivre("data", e.target.value)} className="input" />
            </div>
            <div className="form-grupo">
              <label>Componente *</label>
              <input value={formLivre.componente} onChange={e => setLivre("componente", e.target.value)} className="input" placeholder="Ex: CC22 DARK EDITION" />
            </div>
            <div className="form-grupo">
              <label>Nível</label>
              <input type="number" min={0} max={10} value={formLivre.nivel} onChange={e => setLivre("nivel", parseInt(e.target.value))} className="input" />
            </div>
            <div className="form-grupo">
              <label>Posição Y</label>
              <input type="number" min={0} value={formLivre.posicao} onChange={e => setLivre("posicao", parseInt(e.target.value))} className="input" />
            </div>
          </div>

          <button className="btn-secundario" onClick={adicionarLivre}>+ Adicionar Milestone Livre</button>

          {milestonesLivres.length > 0 && (
            <div className="tabela-wrapper">
              <table className="tabela">
                <thead><tr><th>Nome</th><th>Componente</th><th>Data</th><th>Nível</th><th></th></tr></thead>
                <tbody>
                  {milestonesLivres.map((m, i) => (
                    <tr key={i}>
                      <td>{m.nome}</td>
                      <td>{m.componente}</td>
                      <td>{m.data}</td>
                      <td>{m.nivel}</td>
                      <td><button onClick={() => onChangeLivres(p => p.filter((_, j) => j !== i))} className="btn-icon">🗑️</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {erro && <p className="erro">⚠️ {erro}</p>}

      <div className="step-acoes">
        <button className="btn-ghost" onClick={onVoltar}>← Voltar</button>
        <button className="btn-primario" onClick={onGerar} disabled={carregando}>
          {carregando ? "⏳ Gerando..." : "🚀 Gerar Cronograma"}
        </button>
      </div>
    </div>
  )
}
