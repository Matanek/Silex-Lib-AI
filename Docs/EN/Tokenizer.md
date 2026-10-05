# Encode and reconstruct byte-level text

`AI.Tokenizer` loads an immutable byte-level alphabet, encodes UTF-8 text into
`int[]` IDs and reconstructs exact bytes or text. This first surface supports
models **without merge rules**, `identity` normalization and no pre-tokenization.
Models with merges fail with `LoadErrorKind.unsupported_model`; rules are never
silently ignored.

## Load, encode and decode

Supply `vocab.json` and `merges.txt` in the runtime working directory. The vocabulary
is a JSON object mapping GPT-2 byte-level alphabet symbols to unique non-negative
integer IDs. It covers all 256 bytes; the merges file is empty or contains only
`#version: 0.2`. This program uses an application-provided model:

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.load_bpe("vocab.json", "merges.txt") else error {
        panic(error.detail)
    }
    let encoding = try tokenizer.encode("Bonjour é 世界 👩‍💻") else error {
        panic(error.detail)
    }
    let decoded = try tokenizer.decode(encoding.ids()) else error {
        panic(error.detail)
    }
    print(decoded)
    print("$(encoding.count()) tokens")
}
```

The output is `Bonjour é 世界 👩‍💻`, followed by `29 tokens`. Without merges,
one token represents one byte, so multibyte characters produce multiple IDs.
Vocabulary tokens may also represent several bytes when decoding, even though
this first encoder does not emit them.

An [executable consumer](../../Tests/TokenizerConsumer/Example.sx) provides the
same flow with a versioned miniature alphabet. From the development workspace
root, with the AI/STD/JSON candidates linked to that workspace:

```sh
silex run Packages/AI/Tests/TokenizerConsumer/Example.sx
silex test Packages/AI/Tests/TokenizerConsumer
```

Development qualification uses AI and STD candidates. The new `Dictionary.find`
and `Text.UTF8.byte_count` calls must be available in the STD version selected
for publication; this surface does not claim to be installable from the existing
AI 0.1.0 tag.

## Load an embedded model from memory

`Tokenizer.parse_bpe(vocabulary_json, merges_text, options)` parses the same
formats with the same limits as `load_bpe`, without opening files. It supports
models embedded with `embed_text` or content already read by the application.
`LoadError.path` is absent for memory input and present for a file-related error.

The [in-memory flow](../../Tests/TokenizerConsumer/InMemoryRoundTrip.sx) embeds
the same alphabet and checks IDs, spans, 256 bytes and strict decoding.
Qualification compares its output in the reference interpreter and Debug/Release
binaries; loading from the filesystem remains native.

## Inspect the encoding

`encoding.ids()` returns a detached list usable at a model boundary.
`encoding.pieces()` returns `Piece` values with `id`, `bytes` and `span`;
`encoding.count()` counts tokens. `normalized_text()` provides the text referenced
by spans, which is exactly the input in this version.

A `Span` is a half-open `[start, end)` interval in **UTF-8 bytes**, not scalars,
UTF-16 units or graphemes. For example, `é` produces two one-byte pieces with
spans `[0, 1)` and `[1, 2)`. Neither individual byte is valid UTF-8. The optional
span type reserves source absence for future injected tokens; every piece in
this first surface has a span.

`decode_bytes(ids)` preserves bytes. `decode(ids)` validates them strictly:
unknown IDs or invalid UTF-8 return a `DecodeError` without replacement.
Its `position` is the ID index for unknown IDs or output limits, and the byte
offset for invalid UTF-8.

The tokenizer owns its model and borrows neither paths nor input. Sharing it
mutates no state; returned lists and encodings retain value semantics. The
submodule requires no Tensor, GFX, GPU or Python operations; dependencies of
other AI modules remain in place.

## Set limits and handle errors

`Tokenizer.load_bpe` returns `Result<Tokenizer, LoadError>`. `kind`, `path` and
`detail` distinguish I/O, invalid options, JSON, vocabulary, incomplete alphabet,
invalid rules, exceeded limits and unsupported models. Fractional, out-of-range
or duplicate IDs, empty/out-of-alphabet tokens and unknown or duplicate merges
are rejected before use.

`LoadOptions` bounds each file to 16 MiB, JSON depth to 32, vocabulary entries
and merge rules to 100,000, and each token to 4,096 bytes. Fields are configurable.
Reading remains bounded if a file grows; entry limits are checked after JSON
parsing, which is already bounded by file size and depth.

`EncodeOptions` defaults to 16 MiB for input bytes and 16 Mi tokens;
`DecodeOptions` defaults to 16 MiB for output bytes. Negative limits return an
options error. Calls without options retain these defaults. Encoding counts
bytes before materializing arrays, and decoding checks remaining capacity before
appending a token.

## Compatibility of this first surface

NFC/NFKC, GPT-2 pre-tokenization, BPE merges, special tokens and BOS/EOS are not
yet available. Byte-level describes the alphabet and round trip; it does not
qualify the complete GPT-2 pipeline against an independent oracle. No training,
model downloads, padding, batching or tensor conversion is provided. Model files
remain owned by the application.

[Return to the AI index](README.md)
