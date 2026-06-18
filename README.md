# Bioinformatics Courses Demo

A collection of runnable bioinformatics teaching demos for the **生物信息学 (Bioinformatics)** service course at 河北医科大学 (Hebei Medical University). Each subdirectory is a self-contained project with its own environment and entry points.

> This repository is included in the parent course repo `MEDBIO_Bioinformatics` as a git submodule.

---

## ⚠️ Prerequisites — Git LFS required

This repo stores **Protein Data Bank structure files (`*.pdb`)** in [Git LFS](https://git-lfs.com). Without Git LFS installed, cloned `.pdb` files will be small text *pointer* files instead of real structures, and docking/MD demos will fail.

> 需要先安装 Git LFS，否则克隆得到的 `.pdb` 文件将是指针文件而非真实的结构数据。

Install once per machine:

```bash
git lfs install
```

## Clone

Clone with submodules **and** LFS content:

```bash
git clone --recursive https://github.com/Lilong-Dong-Lab/Bioinformatics_Courses_Demo.git
```

If you don't need the large structure files right away, skip them on clone and fetch on demand:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --recursive https://github.com/Lilong-Dong-Lab/Bioinformatics_Courses_Demo.git
# later, when you need the structures:
git lfs pull -I "*.pdb"
```

> Note: the parent repo `MEDBIO_Bioinformatics` *also* uses LFS for `*.xtc`, `*.key`, and `*.pptx`, so Git LFS is needed for the full course material regardless.

## Projects

| Project | Description | Entry point |
|---|---|---|
| [`BLAST/`](BLAST/README.md) | EGFR protein-sequence BLAST (local CLI + remote BioPython), aligned with lecture materials | `pixi run run-blast` |
| [`pdb_query/`](pdb_query/README.md) | T008 — Protein structure acquisition from the Protein Data Bank | `pixi run <task>` |
| [`binding_site_detection/`](binding_site_detection/README.md) | T014 — Detecting protein binding sites | see project README |
| [`protein_ligand_docking_analysis/`](protein_ligand_docking_analysis/README.md) | T015 — Protein–ligand docking ⚠️ **Linux x86_64 only** | `pixi run jupyter` / `pixi run verify` |
| [`md_simulation_analysis/`](md_simulation_analysis/) | Molecular dynamics simulation analysis | `pixi run <task>` |
| [`single_cell_analysis/`](single_cell_analysis/) | Single-cell RNA-seq analysis with Scanpy | Jupyter notebook |
| [`database_construction_demo/`](database_construction_demo/) | Building a bioinformatics database demo | `pixi run <task>` |

## Running a demo

Most projects use [Pixi](https://pixi.sh) for environment management:

```bash
cd <project>          # e.g. cd BLAST
pixi install           # create the project environment
pixi run <task>        # e.g. pixi run run-blast
```

See each project's `README.md` (where present) and `pixi.toml` for the available tasks.

## Notes

- `results/` is generated output (gitignored) — produced by running the demos, not committed.
- Several projects (T008/T014/T015/…) are adapted from the [OpenCADD](https://github.com/volkamerlab/teachopencadd) talktorials.
