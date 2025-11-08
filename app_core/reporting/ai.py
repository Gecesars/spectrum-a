from __future__ import annotations

import json
import re
from typing import Any, Dict

import google.generativeai as genai
from flask import current_app


class AIUnavailable(RuntimeError):
    """Raised when the Gemini client cannot be used."""


class AISummaryError(RuntimeError):
    """Raised when the summary request fails for any reason."""


ANALYSIS_PROMPT = """Você é um engenheiro especialista em radiodifusão.
Não invente dados: se algo não existir, explique a limitação explicitamente.
Responda EXCLUSIVAMENTE em JSON válido no formato:
{{
  "overview": "...",
  "coverage": "...",
  "profile": "...",
  "pattern_horizontal": "...",
  "pattern_vertical": "...",
  "recommendations": ["...", "..."]
}}

Contexto:
- Projeto: {project_name} ({project_slug})
- Serviço: {service} / Classe {service_class}
- Região: {location}
- Engine: {engine}
- Clima: {climate}

Parâmetros principais:
- ERP estimada: {erp_dbm} dBm
- Raio planejado: {radius_km} km
- Frequência: {frequency_mhz} MHz
- Polarização: {polarization}
- Campo no centro: {field_center} dBµV/m
- Potência RX: {rx_power} dBm
- Perda combinada: {loss_center} dB
- Ganho efetivo: {gain_center} dB

Requisitos:
- overview: resumo executivo até 3 frases.
- coverage: análise da mancha/cobertura.
- profile: análise do perfil de enlace.
- pattern_horizontal: comentários sobre direcionalidade azimutal.
- pattern_vertical: comentários sobre tilt/elevação.
- recommendations: lista com 2 recomendações objetivas.
"""


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.S)


def _extract_json_text(raw_text: str) -> str:
    raw_text = (raw_text or "").strip()
    if not raw_text:
        raise AISummaryError("Resposta vazia do modelo Gemini.")
    # tenta detectar bloco ```json ... ```
    fence_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.S | re.I)
    if fence_match:
        return fence_match.group(1)
    match = _JSON_BLOCK_RE.search(raw_text)
    if match:
        return match.group(0)
    return raw_text


def build_ai_summary(project, snapshot: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        raise AIUnavailable("GEMINI_API_KEY não configurada.")
    model_name = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    prompt = ANALYSIS_PROMPT.format(
        project_name=project.name,
        project_slug=project.slug,
        service=metrics.get("service") or project.settings.get("serviceType") if project.settings else "FM",
        service_class=metrics.get("service_class") or project.settings.get("serviceClass") if project.settings else "—",
        location=metrics.get("location") or snapshot.get("tx_location_name") or "—",
        erp_dbm=metrics.get("erp_dbm") or "—",
        radius_km=metrics.get("radius_km") or "—",
        frequency_mhz=metrics.get("frequency_mhz") or "—",
        polarization=metrics.get("polarization") or "—",
        field_center=metrics.get("field_center") or "—",
        rx_power=metrics.get("rx_power") or "—",
        loss_center=metrics.get("loss_center") or "—",
        gain_center=metrics.get("gain_center") or "—",
        engine=snapshot.get("engine") or "—",
        climate=metrics.get("climate") or "Não informado",
    )

    response = model.generate_content(prompt)
    text = _extract_json_text(getattr(response, "text", ""))

    try:
        summary = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AISummaryError("Formato de resposta inválido do modelo.") from exc

    required = [
        "overview",
        "coverage",
        "profile",
        "pattern_horizontal",
        "pattern_vertical",
        "recommendations",
    ]
    for key in required:
        if key not in summary:
            raise AISummaryError(f"Campo '{key}' ausente na resposta do modelo.")
    recs = summary.get("recommendations")
    if isinstance(recs, str):
        recs = [item.strip() for item in recs.split("\n") if item.strip()]
    if not isinstance(recs, list):
        raise AISummaryError("Campo 'recommendations' deveria ser uma lista.")
    summary["recommendations"] = recs[:2] if recs else []
    return summary
