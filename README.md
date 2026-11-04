# <Analysis Track>

**Group:** Catalina, Vera, Christian, Janine and Elena
**Track:** analysis (`spatial-decode`) 


## What this does

This builds a program that takes synthetic spatial-transcriptomics data (gene counts from square wells + coordi-
nates + a single-cell reference), bins it, and (a) estimates the cell-type composition of each
bin (deconvolution) and (b) partitions the tissue into spatial domains (domain detection), then
measures how close it got to the simulator’s truth.


## Install

```
bash
conda env create -f environment.yml
conda activate pls2026
pip install -e .
```
The `-e` points the install at the source files, so an edit takes effect without reinstalling.
If you only wants to *run* this project rather than work on it, you can leave it out.


## Run: to be completed at the end!!

```
bash
python nameofprogram.py 
```


## Repository layout

```
src/        contains folder spatial_decode, package to run
tests/      tests for each part of the project, to see if they work
config/     parameters set by authors
SPEC.md     what tthe program does and what checks we can run to see if it is correct
ai_log/     AI logs for each author, recoring the most significant uses of AI throughout the coding
```

## Data

???

## Checks

```bash
pytest        # the tests must pass
ruff check .  # the style checks must pass
```

---


## Run in a container *(Week 11)*

There are two separate things here. **A** happens on GitHub without anyone doing anything; **B** is
optional and is the only part that needs software on your computer. Fill in both.

### A. Built and run on GitHub — nothing to install

Every push, the `build-image` workflow builds this project's image from the `Dockerfile`, publishes
it, and runs the analysis inside it. This happens on GitHub's machines, so it works whether or not
anyone in this group — or anyone reading this — has Docker.

* **Image:** `<ghcr.io/your-group/your-project:tag>`
* **A recent successful build:** `<link to the workflow run>`

<**Where to find both.** On your repository page, the *Packages* panel on the right lists the image;
click it and the page shows the full name and every tag that has been published. The *Actions* tab
lists the workflow runs — open the most recent green `image` run and copy its URL.

The name is not a mystery once you have seen it: it is `ghcr.io/` + the owner and repository, in
lower case, exactly as they appear in your GitHub URL. So `github.com/Ada-Group/spatial-decode`
publishes to `ghcr.io/ada-group/spatial-decode`. The **tag** after the colon is added by the
workflow: `sha-3f9a1c2` for the commit it was built from, and the branch name for the latest build
on that branch. Use the commit tag here — it names one exact version, which `main` does not.>

<If the *Packages* panel is empty, the workflow has not published yet: check the *Actions* tab for a
failed run. If it is there but a classmate cannot pull it, the package is private — open it, then
*Package settings → Change visibility → Public*.>

### B. Running the image yourself — needs Docker or Podman

**Optional.** Only do this if you want the image on your own machine; the project is fully usable
without it, through the *Install* and *Run* sections above. Installing a runtime needs administrator
rights, and on macOS or Windows it runs a Linux virtual machine.

```bash
<docker pull ghcr.io/your-group/your-project:tag>
<docker run --rm \
    -v "$PWD/data:/data:ro" \
    -v "$PWD/results:/results" \
    ghcr.io/your-group/your-project:tag --data-dir /data/raw --out-dir /results>
```

<`podman` takes the same arguments. The two `-v` options are what give the container your data and
somewhere to write; without them it can see neither.>

## Run the whole pipeline *(Week 12)*

```bash
<nextflow run main.nf -profile conda ...>      # conda: no container runtime needed
<nextflow run main.nf -profile docker ...>     # docker: what CI uses, if the reader has it
```

## Verifying you got the right answer *(Week 13–14)*

<The result a correct run produces on the reference dataset — a number, or the checksums of the
output files. Say whether agreement should be exact or to a tolerance, and why.>

## Citation and version *(Week 14)*

<The version this README describes, and the DOI. `CITATION.cff` holds the full record.

In this course the deposit is made on sandbox.zenodo.org, so the DOI starts with 10.5072 and the
record is a practice one — say that here for complete clarity.>

## License *(Week 14)*

<The license your group chose, matching the LICENSE file.>
