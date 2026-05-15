---
description: Run a brand compliance audit on the current project
disable-model-invocation: true
argument-hint: [path-to-project]
---

# Brand Compliance Audit Command

Run a comprehensive brand audit to ensure all assets follow company guidelines.

## Audit Steps

1. **Color Audit**
   - Scan CSS/SCSS/Tailwind files for color values
   - Compare against approved brand palette
   - Flag off-brand colors with suggestions

2. **Typography Check**
   - Verify font family usage
   - Check type scale compliance
   - Review font weight usage

3. **Spacing Analysis**
   - Check for 4px grid compliance
   - Identify inconsistent spacing values
   - Review padding/margin patterns

4. **Component Review**
   - Audit button styles
   - Check form elements
   - Review card/container styling
   - Verify border-radius consistency

5. **Accessibility Check**
   - Test color contrast ratios
   - Verify focus states exist
   - Check alt text presence
   - Review heading hierarchy

6. **Content Tone (if applicable)**
   - Review copy for brand voice
   - Check terminology consistency
   - Flag jargon or off-brand language

## Output Format

Generate a report with:

```
# Brand Compliance Report

## Summary
- Compliance Score: X/100
- Critical Violations: X
- Warnings: X
- Compliant Items: X

## Critical Violations
1. [Violation] - [File:Line] - [Expected] vs [Found]

## Warnings
1. [Issue] - [File:Line] - [Recommendation]

## Compliant
- [Area]: Passed

## Remediation Plan
1. [Fix] - Priority: High/Medium/Low
```
