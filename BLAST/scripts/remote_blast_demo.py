#!/usr/bin/env python3
"""
Remote BLAST Demo Script
========================

This script demonstrates how to perform remote BLAST searches using NCBI's online services.
Remote BLAST allows you to search against comprehensive databases like nr, nt, refseq, etc.

Note: Remote BLAST requires internet connection and may have usage limits.

Author: Bioinformatics Course Demo
Date: 2025-11-14
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(cmd, capture_output=True):
    """
    Run a command and return the result.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}:")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return None

def run_remote_blast(query_file, program="blastp", database="nr", output_file=None):
    """
    Run remote BLAST search against NCBI databases.

    Args:
        query_file (str): Path to query sequence file
        program (str): BLAST program (blastp, blastn, blastx, etc.)
        database (str): NCBI database (nr, nt, refseq, etc.)
        output_file (str): Output file path
    """
    print(f"🌐 Running Remote BLAST...")
    print(f"  Program: {program}")
    print(f"  Database: {database}")
    print(f"  Query: {query_file}")
    print(f"  Output: {output_file}")
    print(f"  Note: This may take 1-5 minutes depending on server load")

    # Basic remote BLAST command
    cmd = [
        program,
        '-query', query_file,
        '-db', database,
        '-remote',  # This is the key parameter for remote BLAST
        '-out', output_file,
        '-outfmt', '6',  # Tabular format
        '-evalue', '0.001',
        '-max_target_seqs', '10'
    ]

    print(f"  Command: {' '.join(cmd)}")

    result = run_command(cmd, capture_output=False)
    if result is not None:
        print(f"✓ Remote BLAST completed successfully!")
        return True
    else:
        print(f"✗ Remote BLAST failed!")
        return False

def run_advanced_remote_blast(query_file, output_file):
    """
    Run advanced remote BLAST with more parameters.
    """
    print(f"\n🔬 Advanced Remote BLAST...")

    cmd = [
        'blastp',
        '-query', query_file,
        '-db', 'nr',
        '-remote',
        '-out', output_file,
        '-outfmt', '5',  # XML format for more detailed results
        '-evalue', '0.0001',
        '-max_target_seqs', '20',
        '-entrez_query', '"Homo sapiens[Organism]"',  # Limit to human sequences
        '-matrix', 'BLOSUM62',  # Scoring matrix
        '-gapopen', '11',  # Gap opening penalty
        '-gapextend', '1'   # Gap extension penalty
    ]

    print(f"  Running advanced BLAST with human-only filter...")

    result = run_command(cmd, capture_output=False)
    if result is not None:
        print(f"✓ Advanced Remote BLAST completed!")
        return True
    else:
        print(f"✗ Advanced Remote BLAST failed!")
        return False

def parse_remote_results(result_file):
    """
    Parse and display remote BLAST results.
    """
    print(f"\n📊 Parsing Remote BLAST Results from: {result_file}")

    if not os.path.exists(result_file):
        print(f"✗ Result file not found: {result_file}")
        return

    try:
        with open(result_file, 'r') as f:
            lines = f.readlines()

        if not lines:
            print(f"✗ No results found in file")
            return

        print(f"Found {len(lines)} hits from remote database!")
        print("\nTop Remote BLAST hits:")
        print("-" * 120)
        print(f"{'Rank':<5} {'Accession':<15} {'Description':<40} {'% Identity':<12} {'E-value':<12} {'Bit Score':<10}")
        print("-" * 120)

        for i, line in enumerate(lines[:10]):  # Show top 10
            parts = line.strip().split('\t')
            if len(parts) >= 12:
                subject_id = parts[1]
                # Extract short description from subject ID
                description = subject_id.split('|')[2] if '|' in subject_id and len(subject_id.split('|')) > 2 else subject_id[:40]
                percent_identity = parts[2]
                evalue = parts[10]
                bit_score = parts[11]

                print(f"{i+1:<5} {subject_id:<15} {description[:40]:<40} {percent_identity:<12} {evalue:<12} {bit_score:<10}")

    except Exception as e:
        print(f"✗ Error parsing results: {e}")

