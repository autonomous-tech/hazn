# CRO Skills Comparison: HAZN vs MarketingSkills

**Analysis Date:** 2025-01-17  
**Analyst:** CRO Skills Analyst (Subagent)

---

## Executive Summary

HAZN and MarketingSkills approach CRO from fundamentally different angles:

- **HAZN** = Strategic, holistic auditing (diagnose → recommend → roadmap)
- **MarketingSkills** = Tactical, execution-focused optimization (individual touchpoint optimization + experimentation)

Neither is complete without the other. HAZN excels at comprehensive analysis but lacks granular implementation skills. MarketingSkills excels at specific touchpoint optimization but may lack strategic context.

---

## 1. Overlap Analysis

### Where We Cover the Same Ground

| Area | HAZN Skill | MarketingSkills Skill | Overlap Level |
|------|------------|----------------------|---------------|
| Page-level conversion | `conversion-audit`, `website-audit` | `page-cro` | **High** |
| Form optimization | Within `conversion-audit` (CTA/form analysis) | `form-cro` | **Medium** |
| UI/UX patterns | `ui-audit`, `b2b-marketing-ux` | Implied in various CRO skills | **Medium** |

### Detailed Overlap

**Page Conversion Optimization**
- Both analyze headlines, CTAs, value propositions, and social proof
- HAZN provides scored audits with before/after recommendations
- MarketingSkills likely provides implementation-ready optimizations
- *Our edge:* Comprehensive frameworks (PAS, AIDA, StoryBrand), branded deliverables, CVR projections

**Form Analysis**
- HAZN covers forms within broader audit context (friction points, field analysis)
- MarketingSkills has dedicated `form-cro` skill
- *Their edge:* Likely deeper on form-specific patterns (multi-step, conditional logic, field psychology)

---

## 2. Their Advantages — What We're Missing

### Critical Gaps

#### 🔴 **signup-flow-cro** (Registration Flow Optimization)
**Gap Level:** HIGH

We lack dedicated expertise in:
- Multi-step registration optimization
- Social login vs. email trade-offs
- Progressive profiling strategies
- Registration abandonment recovery
- Mobile-specific signup patterns

**Impact:** Missing revenue from registration friction. SaaS and B2C clients need this.

#### 🔴 **onboarding-cro** (Post-Signup Activation)
**Gap Level:** HIGH

We completely lack:
- First-run experience optimization
- Activation milestone design
- Aha-moment identification
- Onboarding checklist patterns
- Time-to-value optimization
- Retention-focused activation flows

**Impact:** Huge gap for SaaS clients. Onboarding is often the highest-leverage CRO work.

#### 🔴 **ab-test-setup** (Experiment Design & Implementation)
**Gap Level:** HIGH

We lack:
- Hypothesis formulation frameworks
- Sample size calculations
- Statistical significance guidance
- Test prioritization frameworks (ICE, PIE, etc.)
- Variant design principles
- Test documentation standards
- Bayesian vs. frequentist guidance

**Impact:** We can recommend changes but can't help implement rigorous testing.

#### 🔴 **analytics-tracking** (Event Tracking Setup)
**Gap Level:** HIGH

We lack:
- Event taxonomy design
- Tracking plan templates
- GA4/GTM implementation patterns
- Conversion funnel instrumentation
- Custom event architecture
- Data layer specifications

**Impact:** Without tracking, we can't measure the impact of our audit recommendations.

#### 🟡 **popup-cro** (Modals & Overlay Optimization)
**Gap Level:** MEDIUM

We mention popups negatively in `b2b-marketing-ux` ("No pop-ups on first visit") but lack:
- Exit-intent optimization
- Scroll-trigger timing
- Mobile popup patterns (compliant with Google)
- Offer/value testing frameworks
- Popup frequency/suppression logic

**Impact:** Popups are a major lead gen tool. We dismiss them rather than optimize them.

#### 🟡 **paywall-upgrade-cro** (In-App Upgrade Moments)
**Gap Level:** MEDIUM

We completely lack:
- Freemium-to-paid conversion optimization
- Feature gating strategy
- Upgrade prompt timing
- Pricing page optimization (in-app context)
- Trial conversion optimization

**Impact:** Gap for SaaS clients with freemium models.

---

## 3. Our Advantages — What We Have That They Don't

### Strategic Strengths

#### 🟢 **Comprehensive Audit Frameworks**
**Advantage Level:** HIGH

Our `conversion-audit` and `website-audit` provide:
- **Structured scoring system** (1-10 across pillars)
- **Three-pillar framework:** Copy + SEO + Frontend Design
- **CVR projection methodology** with industry benchmarks
- **Implementation roadmaps** (Quick wins → Short-term → Long-term)
- **Branded deliverables** (HTML reports, professional presentation)

*They likely lack:* Formal audit structure, scoring systems, branded client deliverables.

#### 🟢 **B2B Marketing UX Specialization**
**Advantage Level:** HIGH

Our `b2b-marketing-ux` provides deep expertise in:
- Services business conversion (trust before transaction)
- Page architecture blueprints (Homepage, Services, Case Studies, Packages)
- B2B buyer psychology (longer sales cycles, committee decisions)
- Credibility hierarchy (logos → results → testimonials → case studies)
- Professional services pricing presentation

*They likely lack:* B2B-specific patterns. Most CRO content is B2C/ecommerce focused.

#### 🟢 **UI Audit Framework (Tommy Geoco's Framework)**
**Advantage Level:** HIGH

Our `ui-audit` provides:
- **3 Pillars:** Scaffolding, Decisioning, Crafting
- **Macro bet alignment** (Velocity, Efficiency, Accuracy, Innovation)
- **Comprehensive pattern library** (30+ reference documents)
- **Design decision workflow** with weighted criteria
- **Contextual audit sections** based on design type

