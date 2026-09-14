"""Copy airas-eval's numbers into metrics.json. Computes nothing itself."""

import json
import sys
from pathlib import Path


def _argv(key: str, default: str) -> str:
    for arg in sys.argv[1:]:
        k, sep, v = arg.partition("=")
        if sep and k == key:
            return v
    return default


def main() -> None:
    results_dir = Path(_argv("results_dir", ".research/results"))
    # Hydra list syntax, quoted or not: '["a","b"]' or [a,b].
    run_ids = [
        item.strip().strip("\"'")
        for item in _argv("run_ids", "[]").strip().strip("[]").split(",")
        if item.strip()
    ]
    for run_id in run_ids:
        run_dir = results_dir / run_id
        metrics: dict[str, float] = {}
        for report_path in sorted((run_dir / "evaluation").glob("*.json")):
            report = json.loads(report_path.read_text())
            metrics.update({k: float(v) for k, v in report["metrics"].items()})
        (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
        print(f"wrote {run_dir / 'metrics.json'}: {metrics}")


if __name__ == "__main__":
    main()
