# tests/conftest.py
"""
Shared fixtures for BLAST demo tests.

This module provides common fixtures for testing BLAST demonstration scripts:
- Path fixtures for project directories
- Sequence fixtures for FASTA data
- Mock BLAST results (tabular and XML formats)
- Subprocess and BioPython mocks
- Temporary file fixtures
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from io import StringIO


# ============ Path Fixtures ============


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root):
    """Return the data directory path."""
    return project_root / "data"


@pytest.fixture
def scripts_dir(project_root):
    """Return the scripts directory path."""
    return project_root / "scripts"


@pytest.fixture
def test_data_dir():
    """Return the tests/data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def results_dir(project_root, tmp_path):
    """Return a temporary results directory for testing."""
    results = tmp_path / "results"
    results.mkdir(exist_ok=True)
    return results


# ============ Sequence Fixtures ============


@pytest.fixture
def sample_fasta_content():
    """Return a minimal valid FASTA content."""
    return ">test_protein\nMKVLWAALLVTFLTCVAP\n"


@pytest.fixture
def egfr_sequence_path(data_dir):
    """Return path to EGFR protein FASTA file."""
    return data_dir / "egfr_protein.fasta"


# ============ Mock BLAST Results ============


@pytest.fixture
def mock_tabular_result():
    """Return mock tabular BLAST result (outfmt 6).

    Columns: qseqid, sseqid, pident, length, mismatch, gapopen,
             qstart, qend, sstart, send, evalue, bitscore
    """
    return """query_test\tgi|123456789|ref|NP_001234.1|\t100.00\t18\t0\t0\t1\t18\t1\t18\t2e-10\t40.0
query_test\tgi|987654321|ref|NP_005678.1|\t95.00\t18\t1\t0\t1\t18\t1\t18\t1e-08\t38.0
query_test\tgi|111111111|ref|NP_009999.1|\t90.00\t18\t2\t0\t1\t18\t1\t18\t5e-07\t35.0
"""


@pytest.fixture
def mock_xml_result():
    """Return mock XML BLAST result (outfmt 5)."""
    return """<?xml version="1.0"?>
<!DOCTYPE BlastOutput PUBLIC "-//NCBI//NCBI BlastOutput/EN" "NCBI_BlastOutput.dtd">
<BlastOutput>
  <BlastOutput_program>blastp</BlastOutput_program>
  <BlastOutput_version>BLASTP 2.15.0+</BlastOutput_version>
  <BlastOutput_reference>Reference: Altschul et al.</BlastOutput_reference>
  <BlastOutput_db>nr</BlastOutput_db>
  <BlastOutput_query-ID>Query_1</BlastOutput_query-ID>
  <BlastOutput_query-def>test_protein</BlastOutput_query-def>
  <BlastOutput_query-len>50</BlastOutput_query-len>
  <BlastOutput_iterations>
    <Iteration>
      <Iteration_iter-num>1</Iteration_iter-num>
      <Iteration_query-ID>Query_1</Iteration_query-ID>
      <Iteration_query-def>test_protein</Iteration_query-def>
      <Iteration_query-len>50</Iteration_query-len>
      <Iteration_hits>
        <Hit>
          <Hit_num>1</Hit_num>
          <Hit_id>gi|123456789|ref|NP_001234.1|</Hit_id>
          <Hit_def>Test protein Homo sapiens</Hit_def>
          <Hit_accession>NP_001234</Hit_accession>
          <Hit_len>100</Hit_len>
          <Hit_hsps>
            <Hsp>
              <Hsp_bit-score>180</Hsp_bit-score>
              <Hsp_score>100</Hsp_score>
              <Hsp_evalue>1e-50</Hsp_evalue>
              <Hsp_query-from>1</Hsp_query-from>
              <Hsp_query-to>50</Hsp_query-to>
              <Hsp_hit-from>1</Hsp_hit-from>
              <Hsp_hit-to>50</Hsp_hit-to>
              <Hsp_identity>50</Hsp_identity>
              <Hsp_positive>50</Hsp_positive>
              <Hsp_align-len>50</Hsp_align-len>
              <Hsp_qseq>MKVLWAALLVTFLTCVAPMKVLWAALLVTFLTCVAPMKVLWAALLVTFLTCVA</Hsp_qseq>
              <Hsp_hseq>MKVLWAALLVTFLTCVAPMKVLWAALLVTFLTCVAPMKVLWAALLVTFLTCVA</Hsp_hseq>
            </Hsp>
          </Hit_hsps>
        </Hit>
        <Hit>
          <Hit_num>2</Hit_num>
          <Hit_id>gi|987654321|ref|NP_005678.1|</Hit_id>
          <Hit_def>Similar protein Mus musculus</Hit_def>
          <Hit_accession>NP_005678</Hit_accession>
          <Hit_len>95</Hit_len>
          <Hit_hsps>
            <Hsp>
              <Hsp_bit-score>170</Hsp_bit-score>
              <Hsp_score>95</Hsp_score>
              <Hsp_evalue>1e-45</Hsp_evalue>
              <Hsp_query-from>1</Hsp_query-from>
              <Hsp_query-to>48</Hsp_query-to>
              <Hsp_hit-from>1</Hsp_hit-from>
              <Hsp_hit-to>48</Hsp_hit-to>
              <Hsp_identity>46</Hsp_identity>
              <Hsp_positive>47</Hsp_positive>
              <Hsp_align-len>48</Hsp_align-len>
            </Hsp>
          </Hit_hsps>
        </Hit>
      </Iteration_hits>
    </Iteration>
  </BlastOutput_iterations>
</BlastOutput>
"""


