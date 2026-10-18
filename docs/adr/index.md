# Architecture decisions

Each decision has a short record. A record gives the context, the decision and the effects.

| Record | Decision |
| --- | --- |
| [0001](0001-toolchain.md) | Use uv, ruff, ty, pytest, Hypothesis, mutmut and import-linter. |
| [0002](0002-pure-domain-core.md) | Keep the domain pure. Put side effects in adapters. |
| [0003](0003-editorial-text-removed.md) | Remove editorial text. Keep Corneille's own words. |
| [0004](0004-manifest-and-hosting.md) | Pin checksums in a manifest. Host code on GitHub and data on Hugging Face. |
| [0005](0005-stdlib-runtime.md) | Use only the standard library at run time. |
| [0006](0006-complexity-and-crap.md) | Use complexity and CRAP as guardrails, not as targets. |
