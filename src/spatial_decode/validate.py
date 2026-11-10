"""Check a dataset against the Data Contract before anything else reads it.

`validate_dataset(path)` implements the contract's minimal conformance checklist (§7).
It is called once, at the boundary where a dataset enters the program — the first line of
`load_dataset()` — so every function downstream may assume well-formed input.

The checks run in four layers, each catching faults the one before cannot see:

1. presence  — the required files and folders exist;
2. schema    — the required columns exist and have the right types;
3. values    — every number is possible (non-negative integer counts, supported version);
4. invariants across rows and files — full grid, µm coordinates agree with the indices,
   the same square_ids in the same order, reference covers the tissue, composition sums
   to counts.

The first violation stops the run with a message that names the file, the offending
value, where it is, and the contract section it breaks. Nothing is repaired or defaulted.

`ground_truth/composition.csv` is opened here only to check the consistency requirement
of §3.6 / §7. Nothing read from `ground_truth/` leaves this module: the function returns
None, so inference code never sees the answer key (§2).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

SUPPORTED_CONTRACT_VERSION = "1.0"

COORDINATE_COLUMNS = ["square_id", "array_row", "array_col", "x_um", "y_um"]
REFERENCE_LABEL_COLUMNS = ["cell_id", "cell_type"]
COMPOSITION_COLUMNS = ["square_id", "cell_type", "n_transcripts"]

# µm coordinates are written as floats; allow for their rounding, nothing more.
COORDINATE_ATOL_UM = 1e-6

_PARTNER_HINT = (
    " If this dataset came from a partner group, open an issue on their repository "
    "quoting this message."
)


class ContractViolation(ValueError):
    """A dataset does not conform to the Data Contract.

    Subclasses ValueError, so callers that catch ValueError still catch it. Missing files
    raise FileNotFoundError instead, so the two kinds of fault can be told apart.
    """


def _violation(where, found, required, section):
    """Build a ContractViolation with the four parts a useful message needs."""
    return ContractViolation(
        f"{where}: {found}; the contract requires {required} (§{section})."
        + _PARTNER_HINT
    )


def _line(index):
    """CSV line number of a 0-based data row (line 1 is the header)."""
    return int(index) + 2


def validate_dataset(path):
    """Check that a dataset directory conforms to Data Contract v1.0.

    Args:
        path: dataset directory (the folder holding metadata.json).

    Returns:
        None. Silence means the dataset conforms.

    Raises:
        FileNotFoundError: a required file or folder is missing.
        ContractViolation: anything else in the §7 checklist fails.
    """
    root = Path(path).expanduser()
    name = root.name

    def label(relative):
        return f"{name}/{relative}"

    # ---- layer 1: presence -----------------------------------------------------------
    if not root.is_dir():
        raise FileNotFoundError(
            f"dataset directory {root} does not exist or is not a directory; "
            "pass the folder that contains metadata.json (Data Contract §2)."
        )
    required = [
        "metadata.json",
        "coordinates.csv",
        "counts.csv",
        "reference/reference_counts.csv",
        "reference/reference_labels.csv",
        "ground_truth/composition.csv",
    ]
    missing = [relative for relative in required if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError(
            f"{name}: required file(s) missing: {', '.join(missing)}. The contract's "
            "directory layout requires them (§2); a missing file usually means an "
            "interrupted or partial write." + _PARTNER_HINT
        )

    # ---- metadata.json ---------------------------------------------------------------
    metadata = _read_metadata(root / "metadata.json", label("metadata.json"))
    square_size_um = metadata["square_size_um"]

    # ---- layer 2 + 3: schema and values, file by file --------------------------------
    coordinates = _read_csv(root / "coordinates.csv", label("coordinates.csv"))
    _require_columns(coordinates, COORDINATE_COLUMNS, label("coordinates.csv"), "3.2")
    _require_strings(coordinates, "square_id", label("coordinates.csv"), "3.2")
    _require_unique(coordinates, "square_id", label("coordinates.csv"), "3.2")
    for column in ("array_row", "array_col"):
        _require_non_negative_integers(
            coordinates, [column], label("coordinates.csv"), "3.2", "square_id"
        )
    for column in ("x_um", "y_um"):
        _require_floats(coordinates, column, label("coordinates.csv"))

    counts = _read_csv(root / "counts.csv", label("counts.csv"))
    _require_first_column(counts, "square_id", label("counts.csv"), "3.3")
    genes = list(counts.columns[1:])
    if not genes:
        raise _violation(
            label("counts.csv"),
            "no gene columns after square_id",
            "one column per gene after square_id",
            "3.3",
        )
    _require_strings(counts, "square_id", label("counts.csv"), "3.3")
    _require_non_negative_integers(counts, genes, label("counts.csv"), "3.3", "square_id")

    ref_counts = _read_csv(
        root / "reference/reference_counts.csv", label("reference/reference_counts.csv")
    )
    ref_counts_label = label("reference/reference_counts.csv")
    _require_first_column(ref_counts, "cell_id", ref_counts_label, "3.4")
    ref_genes = list(ref_counts.columns[1:])
    if ref_genes != genes:
        raise _violation(
            ref_counts_label,
            f"gene columns differ from counts.csv ({_first_difference(genes, ref_genes)})",
            "the same gene columns as counts.csv, in the same order",
            "3.4",
        )
    _require_unique(ref_counts, "cell_id", ref_counts_label, "3.4")
    _require_non_negative_integers(ref_counts, ref_genes, ref_counts_label, "3.4", "cell_id")

    ref_labels_label = label("reference/reference_labels.csv")
    ref_labels = _read_csv(root / "reference/reference_labels.csv", ref_labels_label)
    _require_columns(ref_labels, REFERENCE_LABEL_COLUMNS, ref_labels_label, "3.4")
    _require_strings(ref_labels, "cell_type", ref_labels_label, "3.4")

    composition_label = label("ground_truth/composition.csv")
    composition = _read_csv(root / "ground_truth/composition.csv", composition_label)
    _require_columns(composition, COMPOSITION_COLUMNS, composition_label, "3.6")
    _require_non_negative_integers(
        composition, ["n_transcripts"], composition_label, "3.6", "square_id"
    )

    # ---- layer 4: invariants across rows and files -----------------------------------
    _check_grid(coordinates, metadata, label("coordinates.csv"))
    _check_um_coordinates(coordinates, square_size_um, label("coordinates.csv"))
    _check_same_square_ids(coordinates, counts, name)
    _check_reference(ref_counts, ref_labels, composition, metadata, name)
    _check_composition_sums(composition, counts, genes, name)


# ---------------------------------------------------------------------------------------
# reading


def _read_metadata(path, where):
    try:
        metadata = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise _violation(
            where,
            f"not valid JSON ({error.msg} at line {error.lineno}, column {error.colno})",
            "a valid JSON object",
            "3.1",
        ) from error
    if not isinstance(metadata, dict):
        raise _violation(
            where, f"top level is a {type(metadata).__name__}", "a JSON object", "3.1"
        )

    if "contract_version" not in metadata:
        raise _violation(
            where, "key 'contract_version' is missing", "a 'contract_version' key", "3.1"
        )
    version = metadata["contract_version"]
    if version != SUPPORTED_CONTRACT_VERSION:
        raise _violation(
            where,
            f"contract_version is {version!r}, which this program does not support",
            f'contract_version == "{SUPPORTED_CONTRACT_VERSION}"',
            "3.1, §7",
        )

    if "square_size_um" not in metadata:
        raise _violation(
            where, "key 'square_size_um' is missing", "a 'square_size_um' key", "3.1"
        )
    size = metadata["square_size_um"]
    if isinstance(size, bool) or not isinstance(size, (int, float)) or not size > 0:
        raise _violation(
            where,
            f"square_size_um is {size!r}",
            "square_size_um to be a positive number of micrometres",
            "3.1",
        )
    return metadata


def _read_csv(path, where):
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError as error:
        raise _violation(where, "the file is empty", "a header row", "3") from error
    except pd.errors.ParserError as error:
        raise _violation(
            where, f"cannot be parsed as CSV ({error})", "well-formed CSV", "3"
        ) from error


# ---------------------------------------------------------------------------------------
# schema and values


def _require_columns(table, columns, where, section):
    absent = [column for column in columns if column not in table.columns]
    if absent:
        raise _violation(
            where,
            f"missing required column(s) {', '.join(repr(c) for c in absent)} "
            f"(found columns: {', '.join(map(str, table.columns))})",
            f"the columns {', '.join(columns)}",
            section,
        )


def _require_first_column(table, column, where, section):
    if len(table.columns) == 0 or table.columns[0] != column:
        first = table.columns[0] if len(table.columns) else "nothing"
        raise _violation(
            where,
            f"missing required column {column!r} as the first column (found {first!r})",
            f"the first column to be {column!r}",
            section,
        )


def _require_strings(table, column, where, section):
    blank = table[column].isna() | (table[column].astype(str).str.strip() == "")
    if blank.any():
        index = blank.idxmax()
        raise _violation(
            f"{where}, line {_line(index)}",
            f"{column} is empty",
            f"every {column} to be a non-empty string",
            section,
        )


def _require_unique(table, column, where, section):
    duplicated = table[column].duplicated()
    if duplicated.any():
        index = duplicated.idxmax()
        raise _violation(
            f"{where}, line {_line(index)}",
            f"{column} {table.at[index, column]!r} appears more than once",
            f"each {column} to be unique",
            section,
        )


def _require_non_negative_integers(table, columns, where, section, id_column):
    """Every value in `columns` must be a non-negative integer; report the first that isn't."""
    for column in columns:
        values = table[column]
        numeric = pd.to_numeric(values, errors="coerce")
        bad = numeric.isna()
        if not bad.any():
            bad = (numeric < 0) | (numeric != np.floor(numeric))
        if bad.any():
            index = bad.idxmax()
            raise _violation(
                f"{where}, line {_line(index)} ({id_column} {table.at[index, id_column]})",
                f"{column} has value {_show(values.iloc[index])}",
                "non-negative integers",
                section,
            )


