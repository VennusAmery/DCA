"""
LUMES — Generador de PDF v4.0
"""

import os, re, logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak, Image
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import Flowable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LUMES] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# PALETA
class P:
    CRIMSON    = HexColor("#C13A5A")
    ROSE       = HexColor("#C96B7B")
    BLUSH      = HexColor("#E8A0B0")
    PETAL      = HexColor("#F5CEDE")
    COTTON     = HexColor("#FBDDE9")
    NAVY       = HexColor("#1E2130")
    NAVY_MID   = HexColor("#2A3048")
    OFF_WHITE  = HexColor("#FAF5F7")
    LAVENDER   = HexColor("#F5F0F7")
    GRAY_TEXT  = HexColor("#64748B")
    GRAY_LIGHT = HexColor("#E8ECF0")
    TEXT_BODY  = HexColor("#2D3748")
    TEXT_NJ    = HexColor("#3D1A26")
    WHITE      = white

    # Alertas
    ALTA_BG    = HexColor("#FCEBEB")
    MEDIA_BG   = HexColor("#FEF3E2")
    BAJA_BG    = HexColor("#EEF2FF")
    ALTA_BR    = HexColor("#C13A5A")
    MEDIA_BR   = HexColor("#C0870A")
    BAJA_BR    = HexColor("#2A3048")
    MEDIA_TXT  = HexColor("#7A5200")

    # Cajas
    NJ_BG      = HexColor("#FAF0F4")
    J_BG       = HexColor("#EEF2FF")

    # Sumario / noticias
    SUM_BG     = HexColor("#F7F0F3")
    NOT_BG     = HexColor("#FAF5F7")


# CONSTANTES
STORAGE_DIR = Path("storage/reportes")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
LOGO_PATH   = Path("assets/Lumes-Logo.png")
MARGEN_H    = 2.2 * cm
MARGEN_V    = 2.0 * cm
ANCHO       = letter[0] - 2 * MARGEN_H  

NIVELES     = {"alta", "media", "baja"}
_BOLD_RE    = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE  = re.compile(r"\*(.+?)\*")
_GLOS_RE    = re.compile(r"\*\*(.+?)\*\*\s*[:\-–]\s*(.+?)(?=\n\*\*|\s*\Z)", re.DOTALL)


# HELPERS MARKDOWN
def _bold(t: str) -> str:
    t = _BOLD_RE.sub(r"<b>\1</b>", t)
    t = _ITALIC_RE.sub(r"<i>\1</i>", t)
    return t

def _md2flow(texto: str, st_p, st_b) -> list:
    """Markdown básico → lista de Paragraph."""
    out = []
    for ln in texto.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith(("- ", "* ")):
            out.append(Paragraph(_bold(ln[2:]), st_b))
        else:
            out.append(Paragraph(_bold(ln), st_p))
    return out

# FLOWABLES PERSONALIZADOS
class BandaCrimson(Flowable):
    """Franja crimson de 4pt de altura."""
    def __init__(self, ancho: float):
        super().__init__()
        self.ancho = ancho
        self.height = 4

    def draw(self):
        self.canv.setFillColor(P.CRIMSON)
        self.canv.rect(0, 0, self.ancho, 4, fill=1, stroke=0)


class DivisorSeccion(Flowable):
    """Línea gris con segmento crimson inicial de 40pt."""
    def __init__(self, ancho: float):
        super().__init__()
        self.ancho = ancho
        self.height = 8

    def draw(self):
        c = self.canv
        c.setStrokeColor(P.GRAY_LIGHT)
        c.setLineWidth(1.2)
        c.line(0, 4, self.ancho, 4)
        c.setStrokeColor(P.CRIMSON)
        c.setLineWidth(2)
        c.line(0, 4, 40, 4)


class PuntoCrimson(Flowable):
    """Círculo crimson 6pt para eyebrow."""
    def __init__(self):
        super().__init__()
        self.width = 10
        self.height = 10

    def draw(self):
        self.canv.setFillColor(P.CRIMSON)
        self.canv.circle(5, 5, 3, fill=1, stroke=0)


class BulletCircle(Flowable):
    """Círculo outline crimson para bullets."""
    def __init__(self):
        super().__init__()
        self.width = 12
        self.height = 12

    def draw(self):
        c = self.canv
        c.setStrokeColor(P.CRIMSON)
        c.setLineWidth(1.5)
        c.circle(4, 4, 3, fill=0, stroke=1)

