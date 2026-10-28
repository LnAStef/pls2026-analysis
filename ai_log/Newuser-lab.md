# AI + verification logs

**One file per person.** Name it after your GitHub account: `ai_log/<your-github-username>.md`.

The repository is shared with your group; this log is not. Keeping separate files means
you never merge anybody else's notes, and it is obvious who wrote what — the commits
touching `ai_log/<your-github-username>.md` should be authored by you.

Copy the block below into your own file and delete nothing else from this directory.

---

## <date> — <what you were building>

- **Prompt / ask:** <what you asked, or "wrote by hand">
- **What it produced:** <a line or two>
- **How you checked it:** <the specific check you ran — not "I read it">
- **What was wrong:** <bugs, hallucinations, or "nothing found">
- **Decision:** <accepted / edited / rejected — and why>

---

Record your one or two most significant AI uses each week — the ones where verification
actually mattered. Not every keystroke.

## Week04: 10.10.2026 - Estimate cell-type signatures

- **Prompt (duck.ai):** I have two csv files. One with cell_id and genes and one with cell_id and cell_type. I need a matrix S with mean expression of of each gene of each cell_type.
- **What it produced:**

import pandas as pd

expression = pd.read_csv("expression.csv")  # cell_id, gene1, gene2, ...
types = pd.read_csv("cell_types.csv")       # cell_id, cell_type

merged = expression.merge(types, on="cell_id", how="inner")

S = merged.groupby("cell_type").mean(numeric_only=True)
S = S.drop(columns=["cell_id"], errors="ignore")  # if cell_id was read as numeric

S.to_csv("mean_expression_by_cell_type.csv")

- **Check:** I wrote a two little data.frames corresponding the structure of reference_counts.csv and reference_labels.csv and run the proposed script on this data. I checked the results by hand. 
- **What was wrong:** The mean values of my test data were right. 
- **Decision:** I took the code and adapted it in order to have functions and to get the resulting matrix S with genes in rows and cell types in columns. With this code it is vice versa but I was not defining it in my prompt.



## Week05: 20.10.2026 - Characterisation test

- **Prompt (duck.ai):** 
That is what I have to do: A characterization test in tests/, with the golden output committed, that fails if the
program’s results change.

And that is what I already have:  

def output_hash(path):
    """Fingerprint the program's output, so that any change to it is detectable."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

GOLDEN = output_hash(RESULTS/"binned.csv")
print("golden:", GOLDEN)

def check_unchanged(label):
    """The characterization test: compare the output on disk with the golden output."""
    out = RESULTS/"binned.csv"
    if not out.exists():
        print(f"{label:<28} no output file at all — did the writer run?")
        return False
    now = output_hash(out)
    print(f"{label:<28} {'unchanged' if now == GOLDEN else 'CHANGED — stop and look'}")
    return now == GOLDEN

check_unchanged("before any refactoring")

- **What it produced:**
import hashlib
from pathlib import Path

RESULT = RESULTS / "binned.csv"
GOLDEN_SHA256 = "paste-the-reviewed-hash-here"

def test_binned_output_matches_golden():
    # Run the program here if the test is responsible for producing the output.
    assert RESULT.exists(), f"Expected output file not found: {RESULT}"

    actual = hashlib.sha256(RESULT.read_bytes()).hexdigest()
    assert actual == GOLDEN_SHA256, (
        f"binned.csv changed: expected {GOLDEN_SHA256}, got {actual}"
    )
Together with AI, I adapted the code. The final version was: 

import hashlib
from pathlib import Path


def output_hash(path):
    """Fingerprint the program's output, so that any change to it is detectable."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_output_matches_golden(path, golden):
    path = Path(path)
    golden = Path(golden)

    assert path.is_file(), f"Expected output file not found: {path}"
    assert golden.is_file(), f"Golden hash file not found: {golden}"

    expected = golden.read_text(encoding="utf-8").strip()
    actual = output_hash(path)

    assert actual == expected, (
        f"{path} changed: expected {expected}, got {actual}"
    )


- **Check:** I wrote a test code. Then I made a golden hash. After that, I changed the code in order to have a different output. Then I used test_output_matches_golden, and it successfully reported that the hashes are not identical, so the output changed.  

- **What was wrong:** I added the variables path and golden. 


- **Decision:** The final function worked. In our repository, another group member added a test_charaterisation.py. 



## Week06: 28.10.2026 - pytest --doctest-modules output interpretation

- **Prompt (duck.ai):** I run pytest --doctest-modules and asked AI what the output means.
- **What it produced:** One problem of my test_estimate_cell_type_signatures.py was:
This code runs at the top level of the test file, so pytest executes it while importing the file for collection. The traceback says the failure occurs inside load_reference_counts, when it calls pd.read_csv(path_ref_counts).

The likely issue is the value ultimately used as path_ref_counts: it’s a method rather than a path or file-like object. 

- **Check:** 

