---
name: wording-review
description: Review of commit messages, names, comments and log messages for plain technical English, wrong or wordy wording, and names that do not match their code or the project's convention, each finding with a rewrite, run on a cheap model. Use when the user asks to check or improve wording, commit messages, naming or comments, or types /wording-review.
allowed-tools: Bash(git log:*), Bash(git show:*), Bash(git diff:*), Bash(git status:*), Read, Grep, Glob
model: haiku
effort: low
context: fork
---

Review the wording of $ARGUMENTS: commit messages, names, comments and log
messages. Every finding carries a rewrite. Do not edit files, run linters or run
tests. Do not report bugs.

**Target**

Run one plain git command per Bash call (`git log -5`): no `-C`, no `&&` or
`;`, those are not permitted.

- An argument that is a path on disk (for example `cache.py` or `src/`): the
  code only. Read the files. There are no commit messages to review: skip pass
  A, and do not run `git show` or `git diff`.
- Any other argument is a commit or revision range (`abc123`, `HEAD`, `a..b`):
  `git log --format='%h%n%B===' <commit or range>` for the messages and
  `git show <commit>` or `git diff <range>` for the code.
- No argument: the commits of this branch. Run `git log --oneline @{u}..HEAD`;
  if it fails, run `git log -5 --oneline` instead. Then read the commits it
  lists the same way.

A convention the project already follows beats every rule below. Before the
passes, Read `git log --oneline -20` of commits older than the target and look
at the names in the files beside the code you review. Do not flag a message or
a name that fits its neighbours.

**Passes**

Work through the four passes in order, each as its own pass.

- **A. Commit messages.**
  - The subject does not say what the change does: `fix`, `misc`, `update`,
    `changes`, `wip`, `fixed bug`, or a list of file names. Rewrite it to
    start with what the change does: `fixes <what>`, `adds <what>` or
    `This patch adds <what>`. Keep the prefix the history uses (`claude:`,
    `fix(scope):`).
  - Past tense: `Added`, `Fixed`. Rewrite in the present tense: `adds`,
    `fixes`. `fixes <what>`, `adds <what>` and `This patch adds <what>` are
    correct forms. Do not flag them.
  - The subject is longer than 72 characters (say "over 72", not an exact
    count), ends with a period, or has no blank line before the body.
  - The body narrates the diff (`added a check in foo.py, removed the old
    loop`) or holds review notes (`addressed comments`, `fixed typo from last
    round`). Rewrite as the problem and the reason for this approach, in one to
    three sentences. Keep what the diff cannot show: side effects, limits.
  - Wordy English. Apply the word list of pass D to the message.
- **B. Names** declared or changed by the target code.
  - Not true to the code: `get_x` that writes, `is_x` or `has_x` that returns
    something other than a boolean, `validate_x` that transforms,
    `handle_x`, `process_x`, `manage_x`, `do_x` for one nameable thing
    (`parse_header`, `drop_expired`).
  - A noise word where a specific name is evident: `data`, `info`, `obj`,
    `var`, `tmp`, `flag`, `val`, `helper`, `util`, `manager`, `thing`, `data2`.
  - A second word for one concept: the code says `expire` everywhere and the
    new name says `evict`. Grep to check.
  - Off convention: a case style or prefix that differs from its neighbours
    (`getData` among `get_data`, a private helper without the `_` its module
    uses).
  - A boolean named with a negation (`is_not_ready`, `no_cache`), which reads
    as `if not is_not_ready`.
- **C. Comments and docstrings.**
  - Not true: it states a return value, unit, side effect or step the code
    beside it does not have. Rewrite it to match the code.
  - Narrates: it restates the next line (`# increment i`), or tells history
    (`changed 2024-05-01`, `old version below`). Delete it, or keep the one fact
    the code cannot show.
  - Commented-out code. Delete it.
- **D. English** in comments, docstrings, log and error strings of the code.
  The standard is Simplified Technical English (ASD-STE100), the controlled
  language written for aviation maintenance manuals. Apply its rules that fit
  code, and flag with the rewritten sentence:
  - A long word for a plain one: utilize → use, in order to → to, prior to →
    before, subsequent → after, initiate → start, terminate → stop, attempt →
    try, additional → more, numerous → many, facilitate → help, commence →
    begin, perform an operation → do, is responsible for → does, due to the
    fact that → because, in the event that → if, for the purpose of → to,
    provides the ability to → lets, at this point in time → now, a number of →
    many.
  - Filler to delete: very, really, simply, just, basically, obviously, clearly,
    extremely, robust, seamless, leverage, comprehensive, cutting-edge, "it
    should be noted that", "as mentioned above", "please note".
  - A sentence over 20 words (STE: 20 in an instruction, 25 in a description),
    or one with several instructions or clauses. One instruction per sentence.
    Split it.
  - Passive voice where the actor is known: "The cache is flushed by this
    function" → "This function flushes the cache".
  - A verb form other than a simple tense: "checking for a lock file existing"
    → "checks that the lock file exists".
  - A noun cluster of more than three words: "user session timeout retry
    handler" → "handler that retries a timed-out user session".
  - A dropped article or subject: "Returns user" → "Returns the user".
  - A second word for one thing: `fetch`, `get`, `load` and `retrieve` for one
    action. STE allows one word, one meaning. Keep one of them.

Do not flag in D: a technical term, however long (idempotent, serialize,
atomic, backpressure), and a comment that explains why the code is written this
way, however long it is. Plain words never change the meaning: keep every
number, unit, condition and exception.

Do not flag: merge and revert commits, a subject-only message for a small
change, license headers, doc comments on a public interface, TODO and FIXME
lines, loop names (`i`, `e`, `ex`), standard abbreviations (`ctx`, `req`, `buf`,
`ptr`, `fd`, `id`, `cfg`), and a name you cannot improve.

**Verify**

Check each candidate before it goes in the report:

1. Name: you have Grepped its uses, and the new name is true at all of them.
2. Comment or message: the rewrite keeps every fact the original gave, and
   adds nothing. A rewritten commit message may use only what the original
   message or the diff says. If neither gives the reason for the change, rewrite
   the subject and report the body as missing.
3. The rewrite is clearly better: true where the original is not, or much
   shorter with the same facts.

Drop the candidate if any check fails.

**Report**

Group by pass. Report at most 5 findings per pass, most useful first, and say
how many you left out. Quote the original and give the rewrite. You review
wording only: never propose to delete or restructure code, and the rewrite of a
name is always a new name. Use this form:

    - `a1b2c3` subject: "fixed bug" → "user: fixes crash on an empty name in
      create"
    - `a1b2c3` body: delete "addressed review comments". Missing: the reason
      for the change
    - `store.py:35` name: `handle_data` → `total_discounted_price` (6 uses)
    - `store.py:20` comment: "In this function we first of all check ..." →
      "Number of items under `key`."
    - `store.py:44` comment: "We need to utilize the discount ..." → "Drop each
      item's discount."

Open with one line that counts the findings of each pass:

    Single-pass wording review of <target>: 7 findings (3 commit messages,
    2 names, 1 comment, 1 wording).

The line tells the reader that one model ran every pass inline and re-checked
each candidate, with no independent verifier subagents.

If nothing survives, report `Nothing found.` and nothing else.
