Reproducible Comparative Study of GA-PSO and Baseline Metaheuristics for Constrained Operational Optimization of Radial Distribution Networks

[DOI]

This repository provides the public reproducibility package for the
study:

Reproducible Comparative Study of GA-PSO and Baseline Metaheuristics for
Constrained Operational Optimization of Radial Distribution Networks.

The repository contains the source code, configuration files, random
seeds, benchmark descriptions, result tables, and figure-generation
scripts required to reproduce the comparative experiments reported in
the manuscript.

Authors

Qiu Hong North China Electric Power University (Beijing), Beijing, China
Guangzhou Power Supply Bureau, China Southern Power Grid, Guangzhou,
China ORCID: https://orcid.org/0009-0001-4785-6637

Ximing Wang North China Electric Power University (Baoding), Baoding,
China

Repository URL https://github.com/hqhighboy/epsr_public_release

Permanent archive (Zenodo): https://doi.org/10.5281/zenodo.18920852

Scope of this public release

This repository supports computational reproducibility of the
comparative metaheuristic experiments presented in the manuscript.

The public release includes: - algorithm implementations for GA, PSO,
DE, GA-PSO, MOEA/D, and NSGA-III - configuration files for the benchmark
systems - random seed lists used for controlled repeated experiments -
scripts for running experiments and recomputing statistical summaries -
manuscript-ready tables and figures - supplementary tables describing
decision-variable bounds and discretization settings

Confidential operational feeder data are not included in this
repository. Where real feeder information is involved, redacted or
aggregated representations are provided.

Repository structure

. ├── src/ core algorithm implementations ├── scripts/ experiment
runners and analysis scripts ├── config/ configuration files for
benchmark systems ├── data/ public or redacted benchmark descriptions
├── seeds/ random seeds for reproducible runs ├── results/ │ ├── tables/
manuscript-ready tables │ ├── figures/ manuscript-ready figures │ └──
fairness_check/ auxiliary validation outputs ├── supplementary/
supplementary tables ├── docs/ documentation and reproducibility notes
├── requirements.txt ├── CITATION.cff ├── LICENSE └── README.md

Environment

Recommended environment: - Python 3.10 or newer - Windows, Linux, or
macOS - A clean Python virtual environment is recommended

Install dependencies: pip install -r requirements.txt

Reproducibility workflow

A typical workflow to reproduce the experiments is:

1.  create and activate a Python environment
2.  install dependencies from requirements.txt
3.  inspect configuration files under config/
4.  run the experiments using the scripts in scripts/
5.  recompute summary statistics and statistical tests
6.  compare generated outputs with the released tables and figures

Example commands

Run the main experiments: python scripts/run_experiments.py

Run PF-call-budget experiments: python
scripts/run_pf_budget_experiment.py

Recompute summary statistics: python scripts/recompute_summary.py

Run statistical tests: python scripts/stat_tests.py

Generate manuscript artifacts: python
scripts/generate_paper_artifacts.py

Released assets

The public release includes: - algorithm implementations - benchmark
configuration files - random seed lists - result tables and figures -
fairness-check outputs - supplementary tables and documentation

Citation

If you use this code or repository in your research, please cite:

Q. Hong and X. Wang, Reproducible Comparative Study of GA-PSO and
Baseline Metaheuristics for Constrained Operational Optimization of
Radial Distribution Networks.

Zenodo archive: https://doi.org/10.5281/zenodo.18920852

License

This project is released under the MIT License. See the LICENSE file for
details.
