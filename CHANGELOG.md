# Changelog

## [Unreleased]

- Check the total budget including controls and BOS/EOS before final pieces,
  after merging when required; qualify exact limits and hostile inputs.

- Add immutable role-based controls, explicit input policies, BOS/EOS and included/skipped decoding; pin Tokenizers 0.22.1 across 594 multilingual and adversarial cases, with no Python dependency in ordinary calls or tests.

- Apply BPE merges by rank then leftmost occurrence, preserving boundaries
  and spans; bound the fused token count without rescanning the sequence.

- Add immutable identity/NFC/NFKC and none/GPT-2 loading choices, expose
  normalized segment spans, and bound normalized size separately.

- Add `AI.Tokenizer` to load a complete byte-level alphabet,
  parse the same model from memory, encode portable IDs and decode exact bytes
  or strict UTF-8. Owned encodings
  include UTF-8 spans, structured errors and configurable limits.
- Validate vocabulary and merge rules; explicitly reject models with merges
  until their encoding is qualified. Unicode normalization, pre-tokenization
  and controls remain outside this first surface.
- Add a public consumer and FR/EN guide. New required STD calls will be accounted
  for when preparing versions; existing tags do not retroactively gain tokenizer support.
