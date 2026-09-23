# <project name>

**Group:** <names of all of you>
**Track:** simulation (`tissue-sim`) / analysis (`spatial-decode`) — delete one

> Replace everything in angle brackets. This README is graded, and the criterion is simple:
> can someone who has never met you clone this repository and reproduce a result?
>
> **One repository per group.** One of you creates it from the course template with git's *Use this
> template*; the other two are added under *Settings → Collaborators* and clone it. Everyone making their own copy is the tangle we would spend a session undoing.

## What this does

<One paragraph, in your own words. What problem does this program solve, and for whom?>

## Install

```bash
conda env create -f environment.yml
conda activate pls2026
pip install -e .
```

The `-e` points the install at the source files, so an edit takes effect without reinstalling.
Someone who only wants to *run* this project rather than work on it can leave it out; see the
course document *Running a project from GitHub*.

## Run

```bash
<the one command that produces a result>
```

## Repository layout

```
src/        the package you write
tests/      the checks that prove it works
config/     parameters — no magic numbers in the source
SPEC.md     what this program must do, and how you will know it is correct
ai_log/     your AI + verification log — one file per person, named for you
```

## Data

The reference dataset is **not** in this repository. Refer to it by path; never commit data.

<From Week 3: say where the data comes from and where the program expects it — a URL, a DOI, or
"produced by group X's simulator". Someone who has only this repository has to be able to get it.>

## Checks

```bash
pytest        # the tests must pass
ruff check .  # the style checks must pass
```

---

The sections below are stubs. Each is filled in during the week named, and together they are what
makes this repository runnable by someone who has never met you. The long-form explanation of what a
runner does with them is the course document *Running a project from GitHub* — do not copy it in
here; a README is answers, not a manual.

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
