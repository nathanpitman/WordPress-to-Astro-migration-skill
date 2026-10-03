# wordpress-to-astro changelog

One entry per version, newest first. Every change to a phase, policy or script that alters what a run produces needs a line here, naming the phases it affects, so an existing migration can be updated (`policies/updating-a-run.md`).

Format:

```
## <version> (YYYY-MM-DD) <MAJOR|MINOR|PATCH>
Affects phases: <numbers, or "none">
- <phase N>: <what changed and why it matters, in plain English>
Output effect: <none | docs only | source and rendered output may differ>
New decisions: <questions or config keys added, with defaults, or "none">
```

## 1.0.0 (baseline) MAJOR
Affects phases: none (first stamped version)
- Introduces version stamping, `skillVersion` and per-phase `ranWith` in `docs/run-state.json`, and the update workflow.
- Reference scripts: new `stamp.py`; `build_source.py`, `assets_report.py`, `download_assets.py` and `seo_inventory.py` write through it so hand edits survive a re-run; `crawl.py`, `a11y_audit.py` and `errors_audit.py` record that they ran.
- Runs created before this version have no stamp and are treated as version 0.
Output effect: none
New decisions: none
