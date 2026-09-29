"""Génère le plan d'avancement (roadmap) RGESN depuis un declaration.json.

Usage:
    python scripts/roadmap.py <declaration.json> [<output.md>]

Aucune dépendance hors bibliothèque standard.
Si <output.md> n'est pas fourni, le fichier est écrit dans out/<service>_<date>_roadmap.md.

Chaque critère « Non conforme » ou « À évaluer » devient une action, rangée dans une phase :
  - Phase 0 : lever les inconnues   (critères « À évaluer »)
  - Phase 1 : quick wins            (effort Faible)
  - Phase 2 : chantiers             (effort Moyen)
  - Phase 3 : chantiers structurants (effort Fort)

L'effort vaut par défaut la difficulté du référentiel (data/criteres_rgesn.json) ;
le champ optionnel `effort` d'un critère du JSON la remplace. Le champ optionnel
`depend_de` (liste d'ids) repousse un critère au moins dans la phase de ses
dépendances, et après elles dans la phase.

Le score suit la formule RGESN 2024 : Σ pondérations validées / Σ pondérations
applicables × 100 (N/A exclus, « À évaluer » compté comme non validé).
"""
from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITERES = ROOT / "data" / "criteres_rgesn.json"

VALID_EVAL = {"Conforme", "Non conforme", "Non applicable", "À évaluer"}
EFFORTS = ("Faible", "Moyen", "Fort")
PHASES = OrderedDict(
    [
        (0, "Phase 0 — Lever les inconnues"),
        (1, "Phase 1 — Quick wins (effort faible)"),
        (2, "Phase 2 — Chantiers (effort moyen)"),
        (3, "Phase 3 — Chantiers structurants (effort fort)"),
    ]
)
PRIORITE_RANG = {"Prioritaire": 0, "Recommandé": 1, "Modéré": 2}


def slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", s).strip("_") or "service"


def id_sort_key(cid: str) -> tuple:
    a, b = cid.split(".")
    return int(a), int(b)


