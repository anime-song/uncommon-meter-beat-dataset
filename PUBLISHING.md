# Publishing Guide

This repository is already close to publishable as an annotation-only dataset.

## Recommended Release Strategy

Publish the dataset without `audios/`.

Why:

- The current documentation already says audio is not distributed.
- `audios/` contains MP3 files that are likely subject to third-party rights.
- The annotation-only subset is small and easy to host.

Current local size snapshot:

- Annotation-only release: about 5.3 MB
- `audios/`: about 844 MB

## What To Publish

Recommended public files:

- `beats/`
- `parsed_beats/`
- `metadata.csv`
- `output_graphs/`
- `README.md`
- `README.ja.md`
- `DATASET_CARD.md`
- `DATASET_CARD.ja.md`
- `LICENSE`
- `*.py`
- `run.bat`

Do not publish unless you have explicit redistribution rights:

- `audios/`

The root `.gitignore` already excludes `audios/` and `__pycache__/`.

## Publish To GitHub

1. Create a new public repository on GitHub, for example:

   `https://github.com/<your-user>/uncommon-meter-beat-dataset`

2. Run the following commands locally from this directory:

```powershell
cd F:\BeatAnnotation
git init
git add .
git status --short
git commit -m "Initial dataset release"
git branch -M main
git remote add origin https://github.com/<your-user>/uncommon-meter-beat-dataset.git
git push -u origin main
```

Notes:

- `git add .` is safe here because `.gitignore` already excludes `audios/`.
- Check `git status --short` before committing so you do not accidentally publish extra local files.

## Publish To Hugging Face

### Option A: Push the same Git repository

1. Create a public dataset repository on Hugging Face:

   `https://huggingface.co/new-dataset`

2. Add a second remote and push:

```powershell
cd F:\BeatAnnotation
git remote add hf https://huggingface.co/datasets/<your-user>/uncommon-meter-beat-dataset
git push hf main
```

Notes:

- Hugging Face dataset repos use Git, so the same tracked files can be pushed there.
- When prompted, use your Hugging Face username and a write-enabled access token.
- `README.md` becomes the dataset card shown on the dataset page.

### Option B: Upload with Python

Use this if you do not want to manage a second Git remote.

```powershell
pip install -U huggingface_hub
```

```python
from huggingface_hub import HfApi

repo_id = "<your-user>/uncommon-meter-beat-dataset"
api = HfApi()

api.create_repo(repo_id=repo_id, repo_type="dataset", private=False, exist_ok=True)
api.upload_folder(
    repo_id=repo_id,
    repo_type="dataset",
    folder_path="F:/BeatAnnotation",
    ignore_patterns=[
        "audios/*",
        "__pycache__/*",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".venv/*",
        "venv/*",
    ],
)
```

## Recommended Metadata On Both Platforms

Use the same dataset name on both platforms:

- `uncommon-meter-beat-dataset`

Short description:

`Annotation-only beat/downbeat and time-signature dataset focused on odd meter and meter changes.`

Suggested topics/tags:

- beat tracking
- downbeat tracking
- music information retrieval
- rhythm
- time signature
- odd meter
- changing meter

## Before You Make It Public

Check these items:

- The public copy does not include `audios/`.
- `README.md` and `DATASET_CARD.md` match what is actually distributed.
- `metadata.csv` does not contain anything private.
- The license is the one you want for the annotations and derived files.
- Filenames and links render correctly on GitHub and Hugging Face.

## If You Want To Publish Audio Too

Only do that if you have the legal right to redistribute every track.

If you decide to release audio:

- Update `README.md` and `DATASET_CARD.md` because they currently state that audio is excluded.
- Prefer a separate audio release or separate repository.
- Hugging Face is generally a better home for audio assets than GitHub.
- GitHub has hard per-file limits and recommends keeping repositories small.

If rights are unclear, publish annotations and metadata only.