# ESTILOS
def _estilos() -> dict:
    return {
        # Cabecera
        "hdr_label":  ParagraphStyle("hdr_label", fontName="Helvetica",
                        fontSize=8, textColor=P.ROSE, leading=10),
        "hdr_title":  ParagraphStyle("hdr_title", fontName="Helvetica-Bold",
                        fontSize=19, textColor=white, leading=24,
                        spaceAfter=10, alignment=TA_LEFT),
        "hdr_sub":    ParagraphStyle("hdr_sub", fontName="Helvetica",
                        fontSize=9, textColor=P.PETAL, leading=12,
                        alignment=TA_LEFT),

        # Meta
        "meta_key":   ParagraphStyle("meta_key", fontName="Helvetica",
                        fontSize=8, textColor=P.GRAY_TEXT, leading=11),
        "meta_val":   ParagraphStyle("meta_val", fontName="Helvetica-Bold",
                        fontSize=9, textColor=P.NAVY, leading=13),

        # Alerta
        "alert_lbl":  ParagraphStyle("alert_lbl", fontName="Helvetica-Bold",
                        fontSize=8, textColor=P.CRIMSON,
                        spaceAfter=3, leading=10),
        "alert_lbl_m":ParagraphStyle("alert_lbl_m", fontName="Helvetica-Bold",
                        fontSize=8, textColor=P.MEDIA_BR,
                        spaceAfter=3, leading=10),
        "alert_lbl_b":ParagraphStyle("alert_lbl_b", fontName="Helvetica-Bold",
                        fontSize=8, textColor=P.NAVY_MID,
                        spaceAfter=3, leading=10),
        "alert_txt":  ParagraphStyle("alert_txt", fontName="Helvetica",
                        fontSize=10, textColor=P.TEXT_BODY, leading=15),

        # Sección
        "eyebrow":    ParagraphStyle("eyebrow", fontName="Helvetica-Bold",
                        fontSize=8, textColor=P.CRIMSON,
                        spaceAfter=3, leading=10),
        "sec_title":  ParagraphStyle("sec_title", fontName="Helvetica-Bold",
                        fontSize=13, textColor=P.NAVY, leading=17,
                        spaceBefore=2, spaceAfter=8),

        # Cuerpo
        "cuerpo":     ParagraphStyle("cuerpo", fontName="Helvetica",
                        fontSize=10, textColor=P.TEXT_BODY, leading=16,
                        alignment=TA_JUSTIFY, spaceAfter=7),
        "bullet":     ParagraphStyle("bullet", fontName="Helvetica",
                        fontSize=10, textColor=P.TEXT_BODY, leading=15,
                        leftIndent=14, spaceAfter=4),

        # Cajas NJ / J
        "nj_head":    ParagraphStyle("nj_head", fontName="Helvetica-Bold",
                        fontSize=9, textColor=P.CRIMSON,
                        spaceAfter=6, leading=12),
        "nj_body":    ParagraphStyle("nj_body", fontName="Helvetica",
                        fontSize=10, textColor=P.TEXT_NJ, leading=15,
                        alignment=TA_JUSTIFY, spaceAfter=4),
        "nj_bullet":  ParagraphStyle("nj_bullet", fontName="Helvetica",
                        fontSize=10, textColor=P.TEXT_NJ, leading=15,
                        leftIndent=14, spaceAfter=4),
        "j_head":     ParagraphStyle("j_head", fontName="Helvetica-Bold",
                        fontSize=9, textColor=P.NAVY,
                        spaceAfter=6, leading=12),
        "j_body":     ParagraphStyle("j_body", fontName="Helvetica",
                        fontSize=10, textColor=P.NAVY_MID, leading=15,
                        alignment=TA_JUSTIFY, spaceAfter=4),
        "j_bullet":   ParagraphStyle("j_bullet", fontName="Helvetica",
                        fontSize=10, textColor=P.NAVY_MID, leading=15,
                        leftIndent=14, spaceAfter=4),

        # Noticias
        "not_num":    ParagraphStyle("not_num", fontName="Helvetica-Bold",
                        fontSize=8, textColor=P.CRIMSON,
                        leading=11, spaceAfter=2),
        "not_title":  ParagraphStyle("not_title", fontName="Helvetica-Bold",
                        fontSize=11, textColor=P.NAVY, leading=14,
                        spaceAfter=3),
        "not_desc":   ParagraphStyle("not_desc", fontName="Helvetica",
                        fontSize=9, textColor=P.GRAY_TEXT, leading=13,
                        alignment=TA_JUSTIFY),

        # Glosario
        "glos_hdr":   ParagraphStyle("glos_hdr", fontName="Helvetica-Bold",
                        fontSize=9, textColor=white, leading=12),
        "glos_term":  ParagraphStyle("glos_term", fontName="Helvetica-Bold",
                        fontSize=9, textColor=P.NAVY, leading=13),
        "glos_def":   ParagraphStyle("glos_def", fontName="Helvetica",
                        fontSize=9, textColor=P.TEXT_BODY, leading=13,
                        alignment=TA_JUSTIFY),

        # Sumario
        "sum_num":    ParagraphStyle("sum_num", fontName="Helvetica-Bold",
                        fontSize=12, textColor=white, alignment=TA_CENTER,
                        leading=15),
        "sum_title":  ParagraphStyle("sum_title", fontName="Helvetica-Bold",
                        fontSize=10, textColor=P.NAVY, leading=13,
                        spaceAfter=2),
        "sum_desc":   ParagraphStyle("sum_desc", fontName="Helvetica",
                        fontSize=9, textColor=P.GRAY_TEXT, leading=13),

        # Footer
        "footer":     ParagraphStyle("footer", fontName="Helvetica",
                        fontSize=7, textColor=P.GRAY_TEXT, alignment=TA_CENTER),
    }