def load_declaration(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "service" not in data or "criteres" not in data:
        raise ValueError("declaration.json invalide : 'service' et 'criteres' requis")
    for c in data["criteres"]:
        if c.get("evaluation") and c["evaluation"] not in VALID_EVAL:
            raise ValueError(f"Évaluation invalide pour {c.get('id')} : {c['evaluation']!r}")
        if c.get("effort") and c["effort"] not in EFFORTS:
            raise ValueError(f"Effort invalide pour {c.get('id')} : {c['effort']!r}")
        deps = c.get("depend_de", [])
        if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
            raise ValueError(f"depend_de invalide pour {c.get('id')} : liste d'ids attendue, reçu {deps!r}")
    return data


def load_criteres_index() -> OrderedDict:
    raw = json.loads(CRITERES.read_text(encoding="utf-8"))
    return OrderedDict((c["id"], c) for c in raw)


def fmt(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


def cell(s: str | None) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def plan(declaration: dict, index: OrderedDict) -> dict:
    # Comme dans le tableur, un critère absent du JSON reste « À évaluer » et compte au dénominateur.
    entries = {cid: {"id": cid, "evaluation": "À évaluer", "absent": True} for cid in index}
    entries.update({c["id"]: c for c in declaration["criteres"] if c["id"] in index})

    applicables = [cid for cid, c in entries.items() if c.get("evaluation") != "Non applicable"]
    denom = sum(index[cid]["ponderation"] for cid in applicables)
    valides = sum(index[cid]["ponderation"] for cid in applicables if entries[cid]["evaluation"] == "Conforme")

    todo = {
        cid: c for cid, c in entries.items() if c.get("evaluation") in ("Non conforme", "À évaluer")
    }

    effort = {cid: c.get("effort") or index[cid]["difficulte"] for cid, c in todo.items()}
    base_phase = {
        cid: 0 if c["evaluation"] == "À évaluer" else EFFORTS.index(effort[cid]) + 1
        for cid, c in todo.items()
    }
    deps = {cid: [d for d in c.get("depend_de", []) if d in todo] for cid, c in todo.items()}

    # Une action ne peut pas précéder ses dépendances : phase = max(phase, phases des dépendances).
    phase: dict[str, int] = {}

    def resolve(cid: str, stack: tuple = ()) -> int:
        if cid in phase:
            return phase[cid]
        if cid in stack:
            raise ValueError(f"Dépendance circulaire : {' → '.join(stack + (cid,))}")
        p = max([base_phase[cid]] + [resolve(d, stack + (cid,)) for d in deps[cid]])
        phase[cid] = p
        return p

    for cid in todo:
        resolve(cid)

    def rank(cid: str) -> tuple:
        m = index[cid]
        return (-m["ponderation"], PRIORITE_RANG[m["priorite"]], id_sort_key(cid))

    # Dans une phase : tri par gain puis priorité, en plaçant chaque dépendance avant.
    by_phase: dict[int, list[str]] = defaultdict(list)
    for p in PHASES:
        members = sorted((cid for cid in todo if phase[cid] == p), key=rank)
        ordered: list[str] = []

        def visit(cid: str) -> None:
            if cid in ordered:
                return
            for d in sorted(deps[cid], key=rank):
                if phase[d] == p:
                    visit(d)
            ordered.append(cid)

        for cid in members:
            visit(cid)
        by_phase[p] = ordered

    return {
        "entries": entries,
        "denom": denom,
        "valides": valides,
        "effort": effort,
        "deps": deps,
        "by_phase": by_phase,
    }


def render(declaration: dict, index: OrderedDict, p: dict) -> str:
    service = declaration["service"]
    nom = service.get("nom", "[service]")
    eval_date = service.get("date_evaluation") or date.today().isoformat()
    entries, denom, effort, deps = p["entries"], p["denom"], p["effort"], p["deps"]
    score = p["valides"] / denom * 100 if denom else 0.0

    def gain(cid: str) -> float:
        return index[cid]["ponderation"] / denom * 100 if denom else 0.0

    def action(cid: str) -> tuple[str, bool]:
        c = entries[cid]
        if c.get("absent"):
            return "Évaluer le critère (absent du declaration.json).", True
        if c.get("actions_a_mener"):
            return c["actions_a_mener"], True
        if c.get("evolutions_potentielles"):
            return c["evolutions_potentielles"], True
        return "[À définir]", False

    out: list[str] = []
    out.append(f"# Plan d'avancement RGESN — {nom}")
    out.append("")
    out.append(f"Établi à partir de l'évaluation du {eval_date}.")
    out.append("")
    out.append(f"**Score d'avancement actuel : {fmt(score)} %** ({fmt(p['valides'])} / {fmt(denom)} points).")
    out.append("")
    out.append(
        "Les gains indiqués sont les points de score gagnés si le critère devient conforme. "
        "Pour les critères de la phase 0, le gain n'est acquis que si la vérification conclut à la conformité."
    )
    out.append("")

    out.append("## Synthèse")
    out.append("")
    out.append("| Phase | Critères | Gain | Score cumulé |")
    out.append("|---|---|---|---|")
    cumul = score
    for num, titre in PHASES.items():
        ids = p["by_phase"][num]
        if not ids:
            continue
        g = sum(gain(cid) for cid in ids)
        cumul += g
        out.append(f"| {titre} | {', '.join(ids)} | +{fmt(g)} pts | {fmt(cumul)} % |")
    out.append("")

    for num, titre in PHASES.items():
        ids = p["by_phase"][num]
        if not ids:
            continue
        out.append(f"## {titre}")
        out.append("")
        out.append("| # | Critère | Priorité | Effort | Gain | Action | Qui | Quand |")
        out.append("|---|---|---|---|---|---|---|---|")
        for i, cid in enumerate(ids, 1):
            m, c = index[cid], entries[cid]
            texte, _ = action(cid)
            if deps[cid]:
                texte += f" *(après {', '.join(deps[cid])})*"
            eff = effort[cid] + ("*" if c.get("effort") and c["effort"] != m["difficulte"] else "")
            out.append(
                f"| {i} | **{cid}** {cell(m['libelle'])} | {m['priorite']} | {eff} | +{fmt(gain(cid))} "
                f"| {cell(texte)} | {cell(c.get('qui')) or '[À attribuer]'} | {cell(c.get('quand')) or '—'} |"
            )
        out.append("")

    if any(entries[cid].get("effort") and entries[cid]["effort"] != index[cid]["difficulte"]
           for ids in p["by_phase"].values() for cid in ids):
        out.append(
            "\\* Effort réestimé pour ce service ; le référentiel indique une autre difficulté."
        )
        out.append("")

    owners: dict[str, list[str]] = defaultdict(list)
    for ids in p["by_phase"].values():
        for cid in ids:
            owners[entries[cid].get("qui") or "[À attribuer]"].append(cid)
    out.append("## Par responsable")
    out.append("")
    out.append("| Qui | Critères |")
    out.append("|---|---|")
    for qui in sorted(owners, key=lambda q: (q == "[À attribuer]", q)):
        out.append(f"| {cell(qui)} | {', '.join(sorted(owners[qui], key=id_sort_key))} |")
    out.append("")

    sans_action = [cid for ids in p["by_phase"].values() for cid in ids if not action(cid)[1]]
    sans_qui = owners.get("[À attribuer]", [])
    todo_ids = [cid for ids in p["by_phase"].values() for cid in ids]
    sans_quand = [cid for cid in todo_ids if not entries[cid].get("quand")]
    absents = [cid for cid in todo_ids if entries[cid].get("absent")]
    manques = []
    if absents:
        manques.append(f"- Critères absents du declaration.json, comptés « À évaluer » : {len(absents)}")
    if sans_action:
        manques.append(f"- Action à définir : {', '.join(sorted(sans_action, key=id_sort_key))}")
    if sans_qui:
        manques.append(f"- Responsable à attribuer : {', '.join(sorted(sans_qui, key=id_sort_key))}")
    if sans_quand and len(sans_quand) == len(todo_ids):
        manques.append("- Aucune échéance renseignée (champ `quand`).")
    elif sans_quand:
        manques.append(f"- Échéance à fixer : {', '.join(sorted(sans_quand, key=id_sort_key))}")
    if manques:
        out.append("## Points à compléter")
        out.append("")
        out.extend(manques)
        out.append("")

    return "\n".join(out)


def generate(declaration_path: Path, output_path: Path | None = None) -> Path:
    declaration = load_declaration(declaration_path)
    index = load_criteres_index()

    service = declaration["service"]
    eval_date = service.get("date_evaluation") or date.today().isoformat()
    if output_path is None:
        slug = slugify(service.get("nom", "service"))
        output_path = ROOT / "out" / f"{slug}_{eval_date}_roadmap.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    p = plan(declaration, index)
    output_path.write_text(render(declaration, index, p), encoding="utf-8")

    unknown = [c["id"] for c in declaration["criteres"] if c["id"] not in index]
    n = sum(len(ids) for ids in p["by_phase"].values())
    rel = output_path.relative_to(ROOT) if output_path.is_relative_to(ROOT) else output_path
    print(f"OK {n} actions planifiées dans {rel}")
    if unknown:
        print(f"  Avertissement : ids inconnus ignorés : {', '.join(unknown)}")
    return output_path


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    decl = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    generate(decl, out)


if __name__ == "__main__":
    main()
