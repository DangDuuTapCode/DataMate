# Training and reproducibility

This baseline performs no model training, fine-tuning, or synthetic-data generation. It has no trainable weights or training entry point. Inference is a deterministic Python rule engine and does not read this directory.

The official training archive is copied to `training_code/data/train.zip` in the final Docker build context as required by the DataMate Docker Guide. `data_manifest.json` records its source, checksum, size, and dataset inventory. The archive is retained only for reproducibility and organizer verification; runtime reads test inputs exclusively from `/data`.

To reproduce the software checks before building:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
```

There are no training dependencies or training command because no training was performed. Runtime dependencies are pinned in the top-level `requirements.txt`.
