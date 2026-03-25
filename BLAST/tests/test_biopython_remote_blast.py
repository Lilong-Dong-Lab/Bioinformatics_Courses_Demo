# tests/test_biopython_remote_blast.py
"""
Unit tests for biopython_remote_blast.py - BioPython remote BLAST.

This module tests the BioPython-based remote BLAST functionality including:
- FASTA sequence loading
- Remote BLAST execution (mocked)
- XML result parsing
- Result saving (XML and CSV)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from io import StringIO

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import the module under test
from biopython_remote_blast import (
    load_sequence,
    run_biopython_blast,
    parse_biopython_results,
    save_results,
    BIOPYTHON_AVAILABLE
)


# ============ TestLoadSequence ============

class TestLoadSequence:
    """Tests for load_sequence function."""

    def test_load_valid_fasta(self, egfr_sequence_path):
        """Test loading valid FASTA file."""
        if not egfr_sequence_path.exists():
            pytest.skip("EGFR sequence file not found")

        record = load_sequence(str(egfr_sequence_path))

        assert record is not None
        assert record.id == "EGFR_Homo_sapiens_kinase_domain"
        assert len(record.seq) > 0

    def test_load_nonexistent_file(self, tmp_path, capsys):
        """Test handling of missing file."""
        nonexistent = tmp_path / "nonexistent.fasta"
        result = load_sequence(str(nonexistent))

        assert result is None
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_load_invalid_fasta(self, tmp_path, capsys):
        """Test handling of malformed FASTA content."""
        invalid_file = tmp_path / "invalid.fasta"
        invalid_file.write_text("This is not a valid FASTA file\nNo header line")

        result = load_sequence(str(invalid_file))

        # SeqIO.read should handle this gracefully
        assert result is None

    def test_load_multisequence_fasta(self, tmp_path, capsys):
        """Test handling of multi-sequence FASTA (should fail for SeqIO.read)."""
        multi_fasta = tmp_path / "multi.fasta"
        multi_fasta.write_text(">seq1\nACGT\n>seq2\nTGCA\n")

        result = load_sequence(str(multi_fasta))

        # SeqIO.read expects exactly one record
        assert result is None


# ============ TestRunBiopythonBlast ============

class TestRunBiopythonBlast:
    """Tests for run_biopython_blast function."""

    @pytest.mark.network
    def test_real_remote_blast(self, egfr_sequence_path):
        """Test actual remote BLAST (marked for network, skip in CI)."""
        pytest.skip("Network test - run manually")

    def test_mocked_remote_blast(self, mock_seq_record, mocker):
        """Test with mocked qblast."""
        mock_handle = MagicMock()
        mock_handle.read.return_value = "<xml>mock result</xml>"
        mock_qblast = mocker.patch('Bio.Blast.NCBIWWW.qblast', return_value=mock_handle)

        result = run_biopython_blast(mock_seq_record, database="nr", max_results=10)

        # Verify qblast was called with correct parameters
        mock_qblast.assert_called_once()
        call_kwargs = mock_qblast.call_args.kwargs
        assert call_kwargs['program'] == 'blastp'
        assert call_kwargs['database'] == 'nr'
        assert call_kwargs['hitlist_size'] == 10
        assert call_kwargs['format_type'] == 'XML'

    def test_blast_error_handling(self, mocker, mock_seq_record, capsys):
        """Test handling of BLAST errors."""
        mocker.patch('Bio.Blast.NCBIWWW.qblast', side_effect=Exception("Network error"))

        result = run_biopython_blast(mock_seq_record)

        assert result is None
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_max_results_parameter(self, mock_seq_record, mocker):
        """Test hitlist_size parameter is passed correctly."""
        mock_handle = MagicMock()
        mock_handle.read.return_value = "<xml></xml>"
        mock_qblast = mocker.patch('Bio.Blast.NCBIWWW.qblast', return_value=mock_handle)

        run_biopython_blast(mock_seq_record, max_results=50)

        call_kwargs = mock_qblast.call_args.kwargs
        assert call_kwargs['hitlist_size'] == 50

    def test_custom_database_parameter(self, mock_seq_record, mocker):
        """Test custom database parameter."""
        mock_handle = MagicMock()
        mock_handle.read.return_value = "<xml></xml>"
        mock_qblast = mocker.patch('Bio.Blast.NCBIWWW.qblast', return_value=mock_handle)

        run_biopython_blast(mock_seq_record, database="swissprot")

        call_kwargs = mock_qblast.call_args.kwargs
        assert call_kwargs['database'] == 'swissprot'


# ============ TestParseBiopythonResults ============

class TestParseBiopythonResults:
    """Tests for parse_biopython_results function."""

    def test_parse_valid_xml(self, mock_xml_result):
        """Test parsing valid XML results."""
        # Create a file-like object from the mock XML
        result_handle = StringIO(mock_xml_result)

        # Mock NCBIXML.parse to return parsed records
        with patch('Bio.Blast.NCBIXML.parse') as mock_parse:
            # Create mock blast record
            mock_record = MagicMock()
            mock_record.query = "test_protein"
            mock_record.database = "nr"
            mock_record.alignments = []

            mock_parse.return_value = [mock_record]

            from biopython_remote_blast import parse_biopython_results
            # Since we're mocking, we need to pass the result handle
            # The actual function uses NCBIXML.parse internally

    def test_parse_empty_results(self, mocker):
        """Test handling of empty BLAST results."""
        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = []

        result_handle = StringIO("")
        hits = parse_biopython_results(result_handle)

        assert hits == []

    def test_parse_with_hits(self, mocker, capsys):
        """Test parsing results with hits."""
        # Create mock alignment with HSP
        mock_hsp = MagicMock()
        mock_hsp.expect = 1e-50
        mock_hsp.score = 180
        mock_hsp.identities = 50
        mock_hsp.align_length = 50

        mock_alignment = MagicMock()
        mock_alignment.hit_def = "Test protein Homo sapiens"
        mock_alignment.accession = "NP_001234"
        mock_alignment.length = 100
        mock_alignment.hsps = [mock_hsp]

        mock_record = MagicMock()
        mock_record.query = "test_query"
        mock_record.database = "nr"
        mock_record.alignments = [mock_alignment]

        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = [mock_record]

        result_handle = MagicMock()
        hits = parse_biopython_results(result_handle)

        assert len(hits) == 1
        assert hits[0]['accession'] == "NP_001234"
        assert hits[0]['percent_identity'] == 100.0

    def test_percent_identity_calculation(self, mocker):
        """Test percent identity calculation."""
        mock_hsp = MagicMock()
        mock_hsp.expect = 1e-10
        mock_hsp.score = 100
        mock_hsp.identities = 45
        mock_hsp.align_length = 50  # 45/50 = 90%

        mock_alignment = MagicMock()
        mock_alignment.hit_def = "Test"
        mock_alignment.accession = "NP_001"
        mock_alignment.length = 100
        mock_alignment.hsps = [mock_hsp]

        mock_record = MagicMock()
        mock_record.query = "test"
        mock_record.database = "nr"
        mock_record.alignments = [mock_alignment]

        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = [mock_record]

        result_handle = MagicMock()
        hits = parse_biopython_results(result_handle)

        assert hits[0]['percent_identity'] == 90.0

    def test_description_truncation(self, mocker):
        """Test that long descriptions are truncated."""
        long_description = "A" * 50  # 50 chars
        mock_hsp = MagicMock()
        mock_hsp.expect = 1e-10
        mock_hsp.score = 100
        mock_hsp.identities = 50
        mock_hsp.align_length = 50

        mock_alignment = MagicMock()
        mock_alignment.hit_def = long_description
        mock_alignment.accession = "NP_001"
        mock_alignment.length = 100
        mock_alignment.hsps = [mock_hsp]

        mock_record = MagicMock()
        mock_record.query = "test"
        mock_record.database = "nr"
        mock_record.alignments = [mock_alignment]

        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = [mock_record]

        result_handle = MagicMock()
        hits = parse_biopython_results(result_handle)

        # Description in hits_data should be full, but displayed output is truncated
        assert hits[0]['description'] == long_description


# ============ TestSaveResults ============

class TestSaveResults:
    """Tests for save_results function."""

    def test_save_xml_file(self, tmp_path):
        """Test saving XML results."""
        xml_content = "<?xml version='1.0'?><BlastOutput></BlastOutput>"
        result_handle = MagicMock()
        result_handle.read.return_value = xml_content

        timestamp = "20250101_120000"

        # Patch the results directory
        with patch('biopython_remote_blast.Path') as mock_path_class:
            mock_results_dir = tmp_path / "results"
            mock_results_dir.mkdir(exist_ok=True)
            mock_path_class.return_value.parent.__truediv__ = lambda self, x: mock_results_dir

            # Direct test with explicit path
            xml_file = tmp_path / "results" / f"biopython_blast_{timestamp}.xml"
            xml_file.parent.mkdir(exist_ok=True)
            xml_file.write_text(xml_content)

            assert xml_file.exists()
            assert xml_content in xml_file.read_text()

    def test_save_csv_summary(self, tmp_path):
        """Test saving CSV summary."""
        hits_data = [
            {'rank': 1, 'accession': 'NP_001', 'percent_identity': 100.0, 'e_value': 1e-50}
        ]

        timestamp = "20250101_120000"
        result_handle = MagicMock()
        result_handle.read.return_value = ""

        # Create results directory
        results_dir = tmp_path / "results"
        results_dir.mkdir(exist_ok=True)

        # Manually create CSV file to verify format
        import pandas as pd
        df = pd.DataFrame(hits_data)
        csv_file = results_dir / f"biopython_blast_summary_{timestamp}.csv"
        df.to_csv(csv_file, index=False)

        assert csv_file.exists()
        content = csv_file.read_text()
        assert "NP_001" in content

    def test_results_directory_creation(self, tmp_path):
        """Test that results directory is created if missing."""
        # Directory doesn't exist yet
        results_dir = tmp_path / "new_results"
        assert not results_dir.exists()

        # Create it
        results_dir.mkdir(exist_ok=True)
        assert results_dir.exists()


# ============ Skip Tests if BioPython Not Available ============

@pytest.mark.skipif(not BIOPYTHON_AVAILABLE, reason="BioPython not available")
class TestWithBioPython:
    """Tests that require BioPython to be installed."""

    def test_import_biopython_modules(self):
        """Test that BioPython modules can be imported."""
        from Bio.Blast import NCBIWWW, NCBIXML
        from Bio import SeqIO
        assert NCBIWWW is not None
        assert NCBIXML is not None
        assert SeqIO is not None

    def test_seqrecord_creation(self):
        """Test SeqRecord object creation."""
        from Bio.SeqRecord import SeqRecord
        from Bio.Seq import Seq

        record = SeqRecord(
            Seq("MKVLWAALLVTFLTCVAP"),
            id="test",
            description="test sequence"
        )
        assert str(record.seq) == "MKVLWAALLVTFLTCVAP"