# SANITIZAR METADATA
def _sanitizar(meta: dict) -> dict:
    hoy = datetime.now().strftime("%d/%m/%Y")
    rel = str(meta.get("relevancia", "media")).lower().strip()
    if rel not in NIVELES:
        rel = "media"
    return {
        "titulo":            str(meta.get("titulo", "Publicación DCA"))[:120],
        "categoria":         str(meta.get("categoria", "General")),
        "relevancia":        rel,
        "numero_acuerdo":    str(meta.get("numero_acuerdo", "N/D")),
        "vigencia":          str(meta.get("vigencia", "A partir de su publicación")),
        "fecha":             str(meta.get("fecha", hoy)),
        "metodo_extraccion": str(meta.get("metodo_extraccion", "OCR/PDF")),
    }

def generar_nombre_pdf(meta: dict) -> str:
    """Genera un nombre de archivo limpio usando espacios en lugar de guiones bajos."""
    titulo = meta.get("titulo", "Reporte LUMES")
    fecha = meta.get("fecha", datetime.now().strftime("%d %m %Y"))
    
    # Reemplazamos guiones bajos por espacios normales
    nombre_limpio = titulo.replace("_", " ")
    nombre_limpio = re.sub(r'[\\/*?:"<>|]', "", nombre_limpio)
    fecha_limpia = fecha.replace("/", " ").replace("-", " ")
    # Retorna algo como "Publicacion DCA 17 06 2026.pdf"
    return f"{nombre_limpio} {fecha_limpia}.pdf"

# COMPONENTES — CABECERA
ALTO_CABECERA = 3.4 * cm   # altura del bloque navy
LOGO_SZ       = 2.0 * cm   # tamaño real del logo 


