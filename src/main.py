"""Toy experiment for the AIRAS execution smoke test: no training, no GPU.

Generates deterministic reference labels and a predictor that is wrong on
every `error_every`-th example, and writes the raw predictions for airas-eval.
"""

import json
import math
from pathlib import Path

import hydra
from omegaconf import DictConfig


@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig) -> None:
    mode = cfg.mode
    run = cfg.run
    n = int(run.n_examples[mode])
    reference = [i % int(run.n_classes) for i in range(n)]
    predicted = [
        (label + 1) % int(run.n_classes) if i % int(run.error_every) == 0 else label
        for i, label in enumerate(reference)
    ]

    out_dir = Path(cfg.results_dir) / run.run_id / "eval_inputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "classification.json").write_text(
        json.dumps({"predicted_labels": predicted, "reference_labels": reference})
    )

    if mode in ("sanity", "pilot"):
        tag = mode.upper()
        agreement = sum(p == r for p, r in zip(predicted, reference)) / n
        distinct = len(set(predicted))
        ok = n >= 5 and distinct >= 2 and math.isfinite(agreement)
        if ok:
            print(f"{tag}_VALIDATION: PASS")
            print(
                f"{tag}_VALIDATION_SUMMARY: "
                + json.dumps({"n_examples": n, "distinct_predictions": distinct})
            )
        else:
            print(f"{tag}_VALIDATION: FAIL reason=degenerate_outputs")


if __name__ == "__main__":
    main()
