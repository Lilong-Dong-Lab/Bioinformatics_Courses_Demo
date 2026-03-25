#!/usr/bin/env python3
"""
EGFR BLAST Demo Script (Legacy - Extended Visualization Example)
================================================================

[DEPRECATED] This script is a legacy example with visualization features.
For the primary demo, use run_blast_cli.py or biopython_remote_blast.py instead.

This script demonstrates how to use BioPython to perform BLAST searches
with pandas DataFrames and matplotlib visualizations.

Author: Bioinformatics Course Demo
Date: 2025-11-14
Updated: 2026-03-24 (added deprecation notice, path fixes)
"""

import sys
import time
import os
from pathlib import Path

# Resolve project paths (works regardless of execution directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

from Bio.Blast import NCBIWWW
from Bio import SeqIO
from Bio.Blast import NCBIXML
import pandas as pd
import matplotlib.pyplot as plt

def load_sequence(fasta_file):
    """
    Load protein sequence from FASTA file.

    Args:
        fasta_file (str): Path to FASTA file

    Returns:
        Bio.SeqRecord.SeqRecord: Sequence record
    """
    try:
        record = SeqIO.read(fasta_file, "fasta")
        print(f"✓ Successfully loaded sequence: {record.id}")
        print(f"  Description: {record.description}")
        print(f"  Length: {len(record.seq)} amino acids")
        return record
    except Exception as e:
        print(f"✗ Error loading sequence: {e}")
        return None

