import { useState } from "react"

const STATUS = ["Ontime", "Delayed", "Concluded", "Concluded Delay", "Attention Point"]

const VAZIA = {
  componente: "", sistema: "", descricao: "",
  data_inicial: "", data_final: "", status: "Ontime",
  nivel: 0, milestone: "", milestone_data: "", milestone_status: ""
}

export default function AtividadesStep({ atividades, onChange, onAvancar, onVoltar }) {
  const [form, setForm] = useState(VAZIA)
  const [editIdx, setEditIdx] = useState(null)
  const [erro, setErro] = useState("")

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const validar = () => {
    if (!form.componente.trim()) return "Componente obrigatório"
    if (!form.descricao.trim())  return "Descrição obrigatória"
    if (!form.data_inicial)      return "Data inicial obrigatória"
    if (!form.data_final)        return "Data final obrigatória"
    if (form.data_final < form.data_inicial) return "Data final deve ser após a inicial"
    return ""
  }

  const salvar = () => {
    const e = validar()
    if (e) { setErro(e); return }
    setErro("")
    if (editIdx !== null) {
      onChange(prev => prev.map((a, i) => i === editIdx ? form : a))
      setEditIdx(null)
    } else {
      onChange(prev => [...prev, form])
    }
    setForm(VAZIA)
  }

  const editar = (i) => { setForm(atividades[i]); setEditIdx(i) }
  const remover = (i) => onChange(prev => prev.filter((_, idx) => idx !== i))

  return (
    <div className="step-card">
      <h2 className="step-titulo">Atividades</h2>
      <p className="step-desc">Adicione as atividades do cronograma.</p>

      <div className="form-grid">
        <div className="form-grupo">
          <label>Componente *</label>
          <input value={form.componente} onChange={e => set("componente", e.target.value)} className="input" placeholder="Ex: CC22 DARK EDITION" />
        </div>
        <div className="form-grupo">
          <label>Sistema</label>
          <input value={form.sistema} onChange={e => set("sistema", e.target.value)} className="input" placeholder="Ex: ENG DOC" />
        </div>
        <div className="form-grupo span2">
          <label>Descrição *</label>
          <input value={form.descricao} onChange={e => set("descricao", e.target.value)} className="input" placeholder="Ex: SOURCING (07/05)" />
        </div>
        <div className="form-grupo">
          <label>Data Inicial *</label>
          <input type="date" value={form.data_inicial} onChange={e => set("data_inicial", e.target.value)} className="input" />
        </div>
        <div className="form-grupo">
          <label>Data Final *</label>
          <input type="date" value={form.data_final} onChange={e => set("data_final", e.target.value)} className="input" />
        </div>
        <div className="form-grupo">
          <label>Status</label>
          <select value={form.status} onChange={e => set("status", e.target.value)} className="input">
            {STATUS.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="form-grupo">
          <label>Nível</label>
          <input type="number" min={0} max={10} value={form.nivel} onChange={e => set("nivel", parseInt(e.target.value))} className="input" />
        </div>
        <div className="form-grupo">
          <label>Milestone</label>
          <input value={form.milestone} onChange={e => set("milestone", e.target.value)} className="input" placeholder="Nome do marco" />
        </div>
        <div className="form-grupo">
          <label>Data do Milestone</label>
          <input type="date" value={form.milestone_data} onChange={e => set("milestone_data", e.target.value)} className="input" />
        </div>
      </div>

      {erro && <p className="erro">{erro}</p>}

      <button className="btn-secundario" onClick={salvar}>
        {editIdx !== null ? "✓ Atualizar" : "+ Adicionar Atividade"}
      </button>

      {atividades.length > 0 && (
        <div className="tabela-wrapper">
          <table className="tabela">
            <thead>
              <tr>
                <th>Componente</th>
                <th>Descrição</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Status</th>
                <th>Nv</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {atividades.map((a, i) => (
                <tr key={i}>
                  <td>{a.componente}</td>
                  <td>{a.descricao}</td>
                  <td>{a.data_inicial}</td>
                  <td>{a.data_final}</td>
                  <td><span className={`badge status-${a.status.toLowerCase().replace(/ /g,"-")}`}>{a.status}</span></td>
                  <td>{a.nivel}</td>
                  <td className="acoes">
                    <button onClick={() => editar(i)} className="btn-icon">✏️</button>
                    <button onClick={() => remover(i)} className="btn-icon">🗑️</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="step-acoes">
        <button className="btn-ghost" onClick={onVoltar}>← Voltar</button>
        <button className="btn-primario" onClick={onAvancar} disabled={atividades.length === 0}>
          Próximo → ({atividades.length} atividade{atividades.length !== 1 ? "s" : ""})
        </button>
      </div>
    </div>
  )
}