def _dibujar_cabecera_canvas(canvas, meta: dict):
    """
    Dibuja la cabecera navy full-width directamente en el canvas
    (llamado desde onFirstPage). Cubre toda la página de margen a margen,
    sin depender del sistema de márgenes/tablas de ReportLab — por eso
    SÍ llega de borde a borde, a diferencia de envolver todo en una Table.
    """
    p = P
    w, h = letter
    ALTO  = ALTO_CABECERA
    BANDA = 4  # alto banda crimson inferior
    y0    = h - MARGEN_V - ALTO - BANDA  # esquina inferior del bloque navy

    canvas.saveState()

    # Fondo navy
    canvas.setFillColor(p.NAVY)
    canvas.rect(0, y0 + BANDA, w, ALTO, fill=1, stroke=0)

    # Banda crimson inferior
    canvas.setFillColor(p.CRIMSON)
    canvas.rect(0, y0, w, BANDA, fill=1, stroke=0)

    # ── Logo ──
    logo_sz = LOGO_SZ
    logo_x  = w - MARGEN_H - logo_sz
    logo_y  = y0 + BANDA + (ALTO - logo_sz) / 2

    logo_dibujado = False
    if LOGO_PATH.exists():
        try:
            canvas.drawImage(
                str(LOGO_PATH), logo_x, logo_y,
                width=logo_sz, height=logo_sz,
                preserveAspectRatio=True, mask="auto",
            )
            logo_dibujado = True
        except Exception as e:
            log.warning("No se pudo cargar el logo (%s); usando fallback.", e)

    if not logo_dibujado:
        _logo_fallback(canvas, logo_x, logo_y, logo_sz)

    # ── Textos ──
    tx    = MARGEN_H + 0.4*cm
    max_w = logo_x - tx - 0.4*cm   # ancho disponible antes de chocar con el logo

    top_y = y0 + BANDA + ALTO - 0.62*cm

    # Eyebrow
    canvas.setFillColor(p.ROSE)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(tx, top_y, "RESUMEN EJECUTIVO  ·  DIARIO DE CENTRO AMÉRICA")

    # Título 
    titulo   = meta["titulo"]
    titulo_y = top_y - 0.62*cm
    canvas.setFillColor(white)

    font_size = 16
    canvas.setFont("Helvetica-Bold", font_size)

    if canvas.stringWidth(titulo, "Helvetica-Bold", font_size) > max_w:
        # buscar punto de corte palabra por palabra sin pasarse del ancho
        palabras = titulo.split(" ")
        linea1, linea2 = "", ""
        for palabra in palabras:
            prueba = (linea1 + " " + palabra).strip()
            if canvas.stringWidth(prueba, "Helvetica-Bold", font_size) <= max_w:
                linea1 = prueba
            else:
                linea2 = (linea2 + " " + palabra).strip()
        if not linea1:
            linea1, linea2 = titulo, ""

        canvas.drawString(tx, titulo_y, linea1)
        if linea2:
            canvas.setFont("Helvetica-Bold", font_size - 2)
            canvas.drawString(tx, titulo_y - 0.46*cm, linea2)
            sub_y = titulo_y - 0.92*cm
        else:
            sub_y = titulo_y - 0.46*cm
    else:
        canvas.drawString(tx, titulo_y, titulo)
        sub_y = titulo_y - 0.46*cm

    # Subtítulo: fecha · categoría · LUMES
    canvas.setFillColor(p.PETAL)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(tx, sub_y, f"{meta['fecha']}  ·  {meta['categoria']}  ·  LUMES")

    canvas.restoreState()


def _logo_fallback(canvas, x: float, y: float, sz: float):
    """Círculo crimson con 'L' blanca, usado si el PNG del logo no existe."""
    r  = sz / 2
    cx = x + r
    cy = y + r
    canvas.setFillColor(P.CRIMSON)
    canvas.circle(cx, cy, r, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", int(r * 1.35))
    canvas.drawCentredString(cx, cy - r * 0.32, "L")


def _cabecera(meta: dict, st: dict) -> list:
    """Reserva espacio vertical para la cabecera (que se dibuja en el canvas)."""
    return [Spacer(1, ALTO_CABECERA + 4 + 12)]  

# METADATOS
def _meta_tabla(meta: dict, st: dict) -> Table:
    """Grid 3×2 con micro-labels gray y valores navy bold."""
    p = P
    items = [
        ("NÚMERO DE ACUERDO", meta["numero_acuerdo"]),
        ("PUBLICADO",         meta["fecha"]),
        ("CATEGORÍA",         meta["categoria"]),
        ("VIGENCIA",          meta["vigencia"]),
        ("EXTRACCIÓN",        meta["metodo_extraccion"]),
        ("GENERADO POR",      "Sistema LUMES · IA"),
    ]
    filas = []
    for i in range(0, len(items), 3):
        fila = []
        for j in range(3):
            idx = i + j
            if idx < len(items):
                cell = Table(
                    [[Paragraph(items[idx][0], st["meta_key"])],
                     [Paragraph(items[idx][1], st["meta_val"])]],
                    colWidths=[(ANCHO / 3) - 2],
                )
                cell.setStyle(TableStyle([
                    ("LEFTPADDING",   (0,0),(-1,-1), 10),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 6),
                    ("TOPPADDING",    (0,0),(-1,-1), 8),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 8),
                ]))
                fila.append(cell)
            else:
                fila.append(Spacer(1,1))
        filas.append(fila)

    t = Table(filas, colWidths=[ANCHO/3]*3, spaceBefore=14, spaceAfter=12)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), p.OFF_WHITE),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [p.OFF_WHITE, p.LAVENDER]),
        ("BOX",           (0,0),(-1,-1), 0.5, p.GRAY_LIGHT),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, p.GRAY_LIGHT),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    return t


