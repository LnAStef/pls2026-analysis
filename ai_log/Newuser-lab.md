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

## Week07: 03.11.2026 - Optimise src/spatial_decode/estimate_cell_type_signatures.py and its test in tests/

- **Prompt (duck.ai):** I run pytest and showed AI the output concerning my files. Then we discussed it. 
- **What it produced:** In summary, it told me that I was not coherent in my program and its test. Some examples: I used the name ref_cell in my test but it was expecting cell_id. Then, I changed the name of ma test, so that has the same name as the program (an additional s after signatures). It prompted me to adapt my cell_id_match function in order to return a boolean and not a None. 
- **Check:** I run pytest tests/test_estimate_cell_type_signatures.py. 
- **What was wrong:** The column name of the actual and the expected matrix didn't match. So, I added expected.columns.name = "cell_type". 
- **Decision:** I run pytest again. It passed. 


## Week07: 03.11.2026 - Add docstrings to my functions
- **Prompt (duck.ai):** I fed AI my code and asked it to add docstrings. 
- **What it produced:** It proposed docstrings to all of my functions. One example: 
def load_reference_counts(path_ref_counts):
    """Load the reference count table from a CSV file.

    Parameters
    ----------
    path_ref_counts : str or path-like
        Path to the CSV file containing reference counts.

    Returns
    -------
    pandas.DataFrame
        The count table as read by pandas.
    """
    ref_counts = pd.read_csv(path_ref_counts)
    return ref_counts
- **Check:** No specific check other than reading.
- **What was wrong/Decision:** I think nothing was "wrong" but I adapted and shortened the text slightly. 



## Week07: 03.11.2026 - Add doctest to two functions

- **Prompt (duck.ai):** I handed in my code of estimate_cell_type_signatures.py and asked AI to write me two doctests. 
- **What it produced:** It added to doctests. 
 Examples:
        >>> transcripts = pd.DataFrame({"cell_id": ["c1", "c2"]})
        >>> labels = pd.DataFrame({"cell_id": ["c1", "c2"]})
        >>> cell_id_match(transcripts, labels)
        True


    Examples:
        >>> merged = pd.DataFrame({
        ...     "cell_type": ["A", "A", "B"],
        ...     "Gene1": [2, 4, 6],
        ... })
        >>> S = mean_expression_matrix(merged)
        >>> S.loc["Gene1", "A"]
        3.0

- **Check:** I run: python -m pytest --doctest-modules src/spatial_decode/estimate_cell_type_signatures.py. The second doctest failed.
- **What was wrong:** The second doctest gave an error message because panda returned a float which was not recognized by doctest. 
- **Decision:** I changed this line >>> S.loc["Gene1", "A"] to >>> float(S.loc["Gene1", "A"]) and accepted the two proposed doctests. 