def _require_floats(table, column, where):
    numeric = pd.to_numeric(table[column], errors="coerce")
    if numeric.isna().any():
        index = numeric.isna().idxmax()
        raise _violation(
            f"{where}, line {_line(index)} (square_id {table.at[index, 'square_id']})",
            f"{column} has value {_show(table[column].iloc[index])}",
            f"{column} to be a number in µm",
            "3.2",
        )


# ---------------------------------------------------------------------------------------
# invariants


def _check_grid(coordinates, metadata, where):
    """array_row / array_col must cover the full grid exactly once."""
    rows = coordinates["array_row"].astype(int)
    cols = coordinates["array_col"].astype(int)

    pairs = pd.Series(list(zip(rows, cols, strict=True)))
    duplicated = pairs.duplicated()
    if duplicated.any():
        index = duplicated.idxmax()
        first = pairs[pairs == pairs[index]].index[0]
        raise _violation(
            f"{where}, line {_line(index)} (square_id {coordinates.at[index, 'square_id']})",
            f"grid position (array_row={rows[index]}, array_col={cols[index]}) is a "
            f"duplicate of line {_line(first)}",
            "every grid position exactly once, without gaps or duplicates",
            "3.2, §7",
        )

    grid = metadata.get("grid") or {}
    n_rows = grid.get("n_rows", int(rows.max()) + 1)
    n_cols = grid.get("n_cols", int(cols.max()) + 1)

    outside = (rows >= n_rows) | (cols >= n_cols)
    if outside.any():
        index = outside.idxmax()
        raise _violation(
            f"{where}, line {_line(index)} (square_id {coordinates.at[index, 'square_id']})",
            f"grid position (array_row={rows[index]}, array_col={cols[index]}) lies "
            f"outside the {n_rows} x {n_cols} grid declared in metadata.json",
            "indices inside the declared grid",
            "3.2, §7",
        )

    if len(coordinates) != n_rows * n_cols:
        present = set(pairs)
        gap = next(
            (r, c) for r in range(n_rows) for c in range(n_cols) if (r, c) not in present
        )
        raise _violation(
            where,
            f"{len(coordinates)} squares for a {n_rows} x {n_cols} grid; "
            f"first gap at array_row={gap[0]}, array_col={gap[1]}",
            "every grid position exactly once, without gaps or duplicates",
            "3.2, §7",
        )