def _alerta(nivel: str, st: dict) -> Table:
    """Caja alerta con borde izquierdo grueso e ícono triangular."""
    p = P
    cfg = {
        "alta":  (p.ALTA_BR,  p.ALTA_BG,  st["alert_lbl"],   "ALTA PRIORIDAD",
                  "Requiere atención inmediata. Puede implicar cambios contractuales urgentes."),
        "media": (p.MEDIA_BR, p.MEDIA_BG, st["alert_lbl_m"], "PRIORIDAD MEDIA",
                  "Contiene cambios a revisar en el corto plazo para garantizar cumplimiento normativo."),
        "baja":  (p.BAJA_BR,  p.BAJA_BG,  st["alert_lbl_b"], "INFORMATIVA",
                  "Publicación de consulta. Se recomienda su lectura para mantenerse actualizado."),
    }
    borde, bg, st_lbl, lbl, txt = cfg.get(nivel, cfg["media"])

    banda = Table([[""]], colWidths=[4], rowHeights=[50])
    banda.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), borde),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))

    contenido = Table(
        [[Paragraph(lbl, st_lbl)],
         [Paragraph(txt, st["alert_txt"])]],
        colWidths=[ANCHO - 14],
    )
    contenido.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("TOPPADDING",    (0,0),(0,0),   10),
        ("TOPPADDING",    (0,1),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
    ]))

    outer = Table([[banda, contenido]], colWidths=[4, ANCHO - 4],
                  spaceBefore=0, spaceAfter=14)
    outer.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("BOX",           (0,0),(-1,-1), 0.5, p.GRAY_LIGHT),
    ]))
    return outer


def _cabecera_sec(etiqueta: str, titulo: str, st: dict) -> list:
    """Eyebrow con punto crimson + título + divisor."""
    eyebrow_row = Table(
        [[PuntoCrimson(), Paragraph(etiqueta.upper(), st["eyebrow"])]],
        colWidths=[12, ANCHO - 12],
    )
    eyebrow_row.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
    ]))
    return [
        Spacer(1, 14),
        eyebrow_row,
        Paragraph(titulo, st["sec_title"]),
        DivisorSeccion(ANCHO),
        Spacer(1, 8),
    ]


def _bullet_item(texto: str, st_b) -> Table:
    """Bullet con círculo outline crimson."""
    dot = Table([[BulletCircle()]], colWidths=[12], rowHeights=[15])
    dot.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 2),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    txt = Paragraph(_bold(texto), st_b)
    row = Table([[dot, txt]], colWidths=[12, ANCHO - 12], spaceAfter=3)
    row.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    return row


def _render_simple(texto: str, st: dict) -> list:
    """Renderiza texto libre limpiando marcas '###' residuales y maneja bullets."""
    out = []
    for ln in texto.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
            
        # Si la línea empieza con ### o cualquier cantidad de #, se los quitamos
        if ln.startswith("#"):
            ln = re.sub(r"^[#\s]+", "", ln).strip()
            if not ln:  # Si quedó vacía la línea, la ignoramos
                continue
        
        # Procesamos si es una viñeta/bullet o texto normal
        if ln.startswith(("- ", "* ")):
            out.append(_bullet_item(ln[2:], st["bullet"]))
        else:
            out.append(Paragraph(_bold(ln), st["cuerpo"]))
    return out


def _caja_nj_j(txt_nj: str, txt_j: str, st: dict) -> list:
    """Par de cajas coloreadas con header pill y flowables internos."""
    p = P

    def _make_box(header_txt, st_head, st_body, st_bull, bg, borde, items):
        head = Paragraph(f"&#9632;  {header_txt}", st_head)
        rows = [[head]]
        for ln in items.split("\n"):
            ln = ln.strip()
            if not ln:
                continue
            if ln.startswith(("- ", "* ")):
                rows.append([Paragraph(f"•  {_bold(ln[2:])}", st_bull)])
            else:
                rows.append([Paragraph(_bold(ln), st_body)])

        t = Table(rows, colWidths=[ANCHO])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), bg),
            ("BOX",           (0,0),(-1,-1), 1.5, borde),
            ("LEFTPADDING",   (0,0),(-1,-1), 14),
            ("RIGHTPADDING",  (0,0),(-1,-1), 14),
            ("TOPPADDING",    (0,0),(0,0),   12),
            ("TOPPADDING",    (0,1),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ]))
        return t

    nj = _make_box("Para No Juristas", st["nj_head"], st["nj_body"],
                   st["nj_bullet"], p.NJ_BG, p.CRIMSON, txt_nj)
    j  = _make_box("Para Juristas",    st["j_head"],  st["j_body"],
                   st["j_bullet"],  p.J_BG,  p.NAVY_MID, txt_j)

    return [nj, Spacer(1, 10), j]


