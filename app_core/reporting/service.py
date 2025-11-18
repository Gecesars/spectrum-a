from __future__ import annotations

import base64
import io
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import math
import json

from flask import current_app, url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

from extensions import db
from app_core.models import Asset, AssetType, Project, Report
from app_core.storage import ensure_project_path_exists, storage_root
from .ai import build_ai_summary, AIUnavailable, AISummaryError
from app_core.integrations import ibge as ibge_api
from app_core.analytics.coverage_ibge import summarize_coverage_demographics


MIN_RECEIVER_POWER_DBM = -80.0
MIN_FIELD_DBUV = 25.0
MAX_RECEIVER_ROWS = None
MAX_POP_LOOKUPS = 5
DEFAULT_HEADER_COLOR = "#0d47a1"
GAIN_OFFSET_DBI_DBD = 2.15

CLIMATE_STATE_MAP = {
    "AC": "Equatorial úmido",
    "AM": "Equatorial úmido",
    "AP": "Equatorial úmido",
    "PA": "Equatorial úmido",
    "RO": "Equatorial quente",
    "RR": "Equatorial úmido",
    "TO": "Tropical sazonal",
    "MA": "Tropical úmido",
    "PI": "Semiárido",
    "CE": "Semiárido",
    "RN": "Semiárido",
    "PB": "Semiárido",
    "PE": "Tropical úmido",
    "AL": "Tropical úmido",
    "SE": "Tropical úmido",
    "BA": "Tropical semiárido",
    "MT": "Tropical continental",
    "MS": "Tropical continental",
    "GO": "Tropical sazonal",
    "DF": "Tropical de altitude",
    "MG": "Tropical de altitude",
    "ES": "Tropical litorâneo",
    "RJ": "Tropical úmido",
    "SP": "Tropical de altitude",
    "PR": "Subtropical úmido",
    "SC": "Subtropical úmido",
    "RS": "Subtropical úmido",
}

FM_CLASS_TABLE = [
    {"label": "C", "max_erp_kw": 0.3, "max_haat_m": 60, "contour_km": 7.5},
    {"label": "B2", "max_erp_kw": 1.0, "max_haat_m": 90, "contour_km": 12.5},
    {"label": "B1", "max_erp_kw": 3.0, "max_haat_m": 90, "contour_km": 16.5},
    {"label": "A4", "max_erp_kw": 5.0, "max_haat_m": 150, "contour_km": 24.0},
    {"label": "A3", "max_erp_kw": 15.0, "max_haat_m": 150, "contour_km": 30.0},
    {"label": "A2", "max_erp_kw": 30.0, "max_haat_m": 150, "contour_km": 35.0},
    {"label": "A1", "max_erp_kw": 50.0, "max_haat_m": 150, "contour_km": 38.5},
    {"label": "E3", "max_erp_kw": 60.0, "max_haat_m": 300, "contour_km": 54.5},
    {"label": "E2", "max_erp_kw": 75.0, "max_haat_m": 450, "contour_km": 67.5},
    {"label": "E1", "max_erp_kw": 100.0, "max_haat_m": 600, "contour_km": 78.5},
]

TV_CLASS_TABLE = {
    "vhf": [
        {"label": "C", "max_erp_kw": 0.016, "max_haat_m": 150, "contour_km": 20.2},
        {"label": "B", "max_erp_kw": 0.16, "max_haat_m": 150, "contour_km": 32.3},
        {"label": "A", "max_erp_kw": 1.6, "max_haat_m": 150, "contour_km": 47.9},
        {"label": "Especial", "max_erp_kw": 16.0, "max_haat_m": 150, "contour_km": 65.6},
    ],
    "uhf": [
        {"label": "C", "max_erp_kw": 0.08, "max_haat_m": 150, "contour_km": 18.1},
        {"label": "B", "max_erp_kw": 0.8, "max_haat_m": 150, "contour_km": 29.1},
        {"label": "A", "max_erp_kw": 8.0, "max_haat_m": 150, "contour_km": 42.5},
        {"label": "Especial", "max_erp_kw": 80.0, "max_haat_m": 150, "contour_km": 58.0},
    ],
    "uhf_high": [
        {"label": "C", "max_erp_kw": 0.08, "max_haat_m": 150, "contour_km": 18.1},
        {"label": "B", "max_erp_kw": 0.8, "max_haat_m": 150, "contour_km": 29.1},
        {"label": "A", "max_erp_kw": 8.0, "max_haat_m": 150, "contour_km": 42.5},
        {"label": "Especial", "max_erp_kw": 100.0, "max_haat_m": 150, "contour_km": 58.0},
    ],
}



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


def _safe_float(value) -> float | None:
    try:
        if value in (None, "", []):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _gain_dbi_to_dbd(value):
    num = _safe_float(value)
    if num is None:
        return None
    return num - GAIN_OFFSET_DBI_DBD


def _decode_inline_image(value) -> bytes | None:
    if not value:
        return None
    if isinstance(value, dict):
        data = value.get('data')
    else:
        data = value
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if not isinstance(data, str):
        return None
    payload = data.split(',', 1)[-1] if 'base64,' in data else data
    try:
        return base64.b64decode(payload)
    except Exception:
        return None


def _project_company_logo(project: Project) -> bytes | None:
    settings = project.settings or {}
    logo_meta = settings.get('reportLogo')
    return _decode_inline_image(logo_meta)


def _infer_state_code(project: Project, snapshot: Dict[str, Any]) -> str | None:
    settings = project.settings or {}
    candidate = settings.get('state') or settings.get('uf')
    if not candidate:
        location_label = snapshot.get('tx_location_name') or settings.get('tx_location_name') or getattr(project.user, 'tx_location_name', None)
        if location_label:
            parts = [part.strip() for part in str(location_label).split(',') if part.strip()]
            if len(parts) >= 2:
                candidate = parts[1]
    if not candidate:
        return None
    return ibge_api.normalize_state_code(candidate)


def _climate_from_latitude(lat: float | None) -> str | None:
    if lat is None:
        return None
    try:
        lat_abs = abs(float(lat))
    except (TypeError, ValueError):
        return None
    if lat_abs <= 5.0:
        return "Clima equatorial"
    if lat_abs <= 18.0:
        return "Clima tropical úmido"
    if lat_abs <= 23.5:
        return "Clima tropical"
    if lat_abs <= 32.0:
        return "Clima tropical com invernos amenos"
    if lat_abs <= 40.0:
        return "Clima subtropical"
    return "Clima temperado"


def _infer_climate_descriptor(project: Project, snapshot: Dict[str, Any]) -> str | None:
    state_code = _infer_state_code(project, snapshot)
    location_name = snapshot.get('tx_location_name') or (project.settings or {}).get('tx_location_name') or getattr(project.user, 'tx_location_name', None)
    climate_label = CLIMATE_STATE_MAP.get(state_code)
    if not climate_label:
        center = snapshot.get('center') or {}
        lat = center.get('lat')
        if lat is None:
            lat = getattr(project.user, 'latitude', None)
        climate_label = _climate_from_latitude(lat)
    if climate_label and location_name:
        return f"{climate_label} — {location_name}"
    return climate_label


def _tv_band_for_frequency(freq_mhz: float | None) -> str:
    if freq_mhz is None:
        return 'uhf'
    try:
        freq = float(freq_mhz)
    except (TypeError, ValueError):
        return 'uhf'
    if freq < 470.0:
        return 'vhf'
    if freq >= 668.0:
        return 'uhf_high'
    return 'uhf'


def _dbm_to_kw(value: float | None) -> float | None:
    if value is None:
        return None
    try:
        mw = 10 ** ((float(value)) / 10.0)
    except (TypeError, ValueError):
        return None
    kw = mw / 1_000_000.0
    return max(kw, 0.0)