def _check_um_coordinates(coordinates, square_size_um, where):
    """x_um = (array_col + 0.5) * square_size_um, and likewise y_um from array_row."""
    for column, index_column in (("x_um", "array_col"), ("y_um", "array_row")):
        expected = (coordinates[index_column] + 0.5) * square_size_um
        found = coordinates[column].astype(float)
        wrong = ~np.isclose(found, expected, rtol=0.0, atol=COORDINATE_ATOL_UM)
        if wrong.any():
            index = int(np.argmax(wrong))
            raise _violation(
                f"{where}, line {_line(index)} "
                f"(square_id {coordinates.at[index, 'square_id']})",
                f"{column} is {found.iloc[index]} but {index_column}="
                f"{coordinates.at[index, index_column]} with square_size_um="
                f"{square_size_um} gives {expected.iloc[index]}",
                f"{column} = ({index_column} + 0.5) * square_size_um",
                "3.2, §7",
            )


def _check_same_square_ids(coordinates, counts, name):
    """counts.csv must list exactly the squares of coordinates.csv, in the same order."""
    coordinate_ids = coordinates["square_id"].astype(str)
    count_ids = counts["square_id"].astype(str)

    only_in_counts = sorted(set(count_ids) - set(coordinate_ids))
    only_in_coordinates = sorted(set(coordinate_ids) - set(count_ids))
    if only_in_counts or only_in_coordinates:
        raise _violation(
            f"{name}/counts.csv vs {name}/coordinates.csv",
            "square_ids differ: "
            f"{len(only_in_counts)} only in counts.csv {_preview(only_in_counts)}, "
            f"{len(only_in_coordinates)} only in coordinates.csv "
            f"{_preview(only_in_coordinates)}",
            "the same set of square_ids in both files",
            "3.3, §7",
        )

    if len(count_ids) != len(coordinate_ids):
        raise _violation(
            f"{name}/counts.csv",
            f"{len(count_ids)} rows for {len(coordinate_ids)} squares in coordinates.csv",
            "one row per square",
            "3.3",
        )

    mismatch = (count_ids.to_numpy() != coordinate_ids.to_numpy())
    if mismatch.any():
        index = int(np.argmax(mismatch))
        raise _violation(
            f"{name}/counts.csv, line {_line(index)}",
            f"square_id is {count_ids.iloc[index]!r} where coordinates.csv has "
            f"{coordinate_ids.iloc[index]!r}: same square_ids, different order",
            "counts.csv rows in the same order as coordinates.csv",
            "3.3, §7",
        )


