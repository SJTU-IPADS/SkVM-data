#!/usr/bin/env bash
# deliberate.sh — Deliberation Protocol: template + validation
# Part of Turing Pyramid v1.30.0
#
# Three modes:
#   --template  Generate scaffolding for a deliberative action
#   --validate  Validate a free-form deliberation file
#   --validate-inline  Quick check of conclusion + route without a file
#
# Design: phases are questions, not obligations. Validate checks presence,
# not form. Warn, never block.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"

# ─── Parse arguments ───
MODE="" NEED="" ACTION="" COMPRESSED=false SAVE=false
VALIDATE_FILE="" CONCLUSION="" ROUTE="" CONFIDENCE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --template)     MODE="template"; shift ;;
        --validate)     MODE="validate"; VALIDATE_FILE="${2:-}"; shift; [[ -n "$VALIDATE_FILE" ]] && shift ;;
        --validate-inline) MODE="validate-inline"; shift ;;
        --need)         NEED="$2"; shift 2 ;;
        --action)       ACTION="$2"; shift 2 ;;
        --compressed)   COMPRESSED=true; shift ;;
        --save)         SAVE=true; shift ;;
        --conclusion)   CONCLUSION="$2"; shift 2 ;;
        --route)        ROUTE="$2"; shift 2 ;;
        --confidence)   CONFIDENCE="$2"; shift 2 ;;
        --help|-h)      MODE="help"; shift ;;
        *)              shift ;;
    esac
done

VALID_ROUTES="followup research_thread interest steward_question priority_flag reframe chain concluded"

# ─── Help ───
show_help() {
    cat <<'EOF'
deliberate.sh — Deliberation Protocol for Turing Pyramid

Usage:
  deliberate.sh --template --need <need> --action <name> [--compressed] [--save]
  deliberate.sh --validate <file_path>
  deliberate.sh --validate-inline --conclusion "..." --route "..." [--confidence "..."]

Modes:
  --template        Generate phase scaffolding (full or compressed based on impact)
  --validate        Check a free-form file for conclusion + route + confidence
  --validate-inline Quick inline check without a file

Options:
  --compressed      Force compressed mode (REPRESENT → CONCLUDE → ROUTE)
  --save            Save template to research/deliberations/ (default: off)
  --confidence      Confidence level for --validate-inline (high/medium/low)

Valid routes: followup research_thread interest steward_question priority_flag chain concluded
EOF
}

