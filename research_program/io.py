"""Pinned downloads, deterministic exports and execution provenance."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.request import urlopen

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def data_dir(study: str) -> Path:
    root = Path(os.environ.get('RESEARCH_DATA_DIR', Path.home() / '.cache/michael-gibb-research'))
    path = root / study
    path.mkdir(parents=True, exist_ok=True)
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url: str, destination: Path, expected_sha256: str | None = None, max_bytes: int = 250_000_000) -> Path:
    if not url.startswith('https://'):
        raise ValueError('Downloads require HTTPS')
    if destination.exists():
        if expected_sha256 and sha256(destination) != expected_sha256:
            raise ValueError(f'Cached file checksum mismatch: {destination.name}')
        return destination
    temporary = destination.with_suffix(destination.suffix + '.part')
    try:
        with urlopen(url, timeout=60) as response, temporary.open('wb') as output:
            size = 0
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise ValueError('Download exceeds the declared study size limit')
                output.write(chunk)
        if expected_sha256 and sha256(temporary) != expected_sha256:
            raise ValueError(f'Download checksum mismatch: {destination.name}')
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def normalized(value):
    if isinstance(value, dict):
        return {str(key): normalized(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [normalized(item) for item in value]
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if not np.isfinite(value):
            raise ValueError('Result contains a non-finite value')
        return round(float(value), 8)
    return value


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized(value), indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def provenance(study: str) -> dict:
    paths = sorted([*ROOT.joinpath('research_program').glob('*.py'), *ROOT.joinpath('studies', study).glob('*.py'), ROOT / 'studies' / study / 'config.json', ROOT / 'uv.lock'])
    relative = [str(path.relative_to(ROOT)) for path in paths]
    version = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', *relative], cwd=ROOT, text=True).strip()
    if len(version) != 40:
        raise ValueError('Commit the frozen protocol and code before evaluating')
    if subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', *relative], cwd=ROOT, text=True).strip():
        raise ValueError('Research source changed after its recorded commit')
    return {'code_version': version, 'source_sha256': {str(path.relative_to(ROOT)): sha256(path) for path in paths}}
