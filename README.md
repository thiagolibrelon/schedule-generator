# Schedule Generator — Stellantis MVP

Ferramenta interna para geração de cronogramas de projeto.

## Estrutura

```
schedule-mvp/
├── backend/          # FastAPI + Python (geração da imagem)
│   ├── main.py       # API endpoints
│   ├── generator.py  # Lógica de desenho do cronograma
│   └── requirements.txt
└── frontend/         # React + Vite (interface web)
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   └── index.css
    └── package.json
```

---

## Rodar localmente

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API disponível em http://localhost:8000
# Docs em http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
cp .env.example .env          # já aponta para localhost:8000
npm install
npm run dev
# App disponível em http://localhost:5173
```

---

## Deploy — Railway (Backend)

1. Acesse [railway.app](https://railway.app) e faça login com GitHub
2. Clique em **New Project → Deploy from GitHub repo**
3. Selecione este repositório
4. Em **Settings**, defina:
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Clique em **Deploy**
6. Copie a URL gerada (ex: `https://schedule-api.up.railway.app`)

---

## Deploy — Vercel (Frontend)

1. Acesse [vercel.com](https://vercel.com) e faça login com GitHub
2. Clique em **Add New Project → Import Git Repository**
3. Selecione este repositório
4. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
5. Em **Environment Variables**, adicione:
   ```
   VITE_API_URL = https://sua-url-railway.up.railway.app
   ```
6. Clique em **Deploy**

---

## Funcionalidades do MVP

- ✅ Configuração do projeto (título, largura, fonte, legenda)
- ✅ Cadastro de atividades com componente, datas, status e nível
- ✅ Milestones do cabeçalho (Main Milestone, Milestone, Phase)
- ✅ Milestones livres por componente
- ✅ Geração de cronograma em PNG
- ✅ Download da imagem
- ✅ Linha do "Hoje" automática
- ✅ Legenda opcional (Components + Milestones)

---

## Próximas versões (roadmap)

- [ ] Autenticação SSO (Azure AD)
- [ ] Salvar projetos no banco de dados
- [ ] Exportar para PDF e PPTX
- [ ] Histórico de versões do cronograma
- [ ] Import/Export via Excel
- [ ] Múltiplos usuários por projeto
