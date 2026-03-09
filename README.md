
# Reproducible Comparative Study of GA-PSO and Baseline Metaheuristics for Constrained Operational Optimization of Radial Distribution Networks

This repository provides the public reproducibility package for the study:

**Reproducible Comparative Study of GA-PSO and Baseline Metaheuristics for Constrained Operational Optimization of Radial Distribution Networks**

The repository contains the source code, configuration files, random seeds, redacted/public benchmark assets, result tables, and figure-generation scripts required to reproduce the main comparative experiments reported in the paper.

## Authors

- **Qiu Hong**
  North China Electric Power University (Beijing), Beijing, China
  Guangzhou Power Supply Bureau, China Southern Power Grid, Guangzhou, China
  ORCID: 0009-0001-4785-6637

- **Ximing Wang**
  North China Electric Power University (Baoding), Baoding City, Hebei Province, China

## Repository URL

https://github.com/hqhighboy/epsr_public_release

## Scope of this public release

This public release is intended to support computational reproducibility of the comparative study. It includes:

- source code for GA, PSO, DE, GA-PSO, MOEA/D, and NSGA-III based experiments
- configuration files for the public test systems
- random seed files used for controlled repeated experiments
- public/redacted benchmark descriptions
- scripts for experiment execution, summary recomputation, and statistical testing
- result tables and figures included in or derived for the manuscript

This repository does **not** include confidential operational data. Any non-public feeder information has been removed, anonymized, or replaced with redacted/public equivalents.

## Repository structure

.
├─ src/                  # core algorithm implementations and evaluation logic
├─ scripts/              # experiment runners, statistics, and artifact generation scripts
├─ config/               # experiment configuration files
├─ data/                 # public or redacted benchmark data descriptions
├─ seeds/                # random seeds for reproducible repeated runs
├─ results/
│  ├─ tables/            # manuscript-ready tables
│  ├─ figures/           # manuscript-ready figures
│  └─ fairness_check/    # auxiliary validation and fairness-check outputs
├─ docs/                 # release notes, redaction notes, and reproduction guide
├─ supplementary/        # supplementary tables and ancillary assets
├─ requirements.txt
├─ CITATION.cff
├─ LICENSE
└─ .zenodo.json

## Environment

Recommended environment:

- Python 3.10 or newer
- Windows, Linux, or macOS
- A clean virtual environment is recommended

Install dependencies:

pip install -r requirements.txt

## Reproducibility workflow

A typical workflow is:

1. create and activate a Python environment
2. install dependencies from requirements.txt
3. inspect the benchmark and configuration files under config/ and data/
4. run the experiments using the scripts in scripts/
5. recompute summaries and statistical tests
6. compare generated outputs with the released tables and figures

## Example commands

Run the main experiments:

python scripts/run_experiments.py

Run the PF-budget experiment:

python scripts/run_pf_budget_experiment.py

Recompute summary tables:

python scripts/recompute_summary.py

Run statistical tests:

python scripts/stat_tests.py

Generate paper artifacts:

python scripts/generate_paper_artifacts.py

## Released assets

The public release includes the following categories of assets:

- algorithm source code and evaluation modules
- benchmark configuration files
- released seed lists for controlled repeated runs
- released summary tables and figure files
- auxiliary fairness-check outputs
- redaction notes and reproducibility documentation

Where benchmark assets are redacted, the repository documents the released boundary explicitly and avoids disclosure of confidential operational information.

## Reproduction notes

Please consult the following documentation first:

- docs/reproduction_guide.md
- docs/pre_release_checklist.md
- docs/github_zenodo_release.md
- docs/baituf8_redaction.md

These files explain the released asset boundaries, redaction logic, and recommended reproduction procedure.

## Data availability

The repository contains public and redacted materials sufficient to support computational reproducibility of the reported benchmark comparisons. Confidential operational data are not distributed.

## Citation

If you use this repository, please cite the associated paper and this software release.

Citation metadata are provided in CITATION.cff.

## License

This repository is released under the MIT License. See LICENSE for details.

## Zenodo archive

A Zenodo DOI will be added after the first archived release is created.

## Contact

For questions regarding reproducibility or repository issues, please use the GitHub repository issue tracker.
