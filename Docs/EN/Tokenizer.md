# Encode and reconstruct byte-level text

`AI.Tokenizer` loads an immutable byte-level alphabet, encodes UTF-8 text into
`int[]` IDs and reconstructs exact bytes or normalized text. Byte-level BPE
models support `identity` normalization (default), NFC or NFKC, and `none`
pre-tokenization (default) or `gpt2`. The vocabulary/rules pair is validated once
when loading; encoding never rereads model files.

## Load, encode and decode

Supply `vocab.json` and `merges.txt` in the runtime working directory. The vocabulary
is a JSON object mapping GPT-2 byte-level alphabet symbols to unique non-negative
integer IDs. It covers all 256 bytes; the merges file lists ranked symbol pairs,
optionally headed by `#version: 0.2`. An empty file enables byte fallback.
This program uses an application-provided model:

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
Model merges may produce tokens representing several bytes; decoding restores
their exact byte sequence.

An [executable consumer](../../Tests/TokenizerConsumer/Example.sx) provides the
same flow with a versioned miniature alphabet. From the development workspace
root, with the AI/STD/JSON candidates linked to that workspace:

```sh
silex run Packages/AI/Tests/TokenizerConsumer/Example.sx
silex test Packages/AI/Tests/TokenizerConsumer
```

Development qualification uses AI and STD candidates. The new `Dictionary.find`,
`Text.UTF8.byte_count` and new Regex capabilities must be available in the STD
version selected
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

## Choose model normalization and segmentation

`LoadOptions.normalization` and `pre_tokenizer` set the choices when creating
the model; they remain immutable during encoding. Keep the configuration used
when training the model. NFC composes canonical equivalents; NFKC also changes
compatibility forms, such as `ﬁ` to `fi`, `Ａ` to `A` and `¼` to `1⁄4`.
Decoding restores normalized text; these transformations do not recover the
original form. Tables come from `STD.Text`, Unicode 17.0.0.

This [executable program](../../Tests/TokenizerConsumer/TextPipelineExample.sx)
normalizes text and inspects the GPT-2 profile boundaries:

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.parse_bpe(embed_text("Fixtures/vocab.json"), "",
        Tokenizer.LoadOptions(normalization:Tokenizer.Normalization.nfkc,
            pre_tokenizer:Tokenizer.PreTokenizer.gpt2)) else error { panic(error.detail) }
    let encoding = try tokenizer.encode("ﬁ  世界") else error { panic(error.detail) }
    print(encoding.normalized_text())
    for segment in encoding.segments() { print("$(segment.start):$(segment.end)") }
}
```

Output:

```text
fi  世界
0:2
2:3
3:10
```

`encoding.segments()` returns a detached list of `Span` values covering
normalized text contiguously. `none` produces one segment over the whole
nonempty input; `gpt2` uses the boundaries below. Empty input has no segments.
Without merges, each byte remains one token regardless of segmentation.

### Exact GPT-2 profile

The ordered, case-sensitive pattern comes from
[Transformers 2.10.0](https://huggingface.co/transformers/v2.10.0/_modules/transformers/tokenization_gpt2.html):

```text
's|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+
```

`L` and `N` denote complete Unicode categories; `N` includes nondecimal
numbers. `\s` follows Unicode 17.0.0 `White_Space`, and `\S` its complement.
The optional space before words, numbers or symbols is U+0020 only. No leading
space is added and no space is removed. Thus `we're  ici` becomes `we`, `'re`,
` ` and ` ici`; uppercase contractions do not match the lowercase alternatives.

`STD.Regex` compiles the pattern once during loading. The negative assertion
`(?!\S)` examines exactly the next scalar. Fixtures include all 25 `White_Space`
characters, NUL, combining marks and emoji/ZWJ; FEFF and 001C are not Unicode
whitespace. The independent Node fixture reference uses Unicode 16.0 for
selected stable characters: it qualifies this corpus, not the complete GPT-2
tokenizer or all Unicode 17 characters.

## Apply the model merge rules

The order of lines in `merges.txt` defines rank. Among currently eligible pairs,
the lowest rank wins; at equal rank, the leftmost occurrence is merged. A merge
may make a new pair eligible, even if its rule appears earlier. No merge crosses
a pre-tokenization boundary. Duplicate rules, unknown references and results
missing from the vocabulary fail at loading.

This [executable program](../../Tests/TokenizerConsumer/BPEExample.sx) loads a
miniature fixture where `a b` yields ID 256 and `ab c` yields ID 258:

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.parse_bpe(embed_text("Fixtures/bpe-vocab.json"),
        "a b\nab c\n") else error { panic(error.detail) }
    let encoding = try tokenizer.encode("abc") else error { panic(error.detail) }
    for piece in encoding.pieces() {
        print(piece.id)
        print("$(piece.span!.start):$(piece.span!.end)")
    }
    print(try tokenizer.decode(encoding.ids()) else error { panic(error.detail) })
}
```

Output:

```text
258
0:3
abc
```

Models without rules retain one token per byte. With merges, `maximum_tokens`
bounds the final token count; two merged bytes can therefore fit a one-token
limit. A merged piece's bytes and span cover exactly the contiguous pieces it
replaces. A piece may still cut a UTF-8 scalar; inspect its bytes or decode the
complete sequence. Merge tables and candidates remain private, without a mutable
global cache.

## Inspect the encoding

`encoding.ids()` returns a detached list usable at a model boundary.
`encoding.pieces()` returns `Piece` values with `id`, `bytes` and `span`;
`encoding.count()` counts tokens. `normalized_text()` provides the text referenced
by spans, after the selected normalization.

