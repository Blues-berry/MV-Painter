# Persistent execution memory

Updated: 2026-09-29 UTC

## GPU execution rule

This project uses a shared server GPU. GPU discovery, `nvidia-smi`, CUDA
preflight, model inference, training, rendering, and long-running experiment
launches must be executed outside the filesystem sandbox with the required
server privileges. The sandbox is reserved for source edits, manifests,
static audits, and lightweight CPU checks.

Never conclude that the server GPU is unavailable solely from a sandbox-local
`nvidia-smi` failure. Record the execution context and rerun the check outside
the sandbox before declaring a hardware blocker.

## Revision priority

Historical dataset/file imperfections are logged once and do not block new
experiments unless they change the interpretation of the new comparison.