def _parsear_sub(txt: str) -> list[dict]:
    """Divide contenido en subsecciones limpiando estrictamente los prefijos '#'."""
    items = []
    for parte in re.split(r"\s*###\s+", txt):
        parte = parte.strip()
        if not parte:
            continue

        parte = re.sub(r"^[#\s]+", "", parte).strip()
        
        ls = [l.strip() for l in parte.split("\n") if l.strip()]
        if not ls:
            continue
            
        titulo = re.sub(r"^[#\s]+", "", ls[0]).strip()
        desc   = " ".join(ls[1:]).strip()
        items.append({"titulo": titulo, "desc": desc})
    return items


def _noticias(txt: str, st: dict) -> list:
    """Tarjetas de noticias: borde izquierdo crimson, fondo off-white."""
    p = P
    items = _parsear_sub(txt)
    if not items:
        return _render_simple(txt, st)

    out = []
    for i, it in enumerate(items, 1):
        rows = [
            [Paragraph(f"PUBLICACIÓN {i:02d}", st["not_num"])],
            [Paragraph(_bold(it["titulo"]), st["not_title"])],
        ]
        if it["desc"]:
            rows.append([Paragraph(_bold(it["desc"]), st["not_desc"])])

        # Banda lateral crimson 3pt
        banda = Table([[""]], colWidths=[3], rowHeights=[None])
        banda.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), p.CRIMSON),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ]))

        contenido = Table(rows, colWidths=[ANCHO - 7])
        contenido.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), p.NOT_BG),
            ("LEFTPADDING",   (0,0),(-1,-1), 12),
            ("RIGHTPADDING",  (0,0),(-1,-1), 12),
            ("TOPPADDING",    (0,0),(0,0),   10),
            ("TOPPADDING",    (0,1),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ]))

        card = Table([[banda, contenido]], colWidths=[3, ANCHO - 3],
                     spaceBefore=5, spaceAfter=3)
        card.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("BACKGROUND",    (0,0),(-1,-1), p.NOT_BG),
            ("BOX",           (0,0),(-1,-1), 0.5, p.GRAY_LIGHT),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ]))
        out.append(card)
    return out


def _glosario(txt: str, st: dict) -> list:
    """Tabla glosario: header navy, filas alternadas."""
    p = P
    pares = _GLOS_RE.findall(txt)
    if not pares:
        # fallback línea a línea
        pares = []
        for ln in txt.split("\n"):
            ln = ln.strip().lstrip("- ")
            m = re.match(r"\*\*(.+?)\*\*\s*[:\-]\s*(.+)", ln)
            if m:
                pares.append((m.group(1).strip(), m.group(2).strip()))

    if not pares:
        return _render_simple(txt, st)

    COL_T = ANCHO * 0.28
    COL_D = ANCHO * 0.72

    filas = [[
        Paragraph("<b>Término</b>",    st["glos_hdr"]),
        Paragraph("<b>Definición</b>", st["glos_hdr"]),
    ]]
    for term, defn in pares:
        filas.append([
            Paragraph(f"<b>{term.strip()}</b>", st["glos_term"]),
            Paragraph(_bold(defn.strip()),       st["glos_def"]),
        ])

    styles_t = [
        ("BACKGROUND",    (0,0),(-1,0),   p.NAVY),
        ("BOX",           (0,0),(-1,-1),  0.5, p.NAVY),
        ("INNERGRID",     (0,0),(-1,-1),  0.3, p.GRAY_LIGHT),
        ("LEFTPADDING",   (0,0),(-1,-1),  10),
        ("RIGHTPADDING",  (0,0),(-1,-1),  10),
        ("TOPPADDING",    (0,0),(-1,-1),  6),
        ("BOTTOMPADDING", (0,0),(-1,-1),  6),
        ("VALIGN",        (0,0),(-1,-1),  "TOP"),
    ]
    for idx in range(1, len(filas)):
        bg = p.LAVENDER if idx % 2 == 0 else p.OFF_WHITE
        styles_t.append(("BACKGROUND", (0,idx),(-1,idx), bg))

    t = Table(filas, colWidths=[COL_T, COL_D], spaceBefore=6, spaceAfter=6)
    t.setStyle(TableStyle(styles_t))
    return [t]


