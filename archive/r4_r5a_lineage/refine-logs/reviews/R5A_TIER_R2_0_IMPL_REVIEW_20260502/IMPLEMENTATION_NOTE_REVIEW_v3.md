## Cold-read first impressions of v3

[MED] v3 is much closer to an execution brief: S1/S5 are settled, PR1 has concrete gates/tests, and the cloud-spend gate is explicit.

[HIGH] The main cold-read weak spot is S2: it is called “settled,” but still contains a residual discovery step that can stop PR1. That is safe, but not fully execution-closed.

[MED] v3 also introduces process assertions that look over-tight or false on read: the TRIAGE_LOG “same commit + merge SHA” rule is not mechanically satisfiable, and the note says representative file lists include `TRIAGE_LOG.md` when they do not.

## v2-concern verification table

| v2 concern (severity) | v3 closure status | Notes / cite v3 section |
|---|---|---|
| [HIGH] Expected `n_articles` source undefined | closed | S5 settles article-manifest count and wires PR1 step 4 to it. `IMPLEMENTATION_NOTE.md:45-53`, `:75`. |
| [HIGH] Runstate terminal-state under-specified | partial | Terminal criterion is now stated, but table-name discovery remains; at HEAD, no runstate DDL/writer is visible, so PR1 can stall. `:125-139`. |
| [HIGH] Path-E provenance binding incomplete | closed | v3 now requires `trace_shas`, `probe_set_sha256`, 64-hex values, non-empty values, and roster alignment. `:77-81`. Test gap noted below. |
| [MED] Artifact identity weak across manifest-bound values | partial | SHA equality and row-count are stronger, but runstate remains partially executable and tree wording still overstates e2e coverage. `:107-110`, `:204-205`. |
| [MED] `TRIAGE_LOG.md` closing-PR ownership missing | partial | v3 adds ownership, but asks for PR number + merge SHA in the same commit and falsely says file lists include `TRIAGE_LOG.md`. `:243-245`, `:63`, `:147`, `:169`. |
| [HIGH] Q1 strict validator could block fleet loading | closed | S1 allows `<TBD>` while keeping confirmatory hard-fail rejection. `:37-43`, `:69`. |
| [HIGH] PR3b ordering contradiction | partial | Core PR3b dependency is fixed: PR3b after PR2. But v3 still contradicts itself on PR3a ordering. `:57`, `:214-215`. |
| [HIGH] Plan-of-record conflict | closed | v3 explicitly supersedes plan execution mode and names stale rollback/one-commit parts. `:7-18`, `:112`, `:264`. |
| [MED] Path-E key-presence under-fix | closed | Value shape + roster checks added. `:77-81`, `:118`. |
| [MED] PR1 e2e under-tests #9 SHA half | closed | Equality assertions are now explicit for source JSON and per-model pilot parquet SHA. `:107-110`, `:261`. |
| [MED] PR3a mislabeled as docs-only | closed | v3 relabels as doc/CLI sweep touching Python scripts. `:163-166`, `:175`. |
| [LOW] “three PRs” / four-PR naming drift | partial | No stale “three PRs” remains, but stale “PR3” remains and sequencing language is not unified. `:29`, `:57`. |
| [MED] Dependency tree mostly valid after e2e moved to PR1 | closed | PR1/PR2/PR3b edges are mostly coherent. `:199-216`. |
| [MED] Tree overstates what e2e proves for row-count | partial | Still lists row-count under the e2e edge; row-count is separately tested/DoD’d, but the tree remains misleading. `:204-205`, `:119`, `:259`. |
| [LOW] Closing-PR ledger matches body bullets | closed | The ledger rows match PR section finding lists. `:61`, `:145`, `:167`, `:179`, `:271-274`. |
| [HIGH] Q5 not executable | closed | S5 is now in-body instruction, not a stop point. `:45-53`. |
| [MED] Q1/Q2/Q5 blockers missing from tree | partial | Q1/Q5 are settled; Q2 residual failure path is still not represented as a dependency/blocker. `:218-224`. |
| [HIGH] PR1 could only start step 1 because Q1 blocked step 2 | closed | S1 closes the Q1 blocker. `:37-43`, `:69`. |
| [HIGH] Plan conflict as first unanticipated stall | closed | Supersession stanza is explicit. `:7-18`. |
| [HIGH] Q2 largest execution blocker | partial | Safer than v2 because it says stop rather than invent, but it is still likely to stop at HEAD. `:135-139`, `:237`. |
| [MED] Q5 as PR1 blocker | closed | Settled by S5. `:45-53`, `:75`. |

