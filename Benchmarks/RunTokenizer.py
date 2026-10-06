#!/usr/bin/env python3
"""Run the fixed native tokenizer campaign from a workspace root."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import statistics
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command_output(args):
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def terminate_group(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        pass
    finally:
        # An exited parent may still have descendants that ignored SIGTERM.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def run_bounded(command, workspace, env, timeout, cpu_seconds, priority, stdout=None, stderr=None):
    def limits():
        os.nice(priority)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds+5))
    process = subprocess.Popen(command, cwd=workspace, env=env, stdout=stdout,
                               stderr=stderr, start_new_session=True, preexec_fn=limits)
    try:
        returncode = process.wait(timeout=timeout)
    except BaseException:
        terminate_group(process)
        raise
    if returncode:
        terminate_group(process)
        raise subprocess.CalledProcessError(returncode, command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--silex', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    workload = parser.add_mutually_exclusive_group()
    workload.add_argument('--smoke', dest='smoke', action='store_true', help='small correctness workload (default)')
    workload.add_argument('--full', dest='smoke', action='store_false', help='complete growth campaign; CPU intensive')
    parser.set_defaults(smoke=True)
    parser.add_argument('--mode', choices=('debug', 'release', 'both'), default='both')
    parser.add_argument('--timeout', type=int, default=90, help='wall seconds per build or execution')
    parser.add_argument('--cpu-seconds', type=int, default=60, help='CPU seconds per process')
    parser.add_argument('--nice', type=int, default=15, help='lower process priority by this amount')
    args = parser.parse_args()
    if args.timeout <= 0 or args.cpu_seconds <= 0 or not 0 <= args.nice <= 19:
        parser.error('positive time limits and nice in 0..19 required')
    workspace = args.workspace.resolve()
    cli = args.silex.resolve()
    output = args.output.resolve()
    package = Path(__file__).resolve().parent.parent
    source = package/'Benchmarks/Tokenizer.sx'
    source_argument = str(source.relative_to(workspace))
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env['ZIG_GLOBAL_CACHE_DIR'] = str(workspace/'.silex/zig-global')
    modes = ('debug', 'release') if args.mode == 'both' else (args.mode,)
    binaries = {mode: workspace/f'.silex/tokenizer-benchmark-{mode}' for mode in modes}
    builds = []
    for mode, binary in binaries.items():
        command = [str(cli), 'compile', source_argument, '--'+mode, '--nocache', '-o', str(binary)]
        run_bounded(command, workspace, env, args.timeout, args.cpu_seconds, args.nice)
        builds.append(dict(mode=mode, command=command, sha256=digest(binary)))
    metadata = dict(system=platform.platform(), architecture=platform.machine(),
                    compiler_version=command_output([str(cli), '--version']), compiler_sha256=digest(cli),
                    source_sha256=digest(source),
                    vocabulary_sha256=digest(package/'Tests/TokenizerConsumer/Fixtures/bpe-vocab.json'),
                    ai_head=command_output(['git', '-C', str(package), 'rev-parse', 'HEAD']),
                    ai_status=command_output(['git', '-C', str(package), 'status', '--short']),
                    builds=builds, repetitions=5, workspace=str(workspace), complete=False,
                    smoke=args.smoke, nice=args.nice, cpu_seconds=args.cpu_seconds,
                    timeout=args.timeout,
                    load='fresh parse_bpe from embedded memory; file I/O and OS cold cache excluded',
                    encode='reused model, warmup per size; alternating paired order',
                    reference='naive merges over production segments; excludes segmentation',
                    scope='host measurements only; no cross-architecture performance claim')
    if platform.system() == 'Darwin':
        metadata['cpu'] = command_output(['sysctl', '-n', 'machdep.cpu.brand_string'])
        metadata['memory_bytes'] = int(command_output(['sysctl', '-n', 'hw.memsize']))
        metadata['os_version'] = command_output(['sw_vers', '-productVersion'])
    (output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    summary = []
    for mode, binary in binaries.items():
        print('Running '+mode+' campaign', flush=True)
        raw = output/(mode+'.csv')
        with raw.open('w') as stdout, (output/(mode+'.stderr')).open('w') as stderr:
            command = [str(binary), '--smoke' if args.smoke else '--full']
            run_bounded(command, workspace, env, args.timeout, args.cpu_seconds, args.nice, stdout, stderr)
        with raw.open() as stream:
            rows = list(csv.DictReader(stream))
        expected_count = 175 if args.smoke else 455
        assert len(rows) == expected_count, 'incomplete campaign'
        groups = {}
        for row in rows:
            key = (row['stage'], row['profile'], int(row['bytes']))
            groups.setdefault(key, []).append(row)
        previous = {}
        for (stage, profile, size), values in sorted(groups.items()):
            assert sorted(int(v['round']) for v in values) == list(range(5))
            assert len({v['tokens'] for v in values}) == 1
            times = [float(v['microseconds']) for v in values]
            median = statistics.median(times)
            entry = dict(mode=mode, stage=stage, profile=profile, bytes=size,
                         tokens=int(values[0]['tokens']), median_us=median,
                         min_us=min(times), max_us=max(times),
                         mad_us=statistics.median(abs(t-median) for t in times))
            key = (stage, profile)
            if key in previous:
                entry['growth'] = median/previous[key]
            previous[key] = median
            summary.append(entry)
        print(mode+' passed: '+str(expected_count)+' samples and all ID/roundtrip assertions', flush=True)
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    metadata['complete'] = True
    (output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')


if __name__ == '__main__':
    main()
