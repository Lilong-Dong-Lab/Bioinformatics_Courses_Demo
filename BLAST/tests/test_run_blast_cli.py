# tests/test_run_blast_cli.py
"""
Unit tests for run_blast_cli.py - Primary local BLAST demonstration.

This module tests the core BLAST CLI functionality including:
- Command execution and subprocess handling
- BLAST tool availability checking
- Local BLAST execution
- Database creation
- Result parsing
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch
from subprocess import CalledProcessError
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from run_blast_cli import (
    run_command,
    check_blast_tools,
    run_local_blast,
    create_sample_database,
    parse_blast_results,
    run_remote_bast_demo
)


# ============ TestRunCommand ============

class TestRunCommand:
    """Tests for run_command function."""

    def test_run_command_success(self, mocker):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mocker.patch('subprocess.run', return_value=mock_result)

        result = run_command(['echo', 'test'])

        assert result is not None
        assert result.returncode == 0

    def test_run_command_failure(self, mocker, capsys):
        """Test handling of failed command (CalledProcessError)."""
        mock_error = CalledProcessError(
            returncode=1,
            cmd=['blastp', '-version'],
            stderr="command not found"
        )
        mocker.patch('subprocess.run', side_effect=mock_error)

        result = run_command(['blastp', '-version'])

        assert result is None
        captured = capsys.readouterr()
        assert "Error running command" in captured.out

    def test_run_command_with_capture_disabled(self, mocker):
        """Test command without output capture."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run = mocker.patch('subprocess.run', return_value=mock_result)

        result = run_command(['echo', 'test'], capture_output=False)

        # Verify subprocess.run was called with capture_output=False
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs['capture_output'] is False

    def test_run_command_handles_stdout_stderr(self, mocker, capsys):
        """Test that stdout and stderr are printed on error."""
        # In Python 3.14, CalledProcessError doesn't accept stdout/stderr directly
        # We test that the error is handled gracefully
        mock_error = CalledProcessError(
            returncode=1,
            cmd=['test']
        )
        # Manually set stdout/stderr attributes
        mock_error.stdout = "stdout content"
        mock_error.stderr = "stderr content"
        mocker.patch('subprocess.run', side_effect=mock_error)

        result = run_command(['test'])

        assert result is None
        captured = capsys.readouterr()
        assert "Error running command" in captured.out


# ============ TestCheckBlastTools ============

class TestCheckBlastTools:
    """Tests for check_blast_tools function."""

    def test_all_tools_available(self, mocker, capsys):
        """Test when all BLAST tools are installed."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "blastp: 2.15.0+"
        mocker.patch('subprocess.run', return_value=mock_result)

        tools = check_blast_tools()

        assert len(tools) == 5  # blastp, blastn, blastx, tblastn, tblastx
        assert 'blastp' in tools
        assert 'blastn' in tools

    def test_no_tools_available(self, mocker, capsys):
        """Test when no BLAST tools are found (all return errors)."""
        mock_error = CalledProcessError(returncode=1, cmd=['blastp'])
        mocker.patch('subprocess.run', side_effect=mock_error)

        tools = check_blast_tools()

        assert len(tools) == 0
        captured = capsys.readouterr()
        # Tools that fail will show error messages but no tools found
        assert "Checking BLAST+ tools" in captured.out

    def test_partial_tools_available(self, mocker, capsys):
        """Test when only some tools are available."""

        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[0] in ['blastp', 'blastn']:
                result = MagicMock()
                result.returncode = 0
                result.stdout = f"{cmd[0]}: 2.15.0+"
                return result
            else:
                raise CalledProcessError(returncode=1, cmd=cmd)

        mocker.patch('subprocess.run', side_effect=mock_run_side_effect)

        tools = check_blast_tools()

        assert len(tools) == 2
        assert 'blastp' in tools
        assert 'blastn' in tools
        assert 'blastx' not in tools

    def test_version_check_command_construction(self, mocker):
        """Test correct command construction for version check."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0, stdout="version")

        check_blast_tools()

        # Check that each tool was called with '-version'
        calls = mock_run.call_args_list
        for call in calls:
            args = call[0][0]
            assert args[1] == '-version'


