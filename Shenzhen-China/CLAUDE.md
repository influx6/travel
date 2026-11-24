# Project rules

## Tools live in `./tools`

Any script, helper, or automation tool written for this project must be created inside
`./tools/` — not in `/tmp`, not in the repo root, not anywhere else. This is a hard rule
for this directory.

- Create `./tools/` if it does not exist.
- Give each tool a clear name (`fetch_places.mjs`, `coords.py`, …).
- Anything the tool produces (raw dumps, caches, intermediate JSON) goes in `./tools/out/`.
- Keep throwaway one-liners out of the repo; if it's worth writing down, it goes in `./tools/`.
