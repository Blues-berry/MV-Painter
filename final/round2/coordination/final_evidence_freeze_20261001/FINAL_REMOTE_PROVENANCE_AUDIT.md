# Final remote and evidence provenance audit — 2026-10-01

## Repository identity

| Git remote | URL | Repository visibility / role |
|---|---|---|
| `origin` | `https://github.com/Blues-berry/MV-Painter.git` | Public target repository. GitHub identifies `Blues-berry/MV-Painter` as Public ([repository page](https://github.com/Blues-berry/MV-Painter)). |
| `mvpainter` | `git@github.com:Blues-berry/MVPainter.git` | Different repository, private according to the prior authenticated GitHub API check; it is not the named target. |
| `upstream` | `https://github.com/amap-cvlab/MV-Painter.git` | Upstream project repository. |

At task entry, the repository-local default was `remote.pushDefault=mvpainter`,
which points at the distinct private `Blues-berry/MVPainter` repository. Per
the user's instruction to keep future pushes consistent, on 2026-10-01 this
repository's local setting was changed to `remote.pushDefault=origin`;
`push.default=current` and `push.autoSetupRemote=true` remain in effect. Thus a
plain future `git push` from this repository targets the public
`Blues-berry/MV-Painter` repository. This change is local to this repository;
it does not alter global Git configuration. The private `mvpainter` remote
remains available only when explicitly named.

## Evidence commits and local refs

| Evidence | Commit | Local branch/ref at audit start | Cached remote-tracking evidence |
|---|---|---|---|
| Robustness-1 | `99d6c88f28050a3fb74a04d74f555ba30f27ff3e` | `codex/main-backbone-robustness1-20260930` | `origin/codex/main-backbone-robustness1-20260930` at the same abbreviated SHA |
| Cross-backbone validation | `4f312566ed42a7b56fae9f11d91d4591d71fd1f2` | `codex/next-review-response-20260930` | cached `mvpainter/codex/next-review-response-20260930`; its artifacts are ancestors of the integrated evidence line |
| Evidence integration / forensic audit | `ce4831f40c723631e395f86268dca13afe9d07e9` | `codex/round2-evidence-integrated-20261001` | cached `mvpainter/codex/round2-evidence-integrated-20261001` |
| Current forensic branch at task entry | `450389fb8232c0f03db0b79f21bdc998043a99e0` | `codex/round2-final-forensic-audit-20261001` | cached `mvpainter/codex/round2-final-forensic-audit-20261001` at the same SHA |

At task entry the working branch tracked the private `mvpainter` remote and
matched its *local cached* tracking ref at `450389f`. The cached public
`origin/codex/round2-evidence-integrated-20261001` ref was `2618d15`; the
forensic commits `ce4831f` and `450389f` were not shown in the cached public
ref listing. A tracking ref is not proof of current live remote state.

## Live verification result at task entry

The required commands were attempted:

```text
git ls-remote origin   -> failed: Could not connect to server
git ls-remote mvpainter -> failed: DNS resolution for ssh.github.com failed
```

Therefore this run cannot attest the live remote branch HEAD SHA or live
equality for either remote. The last locally cached forensic branch SHA equals
the task-entry local HEAD, but that is explicitly only cached evidence.

## Final freeze-branch publication and verification

The user-designated delivery branch is
`codex/final-evidence-freeze-20261001`. Audit-package commit
`edaebb6fb88018a966ef52483895ff2af624f71d` was pushed to the public `origin`
and immediately verified with a live `git ls-remote`; the returned branch SHA
exactly matched local `HEAD` at that checkpoint. The required evidence commits
`99d6c88`, `4f31256`, `ce4831f`, and the task-entry forensic commit `450389f`
are all ancestors of the published branch.

The prior branch name `codex/round2-final-forensic-audit-20261001` remains at
`450389f` on private `mvpainter`; it is not separately published under that
name on `origin`. Its content is present in the public freeze branch ancestry.
The public branch is the canonical delivery for this task.

After the public push, the repository-local policy was verified as
`remote.pushDefault=origin`, `push.default=current`, and
`push.autoSetupRemote=true`. Future plain pushes in this repository therefore
target the public repository; no global Git setting was changed.

## Gate 0 disposition

`PASS` for the final evidence delivery branch: its live public ref matched the
published audit commit, and the required evidence history is reachable from
that ref. The earlier forensic branch name itself remains on the private
remote as noted above; do not confuse that branch-name location with the
public final delivery branch.

The task target is the public `Blues-berry/MV-Painter`; the previously used
private `mvpainter` remote is a different repository. The public branch's
current terminal SHA is reported in the task handoff because any later
documentation-only closure commit necessarily advances that ref.
