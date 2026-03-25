# tests/test_blast_demo.py
"""
Unit tests for blast_demo.py - Extended BLAST demo with visualization.

This module tests the extended BLAST demonstration functionality including:
- Sequence loading
- BLAST search execution (mocked)
- Result parsing
- DataFrame summary creation
- Matplotlib visualization
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import the module under test (may fail if BioPython not available)
try:
    from blast_demo import (
        load_sequence,
        perform_blast_search,
        parse_blast_results,
        create_summary_table,
        plot_blast_results
    )
    BLAST_DEMO_AVAILABLE = True
except ImportError:
    BLAST_DEMO_AVAILABLE = False


# ============ TestLoadSequence ============

@pytest.mark.skipif(not BLAST_DEMO_AVAILABLE, reason="blast_demo.py dependencies not available")
class TestLoadSequence:
    """Tests for load_sequence function."""

    def test_load_egfr_sequence(self, egfr_sequence_path):
        """Test loading EGFR sequence."""
        if not egfr_sequence_path.exists():
            pytest.skip("EGFR sequence file not found")

        record = load_sequence(str(egfr_sequence_path))

        assert record is not None
        assert len(record.seq) > 0

    def test_sequence_attributes(self, egfr_sequence_path):
        """Test that sequence has correct attributes."""
        if not egfr_sequence_path.exists():
            pytest.skip("EGFR sequence file not found")

        record = load_sequence(str(egfr_sequence_path))

        assert record is not None
        assert record.id is not None
        assert record.description is not None
        assert len(record.seq) > 0

    def test_load_nonexistent_file(self, tmp_path, capsys):
        """Test handling of missing file."""
        nonexistent = tmp_path / "nonexistent.fasta"
        result = load_sequence(str(nonexistent))

        assert result is None
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_load_invalid_fasta(self, tmp_path, capsys):
        """Test handling of invalid FASTA content."""
        invalid_file = tmp_path / "invalid.fasta"
        invalid_file.write_text("Invalid content without header")

        result = load_sequence(str(invalid_file))

        assert result is None


# ============ TestPerformBlastSearch ============

@pytest.mark.skipif(not BLAST_DEMO_AVAILABLE, reason="blast_demo.py dependencies not available")
class TestPerformBlastSearch:
    """Tests for perform_blast_search function."""

    @pytest.mark.network
    def test_real_blast_search(self, mock_seq_record):
        """Test actual BLAST search (marked for network)."""
        pytest.skip("Network test - run manually")

    def test_blast_parameters(self, mock_seq_record, mocker):
        """Test correct BLAST parameters."""
        mock_handle = MagicMock()
        mock_handle.read.return_value = "<xml>results</xml>"
        mock_handle.seek = MagicMock()

        mock_qblast = mocker.patch('Bio.Blast.NCBIWWW.qblast', return_value=mock_handle)
        mocker.patch('pathlib.Path.mkdir')

        perform_blast_search(mock_seq_record, database="nr", program="blastp", max_results=10)

        call_kwargs = mock_qblast.call_args.kwargs
        assert call_kwargs['program'] == 'blastp'
        assert call_kwargs['database'] == 'nr'
        assert call_kwargs['hitlist_size'] == 10
        assert call_kwargs['expect'] == 0.001
        assert call_kwargs['format_type'] == 'XML'

    def test_result_saving(self, mock_seq_record, mock_ncbiwww_qblast, tmp_path, mocker):
        """Test that results are saved with timestamp."""
        mocker.patch('pathlib.Path.mkdir')
        mock_open = mocker.patch('builtins.open', mocker.mock_open())

        perform_blast_search(mock_seq_record)

        # Verify file was opened for writing
        assert mock_open.called

    def test_handle_seek_after_saving(self, mock_seq_record, mocker):
        """Test that handle is reset (seek(0)) after saving."""
        mock_handle = MagicMock()
        mock_handle.read.return_value = "<xml>results</xml>"
        mock_handle.seek = MagicMock()
        mock_handle.close = MagicMock()

        mocker.patch('Bio.Blast.NCBIWWW.qblast', return_value=mock_handle)
        mocker.patch('pathlib.Path.mkdir')
        mocker.patch('builtins.open', mocker.mock_open())

        result = perform_blast_search(mock_seq_record)

        # seek should have been called to reset position
        assert mock_handle.seek.called

    def test_error_handling(self, mock_seq_record, mocker, capsys):
        """Test error handling during BLAST search."""
        mocker.patch('Bio.Blast.NCBIWWW.qblast', side_effect=Exception("Network error"))

        result = perform_blast_search(mock_seq_record)

        assert result is None
        captured = capsys.readouterr()
        assert "Error" in captured.out


# ============ TestParseBlastResults ============

@pytest.mark.skipif(not BLAST_DEMO_AVAILABLE, reason="blast_demo.py dependencies not available")
class TestParseBlastResults:
    """Tests for parse_blast_results function."""

    def test_hits_data_structure(self, mocker):
        """Test that returned data has correct structure."""
        # Create mock blast record
        mock_hsp = MagicMock()
        mock_hsp.expect = 1e-50
        mock_hsp.score = 180
        mock_hsp.identities = 50
        mock_hsp.align_length = 50

        mock_alignment = MagicMock()
        mock_alignment.hit_def = "Test protein"
        mock_alignment.accession = "NP_001234"
        mock_alignment.length = 100
        mock_alignment.hsps = [mock_hsp]

        mock_record = MagicMock()
        mock_record.query = "test_query"
        mock_record.database = "nr"
        mock_record.query_length = 50
        mock_record.alignments = [mock_alignment]

        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = [mock_record]

        result_handle = MagicMock()
        hits = parse_blast_results(result_handle)

        assert len(hits) == 1
        assert 'rank' in hits[0]
        assert 'hit_description' in hits[0]
        assert 'accession' in hits[0]
        assert 'e_value' in hits[0]
        assert 'bit_score' in hits[0]
        assert 'percent_identity' in hits[0]
        assert 'query_coverage' in hits[0]

    def test_query_coverage_calculation(self, mocker):
        """Test query coverage percentage calculation."""
        mock_hsp = MagicMock()
        mock_hsp.expect = 1e-10
        mock_hsp.score = 100
        mock_hsp.identities = 45
        mock_hsp.align_length = 45  # 45/50 = 90% coverage

        mock_alignment = MagicMock()
        mock_alignment.hit_def = "Test"
        mock_alignment.accession = "NP_001"
        mock_alignment.length = 100
        mock_alignment.hsps = [mock_hsp]

        mock_record = MagicMock()
        mock_record.query = "test"
        mock_record.database = "nr"
        mock_record.query_length = 50
        mock_record.alignments = [mock_alignment]

        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = [mock_record]

        result_handle = MagicMock()
        hits = parse_blast_results(result_handle)

        # Query coverage = (align_length / query_length) * 100
        assert hits[0]['query_coverage'] == 90.0

    def test_empty_alignments_handling(self, mocker, capsys):
        """Test handling when no alignments found."""
        mock_record = MagicMock()
        mock_record.query = "test"
        mock_record.database = "nr"
        mock_record.alignments = []

        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = [mock_record]

        result_handle = MagicMock()
        hits = parse_blast_results(result_handle)

        assert hits == []

    def test_empty_records_handling(self, mocker):
        """Test handling of empty blast records."""
        mock_parse = mocker.patch('Bio.Blast.NCBIXML.parse')
        mock_parse.return_value = []

        result_handle = MagicMock()
        hits = parse_blast_results(result_handle)

        assert hits == []


# ============ TestCreateSummaryTable ============

@pytest.mark.skipif(not BLAST_DEMO_AVAILABLE, reason="blast_demo.py dependencies not available")
class TestCreateSummaryTable:
    """Tests for create_summary_table function."""

    def test_dataframe_creation(self, capsys, mocker):
        """Test that DataFrame is created from hits data."""
        sample_data = [
            {
                'rank': 1,
                'accession': 'NP_001234',
                'e_value': 1e-50,
                'percent_identity': 100.0,
                'query_coverage': 100.0,
                'hit_description': 'Test protein'
            }
        ]
        # Mock file operations to avoid directory issues
        mocker.patch('pandas.DataFrame.to_csv')
        create_summary_table(sample_data)

        captured = capsys.readouterr()
        assert "BLAST Results Summary" in captured.out or "📋 BLAST Results Summary" in captured.out
        assert "NP_001234" in captured.out

    def test_number_formatting(self, capsys, mocker):
        """Test e-value, identity, coverage formatting."""
        sample_data = [
            {
                'rank': 1,
                'accession': 'NP_001234',
                'e_value': 1e-50,
                'percent_identity': 100.0,
                'query_coverage': 100.0,
                'hit_description': 'Test protein'
            }
        ]
        # Mock file operations to avoid directory issues
        mocker.patch('pandas.DataFrame.to_csv')
        create_summary_table(sample_data)

        captured = capsys.readouterr()
        # Check for formatted output
        assert "100.0%" in captured.out or "100.0" in captured.out

    def test_empty_data_handling(self, capsys):
        """Test handling of empty hits data."""
        create_summary_table([])

        captured = capsys.readouterr()
        # Should handle gracefully without crashing
        assert "BLAST Results Summary" not in captured.out or len(captured.out) < 100


# ============ TestPlotBlastResults ============

@pytest.mark.skipif(not BLAST_DEMO_AVAILABLE, reason="blast_demo.py dependencies not available")
class TestPlotBlastResults:
    """Tests for plot_blast_results function."""

    @pytest.mark.slow
    def test_figure_creation(self, tmp_path, mocker):
        """Test that matplotlib figure is created."""
        sample_data = [
            {
                'rank': 1,
                'e_value': 1e-50,
                'percent_identity': 100.0,
                'bit_score': 180,
                'query_coverage': 100.0
            }
        ]
        # Mock matplotlib to avoid display issues
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mocker.patch('matplotlib.pyplot.subplots', return_value=(mock_fig, ((mock_ax, mock_ax), (mock_ax, mock_ax))))
        mocker.patch('matplotlib.pyplot.savefig')
        mocker.patch('matplotlib.pyplot.show')
        mocker.patch('matplotlib.pyplot.tight_layout')

        plot_blast_results(sample_data)

        # Verify subplots was called with 2x2 layout
        import matplotlib.pyplot as plt
        plt.subplots.assert_called_once_with(2, 2, figsize=(15, 10))

    def test_plot_saving(self, tmp_path, mocker, capsys):
        """Test that plot is saved to file."""
        sample_data = [
            {
                'rank': 1,
                'e_value': 1e-50,
                'percent_identity': 100.0,
                'bit_score': 180,
                'query_coverage': 100.0
            }
        ]
        # Must provide proper return value for subplots
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mocker.patch('matplotlib.pyplot.subplots', return_value=(mock_fig, ((mock_ax, mock_ax), (mock_ax, mock_ax))))
        mocker.patch('matplotlib.pyplot.tight_layout')
        mock_savefig = mocker.patch('matplotlib.pyplot.savefig')
        mocker.patch('matplotlib.pyplot.show')

        plot_blast_results(sample_data)

        assert mock_savefig.called
        captured = capsys.readouterr()
        assert "Visualization saved" in captured.out

    def test_subplot_content(self, mocker):
        """Test that subplots contain correct data types."""
        sample_data = [
            {
                'rank': 1,
                'e_value': 1e-50,
                'percent_identity': 100.0,
                'bit_score': 180,
                'query_coverage': 100.0
            }
        ]
        # This is more of an integration test
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_ax3 = MagicMock()
        mock_ax4 = MagicMock()

        mocker.patch('matplotlib.pyplot.subplots',
                     return_value=(mock_fig, ((mock_ax1, mock_ax2), (mock_ax3, mock_ax4))))
        mocker.patch('matplotlib.pyplot.savefig')
        mocker.patch('matplotlib.pyplot.show')
        mocker.patch('matplotlib.pyplot.tight_layout')

        plot_blast_results(sample_data)

        # Each axis should have bar called for plotting
        assert mock_ax1.bar.called
        assert mock_ax2.bar.called
        assert mock_ax3.bar.called
        assert mock_ax4.bar.called

    def test_plot_display_handling(self, mocker, capsys):
        """Test handling of plt.show() in different environments."""
        sample_data = [
            {
                'rank': 1,
                'e_value': 1e-50,
                'percent_identity': 100.0,
                'bit_score': 180,
                'query_coverage': 100.0
            }
        ]
        # Must provide proper return value for subplots
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mocker.patch('matplotlib.pyplot.subplots', return_value=(mock_fig, ((mock_ax, mock_ax), (mock_ax, mock_ax))))
        mocker.patch('matplotlib.pyplot.tight_layout')
        mocker.patch('matplotlib.pyplot.savefig')
        mocker.patch('matplotlib.pyplot.show', side_effect=Exception("Display error"))

        # Should not crash
        plot_blast_results(sample_data)

        captured = capsys.readouterr()
        assert "not available" in captured.out

    def test_empty_data_handling(self, capsys):
        """Test handling of empty hits data."""
        plot_blast_results([])

        captured = capsys.readouterr()
        # Should handle gracefully without crashing
        assert "Creating" not in captured.out


# ============ Integration Tests ============

@pytest.mark.skipif(not BLAST_DEMO_AVAILABLE, reason="blast_demo.py dependencies not available")
@pytest.mark.integration
@pytest.mark.network
class TestIntegrationBlastDemo:
    """Integration tests for blast_demo.py."""

    def test_full_workflow_mocked(self, mock_seq_record, mocker, sample_hits_data, tmp_path):
        """Test the full workflow with mocked components."""
        # Mock all external dependencies
        mock_handle = MagicMock()
        mock_handle.read.return_value = "<xml>results</xml>"
        mock_handle.seek = MagicMock()
        mock_handle.close = MagicMock()

        mocker.patch('Bio.Blast.NCBIWWW.qblast', return_value=mock_handle)
        mocker.patch('Bio.Blast.NCBIXML.parse', return_value=[])
        mocker.patch('pathlib.Path.mkdir')
        mocker.patch('builtins.open', mocker.mock_open())
        mocker.patch('matplotlib.pyplot.subplots')
        mocker.patch('matplotlib.pyplot.savefig')
        mocker.patch('matplotlib.pyplot.show')
        mocker.patch('matplotlib.pyplot.tight_layout')

        # This tests that the workflow doesn't crash
        result_handle = perform_blast_search(mock_seq_record)
        assert result_handle is not None


# ============ BioPython Dependency Tests ============

class TestBioPythonDependencies:
    """Tests for BioPython dependency handling."""

    def test_can_import_bio_if_available(self):
        """Test that Bio modules can be imported if available."""
        try:
            from Bio import SeqIO
            from Bio.Blast import NCBIWWW, NCBIXML
            assert True
        except ImportError:
            pytest.skip("BioPython not available")

    def test_can_import_pandas_if_available(self):
        """Test that pandas can be imported if available."""
        try:
            import pandas as pd
            assert True
        except ImportError:
            pytest.skip("pandas not available")

    def test_can_import_matplotlib_if_available(self):
        """Test that matplotlib can be imported if available."""
        try:
            import matplotlib.pyplot as plt
            assert True
        except ImportError:
            pytest.skip("matplotlib not available")
