#!/usr/bin/env python3
"""
BioPython Remote BLAST Demo
============================

This script demonstrates remote BLAST using BioPython's NCBIWWW module.
This is often more reliable than command-line remote BLAST.

Based on official BioPython documentation:
https://biopython.org/docs/dev/Tutorial/chapter_blast.html#sec-running-www-blast

Author: Bioinformatics Course Demo
Date: 2025-11-14
"""

import sys
import time
import os
from pathlib import Path

try:
    from Bio.Blast import NCBIWWW
    from Bio import SeqIO
    from Bio.Blast import NCBIXML
    BIOPYTHON_AVAILABLE = True
except ImportError:
    print("BioPython not available. Install with: pixi add biopython")
    BIOPYTHON_AVAILABLE = False

def load_sequence(fasta_file):
    """Load protein sequence from FASTA file."""
    try:
        record = SeqIO.read(fasta_file, "fasta")
        print(f"✓ Loaded sequence: {record.id}")
        print(f"  Length: {len(record.seq)} amino acids")
        return record
    except Exception as e:
        print(f"✗ Error loading sequence: {e}")
        return None

def run_biopython_blast(sequence, database="nr", max_results=10):
    """Run BLAST using BioPython's NCBIWWW module."""
    print(f"\n🌐 Running BioPython Remote BLAST...")
    print(f"  Database: {database}")
    print(f"  Query length: {len(sequence.seq)}")
    print(f"  Max results: {max_results}")
    print(f"  This may take 1-3 minutes...")

    # Set email (required by NCBI)
    NCBIWWW.email = "bioinfo.demo@example.com"

    try:
        # Perform BLAST search
        result_handle = NCBIWWW.qblast(
            program="blastp",
            database=database,
            sequence=sequence.seq,
            hitlist_size=max_results,
            expect=0.001,
            format_type="XML"
        )

        print(f"✓ BLAST search completed!")
        return result_handle

    except Exception as e:
        print(f"✗ Error during BLAST search: {e}")
        return None

def parse_biopython_results(result_handle):
    """Parse and display BLAST results."""
    print(f"\n📊 Parsing BLAST Results...")

    try:
        blast_records = list(NCBIXML.parse(result_handle))
        if not blast_records:
            print("✗ No BLAST records found")
            return []

        record = blast_records[0]
        hits_data = []

        print(f"  Query: {record.query}")
        print(f"  Database: {record.database}")
        print(f"  Number of hits: {len(record.alignments)}")

        if len(record.alignments) == 0:
            print("  No significant hits found.")
            return []

        print(f"\n📋 Top BLAST Hits:")
        print("-" * 100)
        print(f"{'Rank':<5} {'Accession':<15} {'Description':<30} {'% Identity':<12} {'E-value':<12}")
        print("-" * 100)

        for i, alignment in enumerate(record.alignments[:10]):
            hit_def = alignment.hit_def
            accession = alignment.accession
            length = alignment.length

            best_hsp = alignment.hsps[0]
            e_value = best_hsp.expect
            score = best_hsp.score
            identity = best_hsp.identities
            align_length = best_hsp.align_length
            percent_identity = (identity / align_length) * 100

            # Truncate description for display
            short_desc = hit_def[:30] + "..." if len(hit_def) > 30 else hit_def

            hits_data.append({
                'rank': i + 1,
                'accession': accession,
                'description': hit_def,
                'length': length,
                'e_value': e_value,
                'bit_score': score,
                'percent_identity': percent_identity
            })

            print(f"{i+1:<5} {accession:<15} {short_desc:<30} {percent_identity:<12.1f} {e_value:<12.2e}")

        return hits_data

    except Exception as e:
        print(f"✗ Error parsing results: {e}")
        return []

def save_results(result_handle, hits_data, timestamp):
    """Save BLAST results to files."""
    try:
        # Save raw XML
        results_dir = "../results"
        Path(results_dir).mkdir(exist_ok=True)

        xml_file = f"{results_dir}/biopython_blast_{timestamp}.xml"
        with open(xml_file, "w") as f:
            f.write(result_handle.read())

        # Save summary
        if hits_data:
            import pandas as pd
            df = pd.DataFrame(hits_data)
            csv_file = f"{results_dir}/biopython_blast_summary_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"\n💾 Results saved:")
            print(f"  XML: {xml_file}")
            print(f"  CSV: {csv_file}")

    except Exception as e:
        print(f"✗ Error saving results: {e}")

def main():
    """Main function to run BioPython BLAST demonstration."""
    print("🧬 BioPython Remote BLAST Demonstration")
    print("=" * 60)

    if not BIOPYTHON_AVAILABLE:
        print("❌ BioPython not available. Please install it first.")
        sys.exit(1)

    # Load sequence
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    query_file = os.path.join(project_dir, "data", "brca1_protein_proper.fasta")

    sequence = load_sequence(query_file)
    if sequence is None:
        print("❌ Failed to load sequence. Exiting.")
        sys.exit(1)

    # Run BLAST
    result_handle = run_biopython_blast(sequence)
    if result_handle is None:
        print("❌ BLAST search failed. This could be due to:")
        print("   • Network connectivity issues")
        print("   • NCBI service temporarily unavailable")
        print("   • Rate limiting")
        print("\n💡 Try:")
        print("   • Running again in a few minutes")
        print("   • Using the web interface instead")
        print("   • Trying during off-peak hours")
        sys.exit(1)

    # Parse results
    hits_data = parse_biopython_results(result_handle)

    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    save_results(result_handle, hits_data, timestamp)

    # Close handle
    result_handle.close()

    print(f"\n✅ BioPython BLAST demonstration completed!")

if __name__ == "__main__":
    main()