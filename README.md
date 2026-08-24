# 📰 DCA Centroamérica — Scraper, Resumen IA & Visor

> Descarga, transcribe y resume automáticamente cada edición del **Diario de Centroamérica (DCA)**, y navégalas desde una interfaz web

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=flat&logo=react&logoColor=black)
![Gemini](https://img.shields.io/badge/Google_Gemini-Resumen_IA-8E75B2?style=flat&logo=google&logoColor=white)
![Status](https://img.shields.io/badge/status-en_desarrollo-C13A5A?style=flat)

---

## ✨ ¿Qué hace este proyecto?

El **DCA (Diario de Centroamérica)** es el diario oficial de Guatemala, y publica una edición en PDF todos los días. Este proyecto automatiza todo el proceso de convertir ese PDF en algo fácil de leer y consultar:

1. 🔎 **Scrapea** el sitio oficial y descarga el PDF de la edición del día.
2. 📄 **Extrae el texto** crudo del PDF.
3. 📝 **Convierte** ese texto a **Markdown** estructurado.
4. 🤖 **Genera un resumen** del contenido usando la **API de Gemini**.
5. 🖥️ Sirve todo a través de un **visor web en React**, donde se puede:
   - Ver el PDF original del DCA.
   - Ver el reporte/resumen generado.
   - Consultar el texto crudo transcrito.
   - Descargar cualquiera de los PDFs.

pip install -r requirements.txt
