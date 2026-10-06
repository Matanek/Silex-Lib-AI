"""Deterministic selected ASCII corpus; independent naive rank/left oracle.

Development only. Ordinary tests and Silex parity programs need no Python.
"""
from pathlib import Path
import itertools
import json
import random

ROOT = Path(__file__).resolve().parent.parent
fixtures = ROOT / "Fixtures"
vocab = json.loads((fixtures / "bpe-vocab.json").read_text())
for token in ["abcabc"]:
    if token not in vocab:
        vocab[token] = max(vocab.values()) + 1
(fixtures / "bpe-vocab.json").write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n")
sparse = json.loads((fixtures / "sparse.json").read_text())
for index, token in enumerate(token for token in vocab if token not in sparse):
    sparse[token] = (2**63 - 1) - 1024 + index
(fixtures / "bpe-sparse.json").write_text(json.dumps(sparse, ensure_ascii=False, indent=2) + "\n")
rules = [
    "a b\nb c\nab c\na a\naa aa\nab ab\naba b\nba ba\nabc abc\n",
    "b c\na b\nbc a\na a\naa aa\nab ab\n",
    "aa aa\na a\na b\nab c\n",
]
inputs = ["", "abc", "abca", "aaaaa", "aaaaaa", "abababab", "abcabc", "baba", "aaaaaaaaaaaaaaaaa"]
inputs += ["".join(value) for length in range(1, 4) for value in itertools.product("abc", repeat=length)]
randomizer = random.Random(52031)
inputs += ["".join(randomizer.choice("abc") for _ in range(randomizer.randrange(1, 97))) for _ in range(64)]

def naive(text, vocabulary, merge_text):
    ranks = {tuple(line.split(" ")): rank for rank, line in enumerate(merge_text.splitlines())}
    pieces = [(symbol, index, index + 1) for index, symbol in enumerate(text)]
    while True:
        candidates = [(ranks[(left[0], right[0])], index) for index, (left, right) in
                      enumerate(zip(pieces, pieces[1:])) if (left[0], right[0]) in ranks]
        if not candidates:
            break
        _, index = min(candidates)
        left, right = pieces[index:index + 2]
        pieces[index:index + 2] = [(left[0] + right[0], left[1], right[2])]
    return [(vocabulary[symbol], start, end) for symbol, start, end in pieces]

trace = []
for model_index in range(4):
    vocabulary = vocab if model_index < 3 else sparse
    merge_text = rules[model_index % 3]
    for case_index, text in enumerate(inputs):
        pieces = naive(text, vocabulary, merge_text)
        trace.append(f"case {model_index}:{case_index}")
        trace.append(f"tokens {len(pieces)}")
        trace.extend(f"{token}:{start}:{end}" for token, start, end in pieces)
(fixtures / "bpe-reference.txt").write_text("\n".join(trace) + "\n")
(fixtures / "bpe-reference.meta.json").write_text(json.dumps({"seed": 52031, "models": 4,
    "cases": len(inputs), "method": "independent naive rescan, rank then left position",
    "scope": "selected ASCII without pretokenization; sparse 64-bit external IDs"}, indent=2) + "\n")

def literal(text):
    return json.dumps(text, ensure_ascii=False)

source = """use AI.Tokenizer

func main() {
    let texts:str[] = [%s]
    let rules:str[] = [%s]
    var model_index = 0
    while model_index < 4 {
        var vocabulary = embed_text("Fixtures/bpe-vocab.json")
        if model_index == 3 { vocabulary = embed_text("Fixtures/bpe-sparse.json") }
        var model = try Tokenizer.parse_bpe(vocabulary, rules[model_index %% 3]) else error { panic(error.detail) }
        var case_index = 0
        for text in texts {
            let result = try model.encode(text) else error { panic(error.detail) }
            let decoded = try model.decode(result.ids()) else error { panic(error.detail) }
            assert(decoded == text)
            print("case $(model_index):$(case_index)")
            print("tokens $(result.count())")
            var cursor = 0
            for piece in result.pieces() {
                assert(piece.span!.start == cursor && piece.span!.end > cursor)
                assert(piece.bytes.count() == piece.span!.end - cursor)
                cursor = piece.span!.end
                print("$(piece.id):$(piece.span!.start):$(piece.span!.end)")
            }
            assert(cursor == text.count())
            case_index++
        }
        model_index++
    }
}
""" % (",\n        ".join(map(literal, inputs)), ", ".join(map(literal, rules)))
(ROOT / "BPEParity.sx").write_text(source)
print(f"Generated {4 * len(inputs)} comparisons")