def show_web_interface_instructions():
    """
    Show instructions for using NCBI web BLAST interface.
    """
    print(f"\n" + "="*80)
    print("ALTERNATIVE: NCBI Web BLAST Interface")
    print("="*80)

    print(f"\n📱 Step-by-step instructions for web-based BLAST:")
    print(f"1. Go to: https://blast.ncbi.nlm.nih.gov/Blast.cgi")
    print(f"2. Select 'Protein BLAST' (blastp)")
    print(f"3. Copy and paste your BRCA1 sequence:")

    # Show the sequence
    try:
        with open("../data/brca1_protein_proper.fasta", 'r') as f:
            content = f.read()
            print(f"\nSequence to copy:")
            print("-" * 50)
            print(content)
            print("-" * 50)
    except:
        print(f"Sequence file not found")

    print(f"4. Select database: 'Non-redundant protein sequences (nr)'")
    print(f"5. Click 'BLAST' button")
    print(f"6. Wait for results (usually 30 seconds to 2 minutes)")
    print(f"7. Review results in web interface")

def show_limitations_and_tips():
    """
    Show important information about remote BLAST limitations and tips.
    """
    print(f"\n" + "="*80)
    print("IMPORTANT: Remote BLAST Limitations & Tips")
    print("="*80)

    print(f"\n⚠️ Limitations:")
    print(f"• Rate limiting: NCBI limits requests per IP address")
    print(f"• Queue times: High server load can cause delays")
    print(f"• File size limits: Large queries may be rejected")
    print(f"• Service availability: NCBI servers may be down for maintenance")

    print(f"\n💡 Tips for Better Results:")
    print(f"• Use short queries for faster results")
    print(f"• Try off-peak hours (early morning/late evening)")
    print(f"• Limit to specific organisms when possible")
    print(f"• Use appropriate E-value thresholds")
    print(f"• Consider using local databases for frequent searches")

def main():
    """
    Main function to demonstrate remote BLAST.
    """
    print("🌐 Remote BLAST Demonstration")
    print("=" * 60)
    print("This script demonstrates remote BLAST searches using NCBI's online services")

    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    query_file = os.path.join(project_dir, "data", "brca1_protein_proper.fasta")

    # Ensure results directory exists
    results_dir = os.path.join(project_dir, "results")
    Path(results_dir).mkdir(exist_ok=True)

    # Define output files
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    basic_output = os.path.join(results_dir, f"remote_blast_basic_{timestamp}.txt")
    advanced_output = os.path.join(results_dir, f"remote_blast_advanced_{timestamp}.xml")

    # Check if query file exists
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        sys.exit(1)

    print(f"Using query file: {query_file}")

    # Option 1: Basic remote BLAST
    print(f"\n" + "="*60)
    print("OPTION 1: Basic Remote BLAST")
    print("="*60)

    if run_remote_blast(query_file, "blastp", "nr", basic_output):
        parse_remote_results(basic_output)
    else:
        print("⚠️ Basic remote BLAST failed. This could be due to:")
        print("   • Network connectivity issues")
        print("   • NCBI service temporarily unavailable")
        print("   • Rate limiting from too many requests")

    # Option 2: Advanced remote BLAST
    print(f"\n" + "="*60)
    print("OPTION 2: Advanced Remote BLAST")
    print("="*60)

    if run_advanced_remote_blast(query_file, advanced_output):
        print(f"✓ Advanced results saved to: {advanced_output}")
        print(f"  (XML format - can be viewed in BLAST viewers)")
    else:
        print("⚠️ Advanced remote BLAST failed")

    # Show web interface instructions
    show_web_interface_instructions()

    # Show limitations and tips
    show_limitations_and_tips()

    print(f"\n✅ Remote BLAST demonstration completed!")
    print(f"💡 For production work, consider:")
    print(f"   • Web interface for occasional searches")
    print(f"   • Local databases for frequent analyses")
    print(f"   • Alternative services like EMBL-EBI")

if __name__ == "__main__":
    main()