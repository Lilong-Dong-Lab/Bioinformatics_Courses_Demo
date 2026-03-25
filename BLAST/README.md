# EGFR BLAST Demonstration

This project demonstrates how to use the NCBI BLAST+ command-line tools for protein sequence analysis, specifically using the **EGFR (Epidermal Growth Factor Receptor)** kinase domain as an example.

> **Note**: EGFR is a key target for non-small cell lung cancer (NSCLC) drugs such as gefitinib, erlotinib, and osimertinib. This demo is aligned with lecture materials on bioinformatics tools in drug discovery.

## 🎯 Project Overview

This repository contains a complete demonstration of BLAST (Basic Local Alignment Search Tool) usage in a bioinformatics context, suitable for educational purposes and practical analysis.

### Features Demonstrated

- **Local BLAST database creation** using `makeblastdb`
- **Protein-protein BLAST searches** using `blastp`
- **Result parsing and analysis** in tabular format
- **Command-line automation** using Python scripts
- **Proper environment management** with Pixi
- **Comprehensive unit tests** with pytest

## 📁 Project Structure

```
BIOINFO_Demo_BLAST/
├── pixi.toml              # Pixi environment configuration
├── README.md              # This file
├── CLAUDE.md              # AI assistant guidance
├── data/                  # Input data files
│   └── egfr_protein.fasta             # EGFR kinase domain (primary demo)
├── scripts/               # Analysis scripts
│   ├── run_blast_cli.py           # Main BLAST demonstration script
│   ├── biopython_remote_blast.py  # BioPython remote BLAST demo
│   ├── remote_blast_demo.py       # CLI remote BLAST demo
│   ├── blast_demo.py              # Extended demo with visualization
│   └── blast_demo_simple.py       # Minimal BioPython example
├── tests/                 # Unit tests
│   ├── conftest.py                # Shared fixtures
│   ├── test_run_blast_cli.py      # Local BLAST tests
│   ├── test_biopython_remote_blast.py  # BioPython tests
│   ├── test_remote_blast_demo.py  # Remote BLAST tests
│   ├── test_blast_demo.py         # Visualization tests
│   └── data/                      # Test data files
└── results/               # Output files (created during execution)
    ├── egfr_blast_results.txt      # BLAST search results
    └── egfr_demo_db.*              # Local BLAST database files
```

## 🚀 Getting Started

### Prerequisites

- **Pixi** package manager (installed on your system)
- **macOS** or **Linux** operating system
- **Internet connection** (for remote BLAST examples)

### Installation and Setup

1. **Navigate to the project directory:**

   ```bash
   cd BIOINFO_Demo_BLAST
   ```

2. **Install the environment:**

   ```bash
   pixi install
   ```

3. **Verify BLAST installation:**
   ```bash
   pixi run verify-blast
   ```

## 🧬 Running the BLAST Demonstration

### Main Demo Script

Run the complete BLAST demonstration:

```bash
pixi run run-blast
```

This script will:

1. Check BLAST+ tool availability
2. Create a local BLAST database from the EGFR sequence
3. Perform a local BLAST search
4. Parse and display results
5. Show remote BLAST examples

### Individual BLAST Commands

You can also run BLAST commands directly:

1. **Create a local database:**

   ```bash
   pixi exec makeblastdb -in data/egfr_protein.fasta -dbtype prot -out egfr_demo_db
   ```

2. **Run BLAST search:**

   ```bash
   pixi exec blastp -query data/egfr_protein.fasta -db egfr_demo_db -out results.txt -outfmt 6
   ```

3. **View results:**
   ```bash
   cat results.txt
   ```

## 🧪 Running Unit Tests

This project includes comprehensive unit tests using pytest. All tests are mocked to run without network access.

### Run All Tests

```bash
pixi run test
```

### Run Tests with Coverage

```bash
pixi run test-cov
```

### Run Specific Test Files

```bash
# Test local BLAST CLI (Priority 1)
pixi run test-cli

# Test BioPython remote BLAST (Priority 2)
pixi run test-biopython

# Run verbose output
pixi run test-verbose
```

### Test Coverage

| Script                      | Coverage | Description                      |
| --------------------------- | -------- | -------------------------------- |
| `run_blast_cli.py`          | 65%      | Local BLAST operations           |
| `biopython_remote_blast.py` | 55%      | BioPython remote BLAST           |
| `blast_demo.py`             | 85%      | Extended demo with visualization |
| `remote_blast_demo.py`      | 66%      | CLI remote BLAST                 |

**Overall coverage: ~60%**

### Test Structure