def _sumario(txt: str, st: dict) -> list:
    """Sumario: pastilla num crimson + contenido gris rosado."""
    p = P
    items = _parsear_sub(txt)
    if not items:
        return _render_simple(txt, st)

    NUM_W  = 32
    REST_W = ANCHO - NUM_W - 4
    out = []

    for i, it in enumerate(items, 1):
        num = Table(
            [[Paragraph(str(i), st["sum_num"])]],
            colWidths=[NUM_W],
        )
        num.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), p.CRIMSON),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
            ("TOPPADDING",    (0,0),(-1,-1), 8),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ]))

        c_rows = [[Paragraph(_bold(it["titulo"]), st["sum_title"])]]
        if it["desc"]:
            c_rows.append([Paragraph(_bold(it["desc"]), st["sum_desc"])])

        cont = Table(c_rows, colWidths=[REST_W])
        cont.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), p.SUM_BG),
            ("LEFTPADDING",   (0,0),(-1,-1), 12),
            ("RIGHTPADDING",  (0,0),(-1,-1), 12),
            ("TOPPADDING",    (0,0),(0,0),   10),
            ("TOPPADDING",    (0,1),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ]))

        row = Table(
            [[num, cont]],
            colWidths=[NUM_W + 4, REST_W],
            spaceBefore=4, spaceAfter=3,
        )
        row.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ]))
        out.append(row)
    return out

# PARSEO SECCIONES
_SEC_RE = re.compile(r"^##\s+(.+?)\s*\n([\s\S]*?)(?=\n##\s|\Z)", re.MULTILINE)


def _parsear_md(md: str) -> dict:
    """
    Divide el Markdown en secciones nivel '##', limpiando caracteres
    especiales de los títulos para asegurar el match con SECCIONES.
    """
    secs = {}
    for titulo, contenido in _SEC_RE.findall(md):
        key = titulo.lower().strip()
        key = re.sub(r"[^a-záéíóúñ\s]", "", key).strip()
        key = " ".join(key.split())
        secs[key] = contenido.strip()
    return secs


SECCIONES = [
    {"keys": ["panorama general", "resumen ejecutivo"],
     "eyebrow": "01 — Panorama General", "titulo": "¿De qué trata esta publicación?",
     "modo": "simple"},
    {"keys": ["aspectos relevantes", "impacto legal"],
     "eyebrow": "02 — Aspectos Relevantes", "titulo": "¿Qué cambió exactamente?",
     "modo": "simple"},
    {"keys": ["impacto juridico", "impacto jurídico", "artículos afectados"],
     "eyebrow": "03 — Impacto Jurídico", "titulo": "Artículos y normas afectadas",
     "modo": "simple"},
    {"keys": ["para no juristas"],
     "eyebrow": "03B — Para No Juristas", "titulo": "Explicación para el trabajador",
     "modo": "nj_only"},
    {"keys": ["para juristas"],
     "eyebrow": "03C — Para Juristas", "titulo": "Análisis técnico-jurídico",
     "modo": "j_only"},
    {"keys": ["recomendaciones"],
     "eyebrow": "04 — Recomendaciones", "titulo": "¿Qué debés hacer?",
     "modo": "simple"},
    {"keys": ["conclusión", "conclusion"],
     "eyebrow": "05 — Conclusión", "titulo": "Síntesis final",
     "modo": "simple"},
    {"keys": ["panorama de noticias", "noticias del dca", "todas las publicaciones"],
     "eyebrow": "06 — Panorama de Publicaciones", "titulo": "Todas las noticias de esta edición",
     "modo": "noticias"},
    {"keys": ["glosario técnico", "glosario tecnico", "glosario"],
     "eyebrow": "07 — Glosario Técnico", "titulo": "Términos clave explicados",
     "modo": "glosario"},
    {"keys": ["sumario general", "sumario"],
     "eyebrow": "08 — Sumario General", "titulo": "Índice completo de publicaciones",
     "modo": "sumario"},
]

_TEXTOS_ALERTA = {
    "alta":  "Requiere atención inmediata. Puede implicar cambios contractuales urgentes o nuevas obligaciones con fecha límite próxima.",
    "media": "Contiene cambios que deben revisarse en el corto plazo para garantizar cumplimiento normativo.",
    "baja":  "Publicación informativa. Se recomienda su lectura para mantenerse actualizado sobre el marco normativo laboral vigente.",
}

