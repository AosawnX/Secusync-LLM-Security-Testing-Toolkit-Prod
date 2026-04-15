# SECUSYNC — Brand Identity Guidelines

**Version:** 1.0  
**Last Updated:** April 2026  
**Applies To:** All project deliverables — UI, reports, documentation, presentations, diagrams

---

## 1. Brand Overview

SECUSYNC is a professional cybersecurity research toolkit. The brand communicates precision, trust, and technical authority. Every visual element — from the dashboard to PDF reports to academic submissions — must follow these guidelines consistently.

---

## 2. Logo

### 2.1 Primary Logo
The SECUSYNC logo consists of two elements that must always appear together:
- **The Mark:** An interlocking S-maze symbol constructed from square geometric lines — representing synchronization, layered security, and recursive analysis
- **The Wordmark:** "SECUSYNC" in spaced uppercase letterforms beneath the mark

### 2.2 Logo Variants

| Variant | Usage |
|---|---|
| **Full Logo** (Mark + Wordmark, vertical) | Primary use: cover pages, dashboard header, reports |
| **Mark Only** | Favicon, small UI elements ≤ 32px, loading spinners |
| **Wordmark Only** | Breadcrumbs, footer text, inline references |

### 2.3 Logo Clear Space
Minimum clear space around the full logo = **1× the height of the wordmark "S"** on all four sides. Never crowd the logo with other elements.

### 2.4 Logo Don'ts
- Do NOT stretch or distort the logo in any dimension
- Do NOT recolor the mark in any color other than Primary Blue or White (on dark backgrounds)
- Do NOT add drop shadows, gradients, or outlines to the logo
- Do NOT rotate the logo
- Do NOT place the logo on a busy, patterned, or low-contrast background
- Do NOT use unofficial recreations of the S-maze geometry

### 2.5 Minimum Size
- Full logo: minimum **120px wide** (digital) / **30mm wide** (print)
- Mark only: minimum **24px wide** (digital)

---

## 3. Color Palette

### 3.1 Primary Colors

| Role | Name | Hex | RGB | Usage |
|---|---|---|---|---|
| **Primary Blue** | Secusync Blue | `#0461E2` | `rgb(4, 97, 226)` | Logo mark, primary buttons, links, active states, chart accent |
| **Dark Navy** | Secusync Navy | `#1B2771` | `rgb(27, 39, 113)` | Wordmark, headings, sidebar, dark UI surfaces |

### 3.2 Secondary Colors

| Role | Name | Hex | RGB | Usage |
|---|---|---|---|---|
| **Light Grey** | Surface Grey | `#ECECEC` | `rgb(236, 236, 236)` | App background, card backgrounds, logo background |
| **White** | Pure White | `#FFFFFF` | `rgb(255, 255, 255)` | Content surfaces, text on dark backgrounds, report paper |
| **Dark Text** | Charcoal | `#1A1A2E` | `rgb(26, 26, 46)` | Body text, table content |

### 3.3 Semantic / Status Colors
These are used only for verdict badges, alerts, and status indicators:

| Role | Name | Hex | Usage |
|---|---|---|---|
| **Vulnerable** | Alert Red | `#DC2626` | VULNERABLE verdict badges, critical findings |
| **Needs Review** | Warning Amber | `#D97706` | NEEDS_REVIEW badges, medium findings |
| **Safe** | Success Green | `#16A34A` | NOT_VULNERABLE badges, passed checks |
| **Uncertain** | Muted Grey | `#6B7280` | UNCERTAIN states, disabled elements |

### 3.4 Color Usage Rules
- Primary Blue and Dark Navy are NEVER used as body text colors on white backgrounds (use Charcoal instead)
- Status colors are NEVER used decoratively — only for their assigned semantic meaning
- Do NOT use Primary Blue on Dark Navy backgrounds (insufficient contrast)
- Minimum contrast ratio for all text: **4.5:1** (WCAG AA)

---

## 4. Typography

### 4.1 Font Stack

| Role | Font | Fallback | Weight(s) |
|---|---|---|---|
| **UI / Dashboard** | Inter | system-ui, sans-serif | 400, 500, 600, 700 |
| **Code / Monospace** | JetBrains Mono | Consolas, monospace | 400, 500 |
| **Reports (PDF)** | Helvetica | Arial, sans-serif | Regular, Bold |
| **Report Code blocks** | Courier New | monospace | Regular |

### 4.2 Type Scale (UI)

| Level | Size | Weight | Usage |
|---|---|---|---|
| H1 | 28px / 1.75rem | 700 | Page titles |
| H2 | 22px / 1.375rem | 600 | Section headers |
| H3 | 18px / 1.125rem | 600 | Sub-section headers, card titles |
| Body | 14px / 0.875rem | 400 | General UI text |
| Small | 12px / 0.75rem | 400 | Labels, metadata, timestamps |
| Code | 13px / 0.8125rem | 400 | Inline code, prompt text |
| Badge | 11px / 0.6875rem | 600 (uppercase) | Status badges, tags |

### 4.3 Type Rules
- Headlines: Dark Navy (`#1B2771`) on light backgrounds
- Body text: Charcoal (`#1A1A2E`)
- Never use Primary Blue for body text
- Monospace font required for all prompt text, responses, regex patterns, and code
- Line height: 1.5 for body, 1.3 for headings

