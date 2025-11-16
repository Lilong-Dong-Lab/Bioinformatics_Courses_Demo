# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a bioinformatics educational project demonstrating BLAST (Basic Local Alignment Search Tool) usage for protein sequence analysis, specifically using the BRCA1 protein sequence. The project is designed for teaching bioinformatics concepts and practical command-line BLAST operations.

## Environment Setup

This project uses Pixi package manager with conda-forge and bioconda channels. All dependencies are managed through `pixi.toml`:

```bash
pixi install                    # Install all dependencies
pixi run verify-blast          # Verify BLAST installation
```

### Available Tools
- **BLAST+ 2.16.0+**: Complete NCBI BLAST suite (blastp, blastn, makeblastdb, etc.)
- **Python 3.10+**: For automation scripts
- **BioPython 1.86+**: For programmatic BLAST operations
- **Pandas**: For result analysis and CSV generation (in BioPython scripts)

### Pixi Tasks (from pixi.toml)
- `pixi run verify-blast` - Check BLAST+ installation
- `pixi run run-blast` - Run main local BLAST demonstration
- `pixi run run-remote-blast` - Run command-line remote BLAST demonstration
- `pixi run run-biopython-blast` - Run BioPython remote BLAST demonstration

## Core Commands

### Local BLAST Operations
```bash
# Main demonstration (creates local DB, runs BLAST, parses results)
pixi run run-blast

# Individual BLAST operations
pixi exec makeblastdb -in data/brca1_protein_proper.fasta -dbtype prot -out demo_db
pixi exec blastp -query data/brca1_protein_proper.fasta -db demo_db -out results.txt -outfmt 6
```

### Remote BLAST Operations
```bash
# Command-line remote BLAST (may face rate limiting)
pixi run run-remote-blast

# BioPython remote BLAST (more reliable)
pixi run run-biopython-blast
```

### Direct BLAST Tool Access
```bash
pixi exec blastp -version        # Check BLAST version
pixi exec blastn -version        # Check nucleotide BLAST
pixi exec makeblastdb -help      # Database creation help
```

## Script Comparison and Use Cases

### Which script to use?

1. **`run_blast_cli.py`** (Recommended for beginners)
   - Best for: Learning BLAST command-line tools
   - Creates local, self-contained databases
   - Demonstrates subprocess calls to BLAST+ tools
   - Does NOT require internet after setup

2. **`biopython_remote_blast.py`** (Recommended for programmatic access)
   - Best for: Automated batch processing
   - Uses NCBI's web service (requires internet)
   - More reliable than command-line remote BLAST
   - Generates CSV summaries and XML output

3. **`remote_blast_demo.py`** (For understanding limitations)
   - Best for: Understanding rate limiting issues
   - Demonstrates why CLI remote BLAST often fails
   - Shows alternative approaches
   - See REMOTE_BLAST_GUIDE.md for details

4. **`blast_demo_simple.py`** (Minimal example - legacy)
   - Simplest BioPython BLAST example
   - Less error handling than biopython_remote_blast.py

5. **`blast_demo.py`** (Extended example - legacy)
   - More features but superseded by run_blast_cli.py
   - Kept for reference

### Choosing Local vs Remote BLAST

**Use Local BLAST when:**
- Testing and learning (fast, no rate limits)
- Working with private/custom sequences
- Running many queries
- You can create local databases

**Use Remote BLAST when:**
- Need comprehensive NCBI databases (nr, nt, refseq)
- One-off queries
- Don't want to download large databases locally
- Okay with potential delays/rate limiting

## Project Architecture

### Script Organization
The project contains multiple Python scripts demonstrating different BLAST approaches:

1. **`run_blast_cli.py`**: Primary local BLAST demonstration
   - Uses subprocess to call BLAST+ tools
   - Creates local databases with `makeblastdb`
   - Parses tabular results (outfmt 6)
   - Provides educational output formatting

