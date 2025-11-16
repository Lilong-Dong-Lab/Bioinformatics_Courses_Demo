#!/usr/bin/env python3
"""
BRCA1 BLAST CLI Demo Script
===========================

This script demonstrates how to use the NCBI BLAST+ command-line tools
to perform BLAST searches on the BRCA1 protein sequence.

This script demonstrates:
1. Local BLAST database setup (optional)
2. Remote BLAST via NCBI (using web-based services)
3. Command-line BLAST operations
4. Result parsing and analysis

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

    Args:
        cmd (list): Command to run
        capture_output (bool): Whether to capture output

    Returns:
        subprocess.CompletedProcess: Command result
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

def check_blast_tools():
    """
    Check if BLAST+ tools are available.
    """
    print("🔧 Checking BLAST+ tools availability...")

    tools = ['blastp', 'blastn', 'blastx', 'tblastn', 'tblastx']
    available_tools = []

    for tool in tools:
        try:
            result = run_command([tool, '-version'])
            if result:
                available_tools.append(tool)
                print(f"  ✓ {tool} available")
        except:
            print(f"  ✗ {tool} not found")

    return available_tools

def run_local_blast(query_file, database, output_file, program="blastp"):
    """
    Run BLAST using local database.

    Args:
        query_file (str): Path to query sequence file
        database (str): BLAST database name
        output_file (str): Output file path
        program (str): BLAST program to use
    """
    print(f"\n🧬 Running local BLAST...")
    print(f"  Program: {program}")
    print(f"  Query: {query_file}")
    print(f"  Database: {database}")
    print(f"  Output: {output_file}")

    cmd = [
        program,
        '-query', query_file,
        '-db', database,
        '-out', output_file,
        '-outfmt', '6',  # Tabular format
        '-evalue', '0.001',
        '-max_target_seqs', '10'
    ]

    result = run_command(cmd, capture_output=False)
    if result is not None:
        print(f"✓ BLAST completed successfully!")
        return True
    else:
        print(f"✗ BLAST failed!")
        return False

def run_remote_bast_demo(query_file):
    """
    Demonstrate remote BLAST capabilities (conceptual).

    Args:
        query_file (str): Path to query sequence file
    """
    print(f"\n🌐 Remote BLAST (NCBI) demonstration:")
    print(f"  Note: Remote BLAST requires network access and API keys")
    print(f"  This script shows the command structure for remote BLAST")

    print(f"\nExample remote BLAST command:")
    print(f"  # For protein queries:")
    print(f"  rpsblast -query {query_file} -db cdd -remote -out results.xml")

    print(f"\n  # For web-based BLAST:")
    print(f"  # Use NCBI's web interface: https://blast.ncbi.nlm.nih.gov/Blast.cgi")
    print(f"  # Or use web scraping/API tools with BioPython")

def create_sample_database(fasta_files, db_name):
    """
    Create a local BLAST database from FASTA files.

    Args:
        fasta_files (list): List of FASTA file paths
        db_name (str): Database name
    """
    print(f"\n📚 Creating local BLAST database: {db_name}")

    cmd = ['makeblastdb', '-in'] + fasta_files + ['-dbtype', 'prot', '-out', db_name]

    result = run_command(cmd)
    if result is not None:
        print(f"✓ Database '{db_name}' created successfully!")
        return True
    else:
        print(f"✗ Database creation failed!")
        return False

def parse_blast_results(result_file):
    """
    Parse BLAST results in tabular format.

    Args:
        result_file (str): Path to BLAST result file
    """
    print(f"\n📊 Parsing BLAST results from: {result_file}")

    if not os.path.exists(result_file):
        print(f"✗ Result file not found: {result_file}")
        return

    try:
        with open(result_file, 'r') as f:
            lines = f.readlines()

        if not lines:
            print(f"✗ No results found in file")
            return

        print(f"Found {len(lines)} hits")
        print("\nTop BLAST hits:")
        print("-" * 100)
        print(f"{'Rank':<5} {'Subject ID':<15} {'% Identity':<12} {'Alignment Length':<15} {'E-value':<12} {'Bit Score':<10}")
        print("-" * 100)

        for i, line in enumerate(lines[:10]):  # Show top 10
            parts = line.strip().split('\t')
            if len(parts) >= 12:
                subject_id = parts[1]
                percent_identity = parts[2]
                alignment_length = parts[3]
                evalue = parts[10]
                bit_score = parts[11]

                print(f"{i+1:<5} {subject_id:<15} {percent_identity:<12} {alignment_length:<15} {evalue:<12} {bit_score:<10}")

    except Exception as e:
        print(f"✗ Error parsing results: {e}")

def main():
    """
    Main function to run the BLAST CLI demonstration.
    """
    print("🧬 BRCA1 BLAST CLI Demonstration")
    print("=" * 60)
    print("This script demonstrates BLAST+ command-line tools for protein analysis")

    # Check BLAST tools
    available_tools = check_blast_tools()
    if not available_tools:
        print("❌ No BLAST tools found. Please check your installation.")
        sys.exit(1)

    # Define file paths (using absolute paths)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    query_file = os.path.join(project_dir, "data", "brca1_protein_proper.fasta")
    db_name = "brca1_demo_db"
    output_file = os.path.join(project_dir, "results", "brca1_blast_results.txt")

    # Ensure results directory exists
    results_dir = os.path.join(project_dir, "results")
    Path(results_dir).mkdir(exist_ok=True)

    # Check if query file exists
    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        sys.exit(1)

    # Option 1: Create a sample database and run local BLAST
    print(f"\n" + "="*60)
    print("OPTION 1: Local BLAST with custom database")
    print("="*60)

    if create_sample_database([query_file], db_name):
        if run_local_blast(query_file, db_name, output_file, "blastp"):
            parse_blast_results(output_file)
        else:
            print("⚠️ Local BLAST failed, continuing to next option")

    # Option 2: Remote BLAST demonstration
    print(f"\n" + "="*60)
    print("OPTION 2: Remote BLAST demonstration")
    print("="*60)
    run_remote_bast_demo(query_file)

    # Show additional BLAST commands
    print(f"\n" + "="*60)
    print("ADDITIONAL BLAST COMMANDS")
    print("="*60)
    print(f"Available BLAST commands you can try:")
    print(f"  1. blastp -query protein.fasta -db nr -remote -out results.xml")
    print(f"  2. blastn -query nucleotide.fasta -db nt -remote -out results.xml")
    print(f"  3. makeblastdb -in sequences.fasta -dbtype prot -out mydb")
    print(f"  4. blastdbcmd -db nr -entry all -out nr_sequences.fasta")
    print(f"  5. blast_formatter -archive archive.tar -outfmt 7 -out formatted_results.txt")

    print(f"\n✅ BLAST CLI demonstration completed!")
    print(f"📁 Results saved in the 'results' directory")
    print(f"💡 Try running individual commands for specific analyses")

if __name__ == "__main__":
    main()