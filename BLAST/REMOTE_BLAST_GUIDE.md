# Remote BLAST Complete Guide

This guide covers all methods for running BLAST searches over the Internet using your BRCA1 protein sequence.

## 🌐 Remote BLAST Options

### Option 1: NCBI Web Interface (Most Reliable)

**URL**: https://blast.ncbi.nlm.nih.gov/Blast.cgi

**Steps**:
1. Go to the website
2. Select "Protein BLAST" (blastp)
3. Paste your BRCA1 sequence:
```fasta
>BRCA1_Homo_sapiens_RING_finger_domain
MGDSDCKTCVQEGELDKLLKQFPEVLEAASLDKKRFGQDVLEAEDGELKDKTKELDKQKELR
```
4. Database: Choose "Non-redundant protein sequences (nr)"
5. Click "BLAST"
6. Wait 30-120 seconds for results

**Pros**:
- Most reliable method
- User-friendly interface
- No rate limiting
- Rich visualization options

**Cons**:
- Manual process
- Limited to single sequences at a time

### Option 2: Alternative Web Services

#### EMBL-EBI BLAST
- **URL**: https://www.ebi.ac.uk/Tools/sss/sequencesearch/
- **Pros**: Often faster than NCBI, European servers
- **Cons**: Different database versions

#### UniProt BLAST
- **URL**: https://www.uniprot.org/blast/
- **Pros**: High-quality curated protein sequences
- **Cons**: Smaller database than NCBI nr

### Option 3: BioPython Remote BLAST (Programmatic)

**Command**: `pixi run run-biopython-blast`

**Advantages**:
- Can be automated
- More reliable than command-line remote BLAST
- Can parse results programmatically

**Example Code**:
```python
from Bio.Blast import NCBIWWW
from Bio import SeqIO

# Load sequence
record = SeqIO.read("sequence.fasta", "fasta")

# Set email (required)
NCBIWWW.email = "your.email@example.com"

# Run BLAST
result_handle = NCBIWWW.qblast(
    program="blastp",
    database="nr",
    sequence=record.seq,
    hitlist_size=10,
    expect=0.001
)

# Parse results
from Bio.Blast import NCBIXML
blast_records = NCBIXML.parse(result_handle)
```

### Option 4: Command Line Remote BLAST (Limited)

**Commands**:
```bash
# Basic remote BLAST
pixi exec blastp -query data/brca1_protein_proper.fasta -db nr -remote -out results.txt

# With specific organism filter
pixi exec blastp -query data/brca1_protein_proper.fasta -db nr -remote -out results.txt -entrez_query "Homo sapiens[Organism]"

# Use smaller database (more reliable)
pixi exec blastp -query data/brca1_protein_proper.fasta -db swissprot -remote -out results.txt
```

**Limitations**:
- Often blocked by NCBI rate limiting
- Can be aborted by Entrez (as we experienced)
- Less reliable than web interface

## 📊 Database Choices

### Protein Databases:
- **nr**: Non-redundant protein sequences (largest, most comprehensive)
- **refseq**: Reference sequences (curated, high quality)
- **swissprot**: UniProt/Swiss-Prot (manually annotated)
- **pat**: Patent sequences
- **pdb**: Protein Data Bank sequences

### Nucleotide Databases (for DNA/RNA sequences):
- **nt**: Nucleotide collection
- **refseq_rna**: Reference RNA sequences
- **est**: Expressed sequence tags

## ⚡ Tips for Successful Remote BLAST

1. **Use Web Interface** for most reliable results
2. **Try Off-Peak Hours** (early morning/late evening)
3. **Use Short Sequences** for faster results
4. **Limit to Specific Organisms** when possible:
   ```bash
   -entrez_query "Homo sapiens[Organism]"
   ```
5. **Use Appropriate E-value Thresholds**:
   - 0.001 for protein searches
   - 1e-5 for more stringent searches
6. **Have Alternative Plans** if one service is down

## 🚨 Common Issues and Solutions

### Rate Limiting
- **Problem**: "search aborted by Entrez"
- **Solution**: Use web interface or try again later

### No Results Found
- **Problem**: Sequence too short or unusual
- **Solution**: Try longer sequence or different database

### Timeouts
- **Problem**: Search takes too long
- **Solution**: Use smaller database or limit organism

### Network Issues
- **Problem**: Cannot connect to NCBI
- **Solution**: Check internet connection, try alternative services

## 📝 Quick Start Commands

```bash
# Install environment (if not done)
pixi install

# Test local BLAST
pixi run run-blast

# Test BioPython remote BLAST
pixi run run-biopython-blast

# Test command line remote BLAST (may fail due to rate limiting)
pixi run run-remote-blast
```

## 🎯 Recommendation

For educational purposes and occasional searches:
1. **Use NCBI Web Interface** - most reliable
2. **Use BioPython Script** - for programmatic access
3. **Avoid Command Line Remote BLAST** - often rate limited

For frequent analyses:
1. **Download local databases** using `update_blastdb.pl`
2. **Use local BLAST** for consistent, fast results
3. **Save databases** locally to avoid network dependencies

## 📚 Additional Resources

- [NCBI BLAST Documentation](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs)
- [BioPython BLAST Tutorial](https://biopython.org/docs/dev/Tutorial/chapter_blast.html)
- [EMBL-EBI Tools](https://www.ebi.ac.uk/services)
- [UniProt BLAST](https://www.uniprot.org/help/blast)

---

💡 **Pro Tip**: Save your favorite BLAST searches as bookmarks for quick access!