"""Functions for spatial binning."""


def bin_counts(counts, coordinates, bin_size_um, square_size_um):
    """Sum square-level gene counts into larger spatial bins."""
    bins_per_side = bin_size_um / square_size_um

    if not bins_per_side.is_integer():
        raise ValueError(
            "bin_size_um must be an integer multiple of square_size_um"
        )

    k = int(bins_per_side)

    if k < 1:
        raise ValueError(
            "bin_size_um must be greater than or equal to square_size_um"
        )

    gene_columns = [
        column
        for column in counts.columns
        if column != "square_id"
    ]

    combined = coordinates[
        ["square_id", "array_row", "array_col"]
    ].merge(
        counts,
        on="square_id",
        how="inner",
        validate="one_to_one",
    )

    combined["bin_row"] = combined["array_row"] // k
    combined["bin_col"] = combined["array_col"] // k

    binned = (
        combined.groupby(
            ["bin_row", "bin_col"],
            sort=True,
        )[gene_columns]
        .sum()
        .reset_index()
    )

    binned.insert(
        0,
        "bin_id",
        [
            f"bin_r{row}_c{col}"
            for row, col in zip(
                binned["bin_row"],
                binned["bin_col"],
		strict=True,
            )
        ],
    )

    return binned