2. **`remote_blast_demo.py`**: Command-line remote BLAST
   - Demonstrates `-remote` flag usage
   - Shows rate limiting issues
   - Includes web interface instructions

3. **`biopython_remote_blast.py`**: Programmatic remote BLAST
   - Uses BioPython's NCBIWWW module
   - More reliable than command-line remote
   - Parses XML results automatically

### Data Structure
- **`data/`**: Input FASTA files (BRCA1 protein sequences)
- **`results/`**: Generated BLAST results and databases
- **Scripts use absolute path resolution** to handle execution from different directories

### BLAST Result Formats
The project primarily uses tabular format (outfmt 6) with these columns:
1. Query ID
2. Subject ID
3. % Identity
4. Alignment Length
5. Mismatches
6. Gap Openings
7. Query Start
8. Query End
9. Subject Start
10. Subject End
11. E-value (statistical significance)
12. Bit Score (alignment quality)

**Available Output Formats:**
- `outfmt 6` - Tabular (used in CLI scripts)
- `outfmt 5` - XML (used in BioPython results)
- `outfmt 0` - Pairwise (default text alignment)

## Key Implementation Details

### Path Handling
Scripts resolve paths dynamically to work regardless of execution location:
```python
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
query_file = os.path.join(project_dir, "data", "sequence.fasta")
```

### BLAST Database Files
When creating databases with `makeblastdb`, multiple index files are generated:
- `.phr` - BLAST database header
- `.pin` - BLAST database index
- `.psq` - BLAST database sequences
- `.pjs`, `.pot`, `.pto`, `.ptf`, `.pdb` - Additional index files

**Do not delete or modify these files manually** - they are required for BLAST searches.

### Error Handling
All scripts include comprehensive error handling for:
- Missing input files (exit with code 1)
- BLAST command failures (subprocess error handling)
- Network connectivity issues (remote BLAST with retries)
- Result parsing errors (try/except blocks)
- Rate limiting (documented in remote_blast_demo.py)

### Remote BLAST Limitations
The project demonstrates and documents known limitations:
- NCBI rate limiting for command-line remote BLAST
- "search aborted by Entrez" errors (see REMOTE_BLAST_GUIDE.md)
- Alternative web-based solutions (NCBI web interface, EMBL-EBI)
- Command-line remote BLAST often fails; BioPython more reliable

## Educational Focus

This project is designed for teaching bioinformatics concepts:
- BRCA1 protein domain analysis (RING finger domain)
- Local vs remote BLAST trade-offs
- Command-line bioinformatics workflows
- Result interpretation (E-values, identity percentages)
- Rate limiting and API best practices
- Path resolution and script portability

## File Management
- **Local databases** are created in project root during execution
- **Results are timestamped** to avoid overwriting (format: YYYYMMDD_HHMMSS)
- **XML and CSV outputs** are available for further analysis
- **Temporary files managed through results/** directory
- **Input sequences** in FASTA format (data/ directory)
- **Don't commit** generated database files (.pdb, .phr, .pin, etc.) - already in .gitignore

## Related Documentation
- **README.md** - Main project documentation and user guide
- **REMOTE_BLAST_GUIDE.md** - Comprehensive remote BLAST options and troubleshooting
- **REFERENCES/** - Additional course materials (if available)

## Troubleshooting Common Issues

1. **"No such file or directory" errors**
   - Check file paths are absolute or properly resolved with `os.path.join()`

2. **"search aborted by Entrez"**
   - NCBI rate limiting; use web interface or wait several minutes
   - See REMOTE_BLAST_GUIDE.md for alternatives

3. **Empty result files**
   - Check query sequence format (must be valid FASTA)
   - Verify databases exist and are properly formatted

4. **Import errors (BioPython)**
   - Ensure Pixi environment is activated or use `pixi run` commands

5. **Permission errors**
   - Check execute permissions on scripts (`chmod +x scripts/*.py`)