```
tests/
├── conftest.py                # Shared fixtures and mocks
├── test_run_blast_cli.py      # 26 tests for local BLAST
├── test_biopython_remote_blast.py  # 19 tests for BioPython
├── test_remote_blast_demo.py  # 22 tests for remote BLAST
├── test_blast_demo.py         # 24 tests for visualization
└── data/                      # Test data files
```

### What's Tested

- ✅ Command execution and subprocess handling
- ✅ BLAST tool availability checking
- ✅ Local BLAST database creation
- ✅ Result parsing (tabular and XML formats)
- ✅ Error handling (missing files, network errors)
- ✅ BioPython sequence loading
- ✅ Mocked remote BLAST operations
- ⏭️ Network tests (skipped by default, run manually)

## 📊 Understanding the Output

### BLAST Results Format

The script generates results in tabular format (outfmt 6) with the following columns:

1. **Query ID** - Your input sequence identifier
2. **Subject ID** - Database sequence identifier
3. **% Identity** - Sequence similarity percentage
4. **Alignment Length** - Length of aligned region
5. **Mismatches** - Number of mismatches
6. **Gap Openings** - Number of gap openings
7. **Query Start** - Start position in query
8. **Query End** - End position in query
9. **Subject Start** - Start position in subject
10. **Subject End** - End position in subject
11. **E-value** - Expectation value (statistical significance)
12. **Bit Score** - Alignment score

### Interpreting Results

- **E-value < 1e-5**: Generally considered significant
- **% Identity > 30%**: Often indicates homology for proteins
- **Bit Score**: Higher scores indicate better alignments

## 🔧 Available BLAST Tools

The project includes the following BLAST+ tools:

- `blastp` - Protein-protein BLAST
- `blastn` - Nucleotide-nucleotide BLAST
- `blastx` - Translated nucleotide-protein BLAST
- `tblastn` - Protein-translated nucleotide BLAST
- `tblastx` - Translated nucleotide-translated nucleotide BLAST
- `makeblastdb` - Create BLAST databases
- `blastdbcmd` - Database utilities

## 🌐 Remote BLAST Options

For comprehensive searches against NCBI databases:

### Web Interface

- Visit: https://blast.ncbi.nlm.nih.gov/Blast.cgi
- Upload your sequence and select appropriate parameters

### Command Line (Remote)

```bash
# Protein BLAST against NCBI nr database
pixi exec blastp -query data/egfr_protein.fasta -db nr -remote -out remote_results.xml

# Requires internet connection and may have usage limits
```

## 📚 Educational Notes

### About EGFR

- **Gene**: EGFR (Epidermal Growth Factor Receptor)
- **Function**: Receptor tyrosine kinase involved in cell growth and differentiation
- **Domain**: Kinase domain (residues 714-950, demonstrated in this example)
- **Clinical relevance**: Target for NSCLC drugs (gefitinib, erlotinib, osimertinib)
- **UniProt**: P00533

### BLAST Principles

1. **Seed Finding**: Identifies short exact matches
2. **Extension**: Extends seeds to longer alignments
3. **Scoring**: Uses substitution matrices (BLOSUM62 for proteins)
4. **Statistical Analysis**: Calculates E-values and bit scores

## 🛠️ Advanced Usage

### Custom Database Creation

```bash
# Create database from multiple FASTA files
pixi exec makeblastdb -in sequences.fasta -dbtype prot -out custom_db -parse_seqids

# Add taxonomic information
pixi exec makeblastdb -in sequences.fasta -dbtype prot -out custom_db -taxid 9606
```

### Advanced BLAST Parameters

```bash
# Stringent search
pixi exec blastp -query protein.fasta -db database.fasta -evalue 1e-10 -outfmt 6

# Include alignments in output
pixi exec blastp -query protein.fasta -db database.fasta -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq"
```

## 🔍 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'Bio'"**
   - Ensure environment is properly installed: `pixi install`

2. **"Query file not found"**
   - Check that data files exist in the `data/` directory
   - Verify file paths are correct

3. **BLAST warnings about invalid residues**
   - These are normal for demonstration sequences
   - BLAST automatically handles invalid characters

4. **Remote BLAST timeouts**
   - NCBI services may be temporarily unavailable
   - Try again later or use local databases

### Getting Help

1. Check BLAST documentation: https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs
2. Review pixi documentation: https://pixi.sh
3. Examine log files in the `results/` directory

## 📄 License

This project is intended for educational purposes. Please cite appropriate sources when using in academic work.

## 🤝 Contributing

Feel free to submit issues and enhancement requests for improving this educational demonstration.

---

**Happy BLASTing! 🧬**
