# Miniature byte-level fixtures

These synthetic fixtures are original test data, with no downloaded model or
weights. `vocab.json` assigns ID b to byte b for all 256 bytes. The reversible
alphabet preserves U+0021–U+007E, U+00A1–U+00AC and U+00AE–U+00FF; remaining
bytes in ascending order map to scalars U+0100 onward. This follows the
[documented GPT-2 byte alphabet](https://huggingface.co/transformers/v2.10.0/_modules/transformers/tokenization_gpt2.html).

`sparse.json` assigns the same alphabet IDs starting at int.max - 255, proving
that external IDs never determine an allocation size. Other files deliberately
alter JSON, IDs, alphabet coverage, token lengths or merge lines. They are
malformed inputs, not supported models. `with-merge.json` adds token `ab` with
ID 1000; its corresponding rule is validated then rejected as unsupported in
the first encoder. `merges.txt`, `empty-merges.txt` and `crlf-merges.txt` have no
rules and are supported. All ordinary tests consume these checked-in fixtures
without Python or model downloads.
