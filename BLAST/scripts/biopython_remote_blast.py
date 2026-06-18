#!/usr/bin/env python3
"""
BioPython Remote BLAST Demo (EGFR)
===================================

This script demonstrates remote BLAST using BioPython's NCBIWWW module.
This is often more reliable than command-line remote BLAST.

Target: EGFR kinase domain (NSCLC drug target)

Based on official BioPython documentation:
https://biopython.org/docs/dev/Tutorial/chapter_blast.html#sec-running-www-blast

Author: Bioinformatics Course Demo
Date: 2025-11-14
Updated: 2026-03-24 (aligned with lecture materials)


Script Overview (脚本概述)
==========================

This script provides a Python-based approach to perform remote BLAST searches
against NCBI databases using the BioPython library. Unlike command-line BLAST,
it offers better error handling and programmatic access to results.

本脚本使用BioPython库对NCBI数据库进行远程BLAST搜索。相比命令行BLAST，
它提供更好的错误处理和程序化结果访问能力。


Key BioPython Modules (核心BioPython模块)
==========================================

1. Bio.Blast.NCBIWWW - Remote BLAST Interface (远程BLAST接口)
   ---------------------------------------------------------
   The NCBIWWW module provides the qblast() function to submit BLAST searches
   to NCBI's web server programmatically.

   NCBIWWW模块提供qblast()函数，用于程序化地向NCBI服务器提交BLAST搜索。

   Key function: NCBIWWW.qblast()
   Parameters:
   - program: BLAST program type (blastp, blastn, blastx, etc.)
     (BLAST程序类型: blastp蛋白质, blastn核酸, blastx翻译等)

   - database: Target database name
     (目标数据库名称)
     Common options:
     • "nr" - Non-redundant protein sequences (非冗余蛋白质序列)
     • "refseq_protein" - NCBI Reference Sequence proteins
     • "swissprot" - UniProtKB/Swiss-Prot curated proteins
     • "pdb" - Protein Data Bank structures

   - sequence: Query sequence (string or Seq object)
     (查询序列，可以是字符串或Seq对象)

   - hitlist_size: Maximum number of hits to return
     (返回的最大匹配数)

   - expect: E-value threshold (default 10.0)
     (E值阈值，默认10.0，建议0.001或更小)

   - format_type: Output format ("XML", "HTML", "Text")
     (输出格式，XML最便于程序解析)

   Important: Set NCBIWWW.email before calling qblast()
   (重要: 调用qblast()前需设置email地址)
   NCBI requires email for tracking and contact purposes.


2. Bio.SeqIO - Sequence Input/Output (序列输入/输出)
   --------------------------------------------------
   SeqIO module handles reading and writing sequence files in various formats.

   SeqIO模块处理各种格式的序列文件读写。

   Key function: SeqIO.read()
   Parameters:
   - file: File path or file handle
     (文件路径或文件句柄)

   - format: File format ("fasta", "genbank", "fastq", etc.)
     (文件格式)

   Returns: SeqRecord object containing:
   - record.id: Sequence identifier (序列标识符)
   - record.seq: Sequence data as Seq object (序列数据)
   - record.description: Full description line (完整描述行)
   - record.annotations: Metadata dictionary (元数据字典)


3. Bio.Blast.NCBIXML - XML Result Parser (XML结果解析器)
   ------------------------------------------------------
   NCBIXML parses XML-formatted BLAST results into Python objects.

   NCBIXML将XML格式的BLAST结果解析为Python对象。

   Key function: NCBIXML.parse()
   Parameters:
   - handle: File handle containing XML data
     (包含XML数据的文件句柄)

   Returns: Iterator of Blast.Record objects

   Key attributes of parsed records:
   - record.query: Query sequence name (查询序列名称)
   - record.database: Database searched (搜索的数据库)
   - record.alignments: List of Alignment objects (比对结果列表)

   Alignment object attributes:
   - alignment.hit_def: Hit definition/description (匹配描述)
   - alignment.accession: Accession number (登录号)
   - alignment.length: Alignment length (比对长度)
   - alignment.hsps: List of HSP objects (高保守区段列表)

   HSP (High-Scoring Pair) attributes:
   - hsp.expect: E-value (期望值)
   - hsp.score: Raw score (原始得分)
   - hsp.bits: Bit score (比特得分)
   - hsp.identities: Number of identical positions (相同位置数)
   - hsp.align_length: Total alignment length (总比对长度)
   - hsp.query: Query sequence segment (查询序列片段)
   - hsp.sbjct: Subject sequence segment (目标序列片段)


Script Workflow (脚本工作流程)
==============================

Step 1: Load Sequence (加载序列)
   Function: load_sequence()
   - Reads FASTA file using SeqIO.read()
   - Extracts sequence ID and length
   - Returns SeqRecord object

Step 2: Run Remote BLAST (执行远程BLAST)
   Function: run_biopython_blast()
   - Sets email for NCBI tracking
   - Calls NCBIWWW.qblast() with parameters
   - Returns result handle (file-like object containing XML)

Step 3: Parse Results (解析结果)
   Function: parse_biopython_results()
   - Parses XML using NCBIXML.parse()
   - Extracts key metrics from each alignment
   - Calculates percent identity: (identities / align_length) * 100
   - Returns list of hit dictionaries

Step 4: Save Results (保存结果)
   Function: save_results()
   - Saves raw XML for future reference
   - Creates CSV summary using pandas
   - Files named with timestamp for organization


Comparison: BioPython vs CLI Remote BLAST
=========================================
(BioPython与命令行远程BLAST对比)

┌────────────────────┬─────────────────────┬─────────────────────┐
│ Feature            │ BioPython           │ CLI Remote BLAST    │
├────────────────────┼─────────────────────┼─────────────────────┤
│ Reliability        │ ✓ More stable       │ ✗ Rate limiting     │
│ Error handling     │ ✓ Python exceptions │ ✗ Exit codes only   │
│ Result access      │ ✓ Direct objects    │ ✗ File parsing      │
│ Automation         │ ✓ Easy integration  │ △ Subprocess calls  │
│ Speed              │ △ Same as CLI       │ △ Same as BioPython │
│ Learning curve     │ △ Python required   │ ✓ Simple commands   │
│ Offline use        │ ✗ Requires network  │ ✗ Requires network  │
└────────────────────┴─────────────────────┴─────────────────────┘

Recommendation: Use BioPython for scripts and automation; use CLI for
quick one-off queries.
(建议: 脚本和自动化使用BioPython; 快速查询使用命令行)


Common Issues and Solutions (常见问题与解决方案)
================================================

1. "HTTP Error 429: Too Many Requests"
   - Cause: NCBI rate limiting (原因: NCBI频率限制)
   - Solution: Wait 10-60 seconds between requests
     (解决: 请求间隔10-60秒)

2. "Connection refused" or timeout
   - Cause: Network issues or NCBI maintenance
     (原因: 网络问题或NCBI维护)
   - Solution: Check internet connection, try again later
     (解决: 检查网络连接，稍后重试)

3. Empty results
   - Cause: E-value threshold too strict or no similar sequences
     (原因: E值阈值过严或无相似序列)
   - Solution: Increase expect parameter (e.g., 0.01 or 1.0)
     (解决: 增大expect参数)

4. Import errors
   - Cause: BioPython not installed
     (原因: BioPython未安装)
   - Solution: pixi add biopython (or pip install biopython)
     (解决: 安装BioPython)


Output Files (输出文件)
=======================

1. biopython_blast_YYYYMMDD_HHMMSS.xml
   - Complete BLAST results in XML format
   - Can be re-parsed later without re-running BLAST
   - (完整的XML格式BLAST结果，可后续重新解析)

2. biopython_blast_summary_YYYYMMDD_HHMMSS.csv
   - Tabular summary with columns:
     rank, accession, description, length, e_value, bit_score, percent_identity
   - (表格格式摘要，包含关键指标)


Best Practices (最佳实践)
=========================

1. Always set email before calling qblast()
   (调用qblast()前始终设置email)

2. Use appropriate E-value threshold for your use case
   (根据需求选择合适的E值阈值)
   - Conservative: expect=0.001 (fewer false positives)
   - Exploratory: expect=0.01 or 1.0 (more hits)

3. Save XML results for reproducibility
   (保存XML结果以确保可重复性)

4. Handle exceptions gracefully in production code
   (生产代码中妥善处理异常)

5. Respect NCBI's usage guidelines:
   - No more than 100 searches per minute
   - Run large batch jobs during off-peak hours (US night time)
   (遵守NCBI使用指南: 每分钟不超过100次搜索)
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
    print("\n🌐 Running BioPython Remote BLAST...")
    print(f"  Database: {database}")
    print(f"  Query length: {len(sequence.seq)}")
    print(f"  Max results: {max_results}")
    print("  This may take 1-3 minutes...")

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
            format_type="XML",
        )

        print("✓ BLAST search completed!")
        return result_handle

    except Exception as e:
        print(f"✗ Error during BLAST search: {e}")
        return None


def parse_biopython_results(result_handle):
    """Parse and display BLAST results."""
    print("\n📊 Parsing BLAST Results...")

    try:
        # Reset stream position in case it was read before
        result_handle.seek(0)

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

        print("\n📋 Top BLAST Hits:")
        print("-" * 100)
        print(
            f"{'Rank':<5} {'Accession':<15} {'Description':<30} {'% Identity':<12} {'E-value':<12}"
        )
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

            hits_data.append(
                {
                    "rank": i + 1,
                    "accession": accession,
                    "description": hit_def,
                    "length": length,
                    "e_value": e_value,
                    "bit_score": score,
                    "percent_identity": percent_identity,
                }
            )

            print(
                f"{i + 1:<5} {accession:<15} {short_desc:<30} {percent_identity:<12.1f} {e_value:<12.2e}"
            )

        return hits_data

    except Exception as e:
        print(f"✗ Error parsing results: {e}")
        return []


def save_results(result_handle, hits_data, timestamp):
    """Save BLAST results to files."""
    try:
        # Save raw XML - reset stream position first
        results_dir = "../results"
        Path(results_dir).mkdir(exist_ok=True)

        result_handle.seek(0)
        xml_file = f"{results_dir}/biopython_blast_{timestamp}.xml"
        with open(xml_file, "w") as f:
            f.write(result_handle.read())

        # Save summary
        if hits_data:
            import pandas as pd

            df = pd.DataFrame(hits_data)
            csv_file = f"{results_dir}/biopython_blast_summary_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print("\n💾 Results saved:")
            print(f"  XML: {xml_file}")
            print(f"  CSV: {csv_file}")

    except Exception as e:
        print(f"✗ Error saving results: {e}")


def main():
    """Main function to run BioPython BLAST demonstration."""
    print("🧬 BioPython Remote BLAST Demonstration (EGFR)")
    print("=" * 60)
    print("Target: EGFR kinase domain (NSCLC drug target)")

    if not BIOPYTHON_AVAILABLE:
        print("❌ BioPython not available. Please install it first.")
        sys.exit(1)

    # Load sequence
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    query_file = os.path.join(project_dir, "data", "egfr_protein.fasta")

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

    print("\n✅ BioPython BLAST demonstration completed!")


if __name__ == "__main__":
    main()
