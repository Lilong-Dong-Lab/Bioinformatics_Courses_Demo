#!/usr/bin/env python3
"""
BRCA1 BLAST Demo Script - Simple Version
========================================

This script demonstrates how to use BioPython to perform BLAST searches
on the BRCA1 protein sequence using NCBI's online BLAST service.

Based on official BioPython documentation:
https://biopython.org/docs/dev/Tutorial/chapter_blast.html#sec-running-www-blast

Author: Bioinformatics Course Demo
Date: 2025-11-14
"""

import sys
import time
from pathlib import Path
from Bio.Blast import NCBIWWW
from Bio import SeqIO
from Bio.Blast import NCBIXML

def main():
    """
    Main function to run the BRCA1 BLAST demonstration.
    """
    print("🧬 BRCA1 BLAST Demonstration")
    print("=" * 50)
    print("This script demonstrates BLAST analysis of the BRCA1 protein")
    print("using BioPython and NCBI's online BLAST service.")

    # Set email for NCBI (required for usage)
    NCBIWWW.email = "bioinfo.demo@example.com"

    # Load BRCA1 sequence
    fasta_file = "../data/brca1_protein.fasta"

    try:
        record = SeqIO.read(fasta_file, "fasta")
        print(f"✓ Successfully loaded sequence: {record.id}")
        print(f"  Description: {record.description}")
        print(f"  Length: {len(record.seq)} amino acids")
    except Exception as e:
        print(f"✗ Error loading sequence: {e}")
        sys.exit(1)

    print(f"\n🔍 Performing BLAST search...")
    print(f"  Program: blastp")
    print(f"  Database: nr")
    print(f"  Query sequence length: {len(record.seq)}")
    print(f"  This may take 30-60 seconds...")

    try:
        # Perform BLAST search - following official documentation
        result_handle = NCBIWWW.qblast("blastp", "nr", record.seq)

        # Save raw results with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"../results/blast_results_{timestamp}.xml"

        # Ensure results directory exists
        Path("../results").mkdir(exist_ok=True)

        # Write results to file
        with open(output_file, "w") as out_handle:
            out_handle.write(result_handle.read())

        print(f"✓ BLAST search completed successfully!")
        print(f"  Results saved to: {output_file}")

        # Close the result handle
        result_handle.close()

        # Now parse and display results
        print(f"\n📊 Parsing BLAST results...")

        # Open the saved XML file for parsing
        with open(output_file, "r") as result_file:
            blast_record = NCBIXML.read(result_file)

        print(f"  Query: {blast_record.query}")
        print(f"  Database: {blast_record.database}")
        print(f"  Number of hits found: {len(blast_record.alignments)}")

        if len(blast_record.alignments) == 0:
            print("  No significant hits found.")
        else:
            print(f"\n📋 Top BLAST Hits:")
            print("-" * 100)

            for i, alignment in enumerate(blast_record.alignments[:5]):  # Show top 5
                hit_def = alignment.hit_def
                accession = alignment.accession
                length = alignment.length

                # Get best HSP (High-scoring Segment Pair)
                best_hsp = alignment.hsps[0]
                e_value = best_hsp.expect
                score = best_hsp.score
                identity = best_hsp.identities
                align_length = best_hsp.align_length
                percent_identity = (identity / align_length) * 100

                print(f"  {i+1}. {accession}")
                print(f"     Description: {hit_def[:80]}...")
                print(f"     Length: {length} aa")
                print(f"     E-value: {e_value:.2e}")
                print(f"     Bit Score: {score}")
                print(f"     Identity: {identity}/{align_length} ({percent_identity:.1f}%)")
                print()

        print(f"\n✅ BLAST demonstration completed successfully!")
        print(f"📁 Full results saved to: {output_file}")
        print(f"💡 You can view the XML file in any text editor or BLAST viewer")

    except Exception as e:
        print(f"✗ Error during BLAST search: {e}")
        print(f"💡 This could be due to:")
        print(f"   - Network connectivity issues")
        print(f"   - NCBI BLAST service being temporarily unavailable")
        print(f"   - Rate limiting (too many requests)")
        sys.exit(1)

if __name__ == "__main__":
    main()