## Novel concerns in v3

[HIGH] Ledger ownership is mis-fixed. v3 requires each PR author to add a PR number and merge SHA “in the same commit as the PR’s last code change,” but a merge SHA does not exist until after merge. `IMPLEMENTATION_NOTE.md:243-244`, `:276`.

[HIGH] v3 claims the PR file lists include `TRIAGE_LOG.md`, but the PR1/PR2/PR3a lists omit it, and PR3b has no file list. This weakens the ledger closure v3 tried to add. `:63`, `:147`, `:169`, `:179-195`, `:245`.

[HIGH] S2 is now safer but still not execution-closed. The note expects a `CREATE TABLE` writer, yet current HEAD appears to have no `scripts/init_runstate_db.py` and no `CREATE TABLE` hit. v3’s “remaining open items don’t block PR1 start” is true only for starting, not finishing. `:135-139`, `:224`, `:237`.

[MED] S2 says “open SQLite” but does not require read-only open or a pre-existing DB check. A naïve `sqlite3.connect(path)` can create a missing DB instead of failing the confirmatory gate cleanly. `:130`, `:133`.

[MED] Path-E gate scope and tests diverge: v3 requires `probe_set_sha256` presence/64-hex, but required negative tests only cover `trace_shas` cases. `:77-80`, `:118`, `:260`.

[MED] S5’s concrete code snippet uses `len(json.loads(...))`; the fail-safe “stop if not list” is stated later, but the snippet itself would count dict keys if copied literally. `:49`, `:53`.

## Drift / completeness

[MED] Dependency closure is valid for the important PR3b rule: PR3b now strictly depends on PR2. `IMPLEMENTATION_NOTE.md:181`, `:215`.

[MED] PR3a sequencing is internally contradictory: v3 says the sequence is `PR1 → PR2 → PR3a → PR3b`, then says PR3a may land after PR3b, while the tree says PR3a can land any order after PR1. `:57`, `:214`.

[LOW] “Four PRs” is mostly unified, but stale “PR3 lands a clean schema” remains. `:29`; no stale “three PRs” found.

[MED] The dependency tree still over-attaches row-count to the e2e test. The body has separate row-count tests/manual DoD, so execution is covered, but the tree text is imprecise. `:119`, `:204-205`, `:259`.

[MED] Ledger table matches section bullets, but ledger process does not match the body/file lists. Findings align in `:271-274`; ownership/file-list claims do not align in `:243-245`.

[LOW] S1/S2/S5 references line up with PR1 sequencing: S1 → step 2, S5 → step 4, S2 → step 7. `:69`, `:75`, `:85-87`, `:125-139`.

## Execution readiness

[HIGH] A fresh implementer can start PR1 from v3, but likely cannot complete PR1 without a parent decision if the S2 grep finds no runstate writer. The first real stall is PR1 step 7 / S2 table discovery. `IMPLEMENTATION_NOTE.md:85-87`, `:135-139`.

[MED] S2’s residual grep is fail-safe in the important sense: it tells the implementer to stop and surface v4 rather than invent semantics. `:139`. It is not completion-safe because the expected writer appears absent at HEAD.

[LOW] S5’s manifest assumption is cheaply verifiable. Current code already treats article inputs as a JSON list of `ArticleRecord`-shaped rows, so this is one file read/type check away. `:47-53`.

## Meta

v3 is sufficient to start execution, but I would not call it fully sufficient to complete execution. The remaining structural blocker is S2: the note’s stop condition is safe, but current repository evidence suggests that stop condition will fire. The ledger ownership fix also needs parent/process clarification before it becomes a reliable PR-close mechanism.
