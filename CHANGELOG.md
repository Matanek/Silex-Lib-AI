# Changelog

## [Unreleased]

- Adopts one `Result` declaration: an ordinary call returns the value or
  stops the program on failure; `try call()` keeps the `Result`. Existing calls
  storing results and propagating failures are made explicit. This revision
  requires the development toolchain with these `try` semantics; publication
  must coordinate compiler and package versions.

- Add `AI.Tokenizer`: immutable byte-level BPE models loaded from files or memory,
  identity/NFC/NFKC normalization and none/GPT-2 segmentation, portable IDs,
  owned pieces and UTF-8 spans, and byte or strict UTF-8 decoding.
- Apply merges by rank then leftmost occurrence within pre-tokenization
  boundaries; structured errors and configurable limits check external models,
  inputs and outputs. The total budget includes controls and BOS/EOS, after
  merging when necessary, before final pieces are materialized.
- Configure immutable controls with roles, explicit permission, BOS/EOS insertion
  and include/skip decoding. The pinned Tokenizers 0.22.1 oracle qualifies 594
  cases of the synthetic model; Python remains confined to development tools.
- Provide a public consumer, FR/EN guides and a reproducible native campaign
  with bounded sequential runs. The tokenizer uses STD and JSON; other modules
  retain their dependencies.
- Add `AI.Evolution` to rank and select application genomes, preserve elites,
  and compose deterministic crossover and mutation.
- Add `AI.NeuroEvolution.FixedStructure` to evolve `Tensor.Neural` parameters,
  then `AI.NeuroEvolution.EvolvingStructure` for innovation tracking, structural
  mutation, crossover and feed-forward speciation. The FixedStructure name
  makes the adapter boundary explicit.

The tokenizer remains a development surface: published AI 0.1.0 does not contain
it, and published STD 0.22.0 lacks some required APIs. The next AI version will
be at least 0.2.0, after its published prerequisites are qualified; existing tags
do not retroactively acquire these additions.