# ─── Template mode ───
do_template() {
    [[ -z "$NEED" || -z "$ACTION" ]] && {
        echo "❌ --template requires --need and --action"
        exit 1
    }

    # Validate action exists and check mode
    local action_mode action_impact
    action_mode=$(jq -r --arg n "$NEED" --arg a "$ACTION" \
        '(.needs[$n].actions[] | select(.name == $a) | .mode) // "operative"' \
        "$CONFIG_FILE" 2>/dev/null || echo "operative")

    if [[ "$action_mode" != "deliberative" ]]; then
        echo "⚠️  Action '$ACTION' is not tagged deliberative (mode=$action_mode)"
        echo "   You can still use deliberation voluntarily."
    fi

    action_impact=$(jq -r --arg n "$NEED" --arg a "$ACTION" \
        '(.needs[$n].actions[] | select(.name == $a) | .impact) // 0' \
        "$CONFIG_FILE" 2>/dev/null || echo "0")

    # Auto-compress for low-impact actions
    if [[ "$COMPRESSED" == "false" ]]; then
        if (( $(echo "$action_impact < 1.0" | bc -l 2>/dev/null || echo 0) )); then
            COMPRESSED=true
        fi
    fi

    local now_iso
    now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local template_content
    if $COMPRESSED; then
        template_content=$(cat <<EOF
═══ DELIBERATION [compressed]: $NEED ═══
Action: $ACTION | Impact: $action_impact | Started: $now_iso

── REPRESENT ──
What am I examining? What do I already know?

── CONCLUDE ──
Conclusion:

Confidence: [high / medium / low]

── ROUTE ──
Where does this go? (followup / research_thread / interest / steward_question / reframe / concluded)

═══════════════════════════════════════════
EOF
)
    else
        template_content=$(cat <<EOF
═══ DELIBERATION: $NEED ═══
Action: $ACTION | Impact: $action_impact | Started: $now_iso

Phases are questions, not obligations.
Skip any phase with a reason — but always reach CONCLUDE and ROUTE.

── Phase 1: REPRESENT ──
What am I thinking about? What do I already know?

── Phase 2: RELATE + TENSION ──
Scan for associations before answering:
  association-scan.sh --keywords "<topic words>" --need $NEED --max-results 3

What from my context is relevant? What doesn't fit?
Where are the contradictions, gaps, mismatches, or conflicts?
(If none: "no tensions detected" is valid — state it, don't skip silently)

── Phase 3: GENERATE ──
What interpretations, conclusions, or questions follow?

── Phase 4: EVALUATE ──
Which candidates are strongest? Why?
(Skip: if only one candidate, state why it's sufficient)

── Phase 5: CONCLUDE ──
Outcome (decision / assessment / diagnosis / question refinement / uncertainty / tension artifact):

Confidence: [high / medium / low]
What would increase confidence:

── Phase 6: ROUTE ──
Where does this outcome go?
(followup / research_thread / interest / steward_question / priority_flag / reframe / chain / concluded)

═══════════════════════════════════════════
EOF
)
    fi

    # Output to stdout
    echo "$template_content"

    # Save if explicitly requested
    if $SAVE && [[ -n "${WORKSPACE:-}" ]]; then
        local delib_dir="$WORKSPACE/research/deliberations"
        mkdir -p "$delib_dir"
        local hash
        hash=$(echo "${NEED}_${ACTION}_${now_iso}" | md5sum | head -c 6)
        local delib_file="$delib_dir/$(date +%Y-%m-%d)_${NEED}_${hash}.md"
        echo "$template_content" > "$delib_file"
        echo "📝 Template saved: $delib_file"
    fi
}

# ─── Validate mode (file) ───
do_validate() {
    [[ -z "$VALIDATE_FILE" ]] && {
        echo "❌ --validate requires a file path"
        exit 1
    }
    [[ ! -f "$VALIDATE_FILE" ]] && {
        echo "❌ File not found: $VALIDATE_FILE"
        exit 1
    }

    local content status warnings
    content=$(cat "$VALIDATE_FILE")
    status="PASS"
    warnings=""

    # Check for outcome artifact (multilingual: EN + RU, multiple outcome types)
    if ! echo "$content" | grep -qiE '(conclusion|outcome|## conclude|finding|verdict|takeaway|assessment|diagnosis|tension|вывод|заключение|итог|оценка|диагноз)'; then
        status="FAIL"
        echo "❌ No conclusion found in $VALIDATE_FILE"
    fi

    # Check for route/routing decision
    if ! echo "$content" | grep -qiE '(route|next step|followup|follow.up|open question|further|todo|reframe|restructure|decompose|what i don.t know|что.* не знаю|дальше|следующ|переформулир)'; then
        if [[ "$status" != "FAIL" ]]; then status="WARN"; fi
        warnings="${warnings}⚠️  No routing decision found. Where does this conclusion go?\n"
    fi

    # Check for confidence
    if ! echo "$content" | grep -qiE '(confidence|certainty|uncertain|likely|probably|уверенн|вероятн)'; then
        warnings="${warnings}💡 No confidence assessment found (optional but recommended).\n"
    fi

    # Low-confidence + no followup check
    if echo "$content" | grep -qiE '(confidence:? *(low|uncertain|низк))'; then
        if ! echo "$content" | grep -qiE '(followup|follow.up|next step|revisit|todo|дальше|вернуться)'; then
            warnings="${warnings}⚠️  Low-confidence conclusion with no followup. Consider revisiting.\n"
        fi
    fi

    # Concluded + implicit action check
    if echo "$content" | grep -qiE '(concluded|nothing further|no further action|no action needed|завершено|ничего дальше)'; then
        if echo "$content" | grep -qiE '(should|need to|update|revisit|next cycle|when .* rises|consider|демонтировать|обновить|вернуться)'; then
            warnings="${warnings}⚠️  'concluded' selected, but outcome contains action language.\n"
            warnings="${warnings}   Is there a residual intention? Consider: followup / soft MINDSTATE note.\n"
        fi
    fi

    if [[ -n "$warnings" ]]; then
        echo -e "$warnings"
    fi
    echo "[$status] Validation complete: $VALIDATE_FILE"

    # Exit code: 0 for PASS/WARN, 1 for FAIL
    [[ "$status" != "FAIL" ]]
}

# ─── Validate-inline mode ───
do_validate_inline() {
    local status="PASS"
    local warnings=""

    if [[ -z "$CONCLUSION" ]]; then
        echo "❌ No --conclusion provided"
        status="FAIL"
    fi

    if [[ -z "$ROUTE" ]]; then
        echo "⚠️  No --route provided"
        [[ "$status" != "FAIL" ]] && status="WARN"
    else
        # Validate route value
        if ! echo "$VALID_ROUTES" | grep -qw "$ROUTE"; then
            warnings="${warnings}⚠️  Unknown route: $ROUTE (valid: $VALID_ROUTES)\n"
        fi
    fi

    # Low-confidence + concluded check
    if [[ "${CONFIDENCE:-}" == "low" && "${ROUTE:-}" == "concluded" ]]; then
        warnings="${warnings}⚠️  Low-confidence conclusion with no followup. Consider revisiting.\n"
        warnings="${warnings}   Suggestion: create-followup.sh --what \"revisit: <topic>\" --in 24h --need <need>\n"
    fi

    # Concluded + action language check
    if [[ "${ROUTE:-}" == "concluded" && -n "$CONCLUSION" ]]; then
        if echo "$CONCLUSION" | grep -qiE '(should|need to|update|revisit|next cycle|consider|демонтировать|обновить|вернуться)'; then
            warnings="${warnings}⚠️  Concluded with action language detected.\n"
            warnings="${warnings}   Residual intention? Consider: --route followup instead.\n"
        fi
    fi

    if [[ -n "$warnings" ]]; then
        echo -e "$warnings"
    fi
    echo "[$status] Inline validation complete"

    [[ "$status" != "FAIL" ]]
}

# ─── Main dispatch ───
case "${MODE:-}" in
    template)        do_template ;;
    validate)        do_validate ;;
    validate-inline) do_validate_inline ;;
    help)            show_help ;;
    *)
        echo "Usage: deliberate.sh --template|--validate|--validate-inline [options]"
        echo "Try: deliberate.sh --help"
        exit 1
        ;;
esac
