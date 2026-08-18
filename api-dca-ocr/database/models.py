from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, LargeBinary, Enum, Date, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base

ESTADOS = ("pendiente", "descargado", "transcrito", "resumido", "error")


class Edicion(Base):
    __tablename__ = "ediciones"
    __table_args__ = (
        UniqueConstraint("nombre_archivo", "fecha_publicacion", name="uq_edicion"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_archivo = Column(String(255), nullable=False)
    fecha_publicacion = Column(Date, nullable=False)
    estado = Column(Enum(*ESTADOS, name="estado_enum"), default="pendiente", nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    transcripcion = relationship(
        "Transcripcion", back_populates="edicion",
        uselist=False, cascade="all, delete-orphan"
    )
    resumen = relationship(
        "Resumen", back_populates="edicion",
        uselist=False, cascade="all, delete-orphan"
    )

class Transcripcion(Base):
    __tablename__ = "transcripciones"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    edicion_id = Column(
        Integer, ForeignKey("ediciones.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    texto = Column(Text(length=4294967295), nullable=False)  # LONGTEXT
    creado_en = Column(DateTime, default=datetime.utcnow)

    edicion = relationship("Edicion", back_populates="transcripcion")


class Resumen(Base):
    __tablename__ = "resumenes"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    edicion_id = Column(
        Integer, ForeignKey("ediciones.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    contenido_md = Column(Text(length=4294967295), nullable=True)   # markdown crudo
    contenido_html = Column(Text(length=4294967295), nullable=True)  # ya convertido
    reporte_pdf = Column(LargeBinary(length=(2**32) - 1), nullable=True)  # LONGBLOB
    reporte_nombre = Column(String(255), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    edicion = relationship("Edicion", back_populates="resumen")


class Edicion(Base):
    __tablename__ = "ediciones"
    id = Column(Integer, primary_key=True)
    nombre_archivo = Column(String(255))
    fecha_publicacion = Column(Date)
    estado = Column(String(50))
    creado_en = Column(DateTime)
    pdf_dca = Column(LargeBinary)  