def _check_reference(ref_counts, ref_labels, composition, metadata, name):
    """reference/ is labelled and covers every cell type in the tissue."""
    counted = set(ref_counts["cell_id"].astype(str))
    labelled = set(ref_labels["cell_id"].astype(str))

    unlabelled = sorted(counted - labelled)
    if unlabelled:
        raise _violation(
            f"{name}/reference/reference_labels.csv",
            f"{len(unlabelled)} reference cell(s) have no label {_preview(unlabelled)}",
            "a cell_type label for every cell in reference_counts.csv",
            "3.4, §7",
        )
    unknown = sorted(labelled - counted)
    if unknown:
        raise _violation(
            f"{name}/reference/reference_labels.csv",
            f"{len(unknown)} label(s) for cells absent from reference_counts.csv "
            f"{_preview(unknown)}",
            "labels only for cells in reference_counts.csv",
            "3.4",
        )
    if ref_labels["cell_id"].duplicated().any():
        index = ref_labels["cell_id"].duplicated().idxmax()
        raise _violation(
            f"{name}/reference/reference_labels.csv, line {_line(index)}",
            f"cell_id {ref_labels.at[index, 'cell_id']!r} is labelled more than once",
            "exactly one label per reference cell",
            "3.4",
        )

    tissue_types = set(composition["cell_type"].astype(str))
    tissue_types |= {str(t) for t in metadata.get("cell_types", [])}
    reference_types = set(ref_labels["cell_type"].astype(str))
    uncovered = sorted(tissue_types - reference_types)
    if uncovered:
        raise _violation(
            f"{name}/reference/reference_labels.csv",
            f"no reference cells of type(s) {', '.join(uncovered)} "
            f"(reference has: {', '.join(sorted(reference_types))})",
            "reference cells for every cell type in the tissue",
            "3.4, §7",
        )


