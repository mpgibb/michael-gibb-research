"""Verify the archived publisher files and reconcile policy/claim grain."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
import rdata
import requests

from research_program.io import data_dir, sha256

CONFIG = json.loads(Path(__file__).with_name('config.json').read_text())


def source_archive():
    path = data_dir('S31') / 'CASdatasets_1.2-0.zip'
    if not path.exists():
        temporary = path.with_suffix('.part')
        try:
            with requests.get(CONFIG['source_url'], stream=True, timeout=(30, 60)) as response:
                response.raise_for_status()
                with temporary.open('wb') as output:
                    size = 0
                    for chunk in response.iter_content(1024 * 1024):
                        size += len(chunk)
                        if size > 220_000_000:
                            raise ValueError('Publisher archive exceeds declared bound')
                        output.write(chunk)
            if sha256(temporary) != CONFIG['archive_sha256']:
                raise ValueError('Publisher archive checksum mismatch')
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    if sha256(path) != CONFIG['archive_sha256']:
        raise ValueError('Cached publisher archive checksum mismatch')
    return path


def join_claims(frequency, severity):
    frequency = frequency.copy()
    severity = severity.copy()
    frequency['IDpol'] = frequency.IDpol.astype(str)
    severity['IDpol'] = severity.IDpol.astype(str)
    if frequency.isna().any().any() or severity.isna().any().any():
        raise ValueError('Unexpected missing source field')
    if frequency.IDpol.duplicated().any() or not severity.IDpol.isin(frequency.IDpol).all():
        raise ValueError('Source policy keys do not reconcile')
    if (frequency.Exposure <= 0).any() or (severity.ClaimAmount <= 0).any():
        raise ValueError('Invalid exposure or severity')
    if not np.array_equal(frequency.ClaimNb, frequency.ClaimNb.astype(int)):
        raise ValueError('Claim counts must be integral')
    severity['CappedAmount'] = severity.ClaimAmount.clip(upper=CONFIG['claim_cap_eur'])
    aggregate = severity.groupby('IDpol', sort=False).agg(
        ClaimRows=('ClaimAmount', 'size'), Loss=('ClaimAmount', 'sum'),
        CappedLoss=('CappedAmount', 'sum'))
    joined = frequency.join(aggregate, on='IDpol', validate='one_to_one')
    joined[['ClaimRows', 'Loss', 'CappedLoss']] = joined[['ClaimRows', 'Loss', 'CappedLoss']].fillna(0)
    if not np.array_equal(joined.ClaimNb, joined.ClaimRows):
        raise ValueError('Policy counts disagree with source severity rows')
    return joined


def split_masks(ids):
    values = np.array([int.from_bytes(hashlib.sha256((CONFIG['split_salt'] + str(i)).encode()).digest()[:8], 'big') / 2**64 for i in ids])
    return values < .6, (values >= .6) & (values < .8), values >= .8


def ingest():
    frames = {}
    with ZipFile(source_archive()) as archive:
        for name, expected in CONFIG['files'].items():
            raw = archive.read(f'CASdatasets/data/{name}.rda')
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError('Extracted R source checksum mismatch')
            path = data_dir('S31') / f'release-{name}.rda'
            path.write_bytes(raw)
            frames[name] = rdata.read_rda(path)[name]
    frequency, severity = frames['freMTPL2freq'], frames['freMTPL2sev']
    joined = join_claims(frequency, severity)
    if (len(joined), len(severity), int(joined.ClaimNb.sum())) != (677991, 26444, 26444):
        raise ValueError('Archived cohort changed')
    amounts = severity.ClaimAmount.to_numpy(float)
    audit = {
        'policies': len(joined), 'claims': len(severity), 'claiming_policies': int((joined.ClaimNb > 0).sum()),
        'missing_cells': 0, 'duplicate_frequency_rows': int(frequency.duplicated().sum()),
        'repeated_severity_rows_retained': int(severity.duplicated().sum()), 'unmatched_claims': 0,
        'count_disagreements': 0, 'exposures_over_one_year': int((joined.Exposure > 1).sum()),
        'exposure_years': float(joined.Exposure.sum()), 'total_loss_eur': float(amounts.sum()),
        'maximum_claim_eur': float(amounts.max()), 'claims_above_cap': int((amounts > CONFIG['claim_cap_eur']).sum()),
        'uncapped_loss_above_cap_eur': float(amounts[amounts > CONFIG['claim_cap_eur']].sum()),
        'capped_total_loss_eur': float(np.minimum(amounts, CONFIG['claim_cap_eur']).sum()),
        'largest_claim_share_of_loss': float(amounts.max() / amounts.sum()),
        'top_one_percent_claim_loss_share': float(np.sort(amounts)[-int(np.ceil(len(amounts) * .01)):].sum() / amounts.sum()),
    }
    return joined.reset_index(drop=True), audit