def _classify_station(service_label, frequency_mhz, erp_dbm, haat_m):
    erp_kw = _dbm_to_kw(_safe_float(erp_dbm))
    haat_value = _safe_float(haat_m)
    if erp_kw is None or haat_value is None:
        return {
            'label': None,
            'erp_kw': erp_kw,
            'haat_m': haat_value,
        }
    service_key = (service_label or '').lower()
    if 'tv' in service_key or 'rtvd' in service_key or 'gtvd' in service_key:
        band = _tv_band_for_frequency(_safe_float(frequency_mhz))
        table = TV_CLASS_TABLE.get(band, TV_CLASS_TABLE['uhf'])
        category = 'TV Digital'
    else:
        table = FM_CLASS_TABLE
        category = 'FM'
    selected = None
    for entry in table:
        if erp_kw <= entry['max_erp_kw'] + 1e-9 and haat_value <= entry['max_haat_m'] + 1e-6:
            selected = entry
            break
    if not selected:
        return {
            'label': 'Fora do plano básico',
            'category': category,
            'erp_kw': erp_kw,
            'haat_m': haat_value,
            'limits': table[-1],
            'contour_km': table[-1].get('contour_km'),
            'reason': 'ERP/HAAT excedem os limites regulamentares.',
        }
    return {
        'label': selected['label'],
        'category': category,
        'erp_kw': erp_kw,
        'haat_m': haat_value,
        'limits': selected,
        'contour_km': selected.get('contour_km'),
    }



def _estimate_population_impact(
    snapshot: Dict[str, Any],
    allow_remote_lookup: bool = True,
) -> tuple[list[Dict[str, Any]], int]:
    """
    Estima o impacto populacional filtrando os RX por LIMIAR em dBµV/m (campo elétrico).
    - Usa os campos do RX: 'field_strength_dbuv_m' ou 'field' (strings como "63.3 dBµV/m" são aceitas).
    - Deduplica por (municipality, state).
    - Reaproveita snapshot['ibge_registry'][code] quando disponível.
    - Chama ibge_api.fetch_demographics_by_city(city, state) apenas quando necessário.

    Observações:
    - Limiar padrão em dBµV/m pode ser passado no snapshot: snapshot['min_field_dbuv_m'].
      Se não vier, usa 28.0 dBµV/m por padrão.
    - Mantém o retorno original: (summary, total).
    """
    import re

    def _coerce_float_dbuvm(value) -> float | None:
        """Extrai float de entradas possivelmente com unidade, ex.: '63.3 dBµV/m', '55,2', 58.0."""
        if value in (None, ""):
            return None
        try:
            return float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            pass
        m = re.search(r"[-+]?\d+(?:[\.,]\d+)?", str(value))
        if not m:
            return None
        try:
            return float(m.group(0).replace(",", "."))
        except (TypeError, ValueError):
            return None

    # 1) Parâmetros e coleções base
    receivers = snapshot.get('receivers') or []
    registry = snapshot.get('ibge_registry') or {}

    # Limiar em dBµV/m (pode vir do snapshot; caso contrário, usa 28.0)
    try:
        field_threshold_dbuv_m = float(str(snapshot.get('min_field_dbuv_m', 28.0)).replace(",", "."))
    except (TypeError, ValueError):
        field_threshold_dbuv_m = 28.0

    shortlisted: list[Dict[str, Any]] = []

    # 2) Coleta e filtro por dBµV/m
    for rx in receivers:
        raw_field = rx.get('field_strength_dbuv_m')
        if raw_field in (None, ""):
            raw_field = rx.get('field')
        field_val = _coerce_float_dbuvm(raw_field)
        if field_val is None or field_val < field_threshold_dbuv_m:
            continue

        location = rx.get('location') or {}
        municipality = (
            rx.get('municipality')
            or location.get('municipality')
            or location.get('city')
            or location.get('cidade')
        )
        state = (
            rx.get('state')
            or location.get('state')
            or location.get('uf')
            or location.get('estado')
        )
        if not municipality:
            # sem município não dá para consultar IBGE
            continue

        ibge_info = rx.get('ibge') or {}
        demographics = ibge_info.get('demographics')
        if isinstance(demographics, dict) and demographics.get('total') is None:
            demographics = None

        shortlisted.append({
            "label": rx.get('label') or rx.get('name') or f"RX {len(shortlisted) + 1}",
            "municipality": municipality,
            "state": state,
            "distance_km": rx.get('distance_km') or rx.get('distance'),
            "power_dbm": rx.get('power_dbm') or rx.get('power'),
            "field_dbuv_m": field_val,  # já como float
            "quality": rx.get('quality') or rx.get('status'),
            "profile": rx.get('profile') or {},
            "ibge_code": ibge_info.get('code') or ibge_info.get('ibge_code'),
            "demographics": demographics,
        })

    # 3) Ordena por campo (desc) para priorizar melhor recepção
    shortlisted.sort(key=lambda it: (it['field_dbuv_m'] if it['field_dbuv_m'] is not None else -1e9), reverse=True)

    # 4) Deduplica por município/UF e consulta IBGE (com cache)
    summary: list[Dict[str, Any]] = []
    total = 0
    seen: set[tuple[str | None, str | None]] = set()

    for entry in shortlisted:
        city = entry.get('municipality')
        state = entry.get('state')
        key = (city, state)
        if key in seen:
            continue
        seen.add(key)

        demographics = entry.get('demographics')
        code = entry.get('ibge_code')

        if not demographics and code and registry.get(code):
            demographics = registry.get(code)

        if not demographics and allow_remote_lookup:
            try:
                demographics = ibge_api.fetch_demographics_by_city(city, state)
            except Exception:
                demographics = None

        population_value = (demographics or {}).get('total')
        summary.append({**entry, 'population': population_value, 'demographics': demographics})
        if isinstance(population_value, (int, float)):
            total += int(population_value)

        if len(summary) >= MAX_POP_LOOKUPS:
            break

    return summary, total



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


def _draw_columns(c: canvas.Canvas, top_y: int, columns: list[tuple[int, list[tuple[str, str]]]]) -> int:
    bottoms = []
    for x, lines in columns:
        bottoms.append(_draw_text_block(c, x, top_y, lines))
    return min(bottoms) if bottoms else top_y


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


def _blob_to_data_uri(blob: bytes | None) -> str | None:
    if not blob:
        return None
    try:
        encoded = base64.b64encode(blob).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return None


def _draw_header_logo(c: canvas.Canvas, blob: bytes | None, x: float, y: float, max_width: float = 70.0, max_height: float = 60.0):
    if not blob:
        return
    try:
        reader = ImageReader(io.BytesIO(blob))
        width, height = reader.getSize()
        ratio = min(max_width / width, max_height / height)
        c.drawImage(reader, x, y, width=width * ratio, height=height * ratio, mask='auto')
    except Exception:
        return


def _render_receiver_profile_plot(receiver: Dict[str, Any]) -> bytes | None:
    asset_blob = _load_profile_asset(receiver)
    if asset_blob:
        return asset_blob
    profile = receiver.get('profile') or {}
    elevations = profile.get('elevations_m') or []
    if not elevations or len(elevations) < 2:
        return None
    try:
        elevations = [float(value) for value in elevations]
    except (TypeError, ValueError):
        return None
    total_distance_km = profile.get('distance_km')
    if total_distance_km is None:
        total_distance_km = receiver.get('distance_km') or receiver.get('distance')
    try:
        total_distance_km = float(total_distance_km)
    except (TypeError, ValueError):
        total_distance_km = None
    n = len(elevations)
    if not total_distance_km or total_distance_km <= 0.0 or n < 2:
        distances = list(range(n))
        xlabel = 'Amostras'
    else:
        step = total_distance_km / (n - 1)
        distances = [i * step for i in range(n)]
        xlabel = 'Distância (km)'
    fig, ax = plt.subplots(figsize=(4.2, 2.2))
    ax.plot(distances, elevations, color='#0d47a1', linewidth=1.5)
    ax.fill_between(distances, elevations, color='#90caf9', alpha=0.3)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylabel('Elevação (m)', fontsize=8)
    ax.grid(True, linestyle='--', alpha=0.25)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return buffer.read()