def perform_blast_search(sequence, database="nr", program="blastp", max_results=10):
    """
    Perform BLAST search using NCBI's online service.

    Args:
        sequence (Bio.SeqRecord.SeqRecord): Protein sequence
        database (str): BLAST database (default: nr)
        program (str): BLAST program (default: blastp)
        max_results (int): Maximum number of results

    Returns:
        str: BLAST results in XML format
    """
    print("\n🔍 Performing BLAST search...")
    print(f"  Program: {program}")
    print(f"  Database: {database}")
    print(f"  Query sequence length: {len(sequence.seq)}")
    print("  This may take 30-60 seconds...")

    try:
        # Perform BLAST search
        result_handle = NCBIWWW.qblast(
            program=program,
            database=database,
            sequence=sequence.seq,
            hitlist_size=max_results,
            expect=0.001,  # E-value threshold
            format_type="XML"
        )

        # Save raw results
        results_dir = os.path.join(PROJECT_DIR, "results")
        Path(results_dir).mkdir(exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(results_dir, f"blast_results_{timestamp}.xml")

        with open(output_file, "w") as f:
            f.write(result_handle.read())

        print("✓ BLAST search completed successfully!")
        print(f"  Results saved to: {output_file}")

        # Reset handle position for reading
        result_handle.seek(0)
        return result_handle

    except Exception as e:
        print(f"✗ Error during BLAST search: {e}")
        return None

def parse_blast_results(result_handle):
    """
    Parse BLAST results and extract key information.

    Args:
        result_handle: BLAST results handle

    Returns:
        list: List of BLAST hits with key information
    """
    print("\n📊 Parsing BLAST results...")

    blast_records = list(NCBIXML.parse(result_handle))
    if not blast_records:
        print("✗ No BLAST records found")
        return []

    record = blast_records[0]
    hits_data = []

    print(f"  Query: {record.query}")
    print(f"  Database: {record.database}")
    print(f"  Number of hits found: {len(record.alignments)}")

    for i, alignment in enumerate(record.alignments[:10]):  # Limit to top 10
        hit = alignment.hit_def
        accessions = alignment.accession
        length = alignment.length

        # Get best HSP (High-scoring Segment Pair) for this hit
        best_hsp = alignment.hsps[0]
        e_value = best_hsp.expect
        score = best_hsp.score
        identity = (best_hsp.identities / best_hsp.align_length) * 100

        hits_data.append({
            'rank': i + 1,
            'hit_description': hit,
            'accession': accessions,
            'length': length,
            'e_value': e_value,
            'bit_score': score,
            'percent_identity': identity,
            'query_coverage': (best_hsp.align_length / record.query_length) * 100
        })

        print(f"    {i+1}. {accessions} - E-value: {e_value:.2e}, Identity: {identity:.1f}%")

    return hits_data

def create_summary_table(hits_data):
    """
    Create a summary table of BLAST results.

    Args:
        hits_data (list): List of BLAST hits
    """
    if not hits_data:
        return

    print("\n📋 BLAST Results Summary:")
    print("=" * 100)

    # Create DataFrame for better formatting
    df = pd.DataFrame(hits_data)

    # Format numbers for better readability
    df['e_value_formatted'] = df['e_value'].apply(lambda x: f"{x:.2e}")
    df['percent_identity_formatted'] = df['percent_identity'].apply(lambda x: f"{x:.1f}%")
    df['query_coverage_formatted'] = df['query_coverage'].apply(lambda x: f"{x:.1f}%")

    # Display formatted table
    print(df[['rank', 'accession', 'e_value_formatted', 'percent_identity_formatted',
              'query_coverage_formatted', 'hit_description']].to_string(index=False))

    # Save detailed results
    results_dir = os.path.join(PROJECT_DIR, "results")
    Path(results_dir).mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(results_dir, f"blast_summary_{timestamp}.csv")
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Detailed results saved to: {csv_file}")

def plot_blast_results(hits_data):
    """
    Create visualizations of BLAST results.

    Args:
        hits_data (list): List of BLAST hits
    """
    if not hits_data:
        return

    print("\n📈 Creating BLAST result visualizations...")

    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('EGFR BLAST Results Analysis', fontsize=16, fontweight='bold')

    df = pd.DataFrame(hits_data)

    # Plot 1: E-values (log scale)
    ax1.bar(range(len(df)), df['e_value'])
    ax1.set_yscale('log')
    ax1.set_xlabel('Hit Rank')
    ax1.set_ylabel('E-value (log scale)')
    ax1.set_title('E-values of Top Hits')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Percent Identity
    ax2.bar(range(len(df)), df['percent_identity'])
    ax2.set_xlabel('Hit Rank')
    ax2.set_ylabel('Percent Identity (%)')
    ax2.set_title('Sequence Identity Percentages')
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)

    # Plot 3: Bit Scores
    ax3.bar(range(len(df)), df['bit_score'])
    ax3.set_xlabel('Hit Rank')
    ax3.set_ylabel('Bit Score')
    ax3.set_title('Bit Scores')
    ax3.grid(True, alpha=0.3)

    # Plot 4: Query Coverage
    ax4.bar(range(len(df)), df['query_coverage'])
    ax4.set_xlabel('Hit Rank')
    ax4.set_ylabel('Query Coverage (%)')
    ax4.set_title('Query Coverage Percentages')
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save plot
    results_dir = os.path.join(PROJECT_DIR, "results")
    Path(results_dir).mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    plot_file = os.path.join(results_dir, f"blast_analysis_{timestamp}.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"📊 Visualization saved to: {plot_file}")

    # Show plot (this may not work in some environments)
    try:
        plt.show()
    except:
        print("Note: Plot display not available in this environment")

def main():
    """
    Main function to run the EGFR BLAST demonstration.
    """
    print("🧬 EGFR BLAST Demonstration (Legacy)")
    print("=" * 50)
    print("[NOTE] This is a legacy script. For primary demos, use:")
    print("       - run_blast_cli.py (local BLAST)")
    print("       - biopython_remote_blast.py (remote BLAST)")
    print()
    print("This script demonstrates BLAST analysis of the EGFR protein")
    print("using BioPython and NCBI's online BLAST service.")

    # Load EGFR sequence with absolute path
    data_dir = Path(PROJECT_DIR) / "data"
    fasta_file = data_dir / "egfr_protein.fasta"
    sequence = load_sequence(fasta_file)

    if sequence is None:
        print("❌ Failed to load sequence. Exiting.")
        sys.exit(1)

    # Perform BLAST search
    result_handle = perform_blast_search(sequence)

    if result_handle is None:
        print("❌ Failed to perform BLAST search. Exiting.")
        sys.exit(1)

    # Parse results
    hits_data = parse_blast_results(result_handle)

    # Create summary table
    create_summary_table(hits_data)

    # Create visualizations
    plot_blast_results(hits_data)

    print("\n✅ BLAST demonstration completed successfully!")
    print("📁 All results saved to the 'results' directory.")

    # Close the result handle
    result_handle.close()

if __name__ == "__main__":
    main()