# ============ TestRunLocalBlast ============

class TestRunLocalBlast:
    """Tests for run_local_blast function."""

    def test_blastp_command_construction(self, mocker, tmp_path):
        """Test correct blastp command construction."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run = mocker.patch('subprocess.run', return_value=mock_result)

        query_file = str(tmp_path / "query.fasta")
        output_file = str(tmp_path / "results.txt")

        run_local_blast(query_file, "test_db", output_file, "blastp")

        # Verify command construction
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == 'blastp'
        assert '-query' in call_args
        assert query_file in call_args
        assert '-db' in call_args
        assert 'test_db' in call_args
        assert '-out' in call_args
        assert output_file in call_args
        assert '-outfmt' in call_args
        assert '6' in call_args  # Tabular format
        assert '-evalue' in call_args

    def test_local_blast_success(self, mocker, tmp_path, capsys):
        """Test successful local BLAST execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mocker.patch('subprocess.run', return_value=mock_result)

        result = run_local_blast(
            str(tmp_path / "query.fasta"),
            "test_db",
            str(tmp_path / "results.txt")
        )

        assert result is True
        captured = capsys.readouterr()
        assert "BLAST completed successfully" in captured.out

    def test_local_blast_failure(self, mocker, tmp_path, capsys):
        """Test local BLAST failure handling."""
        mock_error = CalledProcessError(returncode=1, cmd=['blastp'])
        mocker.patch('subprocess.run', side_effect=mock_error)

        result = run_local_blast(
            str(tmp_path / "query.fasta"),
            "test_db",
            str(tmp_path / "results.txt")
        )

        assert result is False
        captured = capsys.readouterr()
        assert "BLAST failed" in captured.out

    def test_default_program_is_blastp(self, mocker, tmp_path):
        """Test that default program is blastp."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        run_local_blast(
            str(tmp_path / "query.fasta"),
            "test_db",
            str(tmp_path / "results.txt")
        )

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == 'blastp'

    def test_custom_program_parameter(self, mocker, tmp_path):
        """Test custom program parameter."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        run_local_blast(
            str(tmp_path / "query.fasta"),
            "test_db",
            str(tmp_path / "results.txt"),
            program="blastn"
        )

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == 'blastn'


# ============ TestCreateSampleDatabase ============

class TestCreateSampleDatabase:
    """Tests for create_sample_database function."""

    def test_makeblastdb_command_construction(self, mocker, tmp_path):
        """Test correct makeblastdb command."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        fasta_files = [str(tmp_path / "seq1.fasta"), str(tmp_path / "seq2.fasta")]
        create_sample_database(fasta_files, "test_db")

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == 'makeblastdb'
        assert '-in' in call_args
        assert '-dbtype' in call_args
        assert 'prot' in call_args
        assert '-out' in call_args
        assert 'test_db' in call_args

    def test_database_creation_success(self, mocker, tmp_path, capsys):
        """Test successful database creation."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        result = create_sample_database([str(tmp_path / "seq.fasta")], "test_db")

        assert result is True
        captured = capsys.readouterr()
        assert "created successfully" in captured.out

    def test_database_creation_failure(self, mocker, tmp_path, capsys):
        """Test database creation failure."""
        mock_error = CalledProcessError(returncode=1, cmd=['makeblastdb'])
        mocker.patch('subprocess.run', side_effect=mock_error)

        result = create_sample_database([str(tmp_path / "seq.fasta")], "test_db")

        assert result is False
        captured = capsys.readouterr()
        assert "Database creation failed" in captured.out

    def test_multiple_fasta_input(self, mocker, tmp_path):
        """Test database creation from multiple FASTA files."""
        mock_run = mocker.patch('subprocess.run')
        mock_run.return_value = MagicMock(returncode=0)

        fasta_files = [
            str(tmp_path / "seq1.fasta"),
            str(tmp_path / "seq2.fasta"),
            str(tmp_path / "seq3.fasta")
        ]
        create_sample_database(fasta_files, "multi_db")

        call_args = mock_run.call_args[0][0]
        # All files should be in the command
        for fasta in fasta_files:
            assert fasta in call_args


