"""Exécuter les données gelées, un processus interprété par cas."""
import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--silex", default="silex", help="Commande ou chemin absolu du CLI")
parser.add_argument("--evidence", type=Path, help="Résultats JSON facultatifs")
args = parser.parse_args()
consumer = Path(__file__).resolve().parents[2]
probe = consumer / "OracleInterpreterProbe.sx"
results = []
# Création exclusive : préserver une éventuelle exécution concurrente.
with probe.open("x"):
    pass
try:
    for profile in sorted(consumer.glob("OracleParity*.sx")):
        source = profile.read_text()
        begin = source.index("    oracle_check(model,")
        end = source.index('    print("99 oracle cases passed")')
        checks = source[begin:end].strip().splitlines()
        assert len(checks) == 99 and all(line.strip().startswith("oracle_check(model,") for line in checks)
        for index, check in enumerate(checks):
            probe.write_text(source[:begin] + check + '\n    print("oracle case passed")\n}\n')
            command = [args.silex, "interpret", str(probe), "--nocache"]
            run = subprocess.run(command, cwd=Path.cwd(), env=os.environ.copy(), capture_output=True, text=True)
            results.append(dict(profile=profile.name, index=index, command=command,
                                returncode=run.returncode, stdout=run.stdout, stderr=run.stderr))
            if args.evidence:
                args.evidence.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
            if run.returncode or run.stdout != "oracle case passed\n":
                raise SystemExit(f"Échec {profile.name}:{index}: {run.returncode}\n{run.stdout}{run.stderr}")
            if index % 16 == 0:
                print(f"{profile.name}: {index + 1} cas vérifiés", flush=True)
        print(f"{profile.name}: 99 cas vérifiés", flush=True)
finally:
    probe.unlink()
print("594 cas interprétés vérifiés", flush=True)