def _check_composition_sums(composition, counts, genes, name):
    """Per square, the per-type transcript counts sum to the square's total in counts.csv.

    A (square_id, cell_type) pair absent from composition.csv contributed zero (§3.6), so a
    square with no rows there is consistent exactly when its counts.csv total is zero.
    """
    known = set(counts["square_id"].astype(str))
    stray = composition.loc[~composition["square_id"].astype(str).isin(known), "square_id"]
    if len(stray):
        index = stray.index[0]
        raise _violation(
            f"{name}/ground_truth/composition.csv, line {_line(index)}",
            f"square_id {stray.iloc[0]!r} does not appear in counts.csv or coordinates.csv",
            "square_ids consistent across all files",
            "§7",
        )

    totals = counts[genes].astype("int64").sum(axis=1)
    totals.index = counts["square_id"].astype(str)
    truth = (
        composition.assign(square_id=composition["square_id"].astype(str))
        .groupby("square_id")["n_transcripts"]
        .sum()
        .astype("int64")
        .reindex(totals.index, fill_value=0)  # absence means zero (§3.6)
    )
    wrong = truth != totals
    if wrong.any():
        square = wrong.idxmax()
        raise _violation(
            f"{name}/ground_truth/composition.csv vs {name}/counts.csv "
            f"(square_id {square})",
            f"per-type n_transcripts sum to {truth[square]} but the square's total in "
            f"counts.csv is {totals[square]} ({int(wrong.sum())} square(s) disagree)",
            "each square's per-type transcript counts to sum to its total in counts.csv",
            "3.6, §7",
        )


# ---------------------------------------------------------------------------------------
# message helpers


def _show(value):
    """A value as a person would write it: -7, 1.5, 'abc' (not np.int64(-7))."""
    if isinstance(value, np.generic):
        value = value.item()
    return repr(value) if isinstance(value, str) else str(value)


def _preview(items, limit=3):
    shown = ", ".join(map(str, items[:limit]))
    more = ", ..." if len(items) > limit else ""
    return f"(e.g. {shown}{more})" if items else ""


def _first_difference(expected, found):
    if len(expected) != len(found):
        return f"{len(found)} gene columns, counts.csv has {len(expected)}"
    for position, (a, b) in enumerate(zip(expected, found, strict=True)):
        if a != b:
            return f"column {position + 2} is {b!r}, counts.csv has {a!r}"
    return "identical"
