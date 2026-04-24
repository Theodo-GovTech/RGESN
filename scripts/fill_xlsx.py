"""Remplit le tableur officiel RGESN 2024 à partir d'un declaration.json.

Usage:
    python scripts/fill_xlsx.py <declaration.json> [<output.xlsx>]

Le template source est toujours docs/rgesn_2024_outil_declaration.xlsx.
Si <output.xlsx> n'est pas fourni, le fichier est écrit dans out/<service>_<date>.xlsx.

Cellules écrites par critère (dans la feuille thématique) :
  - E{row} : évaluation      (Conforme / Non conforme / Non applicable / À évaluer)
  - F{row} : date d'évaluation (YYYY-MM-DD)
  - G{row} : évolutions potentielles (optionnel)
  - I{row} : actions à mener         (optionnel, usage interne)
  - J{row} : qui                     (optionnel, usage interne)
  - K{row} : pour quand              (optionnel, usage interne)
  - C{row+1} : texte de déclaration (cellule fusionnée C:G, ligne de continuation)

Feuille "Score d'avancement" :
  - C5 : nom du service
  - C6 : échantillons
  - C7 : entité qui évalue
  - C8 : responsable
  - C11 : date de l'évaluation
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs" / "rgesn_2024_outil_declaration.xlsx"
CRITERES = ROOT / "data" / "criteres_rgesn.json"
SCHEMA = ROOT / "schemas" / "declaration.schema.json"

VALID_EVAL = {"Conforme", "Non conforme", "Non applicable", "À évaluer"}

# Mapping terminologie RGESN (schéma JSON) → options de la liste déroulante du xlsx officiel.
# Le template attend "Validé / Non validé", pas "Conforme / Non conforme" — sinon data validation
# rejette la cellule avec "Input must be an item on the specified list".
EVAL_TO_XLSX = {
    "Conforme": "Validé",
    "Non conforme": "Non validé",
    "Non applicable": "Non applicable",
    "À évaluer": "À évaluer",
}


def slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", s).strip("_") or "service"


def load_declaration(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "service" not in data or "criteres" not in data:
        raise ValueError("declaration.json invalide : 'service' et 'criteres' requis")
    for c in data["criteres"]:
        if c.get("evaluation") and c["evaluation"] not in VALID_EVAL:
            raise ValueError(f"Évaluation invalide pour {c.get('id')} : {c['evaluation']!r}")
    return data


def load_criteres_index() -> dict:
    criteres = json.loads(CRITERES.read_text(encoding="utf-8"))
    return {c["id"]: c for c in criteres}


def fill(declaration_path: Path, output_path: Path | None = None) -> Path:
    declaration = load_declaration(declaration_path)
    index = load_criteres_index()

    service = declaration["service"]
    eval_date = service.get("date_evaluation") or date.today().isoformat()

    if output_path is None:
        slug = slugify(service.get("nom", "service"))
        output_path = ROOT / "out" / f"{slug}_{eval_date}.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEMPLATE, output_path)

    wb = openpyxl.load_workbook(output_path)

    score = wb["Score d'avancement"]
    score["C5"] = service.get("nom", "")
    score["C6"] = service.get("echantillons", "")
    score["C7"] = service.get("entite_evaluation", "")
    score["C8"] = service.get("responsable_evaluation", "")
    score["C11"] = eval_date

    unknown = []
    written = 0
    for c in declaration["criteres"]:
        meta = index.get(c["id"])
        if not meta:
            unknown.append(c["id"])
            continue
        ws = wb[meta["feuille_xlsx"]]
        row = meta["ligne_xlsx"]
        evaluation = c.get("evaluation", "À évaluer")
        ws.cell(row=row, column=5, value=EVAL_TO_XLSX.get(evaluation, evaluation))
        ws.cell(row=row, column=6, value=c.get("date_evaluation") or eval_date)
        if c.get("evolutions_potentielles"):
            ws.cell(row=row, column=7, value=c["evolutions_potentielles"])
        if c.get("actions_a_mener"):
            ws.cell(row=row, column=9, value=c["actions_a_mener"])
        if c.get("qui"):
            ws.cell(row=row, column=10, value=c["qui"])
        if c.get("quand"):
            ws.cell(row=row, column=11, value=c["quand"])
        if c.get("texte_declaration"):
            ws.cell(row=row + 1, column=3, value=c["texte_declaration"])
        written += 1

    wb.save(output_path)

    rel = output_path.relative_to(ROOT) if output_path.is_relative_to(ROOT) else output_path
    print(f"OK {written} critères écrits dans {rel}")
    if unknown:
        print(f"  Avertissement : ids inconnus ignorés : {', '.join(unknown)}")
    return output_path


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    decl = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    fill(decl, out)


if __name__ == "__main__":
    main()