def _load_profile_asset(receiver: Dict[str, Any]) -> bytes | None:
    candidate_path = receiver.get('profile_asset_path')
    if candidate_path:
        path = storage_root() / candidate_path
        if path.exists():
            try:
                return path.read_bytes()
            except OSError:
                pass
    asset_id = receiver.get('profile_asset_id')
    if asset_id:
        asset = Asset.query.filter_by(id=asset_id).first()
        if asset:
            path = storage_root() / asset.path
            if path.exists():
                try:
                    return path.read_bytes()
                except OSError:
                    pass
    inline = receiver.get('profile_image')
    if inline:
        try:
            base64_data = inline.split(',', 1)[-1]
            return base64.b64decode(base64_data)
        except Exception:
            return None
    return None


def _profile_info_from_meta(meta: Dict[str, Any] | None) -> list[str]:
    if not isinstance(meta, dict) or not meta:
        return []
    lines = []
    distance = meta.get('distance_km')
    if distance is not None:
        try:
            lines.append(f"Distância TX→RX: {float(distance):.2f} km")
        except (TypeError, ValueError):
            pass
    erp_dbm = meta.get('erp_dbm')
    if erp_dbm is not None:
        lines.append(f"ERP na direção: {_format_number(erp_dbm, ' dBm')}")
    rx_power = meta.get('rx_power_dbm')
    if rx_power is not None:
        lines.append(f"Potência recebida estimada: {_format_number(rx_power, ' dBm')}")
    field_val = meta.get('field_dbuv_m')
    if field_val is not None:
        lines.append(f"Campo estimado no RX: {_format_number(field_val, ' dBµV/m')}")
    obstacles = meta.get('obstacles')
    if obstacles:
        lines.append(f"Obstáculos na 1ª Fresnel: {obstacles}")
    return lines


def _build_link_summary(receivers: list[Dict[str, Any]]) -> tuple[str, list[Dict[str, Any]]]:
    if not receivers:
        return "Nenhum receptor cadastrado.", []
    lines = []
    payload: list[Dict[str, Any]] = []
    for rx in receivers:
        label = rx.get('label') or rx.get('name') or 'Receptor'
        municipality = rx.get('municipality') or (rx.get('location') or {}).get('municipality') or '—'
        state = rx.get('state') or (rx.get('location') or {}).get('state') or '—'
        distance = rx.get('distance_km') or rx.get('distance')
        power = rx.get('power_dbm') or rx.get('power')
        field = rx.get('field_strength_dbuv_m') or rx.get('field')
        quality = rx.get('quality') or ''
        try:
            distance_text = f"{float(distance):.1f} km" if distance is not None else "—"
        except (TypeError, ValueError):
            distance_text = "—"
        try:
            power_text = f"{float(power):.1f} dBm" if power is not None else "—"
        except (TypeError, ValueError):
            power_text = "—"
        try:
            field_text = f"{float(field):.1f} dBµV/m" if field is not None else "—"
        except (TypeError, ValueError):
            field_text = "—"
        profile = rx.get('profile') or {}
        profile_span = profile.get('distance_km')
        if profile_span:
            try:
                profile_text = f" · perfil {float(profile_span):.1f} km"
            except (TypeError, ValueError):
                profile_text = ""
        else:
            profile_text = ""
        line = (
            f"{label} — {municipality}/{state} · {distance_text} · campo {field_text} · potência {power_text}"
        )
        if quality:
            line += f" · qualidade {quality}"
        line += profile_text
        lines.append(line)
        payload.append({
            'label': label,
            'municipality': municipality,
            'state': state,
            'distance_km': distance,
            'field_dbuv_m': field,
            'power_dbm': power,
            'quality': quality,
            'profile_distance_km': profile_span,
        })
    return "\n".join(f"- {line}" for line in lines), payload


def _horizontal_peak_to_peak_db(user) -> float | None:
    pattern_data = (
        getattr(user, "antenna_pattern_data_h_modified", None)
        or getattr(user, "antenna_pattern_data_h", None)
    )
    if not pattern_data:
        return None
    try:
        entries = json.loads(pattern_data)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    values: list[float] = []
    for entry in entries:
        gain = entry.get("gain")
        if gain in (None, ""):
            continue
        try:
            values.append(float(str(gain).replace(",", ".")))
        except (TypeError, ValueError):
            continue
    values = [max(value, 1e-6) for value in values if value is not None]
    if len(values) < 2:
        return None
    peak = max(values)
    trough = min(values)
    if trough <= 0:
        return None
    return 20.0 * math.log10(peak / trough)


def _dominant_category(counts: dict[str, int] | None) -> tuple[str | None, float | None]:
    if not counts:
        return None, None
    best_name = None
    best_value = -1
    total = 0
    for name, value in counts.items():
        if value is None:
            continue
        total += value
        if value > best_value:
            best_name = name
            best_value = value
    if best_name is None or best_value <= 0:
        return None, None
    percent = (best_value / total * 100.0) if total else None
    return best_name, percent


def _read_storage_blob(relative_path: str | None) -> bytes | None:
    if not relative_path:
        return None
    candidate = Path(relative_path)
    if not candidate.is_absolute():
        candidate = storage_root() / candidate
    try:
        if candidate.exists():
            return candidate.read_bytes()
    except OSError:
        return None
    return None


def _asset_path(asset_id: str | None) -> Path | None:
    if not asset_id:
        return None
    asset = Asset.query.filter_by(id=asset_id).first()
    if asset is None:
        return None
    return storage_root() / asset.path


def _coverage_summary_path(snapshot: Dict[str, Any]) -> Path | None:
    json_asset_id = snapshot.get('json_asset_id')
    path = _asset_path(json_asset_id)
    if path and path.exists():
        return path

    asset_rel = snapshot.get('asset_path')
    if asset_rel:
        candidate = storage_root() / asset_rel
        if candidate.exists():
            summary_candidate = candidate.with_name(candidate.name.replace('_field.png', '_summary.json'))
            if summary_candidate.exists():
                return summary_candidate
    return None


def _load_coverage_ibge(snapshot: Dict[str, Any], threshold_dbuv: float = 25.0) -> Optional[Dict[str, Any]]:
    summary_path = _coverage_summary_path(snapshot)
    if not summary_path:
        return None
    try:
        return summarize_coverage_demographics(summary_path, min_field_dbuvm=threshold_dbuv)
    except Exception as exc:  # pragma: no cover - proteção adicional
        current_app.logger.warning('reporting.coverage_ibge_failed', extra={'error': str(exc)})
        return None


def _format_user_climate(user) -> str | None:
    parts = []
    if getattr(user, "temperature_k", None):
        temp_c = float(user.temperature_k) - 273.15
        parts.append(f"Temperatura {temp_c:.1f} °C")
    if getattr(user, "pressure_hpa", None):
        parts.append(f"Pressão {float(user.pressure_hpa):.0f} hPa")
    if getattr(user, "water_density", None):
        parts.append(f"Umidade abs. {float(user.water_density):.1f} g/m³")
    if not parts:
        return None
    text = " / ".join(parts)
    if getattr(user, "climate_updated_at", None):
        text += f" (amostrado em {user.climate_updated_at:%d/%m/%Y})"
    return text
