# What "identical" means

A live WordPress site is rarely a stable target. Cache and optimiser plugins (WP Rocket, W3 Total Cache, Autoptimize), CDN features (Cloudflare email obfuscation, challenge scripts, minification), and server-rendered components (Livewire, Gravity Forms, nonces and CSRF tokens) rewrite or randomise the HTML per request, and the same URL can come back in more than one state depending on cache. So "as served" has to be defined before anything is built. Phase 0 does that and writes the result to `docs/baseline.md`:

- **Origin markup:** what remains once hosting-layer output is reversed. Reverse only changes that can be undone exactly (for example restore a lazy-loaded image's real `src` from its `data-` attribute, drop a plugin's injected attributes, scripts, hints and comments, decode obfuscated emails). Count every reversal class.
- **Volatile tokens:** values that change on every render and depend on server secrets (nonces, CSRF values, framework snapshot ids and checksums, form state fields). They cannot be reproduced; emit one canonical capture and mask them when comparing.
- **The comparison contract:** exactly what the verifier reverses, masks and normalises on both sides (whitespace runs, the volatile tokens, the TODO comments from Phase 4, any approved additive artefact). Nothing else may be normalised.

State "identical" only when the verifier has proved it under that contract. Never claim it from spot checks.
