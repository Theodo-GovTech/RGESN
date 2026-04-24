#!/usr/bin/env bash
# install.sh — installe les skills RGESN dans ~/.claude/
#
# Usage :
#   curl -fsSL https://raw.githubusercontent.com/Theodo-GovTech/RGESN/main/install.sh | bash
#
# ou, depuis un clone local :
#   ./install.sh
#
# Variables d'environnement optionnelles :
#   CLAUDE_CONFIG_DIR   répertoire Claude Code cible (défaut: ~/.claude)
#   RGESN_BRANCH        branche à utiliser (défaut: main)
#   RGESN_REPO_URL      URL du repo (défaut: https://github.com/Theodo-GovTech/RGESN.git)
#   RGESN_TOOLKIT_DIR   emplacement du clone (défaut: $CLAUDE_CONFIG_DIR/rgesn-toolkit)
#   RGESN_NO_PYTHON=1   ne pas installer openpyxl
set -euo pipefail

CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
TOOLKIT_DIR="${RGESN_TOOLKIT_DIR:-$CLAUDE_HOME/rgesn-toolkit}"
REPO_URL="${RGESN_REPO_URL:-https://github.com/Theodo-GovTech/RGESN.git}"
BRANCH="${RGESN_BRANCH:-main}"

# Couleurs minimales (tty seulement)
if [ -t 1 ]; then
  C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_INFO=$'\033[36m'; C_END=$'\033[0m'
else
  C_OK=""; C_WARN=""; C_INFO=""; C_END=""
fi
info()  { printf "%s→%s %s\n" "$C_INFO" "$C_END" "$*"; }
ok()    { printf "%s✓%s %s\n" "$C_OK"   "$C_END" "$*"; }
warn()  { printf "%s⚠%s  %s\n" "$C_WARN" "$C_END" "$*"; }

# 0) Prérequis
command -v git >/dev/null 2>&1 || { echo "git est requis pour installer RGESN"; exit 1; }

# Si le script est exécuté depuis un clone local, on préfère ce clone comme source
SCRIPT_DIR=""
if [ "${BASH_SOURCE[0]:-}" != "" ]; then
  _candidate="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
  if [ -n "$_candidate" ] && [ -f "$_candidate/data/criteres_rgesn.json" ] && [ -d "$_candidate/.claude/skills" ]; then
    SCRIPT_DIR="$_candidate"
  fi
fi

# 1) Cloner, copier, ou mettre à jour le toolkit
if [ -n "$SCRIPT_DIR" ] && [ "$SCRIPT_DIR" = "$TOOLKIT_DIR" ]; then
  info "Le toolkit est déjà au bon emplacement ($TOOLKIT_DIR), pas de copie"
elif [ -n "$SCRIPT_DIR" ]; then
  info "Utilisation du clone local $SCRIPT_DIR comme source"
  mkdir -p "$(dirname "$TOOLKIT_DIR")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete \
      --exclude='.venv' --exclude='out' --exclude='.DS_Store' \
      --exclude='.claude/settings.local.json' \
      "$SCRIPT_DIR/" "$TOOLKIT_DIR/"
  else
    rm -rf "$TOOLKIT_DIR"
    cp -R "$SCRIPT_DIR" "$TOOLKIT_DIR"
  fi
elif [ -d "$TOOLKIT_DIR/.git" ]; then
  info "Mise à jour du toolkit dans $TOOLKIT_DIR (branche $BRANCH)"
  git -C "$TOOLKIT_DIR" fetch --quiet origin "$BRANCH"
  git -C "$TOOLKIT_DIR" checkout --quiet "$BRANCH"
  git -C "$TOOLKIT_DIR" pull --ff-only --quiet
else
  info "Clonage de $REPO_URL ($BRANCH) dans $TOOLKIT_DIR"
  git clone --quiet --branch "$BRANCH" --depth 1 "$REPO_URL" "$TOOLKIT_DIR"
fi
ok "Toolkit prêt : $TOOLKIT_DIR"

# 2) Installer les skills officiels (symlinks vers le toolkit)
mkdir -p "$CLAUDE_HOME/skills"
for skill_dir in "$TOOLKIT_DIR"/.claude/skills/*/; do
  [ -d "$skill_dir" ] || continue
  name=$(basename "$skill_dir")
  target="$CLAUDE_HOME/skills/$name"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    warn "$target existe déjà et n'est pas un lien — ignoré"
    continue
  fi
  ln -sfn "$skill_dir" "$target"
  ok "Skill : $name"
done

# 3) Installer les prompts d'audit comme slash commands
mkdir -p "$CLAUDE_HOME/commands"
for prompt_file in "$TOOLKIT_DIR"/skills/*.md; do
  [ -f "$prompt_file" ] || continue
  name=$(basename "$prompt_file")
  target="$CLAUDE_HOME/commands/rgesn-${name}"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    warn "$target existe déjà et n'est pas un lien — ignoré"
    continue
  fi
  ln -sfn "$prompt_file" "$target"
  ok "Commande : /rgesn-${name%.md}"
done

# 4) Dépendances Python pour rgesn-fill-xlsx
if [ "${RGESN_NO_PYTHON:-}" != "1" ]; then
  if command -v python3 >/dev/null 2>&1; then
    if [ ! -d "$TOOLKIT_DIR/.venv" ]; then
      info "Création du venv Python dans $TOOLKIT_DIR/.venv"
      python3 -m venv "$TOOLKIT_DIR/.venv"
    fi
    "$TOOLKIT_DIR/.venv/bin/pip" install --quiet --upgrade pip openpyxl python-docx
    ok "openpyxl et python-docx installés dans le venv du toolkit"
  else
    warn "python3 introuvable — rgesn-fill-xlsx et rgesn-fill-docx ne fonctionneront pas tant que Python, openpyxl et python-docx ne sont pas installés"
  fi
fi

echo
ok "Installation terminée."
echo "   Toolkit  : $TOOLKIT_DIR"
echo "   Skills   : $CLAUDE_HOME/skills/{rgesn-assess,rgesn-fill-xlsx,rgesn-fill-docx}"
echo "   Commandes: $CLAUDE_HOME/commands/rgesn-audit-*.md, /rgesn-generate-declaration, /rgesn-review-pr-ecoconception"
echo
echo "Dans Claude Code, sur n'importe quel projet :"
echo "   — \"évalue ce projet avec le RGESN\"   (déclenche rgesn-assess)"
echo "   — \"génère le tableur RGESN\"           (déclenche rgesn-fill-xlsx)"
echo "   — /rgesn-audit-frontend, /rgesn-audit-backend, ...   (prompts spécialisés)"