def _build_metrics(project: Project, snapshot: Dict[str, Any], center_metrics: Dict[str, Any]) -> Dict[str, Any]:
    settings = project.settings or {}
    user = project.user
    power_w = _safe_float(getattr(user, "transmission_power", None))
    gain_dbi = _safe_float(getattr(user, "antenna_gain", None))
    loss_db = _safe_float(getattr(user, "total_loss", None))
    tx_power_dbm = None
    if power_w is not None:
        try:
            tx_power_dbm = 10 * math.log10(max(power_w, 1e-6) * 1000.0)
        except (ValueError, OverflowError):
            tx_power_dbm = None
    erp_dbm = None
    if tx_power_dbm is not None:
        erp_dbm = tx_power_dbm + (gain_dbi or 0.0) - (loss_db or 0.0)
    climate_text = _infer_climate_descriptor(project, snapshot) or "Clima não informado"
    haat_average = snapshot.get('haat_average_m')
    return {
        "service": settings.get("serviceType") or getattr(user, "servico", "Radiodifusão"),
        "service_class": settings.get("serviceClass") or settings.get("classe") or "—",
        "location": settings.get("tx_location_name") or snapshot.get("tx_location_name") or getattr(user, "tx_location_name", "—"),
        "erp_dbm": erp_dbm,
        "radius_km": snapshot.get("radius_km") or snapshot.get("requested_radius_km"),
        "frequency_mhz": getattr(user, "frequencia", None),
        "polarization": getattr(user, "polarization", None),
        "horizontal_peak_to_peak_db": _horizontal_peak_to_peak_db(user),
        "climate": climate_text,
        "tx_power_w": power_w,
        "antenna_gain_dbi": gain_dbi,
        "antenna_gain_dbd": _gain_dbi_to_dbd(gain_dbi),
        "losses_db": loss_db,
        "haat_average_m": _safe_float(haat_average),
    }


def _receiver_power_dbm(receiver: Dict[str, Any]) -> float | None:
    for key in ("power_dbm", "received_power_dbm", "power"):
        value = receiver.get(key)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _receiver_field_dbuv(receiver: Dict[str, Any]) -> float | None:
    for key in ("field_strength_dbuv_m", "field_dbuv", "field", "field_dbuv_m"):
        value = receiver.get(key)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _collect_receiver_entries(snapshot: Dict[str, Any], limit: int | None = MAX_RECEIVER_ROWS) -> list[Dict[str, Any]]:
    receivers = snapshot.get('receivers') or []
    entries: list[Dict[str, Any]] = []
    for rx in receivers:
        power = _receiver_power_dbm(rx)
        field = _receiver_field_dbuv(rx)
        location = rx.get('location') or {}
        municipality = rx.get('municipality') or location.get('municipality') or location.get('city')
        state = rx.get('state') or location.get('state') or location.get('uf')
        distance = rx.get('distance_km') or rx.get('distance')
        try:
            distance = float(distance) if distance is not None else None
        except (TypeError, ValueError):
            distance = None
        ibge_info = rx.get('ibge') or {}
        demographics = ibge_info.get('demographics')
        if isinstance(demographics, dict) and demographics.get('total') is None:
            demographics = None
        profile_meta = rx.get('profile_meta') or {}
        profile_info = rx.get('profile_info') or rx.get('profile_info_lines')
        entries.append({
            "label": rx.get('label') or rx.get('name') or f"RX {len(entries) + 1}",
            "municipality": municipality,
            "state": state,
            "power_dbm": power,
            "distance_km": distance,
            "field_dbuv_m": field,
            "altitude_m": rx.get('altitude_m') or location.get('altitude'),
            "quality": rx.get('quality') or rx.get('status'),
            "meets_field_min": field is not None and field >= MIN_FIELD_DBUV,
            "demographics": demographics,
            "ibge_code": ibge_info.get('code') or ibge_info.get('ibge_code'),
            "profile": rx.get('profile') or {},
            "profile_meta": profile_meta,
            "profile_info": profile_info,
            "profile_asset_path": rx.get('profile_asset_path'),
            "profile_asset_id": rx.get('profile_asset_id'),
            "profile_asset_url": rx.get('profile_asset_url'),
        })
    entries.sort(
        key=lambda item: item['power_dbm'] if item.get('power_dbm') is not None else MIN_RECEIVER_POWER_DBM,
        reverse=True,
    )
    if limit is None:
        return entries
    return entries[:limit]


def _start_page(
    c: canvas.Canvas,
    width: float,
    height: float,
    title: str,
    subtitle: str,
    theme_color: str = DEFAULT_HEADER_COLOR,
    *,
    company_logo: bytes | None = None,
) -> int:
    try:
        color_value = colors.HexColor(theme_color)
    except Exception:
        color_value = colors.HexColor(DEFAULT_HEADER_COLOR)
    c.setFillColor(color_value)
    c.rect(0, height - 80, width, 80, fill=1, stroke=0)
    c.setFillColor(colors.white)
    if company_logo:
        _draw_header_logo(c, company_logo, 34, height - 75)
        text_x = 120
    else:
        text_x = 40
    c.setFont('Helvetica-Bold', 20)
    c.drawString(text_x, height - 45, title)
    c.setFont('Helvetica', 11)
    c.drawString(text_x, height - 65, subtitle)
    c.setFillColor(colors.black)
    return height - 110


def _ensure_space(
    c: canvas.Canvas,
    y: float,
    required: float,
    width: float,
    height: float,
    title: str,
    subtitle: str,
    theme_color: str = DEFAULT_HEADER_COLOR,
    company_logo: bytes | None = None,
) -> float:
    if y - required < 70:
        c.showPage()
        return _start_page(
            c,
            width,
            height,
            title,
            subtitle,
            theme_color,
            company_logo=company_logo,
        )
    return y


def _draw_table(
    c: canvas.Canvas,
    y: float,
    columns: list[tuple[str, int]],
    rows: list[list[str]],
    width: float,
    height: float,
    project_slug: str,
    continuation_title: str,
    empty_message: str | None = None,
    line_height: int = 14,
    theme_color: str = DEFAULT_HEADER_COLOR,
    company_logo: bytes | None = None,
) -> float:
    if not rows:
        if empty_message:
            c.setFont('Helvetica', 10)
            c.drawString(40, y, empty_message)
            return y - line_height
        return y

    def _draw_header(current_y: float) -> float:
        c.setFont('Helvetica-Bold', 9)
        x = 40
        for label, col_width in columns:
            c.drawString(x, current_y, label)
            x += col_width
        return current_y - line_height

    y = _draw_header(y)
    c.setFont('Helvetica', 9)
    for row in rows:
        if y < 80:
            c.showPage()
            y = _start_page(
                c,
                width,
                height,
                continuation_title,
                project_slug,
                theme_color,
                company_logo=company_logo,
            ) - 20
            y = _draw_header(y)
            c.setFont('Helvetica', 9)
        x = 40
        for text, (_, col_width) in zip(row, columns):
            c.drawString(x, y, text)
            x += col_width
        y -= line_height
    return y



