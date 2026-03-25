# tests/test_remote_blast_demo.py
"""
Unit tests for remote_blast_demo.py - CLI remote BLAST demonstration.

This module tests the command-line remote BLAST functionality including:
- Remote BLAST command construction
- Advanced parameter handling
- Result parsing
- Utility function output
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from subprocess import CalledProcessError

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from remote_blast_demo import (
    run_command,
    run_remote_blast,
    run_advanced_remote_blast,
    parse_remote_results,
    show_web_interface_instructions,
    show_limitations_and_tips
)


# ============ TestRunRemoteBlast ============

class TestRunRemoteBlast:
    """Tests for run_remote_blast function."""

    def test_remote_flag_included(self, mocker, tmp_path):
        """Test that -remote flag is included in command."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.txt")

        run_remote_blast(query_file, "blastp", "nr", output_file)

        call_args = mock_run.call_args[0][0]
        assert '-remote' in call_args

    def test_database_parameter(self, mocker, tmp_path):
        """Test database parameter handling."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.txt")

        run_remote_blast(query_file, "blastp", "swissprot", output_file)

        call_args = mock_run.call_args[0][0]
        assert '-db' in call_args
        assert 'swissprot' in call_args

    def test_output_format_parameter(self, mocker, tmp_path):
        """Test output format specification."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.txt")

        run_remote_blast(query_file, "blastp", "nr", output_file)

        call_args = mock_run.call_args[0][0]
        assert '-outfmt' in call_args
        assert '6' in call_args  # Tabular format

    def test_evalue_threshold(self, mocker, tmp_path):
        """Test E-value threshold setting."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.txt")

        run_remote_blast(query_file, "blastp", "nr", output_file)

        call_args = mock_run.call_args[0][0]
        assert '-evalue' in call_args
        assert '0.001' in call_args

    def test_max_target_seqs_parameter(self, mocker, tmp_path):
        """Test max_target_seqs parameter."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.txt")

        run_remote_blast(query_file, "blastp", "nr", output_file)

        call_args = mock_run.call_args[0][0]
        assert '-max_target_seqs' in call_args

    def test_program_parameter(self, mocker, tmp_path):
        """Test BLAST program parameter."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.txt")

        run_remote_blast(query_file, "blastn", "nt", output_file)

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == 'blastn'

    def test_returns_true_on_success(self, mocker, tmp_path, capsys):
        """Test returns True on successful execution."""
        mocker.patch('subprocess.run', return_value=MagicMock(returncode=0))

        result = run_remote_blast(
            str(tmp_path / "query.fasta"),
            "blastp",
            "nr",
            str(tmp_path / "results.txt")
        )

        assert result is True
        captured = capsys.readouterr()
        assert "completed successfully" in captured.out

    def test_returns_false_on_failure(self, mocker, tmp_path, capsys):
        """Test returns False on failed execution."""
        mock_error = CalledProcessError(returncode=1, cmd=['blastp'])
        mocker.patch('subprocess.run', side_effect=mock_error)

        result = run_remote_blast(
            str(tmp_path / "query.fasta"),
            "blastp",
            "nr",
            str(tmp_path / "results.txt")
        )

        assert result is False


# ============ TestRunAdvancedRemoteBlast ============

class TestRunAdvancedRemoteBlast:
    """Tests for run_advanced_remote_blast function."""

    def test_advanced_parameters(self, mocker, tmp_path):
        """Test advanced BLAST parameters are included."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.xml")

        run_advanced_remote_blast(query_file, output_file)

        call_args = mock_run.call_args[0][0]
        assert '-outfmt' in call_args
        assert '5' in call_args  # XML format
        assert '-matrix' in call_args
        assert '-gapopen' in call_args
        assert '-gapextend' in call_args

    def test_human_only_filter(self, mocker, tmp_path):
        """Test Homo sapiens organism filter."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.xml")

        run_advanced_remote_blast(query_file, output_file)

        call_args = mock_run.call_args[0][0]
        assert '-entrez_query' in call_args
        # Check that Homo sapiens is in the query
        assert any('Homo sapiens' in str(arg) for arg in call_args)

    def test_xml_output_format(self, mocker, tmp_path):
        """Test XML output format for advanced results."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.xml")

        run_advanced_remote_blast(query_file, output_file)

        call_args = mock_run.call_args[0][0]
        outfmt_idx = call_args.index('-outfmt')
        assert call_args[outfmt_idx + 1] == '5'

    def test_stricter_evalue(self, mocker, tmp_path):
        """Test stricter E-value in advanced mode."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.xml")

        run_advanced_remote_blast(query_file, output_file)

        call_args = mock_run.call_args[0][0]
        evalue_idx = call_args.index('-evalue')
        assert call_args[evalue_idx + 1] == '0.0001'


# ============ TestParseRemoteResults ============

class TestParseRemoteResults:
    """Tests for parse_remote_results function."""

    def test_parse_remote_tabular(self, temp_results_file, capsys):
        """Test parsing remote BLAST tabular results."""
        parse_remote_results(str(temp_results_file))

        captured = capsys.readouterr()
        assert "Found 3 hits" in captured.out

    def test_description_extraction_from_subject_id(self, tmp_path, capsys):
        """Test extracting description from subject ID with pipes."""
        results_file = tmp_path / "results.txt"
        results_file.write_text("query\tgi|12345|ref|NP_001234|Description here\t100.00\t50\t0\t0\t1\t50\t1\t50\t1e-50\t180\n")

        parse_remote_results(str(results_file))

        captured = capsys.readouterr()
        assert "Found 1 hits" in captured.out

    def test_nonexistent_file(self, tmp_path, capsys):
        """Test handling of missing file."""
        parse_remote_results(str(tmp_path / "nonexistent.txt"))

        captured = capsys.readouterr()
        assert "Result file not found" in captured.out

    def test_empty_file(self, empty_results_file, capsys):
        """Test handling of empty file."""
        parse_remote_results(str(empty_results_file))

        captured = capsys.readouterr()
        assert "No results found" in captured.out


# ============ TestUtilityFunctions ============

class TestUtilityFunctions:
    """Tests for utility display functions."""

    def test_web_interface_instructions_output(self, tmp_path, capsys):
        """Test web interface instructions are displayed."""
        show_web_interface_instructions()

        captured = capsys.readouterr()
        assert "blast.ncbi.nlm.nih.gov" in captured.out
        assert "Protein BLAST" in captured.out

    def test_limitations_displayed(self, capsys):
        """Test that limitations are shown to user."""
        show_limitations_and_tips()

        captured = capsys.readouterr()
        assert "Rate limiting" in captured.out or "rate" in captured.out.lower()
        assert "Queue times" in captured.out or "server" in captured.out.lower()

    def test_tips_displayed(self, capsys):
        """Test that tips are shown to user."""
        show_limitations_and_tips()

        captured = capsys.readouterr()
        assert "off-peak" in captured.out.lower() or "Tips" in captured.out
        assert "E-value" in captured.out


# ============ TestRunCommand ============

class TestRunCommandRemote:
    """Tests for run_command function in remote_blast_demo.py."""

    def test_success(self, mocker):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mocker.patch('subprocess.run', return_value=mock_result)

        result = run_command(['test', 'command'])
        assert result is not None
        assert result.returncode == 0

    def test_failure(self, mocker, capsys):
        """Test command failure handling."""
        mock_error = CalledProcessError(returncode=1, cmd=['test'])
        mocker.patch('subprocess.run', side_effect=mock_error)

        result = run_command(['test'])
        assert result is None

        captured = capsys.readouterr()
        assert "Error running command" in captured.out


# ============ Integration Tests ============

@pytest.mark.integration
@pytest.mark.network
class TestIntegrationRemoteBlast:
    """Integration tests for remote BLAST (require network)."""

    def test_real_remote_blast_skipped(self):
        """Remote BLAST tests should be skipped in automated testing."""
        pytest.skip("Network tests require manual execution")

    def test_command_construction_only(self, mocker):
        """Test command construction without actual execution."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        # This tests command construction without network access
        run_remote_blast("test.fasta", "blastp", "nr", "output.txt")

        assert mock_run.called