*They likely lack:* Formalized UX decision-making framework.

#### 🟢 **Discovery Workflow**
**Advantage Level:** MEDIUM

Our `website-audit` mandates:
- Audit type selection (Copy, SEO, Visual/UI, CRO)
- Target information gathering (platform, industry, price point, markets)
- Analytics access assessment
- Known context capture

*They likely lack:* Structured intake process. May jump straight to optimization.

#### 🟢 **SEO Integration**
**Advantage Level:** MEDIUM

Our audits integrate SEO analysis:
- Meta tags, headings, schema markup
- Core Web Vitals, mobile optimization
- Content depth, keyword targeting
- Technical SEO checklist

*They may lack:* SEO as part of conversion optimization (it affects traffic quality).

---

## 4. Learning Opportunities — Techniques to Adopt

### Priority 1: Build These Skills (High Value)

#### 📊 **ab-test-setup Skill**
Create a skill covering:
```
- ICE/PIE prioritization frameworks
- Hypothesis template: "If we [change], then [metric] will [improve] because [reason]"
- Sample size calculator integration
- Statistical significance thresholds (95% confidence standard)
- Test documentation template
- Multi-armed bandit vs. A/B decision criteria
- Minimum detectable effect calculations
```

**Why:** Completes the audit → implement → measure loop.

#### 📈 **analytics-tracking Skill**
Create a skill covering:
```
- Event naming conventions (object_action format)
- Conversion funnel mapping
- GA4 event parameter standards
- GTM container architecture
- Data layer specification template
- E-commerce tracking implementation
- Custom dimension/metric design
```

**Why:** Without measurement, we can't prove audit impact.

#### 🚀 **onboarding-cro Skill**
Create a skill covering:
```
- Activation metric identification
- Aha-moment mapping
- Onboarding checklist patterns
- Empty state design
- Progressive onboarding (vs. tour-based)
- Retention hooks during onboarding
- Behavioral triggers for nudges
```

**Why:** Highest-leverage CRO for SaaS clients.

### Priority 2: Enhance Existing Skills (Medium Value)

#### 🔄 **Enhance conversion-audit with:**
- Signup flow analysis section
- Form field optimization checklist
- Modal/popup evaluation criteria (not just dismissal)
- Micro-conversion tracking recommendations

#### 🔄 **Enhance b2b-marketing-ux with:**
- SaaS-specific patterns (pricing pages, feature comparison)
- Trial/freemium conversion patterns
- In-app upgrade moment design
- Self-serve vs. sales-assisted flow optimization

### Priority 3: Reference Learning (Lower Priority)

- Study popup timing research (exit-intent effectiveness data)
- Review paywall conversion benchmarks by industry
- Compile form field reduction case studies

---

## 5. Our Strengths — Where We're Better Positioned

### Strategic Positioning

| Dimension | HAZN | MarketingSkills | Winner |
|-----------|------|-----------------|--------|
| **Audit Depth** | Comprehensive 3-pillar scoring | Likely checklist-based | **HAZN** |
| **B2B Expertise** | Deep B2B/services focus | Likely B2C/ecommerce focus | **HAZN** |
| **Deliverable Quality** | Branded HTML reports | Unknown | **HAZN** |
| **UX Decision Framework** | Formal framework (Geoco) | Likely pattern-only | **HAZN** |
| **Discovery Process** | Mandatory structured intake | Unknown | **HAZN** |
| **Tactical Execution** | Recommendations only | Implementation-focused | MarketingSkills |
| **Experimentation** | Weak/missing | Dedicated skill | MarketingSkills |
| **Measurement** | Weak/missing | Dedicated skill | MarketingSkills |
| **Funnel Granularity** | Page-level | Touchpoint-level | MarketingSkills |

### Our Ideal Client Profile

We're best positioned for:
- **B2B services companies** (agencies, consultancies, professional services)
- **Businesses needing comprehensive audits** (not just quick tweaks)
- **Pre-sale value delivery** (audit as sales tool)
- **Design decision support** (not just conversion optimization)
- **Clients with implementation capacity** (they can execute our recommendations)

We're weaker for:
- **SaaS companies** (need onboarding/activation expertise)
- **High-velocity testing environments** (need A/B test expertise)
- **Data-driven optimization** (need analytics/tracking expertise)
- **Ecommerce** (need transaction-focused patterns)

---

## 6. Action Items

### Immediate (This Week)
1. ✅ Create `ab-test-setup` skill outline
2. ✅ Create `analytics-tracking` skill outline
3. ✅ Add signup flow analysis section to `conversion-audit`

### Short-Term (This Month)
4. Build full `ab-test-setup` skill with ICE framework, hypothesis templates
5. Build full `analytics-tracking` skill with event taxonomy, GA4/GTM patterns
6. Create `onboarding-cro` skill for SaaS activation optimization

### Medium-Term (Next Quarter)
7. Add SaaS-specific section to `b2b-marketing-ux`
8. Create `popup-cro` skill (evidence-based, not dismissive)
9. Add paywall/upgrade patterns to repertoire

---

## Conclusion

**Our moat:** Deep, structured auditing with professional deliverables and B2B expertise.

**Our gap:** Execution-side skills (testing, tracking, specific touchpoint optimization).

**Strategic recommendation:** Don't try to match MarketingSkills skill-for-skill. Instead:
1. **Double down on audit quality** — our reports should be the gold standard
2. **Add measurement capabilities** — we need to close the "prove impact" loop
3. **Add testing framework** — clients need to know *how* to test our recommendations
4. **Keep B2B focus** — don't dilute into generic ecommerce patterns

The optimal position is: **Strategic CRO partner who delivers actionable audits with measurement frameworks** — not a tactical optimizer competing on individual touchpoints.
