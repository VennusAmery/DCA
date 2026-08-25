""" python -m locust -f locustfile.py
"""
from locust import HttpUser, task, between
import random

NOMBRES_EDICIONES = [
    "DCA 17 agosto 2026.pdf",
    "DCA 18 agosto 2026.pdf",
    "DCA 19 agosto 2026.pdf",
    "DCA 1 agosto 2026.pdf",
    "DCA 13 julio 2026.pdf",
]

class DCAUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://dca-kmda.onrender.com"

    @task(5)
    def listar_ediciones(self):
        self.client.get("/api/ediciones")

    @task(3)
    def ver_edicion(self):
        nombre = random.choice(NOMBRES_EDICIONES)
        self.client.get(f"/api/ediciones/{nombre}", name="/api/ediciones/[nombre]")

    @task(2)
    def ver_pdf_reporte(self):
        nombre = random.choice(NOMBRES_EDICIONES)
        self.client.get(f"/api/ediciones/{nombre}/pdf", name="/api/ediciones/[nombre]/pdf")

    @task(1)
    def ver_pdf_original(self):
        nombre = random.choice(NOMBRES_EDICIONES)
        self.client.get(f"/api/ediciones/{nombre}/pdf-dca", name="/api/ediciones/[nombre]/pdf-dca")