A `Span` is a half-open `[start, end)` interval in **UTF-8 bytes**, not scalars,
UTF-16 units or graphemes. For example, `é` produces two one-byte pieces with
spans `[0, 1)` and `[1, 2)`. Neither individual byte is valid UTF-8. The optional
span is absent for added BOS/EOS, and present for literal controls.
`Piece.special` identifies the control role, or is absent for ordinary pieces.
`tokenizer.special_tokens()` returns detached model descriptions.

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
invalid rules or controls and exceeded limits. Fractional, out-of-range
or duplicate IDs, empty/out-of-alphabet tokens and unknown or duplicate merges
are rejected before use.

`LoadOptions` bounds each file to 16 MiB, JSON depth to 32, vocabulary entries
and merge rules to 100,000, and each token to 4,096 bytes. Controls are bounded
to 256 descriptors and 65,536 cumulative surface bytes (`maximum_special_tokens`,
`maximum_special_bytes`); the per-token bound also applies to control surfaces.
Fields are configurable.
Reading remains bounded if a file grows; entry limits are checked after JSON
parsing, which is already bounded by file size and depth.

`EncodeOptions` defaults to 16 MiB each for raw and normalized input bytes
(`maximum_input_bytes`, `maximum_normalized_bytes`), and 16 Mi tokens;
`DecodeOptions` defaults to 16 MiB for output bytes. Negative limits return an
options error. Calls without options retain these defaults. Raw size is checked
before normalization, then normalized size before
segmentation and token creation. Normalization may create intermediate results
before this second check; their volume is bounded by input and Unicode tables.
Decoding checks remaining capacity before appending a token.

The token limit includes literal controls and requested BOS/EOS tokens.
Without rules, a segment's byte count allows rejection before constructing its
pieces. With rules, the tokenizer counts remaining tokens after merging and
checks the budget before constructing final pieces. EOS capacity is reserved
before encoding the body. Simultaneously invalid options or inputs do not
guarantee a diagnostic order.

## Configure and allow controls

`LoadOptions.special_tokens` associates each nonempty surface with a nonnegative
ID and a closed role: `bos`, `eos`, `padding`, `unknown` or `control("name")`.
IDs, surfaces and roles are unique; collisions with ordinary IDs, symbols or
bytes are rejected. Named controls require a nonempty name. Surfaces must already
be stable under the model normalization. Recognition follows normalization and
precedes segmentation: longest surface first, then model order. Identical
surfaces cannot be configured twice.

`EncodeOptions.special_input` defaults to `SpecialInput.reject`: a recognized
literal surface returns `forbidden_special`. `SpecialInput.allow([ids])` permits
only listed controls; unknown or duplicate IDs are invalid options.
`SpecialInput.ordinary_text` treats all such surfaces as ordinary text.
These policies do not automatically add BOS/EOS.

`boundary_tokens` selects `BoundaryTokens.none`, `bos`, `eos` or `bos_and_eos`.
A requested missing role is an invalid option, even for empty input. Added
controls count toward the token limit and have no span.
`DecodeOptions.special_tokens` selects `DecodeSpecialTokens.include` (default)
or `skip`; only configured IDs are skipped, never unknown IDs. Padding/unknown
roles describe controls; they do not enable padding or byte replacement.

This [executable program](../../Tests/TokenizerConsumer/SpecialExample.sx)
explicitly adds BOS/EOS and then reconstructs the text alone:

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.parse_bpe(embed_text("Fixtures/bpe-vocab.json"), "a b\nab c\n",
        Tokenizer.LoadOptions(special_tokens:[
            Tokenizer.SpecialToken(surface:"<bos>", id:1000, role:Tokenizer.SpecialRole.bos),
            Tokenizer.SpecialToken(surface:"<eos>", id:1001, role:Tokenizer.SpecialRole.eos)
        ])) else error { panic(error.detail) }
    let encoding = try tokenizer.encode("abc", Tokenizer.EncodeOptions(
        boundary_tokens:Tokenizer.BoundaryTokens.bos_and_eos)) else error { panic(error.detail) }
    for piece in encoding.pieces() { print(piece.id) }
    print(try tokenizer.decode(encoding.ids(), Tokenizer.DecodeOptions(
        special_tokens:Tokenizer.DecodeSpecialTokens.skip)) else error { panic(error.detail) })
}
```

Output: `1000`, `258`, `1001`, then `abc`.

## Development compatibility

The tokenizer must be tested with the matching Silex and STD candidates.
Installing the published graph on October 6, 2026 fails on `UTF8.byte_count`,
which is absent from STD 0.22.0. The planned route is AI 0.2.0 with STD 0.23.0
and a forthcoming Silex version containing the qualified fixes. These versions
are not presented as published. The AI 0.1.0 tag retains its original content
without a tokenizer.

## Verified compatibility

The [pinned oracle](../../Tests/TokenizerConsumer/Fixtures/Oracle/README.md)
Tokenizers **0.22.1** checks 594 cases of the synthetic model: identity/NFC/NFKC,
ByteLevel with/without regex, no automatic prefix space, normalized controls and
explicit BOS/EOS template. IDs, piece bytes and included/skipped decoding are
compared. Normalized UTF-8 offsets are proved locally without assuming the
oracle offset unit. Compatibility is limited to this model and these options;
Python tools only regenerate development fixtures.
No training,
model downloads, padding, batching or tensor conversion is provided. Model files
remain owned by the application.

[Return to the AI index](README.md)