---

## 5. Iconography

- Use **Lucide Icons** (already in prototype stack) — consistent stroke-width 1.5px
- Icon color follows the element's text color in context
- Active/selected icons: Primary Blue (`#0461E2`)
- Danger icons: Alert Red (`#DC2626`)
- Do NOT mix icon libraries (no mixing Heroicons with Lucide)
- Minimum touch target size: **40×40px**

---

## 6. UI Component Standards

### 6.1 Buttons

| Type | Background | Text | Border | Usage |
|---|---|---|---|---|
| Primary | `#0461E2` | White | None | Main CTAs (Start Scan, Download Report) |
| Secondary | White | `#0461E2` | `1px #0461E2` | Secondary actions |
| Danger | `#DC2626` | White | None | Destructive actions (Delete, Stop Scan) |
| Ghost | Transparent | `#1B2771` | None | Tertiary / text buttons |

### 6.2 Cards
- Background: White `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: `8px`
- Shadow: `0 1px 3px rgba(0,0,0,0.08)`

### 6.3 Verdict Badges

| Verdict | Background | Text | Border |
|---|---|---|---|
| VULNERABLE | `#FEE2E2` | `#DC2626` | `1px #DC2626` |
| NEEDS_REVIEW | `#FEF3C7` | `#D97706` | `1px #D97706` |
| NOT_VULNERABLE | `#DCFCE7` | `#16A34A` | `1px #16A34A` |
| UNCERTAIN | `#F3F4F6` | `#6B7280` | `1px #9CA3AF` |

### 6.4 Navigation / Sidebar
- Background: Dark Navy `#1B2771`
- Active item: Primary Blue `#0461E2` left border (3px) + `rgba(4,97,226,0.12)` background tint
- Text: White `#FFFFFF` (inactive), White bold (active)
- Logo appears at top of sidebar on White or Surface Grey background

---

## 7. Report / PDF Standards

### 7.1 Page Layout
- Paper: A4 (210mm × 297mm)
- Margins: 20mm all sides
- Header: SECUSYNC logo (mark + wordmark) left-aligned + report type right-aligned
- Footer: `SECUSYNC | Confidential | Page N of M` — 9pt Helvetica, Charcoal

### 7.2 Report Color Usage
- Section headers: Dark Navy `#1B2771`, bold, 14pt
- Body: Charcoal `#1A1A2E`, 10pt
- Code/prompt blocks: Light grey background `#F3F4F6`, monospace 9pt, border-left `3px #0461E2`
- Risk rating cells: Use semantic colors (Section 3.3) as background tints (20% opacity)
- Table header rows: Dark Navy `#1B2771` background, White text

### 7.3 Report Cover Page
- Background: White
- Logo: centered, 60mm wide
- Title: Dark Navy, 24pt bold, centered
- Subtitle (report type): Primary Blue, 14pt, centered
- Metadata block (date, run ID, TLLM profile): Charcoal, 10pt, centered
- Horizontal rule: 2pt, Primary Blue, full width

---

## 8. Data Visualization Standards

### 8.1 Chart Color Order
When multiple series are needed, use this order:
1. `#0461E2` (Primary Blue)
2. `#1B2771` (Dark Navy)
3. `#16A34A` (Success Green)
4. `#D97706` (Warning Amber)
5. `#DC2626` (Alert Red)
6. `#6B7280` (Muted Grey)

### 8.2 Chart Rules
- Always label axes
- Always include a legend if more than one series
- Grid lines: `#E5E7EB`, 1px
- No 3D effects
- No pie charts — use bar or donut charts instead
- ASR comparison bar charts must always show baseline and mutant side-by-side in Blue and Navy

---

## 9. Writing / Voice Style

| Principle | Guidance |
|---|---|
| **Professional** | No casual language in UI labels, reports, or documentation |
| **Precise** | Use exact technical terms (e.g., "prompt injection" not "prompt attack") |
| **Active voice** | "SECUSYNC detected 3 vulnerabilities" not "3 vulnerabilities were detected" |
| **Consistent terminology** | Always "TLLM" not "target model" or "victim LLM" |
| **Verdict labels** | Always SCREAMING_SNAKE_CASE: `VULNERABLE`, `NOT_VULNERABLE`, `NEEDS_REVIEW` |
| **Attack class names** | Title Case: Prompt Injection, System Prompt Leakage, File Poisoning, Sensitive Information Disclosure |

---

## 10. File Naming Convention

| Asset Type | Convention | Example |
|---|---|---|
| Python modules | `snake_case.py` | `mutation_engine.py` |
| React components | `PascalCase.tsx` | `RunDetail.tsx` |
| Report PDFs | `secusync_[run_id]_[type]_[date].pdf` | `secusync_a1b2_executive_2026-04.pdf` |
| Logo exports | `secusync_logo_[variant]_[bg].png` | `secusync_logo_full_light.png` |
| Documentation | `PascalCase.md` or `lowercase.md` (match existing) | `PRD.md`, `branding.md` |

---

## 11. Accessibility Standards

- All text must meet WCAG AA contrast (4.5:1 for body, 3:1 for large text)
- Interactive elements must have visible focus states (2px Primary Blue outline)
- Status information must not rely on color alone — always pair with icon or text label
- All images and icons in the UI must have `alt` text or `aria-label`