def build_analysis_preview(project: Project, *, allow_ibge: bool = True) -> Dict[str, Any]:
    snapshot = _latest_snapshot(project)
    user = project.user
    settings = project.settings or {}
    company_logo_blob = _project_company_logo(project)
    center_metrics = snapshot.get('center_metrics') or {}
    loss_components = snapshot.get('loss_components') or {}
    gain_components = snapshot.get('gain_components') or {}
    metrics = _build_metrics(project, snapshot, center_metrics)
    project_notes = (
        (settings.get('projectNotes') or settings.get('project_notes') or settings.get('notes'))
        or project.description
        or getattr(user, 'notes', None)
    )
    metrics['project_notes'] = project_notes or "Sem notas adicionais registradas."

    receivers_full = snapshot.get('receivers') or []
    link_summary_text, link_payload = _build_link_summary(receivers_full)
    coverage_ibge = _load_coverage_ibge(snapshot) if allow_ibge else None
    metrics['link_summary'] = link_summary_text
    metrics['coverage_ibge'] = coverage_ibge

    saved_horizontal = _decode_inline_image(snapshot.get('diagram_horizontal_b64'))
    saved_vertical = _decode_inline_image(snapshot.get('diagram_vertical_b64'))
    diagram_images = {
        "mancha_de_cobertura": _read_storage_blob(snapshot.get('asset_path')),
        "perfil": getattr(user, "perfil_img", None),
        "diagrama_horizontal": saved_horizontal or getattr(user, "antenna_pattern_img_dia_H", None),
        "diagrama_vertical": saved_vertical or getattr(user, "antenna_pattern_img_dia_V", None),
    }

    limited_payload = link_payload[:2]
    summary_lines = link_summary_text.splitlines()
    limited_summary_text = "\n".join(summary_lines[:len(limited_payload)]) if limited_payload else "Nenhum receptor selecionado."
    ai_metrics = dict(metrics)
    ai_metrics['link_summary'] = limited_summary_text
    try:
        ai_sections = build_ai_summary(project, snapshot, ai_metrics, diagram_images, links_payload=limited_payload)
    except (AIUnavailable, AISummaryError) as exc:
        raise AnalysisReportError(str(exc)) from exc

    receiver_entries = _collect_receiver_entries(snapshot, limit=None)
    population_details, population_total = _estimate_population_impact(
        snapshot,
        allow_remote_lookup=allow_ibge,
    )
    haat_radials = snapshot.get('haat_radials') or []
    classification = _classify_station(
        metrics.get('service'),
        metrics.get('frequency_mhz'),
        metrics.get('erp_dbm'),
        metrics.get('haat_average_m'),
    )
    if classification.get('label'):
        metrics['service_class'] = classification['label']
    metrics['classification'] = classification
    metrics['contour_distance_km'] = classification.get('contour_km')
    metrics['contour_distance_km'] = classification.get('contour_km')
    metrics['haat_radials'] = haat_radials

    heatmap_url = None
    colorbar_url = None
    if snapshot.get('asset_id'):
        asset = Asset.query.filter_by(id=snapshot.get('asset_id')).first()
        if asset:
            heatmap_url = url_for('projects.asset_preview', slug=project.slug, asset_id=asset.id)
    if snapshot.get('colorbar_asset_id'):
        asset = Asset.query.filter_by(id=snapshot.get('colorbar_asset_id')).first()
        if asset:
            colorbar_url = url_for('projects.asset_preview', slug=project.slug, asset_id=asset.id)

    return {
        'project': {
            'slug': project.slug,
            'name': project.name,
        },
        'coverage': {
            'engine': snapshot.get('engine'),
            'generated_at': snapshot.get('generated_at'),
            'heatmap_url': heatmap_url,
            'colorbar_url': colorbar_url,
        },
        'metrics': metrics,
        'ai_sections': ai_sections,
        'receivers': receivers_full,
        'receiver_summary': receiver_entries,
        'population': {
            'summary': population_details,
            'total': population_total,
        },
        'coverage_ibge': coverage_ibge,
        'diagram_images': {
            'perfil': _blob_to_data_uri(diagram_images.get('perfil')),
            'diagrama_horizontal': _blob_to_data_uri(diagram_images.get('diagrama_horizontal')),
            'diagrama_vertical': _blob_to_data_uri(diagram_images.get('diagrama_vertical')),
            'company_logo': _blob_to_data_uri(company_logo_blob),
        },
        'header_color': DEFAULT_HEADER_COLOR,
        'notes': metrics['project_notes'],
        'ibge_registry': snapshot.get('ibge_registry'),
        'link_summary': link_summary_text,
        'link_payload': link_payload,
        'branding': {
            'company_logo': _blob_to_data_uri(company_logo_blob),
        },
        'regulatory': {
            'classification': classification,
            'haat_radials': haat_radials,
        },
        'haat': {
            'average_m': metrics.get('haat_average_m'),
            'radials': haat_radials,
        },
    }

def _format_int(value) -> str:
    """
    Formata inteiros com separador de milhar como ponto (1.234.567).
    Aceita value numérico ou string (inclui '1.234,56'); arredonda quando for float.
    Retorna '—' se não for possível converter.
    """
    if value in (None, ""):
        return "—"
    try:
        # normaliza vírgula decimal para ponto e remove espaços
        s = str(value).strip().replace(",", ".")
        n = float(s)
        i = int(round(n))
        return f"{i:,}".replace(",", ".")
    except (TypeError, ValueError):
        return "—"


def _format_currency(value) -> str:
    if value in (None, ""):
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    formatted = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"






