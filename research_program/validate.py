"""Validate program states and research artifacts before publication."""
import json
from pathlib import Path
import re

import jsonschema

from .io import ROOT


def validate_result(result: dict) -> None:
    jsonschema.validate(result, json.loads((ROOT / 'schemas/result.schema.json').read_text()))
    counts = result['samples']
    if counts['test'] < 1:
        raise ValueError('An evaluated result needs a nonempty evaluation cohort')
    for metric in result['metrics']:
        if metric.get('lower') is not None and metric['lower'] > metric['upper']:
            raise ValueError('Inverted uncertainty interval')
    if not result['data']['sha256'] or not result['source_sha256']:
        raise ValueError('Missing data or source provenance')


def validate_catalog(records: list) -> None:
    ids = [item['id'] for item in records]
    if len(ids) != 60 or set(ids) != {f'S{i:02}' for i in range(1, 61)}:
        raise ValueError('Catalog must account for each study exactly once')
    if len({item['slug'] for item in records}) != 60 or len({item['industry'] for item in records}) != 20:
        raise ValueError('Invalid catalog identities or industries')
    for item in records:
        if item['execution_status'] not in ['planned', 'data_ready', 'baseline_complete', 'evaluated', 'blocked']:
            raise ValueError('Unknown execution status')
        if item['publication_status'] not in ['unpublished', 'draft', 'published', 'withheld']:
            raise ValueError('Unknown publication status')
        if item['publication_status'] == 'published':
            if item['execution_status'] != 'evaluated' or not item['result_path'] or not item['code_url'] or not item['published_url']:
                raise ValueError('Publication requires an evaluated result and real links')
            path = (ROOT / item['result_path']).resolve()
            if not path.is_relative_to(ROOT / 'studies'):
                raise ValueError('Result path must remain within the study repository')
            result = json.loads(path.read_text())
            validate_result(result)
            if result['study_id'] != item['id']:
                raise ValueError('Study/result identity mismatch')


if __name__ == '__main__':
    records = json.loads((ROOT / 'catalog/studies.json').read_text())
    validate_catalog(records)
    for path in ROOT.glob('studies/*/results/result.json'):
        validate_result(json.loads(path.read_text()))
    print('Catalog and evaluated artifacts validated.')
