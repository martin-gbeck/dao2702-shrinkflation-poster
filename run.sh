#!/bin/sh
# Rebuild the notebook from shrinkflation.py, execute it, print its text output
cd "$(dirname "$0")"
../.venv/bin/jupytext --to ipynb shrinkflation.py -o shrinkflation.ipynb >/dev/null
IPYTHONDIR="$(mktemp -d)" ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace shrinkflation.ipynb 2>&1 | grep -E "Error" | tail -3
../.venv/bin/python -I -c "
import json
nb = json.load(open('shrinkflation.ipynb'))
for c in nb['cells']:
    if c['cell_type'] != 'code': continue
    for o in c.get('outputs', []):
        if o.get('output_type') == 'stream': print(''.join(o['text']))
        elif o.get('output_type') == 'error': print('ERR', o['ename'], o['evalue'])
        elif 'data' in o and 'text/plain' in o['data'] and 'image/png' not in o['data']: print(''.join(o['data']['text/plain'])[:1500])
"
