#!/usr/bin/env bash
# validate-skill.sh — icp-edi-helper 技能包自动质量门禁
# 配合 references/quality-checklist.md 使用
# 用法：bash scripts/validate-skill.sh [skill-root-dir]
#   默认检查当前目录

set -u

SKILL_ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
REPORT_MD="$SKILL_ROOT/reports/qa-report.md"
REPORT_JSON="$SKILL_ROOT/reports/qa-report.json"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

PASS=0
WARN=0
FAIL=0

pass()  { PASS=$((PASS+1)); echo -e "  ${GREEN}✅ PASS${NC} $1"; }
warn()  { WARN=$((WARN+1)); echo -e "  ${YELLOW}⚠️  WARN${NC} $1"; }
fail()  { FAIL=$((FAIL+1)); echo -e "  ${RED}❌ FAIL${NC} $1"; }

mkdir -p "$SKILL_ROOT/reports"

echo "==============================================="
echo "  icp-edi-helper 技能包质量门禁 v2.3"
echo "  校验目录：$SKILL_ROOT"
echo "==============================================="
echo ""

# ===== 一、结构完整性 =====

echo "📋 一、结构完整性"
echo ""

# Q1: SKILL.md 存在
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  pass "Q1: SKILL.md 存在"
else
  fail "Q1: SKILL.md 缺失"
fi

# Q2: YAML front matter
if [ -f "$SKILL_ROOT/SKILL.md" ] && head -1 "$SKILL_ROOT/SKILL.md" | grep -q '^---$'; then
  pass "Q2: SKILL.md 含 YAML front matter"
else
  fail "Q2: SKILL.md 缺 YAML front matter"
fi

# Q3/Q4: name/description 字段
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  if grep -q '^name:' "$SKILL_ROOT/SKILL.md"; then
    pass "Q3: SKILL.md 含 name 字段"
  else
    fail "Q3: SKILL.md 缺 name 字段"
  fi

  if grep -q '^description:' "$SKILL_ROOT/SKILL.md"; then
    pass "Q4: SKILL.md 含 description 字段"
  else
    fail "Q4: SKILL.md 缺 description 字段"
  fi
fi

# Q5: name 为 lower-kebab-case
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  NAME=$(grep '^name:' "$SKILL_ROOT/SKILL.md" | head -1 | sed 's/^name:[[:space:]]*//' | tr -d '\r')
  if echo "$NAME" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$'; then
    pass "Q5: name 符合 lower-kebab-case ($NAME)"
  else
    fail "Q5: name 不符合 lower-kebab-case: '$NAME'"
  fi
fi

