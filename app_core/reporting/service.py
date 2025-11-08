from __future__ import annotations

import io
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable
import math

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from extensions import db
from app_core.models import Asset, AssetType, Project, Report
from app_core.storage import ensure_project_path_exists, storage_root
from .ai import build_ai_summary, AIUnavailable, AISummaryError


class AnalysisReportError(RuntimeError):
    pass


def _latest_snapshot(project: Project) -> Dict[str, Any]:
    settings = project.settings or {}
    snapshot = settings.get('lastCoverage')
    if not snapshot:
        raise AnalysisReportError('Projeto não possui mancha de cobertura salva.')
    return snapshot


def _format_number(value, unit=""):
    if value in (None, ""):
        return "—"
    if isinstance(value, (int, float)):
        formatted = f"{value:.2f}".rstrip('0').rstrip('.')
    else:
        formatted = str(value)
    return f"{formatted} {unit}".strip()


def _wrap_text(c: canvas.Canvas, text: str, x: int, y: int, width_chars: int = 95, line_height: int = 14) -> int:
    for paragraph in text.splitlines():
        if not paragraph.strip():
            y -= line_height
            continue
        for line in textwrap.wrap(paragraph.strip(), width=width_chars):
            c.drawString(x, y, line)
            y -= line_height
    return y


def _draw_text_block(c: canvas.Canvas, x: int, y: int, lines):
    c.setFont('Helvetica', 10)
    line_height = 14
    for label, value in lines:
        c.drawString(x, y, f"{label}: {value}")
        y -= line_height
    return y


def _embed_image(c: canvas.Canvas, image_path: Path, x: int, y: int, max_width: int, max_height: int):
    try:
        reader = ImageReader(str(image_path))
        width, height = reader.getSize()
        ratio = min(max_width / width, max_height / height)
        c.drawImage(reader, x, y - height * ratio, width=width * ratio, height=height * ratio)
        return y - height * ratio - 20
    except Exception:
        c.setFont('Helvetica-Oblique', 9)
        c.drawString(x, y, 'Prévia da cobertura indisponível.')
        return y - 14


def _embed_binary_image(c: canvas.Canvas, blob: bytes | None, x: int, y: int, max_width: int, max_height: int) -> int:
    if not blob:
        return y
    try:
        reader = ImageReader(io.BytesIO(blob))
        width, height = reader.getSize()
        ratio = min(max_width / width, max_height / height)
        c.drawImage(reader, x, y - height * ratio, width=width * ratio, height=height * ratio)
        return y - height * ratio - 20
    except Exception:
        return y


def _asset_path(asset_id: str | None) -> Path | None:
    if not asset_id:
        return None
    asset = Asset.query.filter_by(id=asset_id).first()
    if asset is None:
        return None
    return storage_root() / asset.path


def _build_metrics(project: Project, snapshot: Dict[str, Any], center_metrics: Dict[str, Any]) -> Dict[str, Any]:
    settings = project.settings or {}
    user = project.user
    power_w = getattr(user, "transmission_power", None)
    erp_dbm = None
    if power_w not in (None, ""):
        try:
            erp_dbm = 10 * math.log10(max(float(power_w), 1e-6) * 1000.0)
        except (TypeError, ValueError):
            erp_dbm = None
    return {
        "service": settings.get("serviceType") or getattr(user, "servico", "Radiodifusão"),
        "service_class": settings.get("serviceClass") or settings.get("classe") or "—",
        "location": settings.get("tx_location_name") or snapshot.get("tx_location_name") or getattr(user, "tx_location_name", "—"),
        "erp_dbm": erp_dbm,
        "radius_km": snapshot.get("radius_km") or snapshot.get("requested_radius_km"),
        "frequency_mhz": getattr(user, "frequencia", None),
        "polarization": getattr(user, "polarization", None),
        "field_center": center_metrics.get("field_center_dbuv_m"),
        "rx_power": center_metrics.get("received_power_center_dbm"),
        "loss_center": center_metrics.get("combined_loss_center_db"),
        "gain_center": center_metrics.get("effective_gain_center_db"),
        "climate": settings.get("clima") or snapshot.get("climate_status") or "Não informado",
    }


