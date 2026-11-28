---
name: light-review
description: Quick review of the current diff, a commit, a revision range or a path, for correctness bugs and for misleading or wordy names and comments, run on a cheap model. Use when the user asks for a light, quick or cheap review, or types /light-review.
allowed-tools: Bash(git diff:*), Bash(git show:*), Bash(git status:*), Bash(git log:*), Read, Grep, Glob
model: haiku
effort: low
context: fork
---

Review the code in $ARGUMENTS for correctness bugs, then for names and comments
that mislead or run long. Do not edit files, run linters or run tests.

**Target**

Run one plain git command per Bash call (`git show HEAD`): no `-C`, no `&&` or
`;`, those are not permitted.

- An argument that is a path on disk: `git diff HEAD -- <path>`.
- Any other argument is a commit or revision range (`abc123`, `HEAD`, `a..b`,
  `a...b`): `git show <commit>` or `git diff <range>`.
- No argument: the uncommitted changes (`git diff HEAD`). If that diff is empty,
  say so and stop.

With an argument, never run `git diff HEAD` alone and never report on the
uncommitted changes.

Read the whole diff. For every hunk, also Read the enclosing function or method:
a bug often sits in an unchanged line of a touched function.

**Angles**

Work through the four angles in order, each as its own pass over the diff.
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
- **D. Names and comments.** Look at changed lines and at the functions that
  hold them. Candidates:
  - a name that says something other than its code does: `get_x` that also
    writes, `is_x` that returns a count, `flag`, `data`, `tmp` where a specific
    name is evident, `handle_x` or `process_x` for a function that does one
    thing;
  - a comment that contradicts the code beside it;
  - a comment that can be shorter: it restates the code line by line, tells
    history, or spends many words on one thought (`utilize`, `in order to`,
    `perform an operation`).

**Verify**

Go through the candidates one at a time. For each, Read the line and confirm:

1. the code says what the candidate claims;
2. nothing nearby already handles the case (a guard, a default, a try/catch);
3. you can name a concrete input or state that produces a wrong result.

For a name or comment candidate confirm instead:

1. the name: you have Grepped its uses, and your new name is true of all of
   them;
2. the comment: your shorter version keeps every reason, unit and limit the
   original gave.

Drop the candidate if any check fails. Merge candidates that describe the same
defect at the same location.

Do not flag: style, missing tests or type annotations, anything a linter or
compiler already rejects, anything that needs an input the code cannot receive,
a name that fits the names around it when no name is clearly better, and a
comment that explains why the code is written this way, however long it is.

**Report**

Give each surviving finding a severity:

- `important`: this change introduces the bug or makes it worse.
- `pre_existing`: the bug was already there and the change only fails to fix it.
- `nit`: a real bug that harms nobody, such as a misleading log line, and every
  name or comment finding.

Report at most 10 findings, bugs first, then name and comment findings, at most
5 of those. Never drop a finding to shorten the list without saying how many
were left out. Use this form:

    - `path:line` [severity] What goes wrong, as a user of the code would see
      it. What triggers it. Fix: the change to make.

For a name or comment finding, say what it gets wrong, and make Fix the
replacement itself: the new name, or the comment rewritten in fewer or simpler
words. Do not report one you cannot improve.

Open with one line: `Single-pass light review of <target>: N findings (B bugs,
C names and comments).` The line tells the reader that one model ran every angle
inline and re-checked each candidate, with no independent verifier subagents.

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
