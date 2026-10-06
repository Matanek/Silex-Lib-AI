# Check tokenizer results and measure growth

The default workload is a small correctness check. From the workspace root,
with AI, STD and JSON linked to that workspace:

```sh
python3 Packages/AI/Benchmarks/RunTokenizer.py \
  --workspace "$PWD" --silex "$(command -v silex)" \
  --output "$PWD/.silex/tokenizer-smoke"
```

The runner builds Debug and Release sequentially before running them sequentially.
It lowers process priority by 15, limits each process to 60 CPU seconds and each
build or execution to 90 wall seconds. A timeout or interruption terminates the
active process group, including compiler children. A failed or interrupted run
never produces a completed campaign. Priority reduction gives other work
precedence; it does not impose a CPU utilization percentage. The Python runner
uses Unix process controls and requires macOS or Linux. The compiled Silex
workload has no Python dependency.

Smoke uses UTF-8 byte budgets of 16 and 32 per input profile, checks exact IDs and
roundtrips, and writes 175 CSV samples per mode. Its timings do not qualify
growth. The native binary also defaults to smoke; `--full` explicitly selects
the intensive workload. Python is only a development runner, not a tokenizer
dependency.

The full campaign must run when CPU-intensive work is acceptable and the machine
has no competing builds, games or other heavy workloads. Pass `--full` and set
appropriate `--cpu-seconds` and `--timeout` values explicitly. `--mode debug` or
`--mode release` selects one configuration. These bounds control resource use,
not performance acceptance; samples from an interrupted campaign are incomplete.

Both workloads use the redistributable miniature vocabulary from the public
consumer, ten fixed merge rules and two control surfaces. Profiles cover raw
byte fallback, equal-rank repeated pairs, alternating pairs, multibyte text,
GPT-2 segmentation, literal controls and a long false control prefix. Both
control surfaces are configured in every model, including raw fallback.

Full doubles UTF-8 byte budgets from 256 through 8192, producing 455 CSV samples
per mode. Whole units are repeated up to each budget; `bytes` records actual
UTF-8 bytes, which can be slightly smaller than the budget. This keeps Unicode
and ASCII workloads comparable and bounds the deliberately quadratic reference.
Five paired repetitions alternate production/reference order. Fresh model
construction parses embedded memory into a new immutable model; file I/O and
cold OS caches are excluded. Encoding reuses a model and warms each size once.
The output records compiler/binary/source hashes, machine configuration, raw
samples, medians, ranges, median absolute deviations and growth factors.

`naive_fusions` independently rescans and rebuilds the ID sequence after each
merge, with rank then leftmost tie-breaking. It takes segments from the public
encoding, excluding normalization, segmentation and control matching.
Production `encode` includes these stages and materializes pieces. Their timing
ratio compares different workloads; it is not an end-to-end comparison with
another tokenizer. The separate pinned oracle qualifies segmentation and
controls. Every paired encoding asserts exact IDs and decoded text.

Measurements describe the recorded host, OS and architecture. They establish
neither a cross-platform speedup nor performance on arbitrary trained models.
Use a separate memory tool on correctness workloads. This campaign does not
invent allocation counts or put timing thresholds into correctness tests.