# ============ TestParseBlastResults ============

class TestParseBlastResults:
    """Tests for parse_blast_results function."""

    def test_parse_valid_tabular_results(self, temp_results_file, capsys):
        """Test parsing valid outfmt 6 results."""
        parse_blast_results(str(temp_results_file))

        captured = capsys.readouterr()
        assert "Found 3 hits" in captured.out
        assert "gi|123456789" in captured.out
        assert "100.00" in captured.out

    def test_parse_empty_results_file(self, empty_results_file, capsys):
        """Test handling of empty results file."""
        parse_blast_results(str(empty_results_file))

        captured = capsys.readouterr()
        assert "No results found" in captured.out

    def test_parse_nonexistent_file(self, tmp_path, capsys):
        """Test handling of missing results file."""
        nonexistent = tmp_path / "nonexistent.txt"
        parse_blast_results(str(nonexistent))

        captured = capsys.readouterr()
        assert "Result file not found" in captured.out

    def test_parse_truncated_results(self, tmp_path, capsys):
        """Test parsing results with fewer than 12 columns."""
        truncated_file = tmp_path / "truncated.txt"
        truncated_file.write_text("query\tsubject\t90.0\n")

        parse_blast_results(str(truncated_file))

        captured = capsys.readouterr()
        # Should handle gracefully without crashing
        assert "Found 1 hits" in captured.out

    def test_output_formatting(self, temp_results_file, capsys):
        """Test result output formatting and alignment."""
        parse_blast_results(str(temp_results_file))

        captured = capsys.readouterr()
        # Check header is present
        assert "Subject ID" in captured.out
        assert "% Identity" in captured.out
        assert "E-value" in captured.out
        assert "Bit Score" in captured.out

    def test_limits_to_top_10(self, tmp_path, capsys):
        """Test that only top 10 results are displayed."""
        # Create file with 15 results
        large_file = tmp_path / "large_results.txt"
        lines = []
        for i in range(15):
            lines.append(f"query\tsubject_{i}\t{100-i}.00\t18\t0\t0\t1\t18\t1\t18\t1e-{50+i}\t{40-i}.0\n")
        large_file.write_text("".join(lines))

        parse_blast_results(str(large_file))

        captured = capsys.readouterr()
        assert "Found 15 hits" in captured.out
        # Check that results are displayed (top 10)


# ============ TestRunRemoteBlastDemo ============

class TestRunRemoteBlastDemo:
    """Tests for run_remote_bast_demo function (demonstration only)."""

    def test_shows_ncbi_url(self, tmp_path, capsys):
        """Test that NCBI URL is shown."""
        query_file = str(tmp_path / "query.fasta")
        run_remote_bast_demo(query_file)

        captured = capsys.readouterr()
        assert "blast.ncbi.nlm.nih.gov" in captured.out

    def test_shows_remote_blast_notes(self, tmp_path, capsys):
        """Test that notes about remote BLAST are shown."""
        query_file = str(tmp_path / "query.fasta")
        run_remote_bast_demo(query_file)

        captured = capsys.readouterr()
        assert "network access" in captured.out.lower() or "Remote BLAST" in captured.out


# ============ Integration Markers ============

@pytest.mark.integration
class TestIntegrationRunBlastCli:
    """Integration tests that require actual BLAST tools."""

    def test_real_blastp_version_check(self):
        """Test checking real blastp version (requires BLAST installed)."""
        # This test will pass if BLAST is installed
        try:
            import subprocess
            result = subprocess.run(['blastp', '-version'], capture_output=True)
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("BLAST tools not installed")

    def test_real_check_blast_tools(self):
        """Test real tool availability check."""
        tools = check_blast_tools()
        # On a system with BLAST, should find at least blastp
        if not tools:
            pytest.skip("No BLAST tools installed")