# Q6: description 长度
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  DESC=$(awk '/^description:/{flag=1; next} /^---$/{if(flag){flag=0; exit}} flag' "$SKILL_ROOT/SKILL.md" | head -1)
  DESC_LEN=${#DESC}
  if [ "$DESC_LEN" -ge 10 ]; then
    pass "Q6: description 长度 $DESC_LEN ≥ 10"
  else
    fail "Q6: description 长度 $DESC_LEN < 10（需补充触发场景）"
  fi
fi

# Q7: AGENTS.md
[ -f "$SKILL_ROOT/AGENTS.md" ] && pass "Q7: AGENTS.md 存在" || fail "Q7: AGENTS.md 缺失"

# Q8: README.md
[ -f "$SKILL_ROOT/README.md" ] && pass "Q8: README.md 存在" || fail "Q8: README.md 缺失"

# Q9: package.json
[ -f "$SKILL_ROOT/package.json" ] && pass "Q9: package.json 存在" || fail "Q9: package.json 缺失"

# Q10: package.json 关键字段
if [ -f "$SKILL_ROOT/package.json" ]; then
  HAS_NAME=$(grep -c '"name"' "$SKILL_ROOT/package.json" || true)
  HAS_VERSION=$(grep -c '"version"' "$SKILL_ROOT/package.json" || true)
  HAS_DESC=$(grep -c '"description"' "$SKILL_ROOT/package.json" || true)
  if [ "$HAS_NAME" -ge 1 ] && [ "$HAS_VERSION" -ge 1 ] && [ "$HAS_DESC" -ge 1 ]; then
    pass "Q10: package.json 含 name/version/description"
  else
    fail "Q10: package.json 缺关键字段"
  fi
fi

# Q11: examples/usage.md
[ -f "$SKILL_ROOT/examples/usage.md" ] && pass "Q11: examples/usage.md 存在" || fail "Q11: examples/usage.md 缺失"

# Q12: examples/ ≥ 2 个用例
if [ -d "$SKILL_ROOT/examples" ]; then
  COUNT=$(ls -1 "$SKILL_ROOT/examples/"*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ "$COUNT" -ge 2 ]; then
    pass "Q12: examples/ 含 $COUNT 个用例"
  else
    warn "Q12: examples/ 仅 $COUNT 个用例（建议 ≥ 2）"
  fi
else
  fail "Q12: examples/ 目录不存在"
fi

# Q13-Q17: 5 个 references
[ -f "$SKILL_ROOT/references/workflow.md" ] && pass "Q13: references/workflow.md 存在" || fail "Q13: references/workflow.md 缺失"
[ -f "$SKILL_ROOT/references/quality-checklist.md" ] && pass "Q14: references/quality-checklist.md 存在" || fail "Q14: 缺失"
[ -f "$SKILL_ROOT/references/error-handling.md" ] && pass "Q15: references/error-handling.md 存在" || fail "Q15: 缺失"
[ -f "$SKILL_ROOT/references/qcc-api-guide.md" ] && pass "Q16: references/qcc-api-guide.md 存在" || fail "Q16: 缺失"
[ -f "$SKILL_ROOT/references/index.md" ] && pass "Q17: references/index.md 存在" || fail "Q17: 缺失"

# Q18: validate-skill.sh 可执行
if [ -x "$SKILL_ROOT/scripts/validate-skill.sh" ]; then
  pass "Q18: scripts/validate-skill.sh 存在且可执行"
else
  fail "Q18: scripts/validate-skill.sh 缺失或不可执行（chmod +x）"
fi

echo ""
echo "📋 二、内容质量"
echo ""

# C1: SKILL.md 行数
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  LINES=$(wc -l < "$SKILL_ROOT/SKILL.md" | tr -d ' ')
  if [ "$LINES" -le 230 ]; then
    pass "C1: SKILL.md 行数 $LINES ≤ 230"
  else
    warn "C1: SKILL.md 行数 $LINES > 230（建议精简）"
  fi
fi

# C2: SKILL.md 含 5 秒决策树
if [ -f "$SKILL_ROOT/SKILL.md" ] && grep -q '5 秒决策树\|5秒决策树' "$SKILL_ROOT/SKILL.md"; then
  pass "C2: SKILL.md 含 5 秒决策树"
else
  fail "C2: SKILL.md 缺 5 秒决策树"
fi

# C3: SKILL.md 不含版本历史/踩坑 小节
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  if grep -qE '^#+[[:space:]]+(版本历史|踩坑|version history)' "$SKILL_ROOT/SKILL.md"; then
    warn "C3: SKILL.md 含版本历史/踩坑小节（应放 README.md）"
  else
    pass "C3: SKILL.md 不含版本历史/踩坑小节（提及 README 包含这些 OK）"
  fi
fi

# C4: SKILL.md 不含市场参考价
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  if grep -qE '代办费|中介报价|市场价' "$SKILL_ROOT/SKILL.md"; then
    fail "C4: SKILL.md 含市场参考价（v1.8 已禁止）"
  else
    pass "C4: SKILL.md 不含市场参考价"
  fi
fi

# C8: 引用闭环（SKILL.md 中"见 xxx.md"中 xxx.md 都存在）
if [ -f "$SKILL_ROOT/SKILL.md" ]; then
  REFS=$(grep -oE '见 `?references/[a-zA-Z0-9_./-]+\.md`?' "$SKILL_ROOT/SKILL.md" | sed -E 's/见 `?references\///' | sed -E 's/`$//' | sort -u)
  MISSING=""
  for ref in $REFS; do
    if [ ! -f "$SKILL_ROOT/references/$ref" ]; then
      MISSING="$MISSING $ref"
    fi
  done
  if [ -z "$MISSING" ]; then
    pass "C8: SKILL.md 引用闭环 OK（$(echo "$REFS" | wc -w | tr -d ' ') 个引用全部命中）"
  else
    fail "C8: SKILL.md 引用缺失文件:$MISSING"
  fi
fi

# C10: .env 不在 git 跟踪
if [ -f "$SKILL_ROOT/.gitignore" ]; then
  if grep -qE '^\.env$|^\.env\b' "$SKILL_ROOT/.gitignore"; then
    pass "C10: .env 已在 .gitignore 中"
  else
    warn "C10: .env 未在 .gitignore 中"
  fi
else
  warn "C10: .gitignore 不存在"
fi

# C12: AGENTS.md 含错误分级 E1-E5
if [ -f "$SKILL_ROOT/AGENTS.md" ]; then
  E_COUNT=$(grep -cE 'E[1-5]' "$SKILL_ROOT/AGENTS.md" || true)
  if [ "$E_COUNT" -ge 5 ]; then
    pass "C12: AGENTS.md 含错误分级（命中 $E_COUNT 次）"
  else
    warn "C12: AGENTS.md 错误分级不完整（命中 $E_COUNT 次，建议 ≥ 5）"
  fi
fi

# C13: AGENTS.md 含汇报格式
if [ -f "$SKILL_ROOT/AGENTS.md" ] && grep -q '汇报格式\|交付汇报' "$SKILL_ROOT/AGENTS.md"; then
  pass "C13: AGENTS.md 含汇报格式"
else
  warn "C13: AGENTS.md 缺汇报格式"
fi

echo ""
echo "==============================================="
echo "  汇总"
echo "==============================================="
echo -e "  ${GREEN}PASS: $PASS${NC}"
echo -e "  ${YELLOW}WARN: $WARN${NC}"
echo -e "  ${RED}FAIL: $FAIL${NC}"
echo ""

# 生成 QA 报告
cat > "$REPORT_MD" << EOF
# QA Report — icp-edi-helper 质量门禁报告

**校验时间**：$(date '+%Y-%m-%d %H:%M:%S')
**校验目录**：\`$SKILL_ROOT\`
**校验脚本**：\`scripts/validate-skill.sh\`

---

## 汇总

| 状态 | 数量 |
|------|------|
| ✅ PASS | $PASS |
| ⚠️ WARN | $WARN |
| ❌ FAIL | $FAIL |

## 质量门禁结果

EOF

if [ "$FAIL" -eq 0 ]; then
  if [ "$WARN" -eq 0 ]; then
    echo "**🟢 PASS** — 所有检查项通过，可交付" >> "$REPORT_MD"
    GATE="PASS"
  else
    echo "**🟡 WARN** — 无 FAIL 项，有 $WARN 个 WARN，建议优化" >> "$REPORT_MD"
    GATE="WARN"
  fi
else
  echo "**🔴 FAIL** — 有 $FAIL 个 FAIL 项，必须修复后重新校验" >> "$REPORT_MD"
  GATE="FAIL"
fi

cat >> "$REPORT_MD" << EOF

---

## 详细结果

见终端输出。

---

## 后续

EOF

if [ "$GATE" = "PASS" ]; then
  cat >> "$REPORT_MD" << EOF
- 可直接交付给加盟商使用
- 下次更新省份文件后建议重跑此脚本
- 建议每月人工抽检 R1-R5 运行时质量指标
EOF
elif [ "$GATE" = "WARN" ]; then
  cat >> "$REPORT_MD" << EOF
- 可交付但建议优先处理 WARN 项
- WARN 项均为非阻塞优化
EOF
else
  cat >> "$REPORT_MD" << EOF
- **不可交付**，必须先修复 FAIL 项
- 修复后重新运行 \`bash scripts/validate-skill.sh\`
EOF
fi

# 生成 JSON 报告
cat > "$REPORT_JSON" << EOF
{
  "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')",
  "skill_root": "$SKILL_ROOT",
  "gate": "$GATE",
  "summary": {
    "pass": $PASS,
    "warn": $WARN,
    "fail": $FAIL
  }
}
EOF

echo "📄 报告已生成："
echo "   - $REPORT_MD"
echo "   - $REPORT_JSON"
echo ""

# 退出码
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