# FOOTER + CABECERA
def _footer_cb(titulo: str, meta: dict = None, primera: bool = False):
    def on_page(canvas, doc):
        # Cabecera solo en la primera página
        if primera and meta:
            _dibujar_cabecera_canvas(canvas, meta)

        # Footer en todas las páginas
        canvas.saveState()
        w, h = letter

        canvas.setStrokeColor(P.GRAY_LIGHT)
        canvas.setLineWidth(0.5)
        canvas.line(MARGEN_H, MARGEN_V - 5, w - MARGEN_H, MARGEN_V - 5)

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(P.GRAY_TEXT)

        tit_corto = titulo[:50] + "..." if len(titulo) > 50 else titulo
        canvas.drawString(MARGEN_H, MARGEN_V - 15, f"LUMES · {tit_corto}")

        page_num = canvas.getPageNumber()
        canvas.drawRightString(w - MARGEN_H, MARGEN_V - 15, f"Página {page_num}")

        canvas.restoreState()
    return on_page

# FUNCIÓN PRINCIPAL
def generar_pdf(resumen_md: str, metadata: Optional[dict] = None) -> str:
    if not resumen_md or not resumen_md.strip():
        raise ValueError("resumen_md no puede estar vacío.")

    meta  = _sanitizar(metadata or {})

    nombre = generar_nombre_pdf(meta)
    ruta   = str(STORAGE_DIR / nombre)

    doc = SimpleDocTemplate(
        ruta,
        pagesize     = letter,
        leftMargin   = MARGEN_H,
        rightMargin  = MARGEN_H,
        topMargin    = MARGEN_V,
        bottomMargin = MARGEN_V + 1*cm,
        title        = f"Resumen DCA — {meta['titulo']}",
        author       = "LUMES · LegalTech Guatemala",
    )

    st  = _estilos()
    els = []

    # ── Cabecera ──
    els.extend(_cabecera(meta, st))

    # ── Metadatos + Alerta ──
    els.append(_meta_tabla(meta, st))
    els.append(_alerta(meta["relevancia"], st))

    # ── Secciones ──
    secs = _parsear_md(resumen_md)

    def _buscar(keys: list) -> str:
        for key in keys:
            for k_real, v in secs.items():
                if key in k_real:
                    return v
        return ""

    nj_j_insertado = False

    for cfg in SECCIONES:
        # Las cajas NJ+J se insertan juntas la primera vez que aparece cualquiera
        if cfg["modo"] in ("nj_only", "j_only"):
            if not nj_j_insertado:
                txt_nj = _buscar([k for c in SECCIONES if c["modo"]=="nj_only" for k in c["keys"]])
                txt_j  = _buscar([k for c in SECCIONES if c["modo"]=="j_only"  for k in c["keys"]])
                if txt_nj or txt_j:
                    bloque_dual = _cabecera_sec(
                        "03B/03C — Para Trabajadores y Juristas",
                        "Explicación para distintos perfiles",
                        st,
                    )
                    bloque_dual.extend(_caja_nj_j(
                        txt_nj or "(sin contenido NJ)",
                        txt_j  or "(sin contenido J)",
                        st,
                    ))
                    els.append(KeepTogether(bloque_dual))
                nj_j_insertado = True
            continue

        contenido = _buscar(cfg["keys"])
        if not contenido:
            continue

        bloque = _cabecera_sec(cfg["eyebrow"], cfg["titulo"], st)

        if cfg["modo"] == "noticias":
            bloque.extend(_noticias(contenido, st))
        elif cfg["modo"] == "glosario":
            bloque.extend(_glosario(contenido, st))
        elif cfg["modo"] == "sumario":
            bloque.extend(_sumario(contenido, st))
        else:
            bloque.extend(_render_simple(contenido, st))

        els.append(KeepTogether(bloque))

    # Fallback
    if not secs:
        log.warning("Sin secciones ##. Modo fallback.")
        els.extend(_cabecera_sec("RESUMEN", "Contenido del documento", st))
        els.extend(_render_simple(resumen_md, st))

    doc.build(
        els,
        onFirstPage=_footer_cb(meta["titulo"], meta=meta, primera=True),
        onLaterPages=_footer_cb(meta["titulo"]),
    )
    log.info("PDF generado: %s", ruta)
    return ruta