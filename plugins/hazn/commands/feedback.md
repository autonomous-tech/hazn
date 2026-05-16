---
description: Capture feedback on a Hazn plugin or skill and open a draft PR (or GitHub issue) in the canonical hazn repo
disable-model-invocation: true
argument-hint: [optional-plugin-or-skill-name]
---

# /hazn:feedback

Closes the feedback loop between Hazn consumers and the canonical hazn marketplace. Captures structured feedback on the most recent (or specified) plugin or skill, then opens a draft PR (preferred) or GitHub issue against `autonomous-tech/hazn`.

## When to use

- Right after a skill produced output that was wrong, off-brand, missing context, or just felt clunky
- When you spotted an opportunity ("this red-team skill should also check X")
- Whenever you want the issue captured in the source of truth rather than lost in chat history

## Flow

### 1. Identify target

If the user passed `$ARGUMENTS`, treat it as the plugin or skill name. Otherwise, look back through the current conversation for the most recent skill that ran or plugin command that was invoked, and propose that. If you genuinely cannot tell, ask the user which plugin or skill the feedback is about — do NOT guess. Confirm the target with the user before continuing.

### 2. Ask 3 questions

Use `AskUserQuestion` (or plain prompts) to gather:

1. **What's wrong / what happened?** — symptom in one or two sentences
2. **What should it do instead?** — desired behavior, or "I don't know yet, just flagging"
3. **Type:** fix-needed | observation-only — drives the PR label and reviewer priority

Also infer severity from the answers: `severity:critical` (broken output, factually wrong, off-brand) or `severity:nice-to-have` (polish, edge case, idea).

### 3. Locate canonical hazn checkout

Look for the local clone in this order:

1. `$HAZN_REPO_PATH` if set
2. `~/Work/autonomous/repos/products/hazn` (the canonical workspace location)
3. `~/repos/autonomous-tech/hazn`

If none found, skip to step 5 (GitHub issue fallback).

### 4. Create branch + commit + draft PR

```bash
cd <hazn-checkout>
git checkout -b "feedback/$(date +%Y%m%d)-<short-slug>"
# write the feedback as docs/feedback/YYYY-MM-DD-<slug>.md including:
#   - Target plugin / skill
#   - User's three answers verbatim
#   - Run context: working directory, brand slug, any input URL, model used
git add docs/feedback/<file>.md
git commit -m "feedback: <one-line summary>"
gh pr create --draft --title "feedback: <summary>" \
  --label "<plugin-name>,severity:<critical|nice-to-have>,type:<fix|observation>" \
  --body "<full report>"
```

### 5. Fallback — GitHub issue

If no local checkout exists, open an issue with the same labels via:

```bash
gh issue create --repo autonomous-tech/hazn \
  --title "<summary>" \
  --label "<plugin-name>,severity:<critical|nice-to-have>,type:<fix|observation>" \
  --body "<full report>"
```

### 6. Report back

Print the PR or issue URL. Done.

## Labels (always apply)

- One label per plugin touched (e.g. `hazn`, `shopify-revenue-audit`, `hazn-legacy`)
- `severity:critical` or `severity:nice-to-have`
- `type:fix` or `type:observation`