def generate_analysis_report(
    project: Project,
    overrides: Dict[str, Any] | None = None,
    *,
    allow_ibge: bool = False,
) -> Report:
    overrides = overrides or {}
    snapshot = _latest_snapshot(project)
    user = project.user
    settings = project.settings or {}
    center_metrics = snapshot.get('center_metrics') or {}
    loss_components = snapshot.get('loss_components') or {}
    gain_components = snapshot.get('gain_components') or {}
    metrics = _build_metrics(project, snapshot, center_metrics)
    project_notes = (
        (settings.get('projectNotes') or settings.get('project_notes') or settings.get('notes'))
        or project.description
        or getattr(user, 'notes', None)
    )
    if overrides.get('project_notes'):
        project_notes = overrides['project_notes']
    metrics['project_notes'] = project_notes or "Sem notas adicionais registradas."

    receivers_full = snapshot.get('receivers') or []
    link_summary_text, link_payload = _build_link_summary(receivers_full)
    metrics['link_summary'] = link_summary_text

    coverage_rel_path = snapshot.get('asset_path')
    coverage_image_path: Path | None = None
    if coverage_rel_path:
        candidate = Path(coverage_rel_path)
        if not candidate.is_absolute():
            candidate = storage_root() / candidate
        if candidate.exists():
            coverage_image_path = candidate

    saved_horizontal = _decode_inline_image(snapshot.get('diagram_horizontal_b64'))
    saved_vertical = _decode_inline_image(snapshot.get('diagram_vertical_b64'))
    diagram_images = {
        "mancha_de_cobertura": _read_storage_blob(coverage_rel_path),
        "perfil": getattr(user, "perfil_img", None),
        "diagrama_horizontal": saved_horizontal or getattr(user, "antenna_pattern_img_dia_H", None),
        "diagrama_vertical": saved_vertical or getattr(user, "antenna_pattern_img_dia_V", None),
    }
    haat_radials = snapshot.get('haat_radials') or []
    classification = _classify_station(
        metrics.get('service'),
        metrics.get('frequency_mhz'),
        metrics.get('erp_dbm'),
        metrics.get('haat_average_m'),
    )
    if classification.get('label'):
        metrics['service_class'] = classification['label']
    metrics['classification'] = classification
    metrics['haat_radials'] = haat_radials

    provided_sections = overrides.get('ai_sections')
    if provided_sections:
        ai_sections = dict(provided_sections)
    else:
        limited_payload = link_payload[:2]
        summary_lines = link_summary_text.splitlines()
        limited_summary_text = "\n".join(summary_lines[:len(limited_payload)]) if limited_payload else "Nenhum receptor selecionado."
        ai_metrics = dict(metrics)
        ai_metrics['link_summary'] = limited_summary_text
        try:
            ai_sections = build_ai_summary(project, snapshot, ai_metrics, diagram_images, links_payload=limited_payload)
        except (AIUnavailable, AISummaryError) as exc:
            raise AnalysisReportError(str(exc)) from exc

    if isinstance(ai_sections.get('recommendations'), str):
        ai_sections['recommendations'] = [
            item.strip()
            for item in ai_sections['recommendations'].splitlines()
            if item.strip()
        ]

    required_ai_fields = ["overview", "coverage", "profile", "pattern_horizontal", "pattern_vertical", "recommendations", "conclusion", "link_analyses"]
    for field in required_ai_fields:
        if field in ("recommendations", "link_analyses"):
            ai_sections.setdefault(field, [])
        else:
            ai_sections.setdefault(field, "")

    receiver_entries = _collect_receiver_entries(snapshot, limit=None)
    population_details, population_total = _estimate_population_impact(
        snapshot,
        allow_remote_lookup=allow_ibge,
    )
    population_lookup = {
        (row.get('municipality'), row.get('state')): row.get('demographics')
        for row in population_details
        if row.get('demographics')
    }
    coverage_ibge = _load_coverage_ibge(snapshot) if allow_ibge else None

    header_color = overrides.get('header_color') or DEFAULT_HEADER_COLOR
    company_logo_blob = _project_company_logo(project)

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
        f"Relatório Técnico — {project.name}",
        f"Gerado em {datetime.utcnow():%d/%m/%Y %H:%M UTC}",
        header_color,
        company_logo=company_logo_blob,
    )

    primary_rx = receiver_entries[0] if receiver_entries else None
    primary_rx_loss = None
    primary_rx_label = None
    if primary_rx:
        try:
            erp_value = float(metrics.get("erp_dbm")) if metrics.get("erp_dbm") is not None else None
            rx_power = float(primary_rx.get('power_dbm')) if primary_rx.get('power_dbm') is not None else None
            if erp_value is not None and rx_power is not None:
                primary_rx_loss = erp_value - rx_power
                primary_rx_label = primary_rx.get('label') or 'RX'
        except (TypeError, ValueError):
            primary_rx_loss = None

    left_column = [
        ('Projeto', project.name),
        ('Slug', project.slug),
        ('Serviço / Classe', f"{metrics.get('service')} / {metrics.get('service_class')}"),
        ('Engine', snapshot.get('engine', '—')),
        ('Localização', metrics.get("location") or '—'),
        ('Raio planejado', _format_number(metrics.get("radius_km"), 'km')),
        ('Clima', metrics.get("climate")),
        ('HAAT médio (3-16 km)', _format_number(metrics.get('haat_average_m'), 'm')),
        ('Radiais analisadas', str(len(haat_radials)) if haat_radials else '—'),
        ('Contorno protegido', _format_number(metrics.get('contour_distance_km'), 'km')),
    ]
    right_column = [
        ('Potência TX', _format_number(metrics.get('tx_power_w'), 'W')),
        ('Ganho TX (dBd)', _format_number(_gain_dbi_to_dbd(getattr(user, 'antenna_gain', None)), 'dBd')),
        ('Perdas Sistêmicas', _format_number(metrics.get('losses_db'), 'dB')),
        ('Polarização', getattr(user, 'polarization', '—')),
        ('Perda combinada', _format_number(center_metrics.get('combined_loss_center_db'), 'dB')),
        ('Ganho efetivo', _format_number(center_metrics.get('effective_gain_center_db'), 'dB')),
        ('L_b (centro)', _format_number((loss_components.get('L_b') or {}).get('center'), 'dB')),
        ('Ajuste horizontal', _format_number(gain_components.get('horizontal_adjustment_db_min'), 'dB')),
        ('Ajuste vertical', _format_number(gain_components.get('vertical_adjustment_db'), 'dB')),
        ('Pico a pico (H)', _format_number(metrics.get('horizontal_peak_to_peak_db'), 'dB')),
    ]
    if primary_rx_label and primary_rx_loss is not None:
        right_column.append((f'Atenuação até {primary_rx_label}', _format_number(primary_rx_loss, 'dB')))
    class_limits = classification.get('limits') or {}
    if class_limits:
        limit_text = f"{_format_number(class_limits.get('max_erp_kw'), 'kW')} / {_format_number(class_limits.get('max_haat_m'), 'm')}"
        right_column.append(('Limite ERP/HAAT da classe', limit_text))
    y = _draw_columns(c, y, [
        (40, left_column),
        (320, right_column),
    ]) - 18

    classification_text = None
    if classification.get('label'):
        erp_text = _format_number(classification.get('erp_kw'), 'kW')
        haat_text = _format_number(classification.get('haat_m'), 'm')
        contour_text = _format_number(classification.get('contour_km'), 'km')
        pieces = [
            f"Classe {classification['label']} ({classification.get('category') or 'FM/TV'})",
            f"ERP analisada {erp_text}",
            f"HAAT efetivo {haat_text}",
        ]
        if classification.get('contour_km') is not None:
            pieces.append(f"Contorno protegido {contour_text}")
        classification_text = ' · '.join(filter(None, pieces))
    elif classification.get('reason'):
        classification_text = classification['reason']
    if classification_text:
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, "Classificação regulamentar")
        y -= 16
        c.setFont('Helvetica', 10)
        y = _wrap_text(c, classification_text, 40, y, width_chars=95)
        y -= 6

    notes_text = metrics.get("project_notes")
    if notes_text:
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, "Notas do projeto")
        y = _wrap_text(c, notes_text, 40, y - 18, width_chars=95)
        y -= 6

    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, "Resumo executivo")
    overview_text = ai_sections.get("overview") or "Resumo indisponível."
    y = _wrap_text(c, overview_text, 40, y - 18, width_chars=95)

    y = _ensure_space(
        c,
        y,
        360,
        width,
        height,
        f"Relatório Técnico — {project.name}",
        f"Gerado em {datetime.utcnow():%d/%m/%Y %H:%M UTC}",
        header_color,
        company_logo=company_logo_blob,
    )
    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, "Mancha de cobertura")
    map_y = y - 20
    colorbar_path = _asset_path(snapshot.get('colorbar_asset_id'))
    max_map_width = int(width - 80)
    if colorbar_path and Path(colorbar_path).exists():
        map_y = _embed_image(c, Path(colorbar_path), 40, map_y, max_width=max_map_width, max_height=50)
    if coverage_image_path:
        map_y = _embed_image(c, coverage_image_path, 40, map_y - 6, max_width=max_map_width, max_height=360)
    else:
        c.setFont('Helvetica-Oblique', 9)
        c.drawString(40, map_y, 'Prévia da cobertura não localizada.')
        map_y -= 18
    c.setFont('Helvetica', 10)
    coverage_text = ai_sections.get("coverage") or "Observações de cobertura indisponíveis."
    map_y = _wrap_text(c, coverage_text, 40, map_y - 6, width_chars=95)
    y = map_y - 10

    c.showPage()

    y = _start_page(
        c,
        width,
        height,
        "Sistema irradiante",
        project.slug,
        header_color,
        company_logo=company_logo_blob,
    )

    antenna_block = [
        ('Modelo', settings.get('antennaModel') or settings.get('antenna_model') or '—'),
        ('Altura da torre', _format_number(getattr(user, 'tower_height', None), 'm')),
        ('Azimute/Tilt', f"{_format_number(getattr(user, 'antenna_direction', None), '°')} / {_format_number(getattr(user, 'antenna_tilt', None), '°')}"),
        ('Polarização', getattr(user, 'polarization', '—')),
    ]
    y = _draw_text_block(c, 40, y, antenna_block)

    antenna_metrics_block = [
        ('ERP estimada', _format_number(metrics.get("erp_dbm"), 'dBm')),
        ('Frequência', _format_number(metrics.get("frequency_mhz"), 'MHz')),
        ('Polarização de projeto', metrics.get("polarization") or '—'),
    ]
    y = _draw_text_block(c, 40, y - 4, antenna_metrics_block)

    diagram_sections = [
        ("Diagrama Horizontal", diagram_images.get("diagrama_horizontal"), ai_sections.get("pattern_horizontal")),
        ("Diagrama Vertical", diagram_images.get("diagrama_vertical"), ai_sections.get("pattern_vertical")),
    ]
    for title, blob, note in diagram_sections:
        if not blob:
            continue
        y = _ensure_space(
            c,
            y,
            260,
            width,
            height,
            "Sistema irradiante (cont.)",
            project.slug,
            header_color,
            company_logo=company_logo_blob,
        )
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, title)
        y = _embed_binary_image(c, blob, 40, y - 6, max_width=int(width - 120), max_height=240)
        explanation = note or "Análise não disponível para este diagrama."
        c.setFont('Helvetica', 10)
        y = _wrap_text(c, explanation, 40, y, width_chars=95, line_height=13)
        y -= 12

    if haat_radials:
        y = _ensure_space(
            c,
            y,
            200,
            width,
            height,
            "Sistema irradiante (cont.)",
            project.slug,
            header_color,
            company_logo=company_logo_blob,
        )
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, "Altura média por radial (3–16 km)")
        y -= 18
        haat_columns = [
            ("Azimute", 80),
            ("HAAT", 80),
            ("Terreno médio", 110),
        ]
        haat_rows = [
            [
                f"{int(item.get('bearing_deg', 0))}°",
                _format_number(item.get('haat_m'), 'm'),
                _format_number(item.get('avg_terrain_m'), 'm'),
            ]
            for item in haat_radials
        ]
        y = _draw_table(
            c,
            y,
            haat_columns,
            haat_rows,
            width,
            height,
            project.slug,
            "Sistema irradiante (cont.)",
            theme_color=header_color,
            company_logo=company_logo_blob,
        )
        y -= 6

    c.showPage()

    y = _start_page(
        c,
        width,
        height,
        "Enlaces e impacto populacional",
        project.slug,
        header_color,
        company_logo=company_logo_blob,
    )

    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, "Perfil do enlace principal")
    profile_blob = getattr(user, "perfil_img", None)
    y = _embed_binary_image(c, profile_blob, 40, y - 6, max_width=int(width - 120), max_height=220)
    profile_text = ai_sections.get("profile") or "Sem observações adicionais registradas para o perfil."
    c.setFont('Helvetica', 10)
    y = _wrap_text(c, profile_text, 40, y, width_chars=95)
    y -= 12

    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, f"Receptores avaliados (≥ {int(MIN_RECEIVER_POWER_DBM)} dBm)")
    y -= 18

    for idx, entry in enumerate(receiver_entries, 1):
        y = _ensure_space(
            c,
            y,
            130,
            width,
            height,
            "Receptores avaliados (cont.)",
            project.slug,
            header_color,
            company_logo=company_logo_blob,
        )
        label = entry.get('label') or f"Receptor {idx}"
        c.setFont('Helvetica-Bold', 10)
        c.drawString(40, y, label)
        y -= 12
        municipality = entry.get('municipality') or '—'
        state = entry.get('state') or '—'
        distance_text = _format_number(entry.get('distance_km'), 'km')
        field_text = _format_number(entry.get('field_dbuv_m'), 'dBµV/m')
        power_text = _format_number(entry.get('power_dbm'), 'dBm')
        altitude_text = _format_number(entry.get('altitude_m'), 'm')
        quality_text = entry.get('quality') or '—'
        compliance = "Atende (>=25 dBµV/m)" if entry.get('meets_field_min') else "Abaixo de 25 dBµV/m"
        info_lines = [
            ("Município/UF", f"{municipality} / {state}"),
            ("Distância", distance_text),
            ("Campo", field_text),
            ("Potência", power_text),
            ("Altitude RX", altitude_text),
            ("Conformidade", compliance),
            ("Qualidade", quality_text),
        ]
        y = _draw_text_block(c, 50, y, info_lines)
        key = (entry.get('municipality'), entry.get('state'))
        demo = population_lookup.get(key) or {}
        pop_value = demo.get('total')
        sex_dom = _dominant_category(demo.get('sex') or {})
        age_dom = _dominant_category(demo.get('age') or {})
        demography_text = ""
        if pop_value:
            demography_text += f"População estimada: {_format_int(pop_value)}."
        if sex_dom[0]:
            demography_text += f" Sexo dominante: {sex_dom[0]}"
            if sex_dom[1] is not None:
                demography_text += f" ({sex_dom[1]:.1f}%)."
        if age_dom[0]:
            demography_text += f" Faixa etária predominante: {age_dom[0]}"
            if age_dom[1] is not None:
                demography_text += f" ({age_dom[1]:.1f}%)."
        if demography_text:
            y = _wrap_text(c, demography_text, 50, y - 4, width_chars=95)
            y -= 4
        y -= 4

    if population_details:
        y = _ensure_space(
            c,
            y,
            120,
            width,
            height,
            "Enlaces e impacto populacional (cont.)",
            project.slug,
            header_color,
            company_logo=company_logo_blob,
        )
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, "Demografia detalhada por município")
        y -= 18
        c.setFont('Helvetica', 9)
        for detail in population_details:
            demo = detail.get('demographics') or {}
            pop_text = _format_int(demo.get('total'))
            sex_breakdown = demo.get('sex') or {}
            age_breakdown = demo.get('age') or {}
            sex_items = sorted(sex_breakdown.items(), key=lambda item: item[1], reverse=True)
            age_items = sorted(age_breakdown.items(), key=lambda item: item[1], reverse=True)
            sex_parts = [f"{name}: {_format_int(value)}" for name, value in sex_items[:2]]
            age_parts = [f"{name}: {_format_int(value)}" for name, value in age_items[:3]]
            label = f"{detail.get('municipality') or '—'} / {detail.get('state') or '—'}"
            text = f"{label} — População: {pop_text}"
            if sex_parts:
                text += f" | Sexo: {'; '.join(sex_parts)}"
            if age_parts:
                text += f" | Idade: {'; '.join(age_parts)}"
            y = _wrap_text(c, text, 40, y, width_chars=95, line_height=12) - 4
            if y < 90:
                c.showPage()
                y = _start_page(
                    c,
                    width,
                    height,
                    "Enlaces e impacto populacional (cont.)",
                    project.slug,
                    header_color,
                    company_logo=company_logo_blob,
                ) - 20
                c.setFont('Helvetica-Bold', 11)
                c.drawString(40, y, "Demografia detalhada por município (cont.)")
                y -= 18
                c.setFont('Helvetica', 9)

    coverage_ibge_municipalities = (coverage_ibge or {}).get('municipalities') if coverage_ibge else []
    if coverage_ibge_municipalities:
        y = _ensure_space(
            c,
            y,
            160,
            width,
            height,
            "Enlaces e impacto populacional (cont.)",
            project.slug,
            header_color,
            company_logo=company_logo_blob,
        )
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, f"Municípios com campo ≥ {int((coverage_ibge or {}).get('threshold_dbuv', 25))} dBµV/m")
        y -= 18
        coverage_columns = [
            ("Município/UF", 150),
            ("Campo máx (dBµV/m)", 100),
            ("População", 90),
            ("Ano Pop", 60),
            ("Renda per capita", 120),
            ("Ano Renda", 70),
        ]
        coverage_rows: List[List[str]] = []
        for entry in coverage_ibge_municipalities:
            city_state = f"{entry.get('municipality') or '—'} / {entry.get('state') or '—'}"
            field_val = entry.get('max_field_dbuvm')
            field_text = f"{field_val:.1f}" if isinstance(field_val, (int, float)) else "—"
            pop_text = _format_int(entry.get('population'))
            pop_year = entry.get('population_year')
            pop_year_text = str(pop_year) if pop_year else "—"
            income_text = _format_currency(entry.get('income_per_capita'))
            income_year = entry.get('income_year')
            income_year_text = str(income_year) if income_year else "—"
            coverage_rows.append([
                city_state,
                field_text,
                pop_text,
                pop_year_text,
                income_text,
                income_year_text,
            ])
        y = _draw_table(
            c,
            y,
            coverage_columns,
            coverage_rows,
            width,
            height,
            project.slug,
            "Municípios com campo ≥ 25 dBµV/m (cont.)",
            theme_color=header_color,
            company_logo=company_logo_blob,
        )
        y -= 6

    link_analysis_map = {}
    for item in ai_sections.get("link_analyses") or []:
        if not isinstance(item, dict):
            continue
        label_key = (item.get('label') or '').strip()
        analysis_text = item.get('analysis')
        if label_key and analysis_text:
            link_analysis_map[label_key.lower()] = str(analysis_text)

    if receivers_full:
        section_title = "Perfis por receptor"
        y = _ensure_space(
            c,
            y,
            220,
            width,
            height,
            section_title,
            project.slug,
            header_color,
            company_logo=company_logo_blob,
        )
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, section_title)
        y -= 18
        for idx, rx in enumerate(receivers_full, 1):
            if y < 200:
                c.showPage()
                y = _start_page(
                    c,
                    width,
                    height,
                    f"{section_title} (cont.)",
                    project.slug,
                    header_color,
                    company_logo=company_logo_blob,
                )
                c.setFont('Helvetica-Bold', 11)
                c.drawString(40, y, f"{section_title} (cont.)")
                y -= 18
            label = rx.get('label') or rx.get('name') or f"Receptor {idx}"
            c.setFont('Helvetica-Bold', 10)
            c.drawString(40, y, label)
            y -= 12
            location = rx.get('location') or {}
            municipality = rx.get('municipality') or location.get('municipality') or '—'
            state = rx.get('state') or location.get('state') or '—'
            lat = location.get('lat') or rx.get('lat')
            lon = location.get('lng') or location.get('lon') or rx.get('lng')
            try:
                coord_text = f"{float(lat):.4f}, {float(lon):.4f}"
            except (TypeError, ValueError):
                coord_text = "—"
            field_value = (
                rx.get('field_strength_dbuv_m')
                or rx.get('field')
                or entry.get('field_dbuv_m')
            )
            power_value = rx.get('power_dbm') or rx.get('power')
            distance_value = rx.get('distance_km') or rx.get('distance')
            altitude_value = rx.get('altitude_m') or location.get('altitude')
            quality_value = rx.get('quality') or rx.get('status') or '—'
            meets_field_min = entry.get('meets_field_min')
            field_compliance = "Atende (>=25 dBµV/m)" if meets_field_min else "Abaixo de 25 dBµV/m"
            info_lines = [
                ('Município/UF', f"{municipality} / {state}"),
                ('Coordenadas', coord_text),
                ('Campo', _format_number(field_value, 'dBµV/m')),
                ('Potência', _format_number(power_value, 'dBm')),
                ('Distância', _format_number(distance_value, 'km')),
                ('Altitude RX', _format_number(altitude_value, 'm')),
                ('Conformidade 25 dBµV/m', field_compliance),
                ('Qualidade', quality_value),
            ]
            y = _draw_text_block(c, 50, y, info_lines)
            analysis_text = None
            key_lower = label.lower()
            if key_lower in link_analysis_map:
                analysis_text = link_analysis_map[key_lower]
            else:
                for key, text_val in link_analysis_map.items():
                    if key in key_lower:
                        analysis_text = text_val
                        break
            if analysis_text:
                c.setFont('Helvetica-Oblique', 9)
                y = _wrap_text(c, f"Observação automática: {analysis_text}", 50, y, width_chars=95, line_height=12)
                y -= 4
            else:
                c.setFont('Helvetica-Oblique', 9)
                y = _wrap_text(
                    c,
                    "Observação automática indisponível; utilize os níveis de campo acima como referência.",
                    50,
                    y,
                    width_chars=95,
                    line_height=12,
                )
                y -= 4
            profile_blob = _render_receiver_profile_plot(rx)
            if profile_blob:
                y = _embed_binary_image(c, profile_blob, 50, y - 4, max_width=int(width - 120), max_height=160)
            profile_info_lines = rx.get('profile_info') or _profile_info_from_meta(rx.get('profile_meta'))
            if profile_info_lines:
                c.setFont('Helvetica', 9)
                for line in profile_info_lines:
                    y -= 12
                    c.drawString(50, y, line)
                y -= 4
            y -= 8

    y = _ensure_space(
        c,
        y,
        120,
        width,
        height,
        "Conclusão e alcance estimado",
        project.slug,
        header_color,
        company_logo=company_logo_blob,
    )
    c.setFont('Helvetica-Bold', 11)
    c.drawString(40, y, "Conclusão e alcance estimado")
    y -= 16
    if population_total:
        viewers_text = f"{population_total:,}".replace(",", ".")
        conclusion = (
            f"Com base nos receptores acima de {int(MIN_RECEIVER_POWER_DBM)} dBm e nos dados públicos do IBGE, "
            f"estima-se que a mancha de cobertura atinge aproximadamente {viewers_text} telespectadores potenciais."
        )
    else:
        conclusion = (
            "Não foi possível estimar o alcance de telespectadores por indisponibilidade temporária dos serviços do IBGE."
        )
    y = _wrap_text(c, conclusion, 40, y, width_chars=95)
    y -= 10

    y = _ensure_space(
        c,
        y,
        120,
        width,
        height,
        "Parecer técnico",
        project.slug,
        header_color,
        company_logo=company_logo_blob,
    )
    ai_conclusion = ai_sections.get("conclusion") or "Dados ainda não consolidados para o parecer automatizado."
    if ai_conclusion:
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, "Parecer técnico consolidado")
        y -= 16
        c.setFont('Helvetica', 10)
        y = _wrap_text(c, ai_conclusion, 40, y, width_chars=95)
        y -= 10
    positive_note = (
        f"A equipe técnica mantém perspectiva otimista para {project.name}, "
        "uma vez que as condições climáticas e os níveis de ERP indicam margem para otimizações contínuas."
    )
    c.setFont('Helvetica', 10)
    y = _wrap_text(c, positive_note, 40, y, width_chars=95)
    y -= 10

    recommendations = ai_sections.get("recommendations") or []
    if recommendations:
        y = _ensure_space(
            c,
            y,
            140,
            width,
            height,
            "Recomendações técnicas",
            project.slug,
            header_color,
            company_logo=company_logo_blob,
        )
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, "Recomendações técnicas")
        y -= 16
        c.setFont('Helvetica', 10)
        for rec in recommendations:
            y = _wrap_text(c, f"- {rec}", 40, y, width_chars=95)
            y -= 4

    c.setFont('Helvetica-Oblique', 8)
    c.drawString(40, 40, "Documento interno ATX Coverage")

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
