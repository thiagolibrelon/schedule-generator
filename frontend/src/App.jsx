import { useState } from "react"
import ConfiguracaoStep from "./components/ConfiguracaoStep"
import AtividadesStep from "./components/AtividadesStep"
import MilestoneStep from "./components/MilestoneStep"
import PreviewStep from "./components/PreviewStep"
import ProgressBar from "./components/ProgressBar"

const STEPS = ["Configuração", "Atividades", "Milestones", "Gerar"]

export default function App() {
  const [step, setStep] = useState(0)
  const [config, setConfig] = useState({
    titulo: "",
    gerar_legenda: true,
    largura_semana: 1.0,
    tamanho_fonte_milestone: 12,
  })
  const [atividades, setAtividades] = useState([])
  const [milestones, setMilestones] = useState([])
  const [milestonesLivres, setMilestonesLivres] = useState([])
  const [imagemUrl, setImagemUrl] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)

  const avancar = () => setStep(s => Math.min(s + 1, STEPS.length - 1))
  const voltar  = () => setStep(s => Math.max(s - 1, 0))

  const gerarCronograma = async () => {
    setCarregando(true)
    setErro(null)
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/gerar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config,
          atividades,
          milestones,
          milestones_livres: milestonesLivres,
        }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "Erro ao gerar cronograma")
      }
      const blob = await res.blob()
      setImagemUrl(URL.createObjectURL(blob))
      avancar()
    } catch (e) {
      setErro(e.message)
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">◈</span>
          <span className="logo-texto">Schedule Generator</span>
        </div>
        <span className="logo-sub">Stellantis Internal Tool</span>
      </header>

      <ProgressBar steps={STEPS} atual={step} />

      <main className="app-main">
        {step === 0 && (
          <ConfiguracaoStep
            config={config}
            onChange={setConfig}
            onAvancar={avancar}
          />
        )}
        {step === 1 && (
          <AtividadesStep
            atividades={atividades}
            onChange={setAtividades}
            onAvancar={avancar}
            onVoltar={voltar}
          />
        )}
        {step === 2 && (
          <MilestoneStep
            milestones={milestones}
            milestonesLivres={milestonesLivres}
            onChangeMilestones={setMilestones}
            onChangeLivres={setMilestonesLivres}
            onGerar={gerarCronograma}
            onVoltar={voltar}
            carregando={carregando}
            erro={erro}
          />
        )}
        {step === 3 && (
          <PreviewStep
            imagemUrl={imagemUrl}
            onVoltar={voltar}
            onNovo={() => { setStep(0); setImagemUrl(null) }}
          />
        )}
      </main>
    </div>
  )
}
