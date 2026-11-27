---
name: light-review
description: Quick correctness review of the current diff, a commit, a revision range or a path, run on a cheap model. Use when the user asks for a light, quick or cheap review, or types /light-review.
allowed-tools: Bash(git diff:*), Bash(git show:*), Bash(git status:*), Bash(git log:*), Read, Grep, Glob
model: haiku
effort: low
context: fork
---

Review the code in $ARGUMENTS for correctness bugs only. Do not edit files, run
linters or run tests.

**Target**

- No argument: the uncommitted changes (`git diff HEAD`). If that diff is empty,
  say so and stop.
- A path: `git diff HEAD -- <path>`.
- A commit or revision range (`abc123`, `a..b`, `a...b`): `git show <commit>` or
  `git diff <range>`.

Read the whole diff. For every hunk, also Read the enclosing function or method:
a bug often sits in an unchanged line of a touched function.

**Angles**

Work through the three angles in order, each as its own pass over the diff.
Keep a running list of candidates; do not report while a pass is in progress.

- **A. Line by line.** For every line ask what input, state or timing makes it
  wrong: inverted conditions, off-by-one, null or undefined dereference, missing
  `await`, falsy zero, wrong variable in a copy-paste, swallowed error, unescaped
  regex metacharacter.
- **B. Removed behavior.** For every deleted or replaced line, name what it
  enforced, then look for where the new code re-establishes it. A dropped guard,
  error path or test is a candidate.
- **C. Callers and callees.** For each function whose signature, return shape,
  preconditions or exceptions changed, Grep its callers and check that none
  breaks. For each new call, check the callee's contract.

**Verify**

Go through the candidates one at a time. For each, Read the line and confirm:

1. the code says what the candidate claims;
2. nothing nearby already handles the case (a guard, a default, a try/catch);
3. you can name a concrete input or state that produces a wrong result.

Drop the candidate if any check fails. Merge candidates that describe the same
defect at the same location.

Do not flag: style, naming, missing tests or type annotations, anything a linter
or compiler already rejects, and anything that needs an input the code cannot
receive.

**Report**

Give each surviving finding a severity:

- `important`: this change introduces the bug or makes it worse.
- `pre_existing`: the bug was already there and the change only fails to fix it.
- `nit`: a real bug that harms nobody, such as a misleading log line.

Report at most 10 findings, most severe first. Never drop a finding to shorten
the list without saying how many were left out. Use this form:

    - `path:line` [severity] What goes wrong, as a user of the code would see
      it. What triggers it. Fix: the change to make.

Open with one line: `Single-pass light review of <target>: N findings.` The line
tells the reader that one model ran every angle inline and re-checked each
candidate, with no independent verifier subagents.

If nothing survives, report `Nothing found.` and nothing else.