def _start_page(c: canvas.Canvas, width: float, height: float, title: str, subtitle: str) -> int:
    c.setFillColor(colors.HexColor("#0d47a1"))
    c.rect(0, height - 80, width, 80, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(40, height - 45, title)
    c.setFont('Helvetica', 11)
    c.drawString(40, height - 65, subtitle)
    c.setFillColor(colors.black)
    return height - 110


def generate_analysis_report(project: Project) -> Report:
    snapshot = _latest_snapshot(project)
    user = project.user
    settings = project.settings or {}
    center_metrics = snapshot.get('center_metrics') or {}
    loss_components = snapshot.get('loss_components') or {}
    gain_components = snapshot.get('gain_components') or {}
    metrics = _build_metrics(project, snapshot, center_metrics)

    storage_dir = ensure_project_path_exists(project, 'assets', 'reports')
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"analysis_{project.slug}_{timestamp}.pdf"
    pdf_path = storage_dir / filename

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4

    y = _start_page(
        c,
        width,
        height,
        f"Relatório de Análise — {project.name}",
        f"Gerado em {datetime.utcnow():%d/%m/%Y %H:%M UTC}",
    )

    section_one = [
        ('Projeto', project.name),
        ('Slug', project.slug),
        ('Serviço', metrics.get("service")),
        ('Classe', metrics.get("service_class")),
        ('Engine', snapshot.get('engine', '—')),
        ('Raio', _format_number(metrics.get("radius_km"), 'km')),
    ]
    y = _draw_text_block(c, 40, y, section_one)

    section_two = [
        ('Potência TX', _format_number(getattr(user, 'transmission_power', None), 'W')),
        ('Ganho TX', _format_number(getattr(user, 'antenna_gain', None), 'dBi')),
        ('Perdas Sistêmicas', _format_number(getattr(user, 'total_loss', None), 'dB')),
        ('Polarização', getattr(user, 'polarization', '—')),
        ('Notas do usuário', getattr(user, 'notes', '—')),
    ]
    y = _draw_text_block(c, 40, y - 10, section_two)

    coverage_lines = [
        ('Campo no centro', _format_number(center_metrics.get('field_center_dbuv_m'), 'dBµV/m')),
        ('Potência recebida', _format_number(center_metrics.get('received_power_center_dbm'), 'dBm')),
        ('Perda combinada', _format_number(center_metrics.get('combined_loss_center_db'), 'dB')),
        ('Ganho efetivo', _format_number(center_metrics.get('effective_gain_center_db'), 'dB')),
    ]
    y = _draw_text_block(c, 40, y - 10, coverage_lines)

    y = _draw_text_block(c, 40, y - 10, [
        ('Componente L_b', _format_number((loss_components.get('L_b') or {}).get('center'), 'dB')),
        ('Ajuste horizontal', _format_number(gain_components.get('horizontal_adjustment_db_min'), 'dB')),
        ('Ajuste vertical', _format_number(gain_components.get('vertical_adjustment_db'), 'dB')),
    ])

    image_path = snapshot.get('asset_path')
    rel_image_path = Path(image_path) if image_path else None
    if rel_image_path:
        coverage_image = storage_root() / rel_image_path
        if coverage_image.exists():
            y = _embed_image(c, coverage_image, 300, y + 160, max_width=280, max_height=320)

    c.showPage()

    # Page 2 – coverage metrics and imagery
    y = _start_page(c, width, height, "Cobertura e métricas", f"{project.slug} · engine {snapshot.get('engine', '—')}")

    coverage_block = [
        ('Campo no centro', _format_number(center_metrics.get('field_center_dbuv_m'), 'dBµV/m')),
        ('Potência recebida', _format_number(center_metrics.get('received_power_center_dbm'), 'dBm')),
        ('Perda combinada', _format_number(center_metrics.get('combined_loss_center_db'), 'dB')),
        ('Ganho efetivo', _format_number(center_metrics.get('effective_gain_center_db'), 'dB')),
        ('Raio planejado', _format_number(metrics.get("radius_km"), 'km')),
        ('Polarização', metrics.get("polarization") or '—'),
    ]
    y = _draw_text_block(c, 40, y, coverage_block)

    y = _draw_text_block(c, 40, y - 10, [
        ('Componente L_b', _format_number((loss_components.get('L_b') or {}).get('center'), 'dB')),
        ('Ajuste horizontal', _format_number(gain_components.get('horizontal_adjustment_db_min'), 'dB')),
        ('Ajuste vertical', _format_number(gain_components.get('vertical_adjustment_db'), 'dB')),
    ])

    colorbar_path = _asset_path(snapshot.get('colorbar_asset_id'))
    if colorbar_path and colorbar_path.exists():
        _embed_image(c, colorbar_path, 40, y - 20, max_width=80, max_height=220)

    image_path = snapshot.get('asset_path')
    rel_image_path = Path(image_path) if image_path else None
    if rel_image_path:
        coverage_image = storage_root() / rel_image_path
        if coverage_image.exists():
            _embed_image(c, coverage_image, 150, y + 200, max_width=350, max_height=350)

    c.showPage()

    # Page 3 – AI summary + ancillary images
    y = _start_page(c, width, height, "Parecer inteligente e anexos", f"{project.slug}")
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, "Resumo técnico assistido por IA")
    y -= 18
    c.setFont('Helvetica', 10)
    try:
        ai_sections = build_ai_summary(project, snapshot, metrics)
    except (AIUnavailable, AISummaryError) as exc:
        raise AnalysisReportError(str(exc)) from exc

    y = _wrap_text(c, ai_sections.get("overview", ""), 40, y, width_chars=90)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, y - 4, "Cobertura:")
    y = _wrap_text(c, ai_sections.get("coverage", ""), 40, y - 18, width_chars=90)

    ancillary_images: Iterable[tuple[str, bytes | None, str | None]] = [
        ("Perfil do enlace", getattr(user, "perfil_img", None), ai_sections.get("profile")),
        ("Diagrama Horizontal", getattr(user, "antenna_pattern_img_dia_H", None), ai_sections.get("pattern_horizontal")),
        ("Diagrama Vertical", getattr(user, "antenna_pattern_img_dia_V", None), ai_sections.get("pattern_vertical")),
    ]
    block_y = y - 20
    for label, blob, explanation in ancillary_images:
        if not blob:
            continue
        if block_y < 180:
            c.showPage()
            block_y = _start_page(c, width, height, "Anexos complementares", project.slug) - 20
        c.setFont('Helvetica-Bold', 10)
        c.drawString(40, block_y, label)
        block_y = _embed_binary_image(c, blob, 40, block_y - 6, max_width=220, max_height=140)
        if explanation:
            c.setFont('Helvetica', 9)
            block_y = _wrap_text(c, explanation, 40, block_y, width_chars=90, line_height=12)
        block_y -= 16

    recommendations = ai_sections.get("recommendations") or []
    if recommendations:
        if block_y < 120:
            c.showPage()
            block_y = _start_page(c, width, height, "Recomendações", project.slug) - 20
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, block_y, "Recomendações")
        block_y -= 16
        c.setFont('Helvetica', 10)
        for rec in recommendations:
            c.drawString(50, block_y, f"- {rec}")
            block_y -= 14

    c.setFont('Helvetica-Oblique', 8)
    c.drawString(40, 40, "Documento interno ATX Coverage — resumo automático gerado para análise rápida.")

    c.showPage()
    c.save()

    relative_path = pdf_path.relative_to(storage_root())
    asset = Asset(
        project_id=project.id,
        type=AssetType.pdf,
        path=str(relative_path),
        mime_type='application/pdf',
        meta={'kind': 'analysis', 'snapshot_asset': snapshot.get('asset_id')},
    )
    db.session.add(asset)
    db.session.flush()

    report_entry = Report(
        project_id=project.id,
        title=f"Relatório de Análise {datetime.utcnow():%d/%m/%Y %H:%M}",
        description='Relatório automático de análise de cobertura.',
        template_name='analysis_pdf',
        json_payload={'snapshot': snapshot, 'generated_at': datetime.utcnow().isoformat()},
        pdf_asset_id=asset.id,
    )
    db.session.add(report_entry)
    db.session.commit()
    return report_entry
