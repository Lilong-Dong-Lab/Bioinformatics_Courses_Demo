#!/usr/bin/env python3
"""
Shared Utilities for BLAST Demo Scripts
========================================

This module provides common utilities used across multiple BLAST demonstration
scripts to reduce code duplication and improve maintainability.

Author: Bioinformatics Course Demo
Date: 2026-03-24
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List, Tuple


def get_project_dir() -> Path:
    """
    Get the project root directory (parent of scripts/).

    Returns:
        Path: Project root directory
    """
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """
    Get the data directory path.

    Returns:
        Path: Data directory path
    """
    return get_project_dir() / "data"


def get_results_dir() -> Path:
    """
    Get the results directory path.

    Returns:
        Path: Results directory path
    """
    return get_project_dir() / "results"


def ensure_results_dir() -> Path:
    """
    Ensure results directory exists and return path.

    Returns:
        Path: Results directory path
    """
    results_dir = get_results_dir()
    results_dir.mkdir(exist_ok=True)
    return results_dir


def timestamp() -> str:
    """
    Get current timestamp for filenames.

    Returns:
        str: Timestamp in format YYYYMMDD_HHMMSS
    """
    return time.strftime("%Y%m%d_%H%M%S")


def run_command(
    cmd: List[str],
    description: str = "Command",
    timeout: Optional[int] = None,
    check: bool = True,
    capture_output: bool = True,
    verbose: bool = True,
) -> Optional[subprocess.CompletedProcess]:
    """
    Run a shell command and return the result.

    This is a unified subprocess wrapper that handles errors consistently
    across all BLAST demo scripts.

    Args:
        cmd: Command and arguments as list
        description: Human-readable description for logging
        timeout: Timeout in seconds (None for no timeout)
        check: Raise exception on non-zero exit
        capture_output: Capture stdout/stderr
        verbose: Print status messages

    Returns:
        subprocess.CompletedProcess on success, None on failure

    Example:
        >>> result = run_command(['blastp', '-version'])
        >>> if result:
        ...     print(result.stdout)
    """
    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] {description}...")

    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )
        return result

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout after {timeout}s: {' '.join(cmd)}")
        return None

    except subprocess.CalledProcessError as e:
        print(f"✗ Error running command: {' '.join(cmd)}")
        print(f"  Return code: {e.returncode}")
        if e.stdout:
            print(f"  stdout: {e.stdout[:500]}")
        if e.stderr:
            print(f"  stderr: {e.stderr[:500]}")
        return None

    except FileNotFoundError:
        print(f"✗ Command not found: {cmd[0]}")
        return None


def load_fasta_sequence(fasta_path: Path) -> Tuple[str, str]:
    """
    Load sequence from a FASTA file without BioPython dependency.

    This is a lightweight alternative to Bio.SeqIO for simple cases.
    Handles multi-line FASTA with optional comment lines.

    Args:
        fasta_path: Path to FASTA file

    Returns:
        Tuple of (header, sequence)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or malformed
    """
    if not fasta_path.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_path}")

    content = fasta_path.read_text().strip()
    if not content:
        raise ValueError(f"Empty FASTA file: {fasta_path}")

    lines = content.split("\n")
    if not lines[0].startswith(">"):
        raise ValueError(f"Invalid FASTA format (missing header): {fasta_path}")

    header = lines[0][1:].strip()  # Remove '>' prefix

    # Collect sequence lines - must be:
    # - Non-empty
    # - Not starting with '>' (additional headers)
    # - Containing only valid sequence characters (no spaces, mostly letters)
    # Valid amino acids plus X, B, Z, J, * for protein
    # Valid nucleotides for DNA/RNA
    valid_sequence_chars = set(
        "ACDEFGHIKLMNPQRSTVWYXBZJacdefghiklmnpqrstvwyxbzj*GTUgtu"
    )

    sequence_parts = []
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(">"):
            continue

        # Sequence lines should NOT contain spaces and should be mostly
        # valid sequence characters
        if " " not in stripped:
            valid_count = sum(1 for c in stripped if c in valid_sequence_chars)
            if valid_count == len(stripped):  # All chars must be valid
                sequence_parts.append(stripped)

    sequence = "".join(sequence_parts)

    if not sequence:
        raise ValueError(f"No sequence found in: {fasta_path}")

    return header, sequence


# Common BLAST program names
BLAST_PROGRAMS = ["blastp", "blastn", "blastx", "tblastn", "tblastx"]

# Common NCBI databases
BLAST_DATABASES = ["nr", "nt", "refseq_protein", "refseq_rna", "swissprot", "pdb"]

# Output format codes for BLAST
BLAST_OUTFMT = {
    0: "pairwise",
    5: "XML",
    6: "tabular",
    7: "tabular with comments",
    10: "comma-separated values",
    11: "BLAST archive format (ASN.1)",
}