# ============ Subprocess Mock Fixtures ============


@pytest.fixture
def mock_subprocess_success(mocker):
    """Mock successful subprocess.run call."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "blastp: 2.15.0+\nPackage: blast 2.15.0"
    mock_result.stderr = ""
    mocker.patch("subprocess.run", return_value=mock_result)
    return mock_result


@pytest.fixture
def mock_subprocess_failure(mocker):
    """Mock failed subprocess.run call."""
    from subprocess import CalledProcessError

    mock_error = CalledProcessError(
        returncode=1,
        cmd=["blastp", "-query", "test.fasta"],
        stderr="Error: database not found",
    )
    mocker.patch("subprocess.run", side_effect=mock_error)
    return mock_error


@pytest.fixture
def mock_subprocess_not_found(mocker):
    """Mock FileNotFoundError for missing BLAST tools."""
    mocker.patch("subprocess.run", side_effect=FileNotFoundError("blastp not found"))


# ============ BioPython Mock Fixtures ============


@pytest.fixture
def mock_seq_record():
    """Mock BioPython SeqRecord object."""
    try:
        from Bio.SeqRecord import SeqRecord
        from Bio.Seq import Seq

        return SeqRecord(
            Seq("MKVLWAALLVTFLTCVAP"),
            id="test_protein",
            description="Test protein sequence",
        )
    except ImportError:
        # Return a simple mock if BioPython not available
        mock_record = MagicMock()
        mock_record.id = "test_protein"
        mock_record.description = "Test protein sequence"
        mock_record.seq = "MKVLWAALLVTFLTCVAP"
        return mock_record


@pytest.fixture
def mock_ncbiwww_qblast(mocker, mock_xml_result):
    """Mock NCBIWWW.qblast to return XML result without network call."""
    mock_handle = MagicMock()
    mock_handle.read.return_value = mock_xml_result
    mock_handle.seek = MagicMock()
    mock_handle.close = MagicMock()
    mocker.patch("Bio.Blast.NCBIWWW.qblast", return_value=mock_handle)
    return mock_handle


@pytest.fixture
def mock_ncbixml_parse(mocker, mock_xml_result):
    """Mock NCBIXML.parse to return parsed BLAST records."""
    mocker.patch("Bio.Blast.NCBIXML.parse", return_value=[])
    return StringIO(mock_xml_result)


# ============ File System Fixtures ============


@pytest.fixture
def temp_fasta_file(tmp_path, sample_fasta_content):
    """Create a temporary FASTA file for testing."""
    fasta_file = tmp_path / "test_query.fasta"
    fasta_file.write_text(sample_fasta_content)
    return fasta_file


@pytest.fixture
def temp_results_file(tmp_path, mock_tabular_result):
    """Create a temporary results file for testing parsing."""
    results_file = tmp_path / "blast_results.txt"
    results_file.write_text(mock_tabular_result)
    return results_file


@pytest.fixture
def temp_xml_results_file(tmp_path, mock_xml_result):
    """Create a temporary XML results file for testing."""
    xml_file = tmp_path / "blast_results.xml"
    xml_file.write_text(mock_xml_result)
    return xml_file


@pytest.fixture
def empty_results_file(tmp_path):
    """Create an empty results file for testing edge cases."""
    empty_file = tmp_path / "empty_results.txt"
    empty_file.write_text("")
    return empty_file


# ============ Sample Data Fixtures ============


@pytest.fixture
def sample_hits_data():
    """Return sample hits data structure for blast_demo tests."""
    return [
        {
            "rank": 1,
            "hit_description": "Test protein Homo sapiens",
            "accession": "NP_001234",
            "length": 100,
            "e_value": 1e-50,
            "bit_score": 180,
            "percent_identity": 100.0,
            "query_coverage": 100.0,
        },
        {
            "rank": 2,
            "hit_description": "Similar protein Mus musculus",
            "accession": "NP_005678",
            "length": 95,
            "e_value": 1e-45,
            "bit_score": 170,
            "percent_identity": 95.0,
            "query_coverage": 96.0,
        },
    ]


# ============ Marker Definitions ============


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (no external dependencies)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (may require BLAST tools)"
    )
    config.addinivalue_line("markers", "network: Tests requiring network access")
    config.addinivalue_line("markers", "slow: Slow-running tests")
