"""Run the complete spatial-decode analysis with one command.

    python scripts/run_analysis.py --config config/default.yaml \
        --data-dir data/raw/reference_dataset/dataset --out-dir results

`python scripts/run_analysis.py --help` lists every option. The logic lives in
spatial_decode/cli.py so that it is importable and tested.
"""

import sys

from spatial_decode.cli import main

if __name__ == "__main__":
    sys.exit(main())
