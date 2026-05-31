"""
Schedule Generator — lógica de desenho do cronograma
Portado e refatorado a partir do VBA original (Stellantis)
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta, date
from typing import List, Optional
import math
import io

# ── Constantes visuais ────────────────────────────────────────────────────────

COR_AZUL_ESCURO    = (31,  56,  100)
COR_AZUL_CLARO     = (173, 193, 229)
COR_BRANCO         = (255, 255, 255)
COR_PRETO          = (0,   0,   0)
COR_CINZA_CLARO    = (230, 235, 240)
COR_CINZA_MEDIO    = (200, 210, 220)
COR_VERMELHO       = (220, 80,  80)
COR_VERMELHO_ESCURO= (180, 30,  30)
COR_LARANJA        = (197, 90,  17)
COR_AMARELO        = (255, 242, 0)
COR_AMARELO_BORDA  = (180, 160, 0)
COR_VERDE          = (70,  150, 80)

STATUS_CORES = {
    "ontime":           COR_AZUL_CLARO,
    "delayed":          COR_VERMELHO,
    "concluded":        COR_AZUL_ESCURO,
    "concluded delay":  COR_LARANJA,
    "attention point":  COR_AMARELO,
}

MILESTONE_CORES = {
    1: COR_AZUL_ESCURO,
    2: (255, 192, 0),
    3: COR_LARANJA,
}

# ── Helpers de data ───────────────────────────────────────────────────────────

def parse_data(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def semana_iso(d: date) -> int:
    return d.isocalendar()[1]

def inicio_semana(d: date) -> date:
    return d - timedelta(days=d.weekday())

def listar_semanas(d_ini: date, d_fim: date):
    atual = inicio_semana(d_ini)
    while atual <= d_fim:
        yield atual
        atual += timedelta(weeks=1)

def listar_meses(d_ini: date, d_fim: date):
    ano, mes = d_ini.year, d_ini.month
    while date(ano, mes, 1) <= d_fim:
        yield date(ano, mes, 1)
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

def listar_anos(d_ini: date, d_fim: date):
    for ano in range(d_ini.year, d_fim.year + 1):
        yield ano

def dias_no_mes(d: date) -> int:
    if d.month == 12:
        return (date(d.year + 1, 1, 1) - date(d.year, 12, 1)).days
    return (date(d.year, d.month + 1, 1) - date(d.year, d.month, 1)).days

# ── Renderer principal ────────────────────────────────────────────────────────

class CronogramaRenderer:

    # Layout
    MARGEM_ESQ       = 160   # largura da coluna de componentes
    LARGURA_SEMANA   = 14    # px por semana (base)
    ALTURA_CABECALHO = 32
    ALTURA_ANOS      = 18
    ALTURA_MESES     = 18
    ALTURA_SEMANAS   = 20
    ALTURA_ATIVIDADE = 22
    ESPACO_COMP      = 8     # espaço entre componentes
    PADDING_TOPO     = 20    # espaço acima do cabeçalho (com legenda)
    PADDING_TOPO_SEM = 10    # espaço acima do cabeçalho (sem legenda)

    def __init__(self, payload):
        self.cfg        = payload.config
        self.atividades = payload.atividades
        self.milestones = payload.milestones
        self.ml_livres  = payload.milestones_livres

        self.larg_sem   = self.LARGURA_SEMANA * self.cfg.largura_semana
        self.gerar_leg  = self.cfg.gerar_legenda

        # Calcular range de datas
        todas_datas = []
        for a in self.atividades:
            todas_datas += [parse_data(a.data_inicial), parse_data(a.data_final)]
        for m in self.milestones:
            todas_datas.append(parse_data(m.data_inicial))
            if m.data_final:
                todas_datas.append(parse_data(m.data_final))

        self.d_ini = min(todas_datas) - timedelta(weeks=1)
        self.d_fim = max(todas_datas) + timedelta(weeks=4)
        self.d_ini = inicio_semana(self.d_ini)

        self.semanas = list(listar_semanas(self.d_ini, self.d_fim))
        self.total_semanas = len(self.semanas)

        # Largura total do cronograma
        self.largura_grid = int(self.total_semanas * self.larg_sem)

        # Componentes únicos ordenados
        self.componentes = []
        seen = set()
        for a in self.atividades:
            key = (a.sistema, a.componente)
            if key not in seen:
                seen.add(key)
                self.componentes.append(key)

        # Calcular altura de cada componente
        self.comp_niveis = {}
        for key in self.componentes:
            ativs = [a for a in self.atividades if (a.sistema, a.componente) == key]
            max_nivel = max((a.nivel for a in ativs), default=0)
            self.comp_niveis[key] = max_nivel

        # Altura da legenda
        self.altura_legenda = 0
        if self.gerar_leg:
            n_ml = len(self.milestones)
            self.altura_legenda = max(
                40 + n_ml * 18 + 20 + 5 * 18 + 20,  # milestones + components
                180
            )

        # Altura do header (cabeçalho + anos + meses + semanas)
        self.y_header = self.altura_legenda + (self.PADDING_TOPO if self.gerar_leg else self.PADDING_TOPO_SEM)
        self.altura_header = self.ALTURA_CABECALHO + self.ALTURA_ANOS + self.ALTURA_MESES + self.ALTURA_SEMANAS

        # Altura de cada componente
        self.comp_alturas = {}
        for key in self.componentes:
            niveis = self.comp_niveis[key]
            self.comp_alturas[key] = (niveis + 1) * self.ALTURA_ATIVIDADE + self.ESPACO_COMP * 2

        # Posições Y de cada componente
        self.comp_y = {}
        y_atual = self.y_header + self.altura_header + 10
        for key in self.componentes:
            self.comp_y[key] = y_atual
            y_atual += self.comp_alturas[key] + self.ESPACO_COMP

        self.altura_total = y_atual + 20
        self.largura_total = self.MARGEM_ESQ + self.largura_grid + 20

        # Fonte
        try:
            self.font_sm  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
            self.font_md  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            self.font_bold= ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
            self.font_lg  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            self.font_ml  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                               self.cfg.tamanho_fonte_milestone)
        except:
            self.font_sm  = ImageFont.load_default()
            self.font_md  = self.font_sm
            self.font_bold= self.font_sm
            self.font_lg  = self.font_sm
            self.font_ml  = self.font_sm

    # ── Helpers de posição ────────────────────────────────────────────────────

    def x_data(self, d: date) -> int:
        """Converte uma data em posição X no grid."""
        delta = (d - self.d_ini).days
        return self.MARGEM_ESQ + int(delta / 7 * self.larg_sem)

    def desenha_retangulo(self, draw, x1, y1, x2, y2, fill, outline=None, radius=3):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline)

    def desenha_texto_centralizado(self, draw, texto, x, y, w, h, font, cor=COR_BRANCO):
        bbox = draw.textbbox((0, 0), texto, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((x + (w - tw) // 2, y + (h - th) // 2), texto, font=font, fill=cor)

    def desenha_triangulo(self, draw, cx, cy, lado, cor, invertido=True):
        if invertido:
            pts = [(cx, cy + lado), (cx - lado//2, cy), (cx + lado//2, cy)]
        else:
            pts = [(cx, cy), (cx - lado//2, cy + lado), (cx + lado//2, cy + lado)]
        draw.polygon(pts, fill=cor)

    # ── Seções do cronograma ──────────────────────────────────────────────────

    def renderiza_legenda(self, draw):
        if not self.gerar_leg:
            return

        x = 5
        y = self.PADDING_TOPO

        # Bloco Milestones
        draw.rounded_rectangle([x, y, x + 140, y + 16], radius=2,
                                fill=COR_AZUL_ESCURO)
        draw.text((x + 5, y + 2), "Milestones", font=self.font_bold, fill=COR_BRANCO)
        y += 20

        for m in self.milestones:
            cor = MILESTONE_CORES.get(m.cor, COR_AZUL_ESCURO)
            self.desenha_triangulo(draw, x + 8, y + 2, 10, cor)
            draw.text((x + 18, y), m.descricao, font=self.font_sm, fill=COR_PRETO)
            y += 16

        y += 10

        # Bloco Components
        draw.rounded_rectangle([x, y, x + 140, y + 16], radius=2,
                                fill=COR_AZUL_ESCURO)
        draw.text((x + 5, y + 2), "Components", font=self.font_bold, fill=COR_BRANCO)
        y += 20

        items = [
            ("Attention Point",  COR_AMARELO),
            ("Concluded",        COR_AZUL_ESCURO),
            ("Concluded Delay",  COR_LARANJA),
            ("Delayed",          COR_VERMELHO),
            ("Ontime",           COR_AZUL_CLARO),
        ]
        for nome, cor in items:
            draw.rounded_rectangle([x + 2, y + 2, x + 13, y + 13], radius=2, fill=cor)
            draw.text((x + 18, y), nome, font=self.font_sm, fill=COR_PRETO)
            y += 16

    def renderiza_cabecalho(self, draw):
        y = self.y_header

        # Barra do título
        draw.rectangle([self.MARGEM_ESQ, y,
                         self.MARGEM_ESQ + self.largura_grid, y + self.ALTURA_CABECALHO],
                        fill=COR_AZUL_ESCURO)
        self.desenha_texto_centralizado(draw, self.cfg.titulo,
                                        self.MARGEM_ESQ, y,
                                        self.largura_grid, self.ALTURA_CABECALHO,
                                        self.font_lg)
        y += self.ALTURA_CABECALHO

        # Anos
        y_anos = y
        for ano in listar_anos(self.d_ini, self.d_fim):
            d_inicio_ano = max(date(ano, 1, 1), self.d_ini)
            d_fim_ano    = min(date(ano, 12, 31), self.d_fim)
            x1 = self.x_data(d_inicio_ano)
            x2 = self.x_data(d_fim_ano + timedelta(days=7))
            draw.rectangle([x1, y_anos, x2, y_anos + self.ALTURA_ANOS],
                            fill=COR_AZUL_ESCURO, outline=COR_BRANCO)
            self.desenha_texto_centralizado(draw, str(ano),
                                            x1, y_anos, x2 - x1, self.ALTURA_ANOS,
                                            self.font_bold)
        y += self.ALTURA_ANOS

        # Meses
        y_meses = y
        nomes_meses = ["Jan","Fev","Mar","Abr","Mai","Jun",
                        "Jul","Ago","Set","Out","Nov","Dez"]
        for d_mes in listar_meses(self.d_ini, self.d_fim):
            d_prox = date(d_mes.year + (1 if d_mes.month == 12 else 0),
                          1 if d_mes.month == 12 else d_mes.month + 1, 1)
            x1 = self.x_data(max(d_mes, self.d_ini))
            x2 = self.x_data(min(d_prox, self.d_fim + timedelta(days=7)))
            cor = COR_AZUL_ESCURO if d_mes.month % 2 == 0 else (50, 80, 130)
            draw.rectangle([x1, y_meses, x2, y_meses + self.ALTURA_MESES],
                            fill=cor, outline=COR_BRANCO)
            self.desenha_texto_centralizado(draw, nomes_meses[d_mes.month - 1],
                                            x1, y_meses, x2 - x1, self.ALTURA_MESES,
                                            self.font_sm)
        y += self.ALTURA_MESES

        # Semanas
        y_sem = y
        for sem in self.semanas:
            x1 = self.x_data(sem)
            x2 = x1 + int(self.larg_sem)
            cor_bg = COR_CINZA_CLARO if sem.month % 2 == 0 else COR_BRANCO
            draw.rectangle([x1, y_sem, x2, y_sem + self.ALTURA_SEMANAS],
                            fill=COR_AZUL_ESCURO, outline=COR_BRANCO)
            num = str(semana_iso(sem))
            self.desenha_texto_centralizado(draw, num,
                                            x1, y_sem, int(self.larg_sem), self.ALTURA_SEMANAS,
                                            self.font_sm)

        # Fundo do grid (listras alternadas por mês)
        y_grid_ini = self.y_header + self.altura_header
        y_grid_fim = self.altura_total - 10
        for d_mes in listar_meses(self.d_ini, self.d_fim):
            d_prox = date(d_mes.year + (1 if d_mes.month == 12 else 0),
                          1 if d_mes.month == 12 else d_mes.month + 1, 1)
            x1 = self.x_data(max(d_mes, self.d_ini))
            x2 = self.x_data(min(d_prox, self.d_fim + timedelta(days=7)))
            if d_mes.month % 2 == 0:
                draw.rectangle([x1, y_grid_ini, x2, y_grid_fim],
                                fill=(240, 244, 250))

    def renderiza_componentes(self, draw):
        for key in self.componentes:
            sistema, componente = key
            y = self.comp_y[key]
            h = self.comp_alturas[key]

            # Bloco azul do componente
            self.desenha_retangulo(draw, 2, y, self.MARGEM_ESQ - 5, y + h - self.ESPACO_COMP,
                                   COR_AZUL_ESCURO, COR_AZUL_CLARO)

            # Texto do componente
            linhas = self._quebra_texto(componente, self.font_sm, self.MARGEM_ESQ - 20)
            ty = y + (h - self.ESPACO_COMP) // 2 - len(linhas) * 7
            for linha in linhas:
                bbox = draw.textbbox((0,0), linha, font=self.font_sm)
                tw = bbox[2] - bbox[0]
                draw.text(((self.MARGEM_ESQ - 5 - 2 - tw) // 2 + 2, ty),
                          linha, font=self.font_sm, fill=COR_BRANCO)
                ty += 14

            # Texto do sistema (pequeno, acima do componente)
            if sistema:
                draw.text((2, y - 10), sistema, font=self.font_sm, fill=COR_CINZA_MEDIO)

            # Linha divisória
            y_linha = y + h - self.ESPACO_COMP
            draw.line([self.MARGEM_ESQ, y_linha, self.MARGEM_ESQ + self.largura_grid, y_linha],
                      fill=COR_CINZA_MEDIO, width=1)

    def renderiza_atividades(self, draw):
        for atv in self.atividades:
            key = (atv.sistema, atv.componente)
            y_comp = self.comp_y[key]
            y_atv = y_comp + self.ESPACO_COMP + atv.nivel * self.ALTURA_ATIVIDADE

            d_ini = parse_data(atv.data_inicial)
            d_fim = parse_data(atv.data_final)

            x1 = self.x_data(d_ini)
            x2 = self.x_data(d_fim)
            if x2 - x1 < 4:
                x2 = x1 + 4

            status_key = atv.status.lower()
            cor_fill = STATUS_CORES.get(status_key, COR_AZUL_CLARO)
            cor_borda = COR_AZUL_ESCURO if "concluded" in status_key else COR_PRETO

            self.desenha_retangulo(draw, x1, y_atv, x2, y_atv + self.ALTURA_ATIVIDADE - 2,
                                   cor_fill, cor_borda, radius=4)

            # Texto da atividade
            txt = atv.descricao
            draw.text((x1 + 3, y_atv + 4), txt, font=self.font_sm,
                      fill=COR_BRANCO if "concluded" in status_key or status_key == "delayed"
                      else COR_PRETO)

            # Milestone individual
            if atv.milestone and atv.milestone_data:
                x_ml = self.x_data(parse_data(atv.milestone_data))
                self.desenha_triangulo(draw, x_ml, y_atv - 2, 10, COR_AZUL_ESCURO)
                draw.text((x_ml + 6, y_atv - 12), atv.milestone,
                          font=self.font_sm, fill=COR_PRETO)

    def renderiza_milestones(self, draw):
        y_base = self.y_header + self.altura_header - self.ALTURA_SEMANAS - 10

        for m in self.milestones:
            cor = MILESTONE_CORES.get(m.cor, COR_AZUL_ESCURO)
            level_off = m.nivel * 14

            if m.tipo == "Main Milestone":
                x = self.x_data(parse_data(m.data_inicial))
                # Linha vertical tracejada
                y_topo = y_base - level_off - 20
                draw.line([x, y_topo, x, self.altura_total - 10],
                          fill=cor, width=2)
                # Triângulo
                self.desenha_triangulo(draw, x, y_topo, 12, cor)
                # Texto
                draw.text((x - 20, y_topo - 14), m.descricao,
                          font=self.font_ml, fill=cor)

            elif m.tipo == "Milestone":
                x = self.x_data(parse_data(m.data_inicial))
                y = y_base - level_off
                self.desenha_triangulo(draw, x, y, 12, cor)
                draw.text((x + 8, y - 4), m.descricao,
                          font=self.font_ml, fill=cor)

            elif m.tipo == "Phase":
                d_ini = parse_data(m.data_inicial)
                d_fim = parse_data(m.data_final) if m.data_final else d_ini + timedelta(weeks=4)
                x1 = self.x_data(d_ini)
                x2 = self.x_data(d_fim)
                y = y_base - level_off
                draw.rounded_rectangle([x1, y, x2, y + 14], radius=3,
                                        fill=cor, outline=COR_PRETO)
                semanas = math.ceil((d_fim - d_ini).days / 7)
                txt = f"{m.descricao} ({semanas}W)"
                self.desenha_texto_centralizado(draw, txt, x1, y, x2 - x1, 14,
                                                self.font_sm)

    def renderiza_milestones_livres(self, draw):
        lado = 14
        for ml in self.ml_livres:
            key = next(((s, c) for s, c in self.componentes if c == ml.componente), None)
            if not key:
                continue
            y_comp = self.comp_y[key]
            y = y_comp + self.ESPACO_COMP + ml.nivel * self.ALTURA_ATIVIDADE + ml.posicao
            x = self.x_data(parse_data(ml.data))

            status_key = ml.tipo.lower()
            cor = STATUS_CORES.get(status_key, COR_AZUL_ESCURO)

            self.desenha_triangulo(draw, x, y, lado, cor)
            draw.text((x - 20, y - 14), ml.nome, font=self.font_sm, fill=COR_PRETO)

    def renderiza_hoje(self, draw):
        hoje = date.today()
        if self.d_ini <= hoje <= self.d_fim:
            x = self.x_data(hoje)
            y_ini = self.y_header + self.altura_header
            y_fim = self.altura_total - 10
            draw.line([x, y_ini, x, y_fim], fill=COR_VERMELHO_ESCURO, width=2)
            draw.text((x + 3, y_ini + 2), "Hoje", font=self.font_sm, fill=COR_VERMELHO_ESCURO)

    def _quebra_texto(self, texto, font, max_w):
        palavras = texto.split()
        linhas = []
        atual = ""
        for p in palavras:
            teste = (atual + " " + p).strip()
            bbox = ImageDraw.Draw(Image.new("RGB", (1,1))).textbbox((0,0), teste, font=font)
            if bbox[2] - bbox[0] <= max_w:
                atual = teste
            else:
                if atual:
                    linhas.append(atual)
                atual = p
        if atual:
            linhas.append(atual)
        return linhas if linhas else [texto]

    # ── Render final ──────────────────────────────────────────────────────────

    def render(self) -> bytes:
        img = Image.new("RGB", (int(self.largura_total), int(self.altura_total)), COR_BRANCO)
        draw = ImageDraw.Draw(img)

        self.renderiza_cabecalho(draw)
        self.renderiza_legenda(draw)
        self.renderiza_componentes(draw)
        self.renderiza_atividades(draw)
        self.renderiza_milestones(draw)
        self.renderiza_milestones_livres(draw)
        self.renderiza_hoje(draw)

        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(150, 150))
        return buf.getvalue()


# ── Entry point ───────────────────────────────────────────────────────────────

def gerar_cronograma(payload) -> bytes:
    renderer = CronogramaRenderer(payload)
    return renderer.render()
