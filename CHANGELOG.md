# Changelog

## [Unreleased]

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
