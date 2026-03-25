# tests/test_utils.py
"""
Unit tests for utils.py - Shared utilities for BLAST demo scripts.

This module tests the shared utility functions including:
- Path resolution
- Subprocess execution
- FASTA file loading
- Timestamp generation
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock
from subprocess import CalledProcessError

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from utils import (
    get_project_dir,
    get_data_dir,
    get_results_dir,
    ensure_results_dir,
    timestamp,
    run_command,
    load_fasta_sequence,
    BLAST_PROGRAMS,
    BLAST_DATABASES,
    BLAST_OUTFMT,
)


# ============ TestPathResolution ============


class TestPathResolution:
    """Tests for path resolution functions."""

    def test_get_project_dir_returns_path(self):
        """Test that project directory is returned as Path."""
        result = get_project_dir()
        assert isinstance(result, Path)

    def test_get_project_dir_contains_expected_files(self):
        """Test that project dir contains expected files."""
        project_dir = get_project_dir()
        assert (project_dir / "scripts").exists()
        assert (project_dir / "data").exists()

    def test_get_data_dir_is_subdir(self):
        """Test that data dir is a subdirectory of project."""
        data_dir = get_data_dir()
        project_dir = get_project_dir()
        assert data_dir.parent == project_dir
        assert data_dir.name == "data"

    def test_get_results_dir_is_subdir(self):
        """Test that results dir is a subdirectory of project."""
        results_dir = get_results_dir()
        project_dir = get_project_dir()
        assert results_dir.parent == project_dir
        assert results_dir.name == "results"

    def test_ensure_results_dir_creates_if_missing(self, tmp_path, mocker):
        """Test that results dir is created if it doesn't exist."""
        # Mock get_project_dir to return tmp_path
        mocker.patch("utils.get_project_dir", return_value=tmp_path)

        results_dir = ensure_results_dir()
        assert results_dir.exists()
        assert results_dir.name == "results"

    def test_ensure_results_dir_returns_existing(self, tmp_path, mocker):
        """Test that existing results dir is returned."""
        results_path = tmp_path / "results"
        results_path.mkdir()

        mocker.patch("utils.get_project_dir", return_value=tmp_path)

        result = ensure_results_dir()
        assert result == results_path


# ============ TestTimestamp ============


class TestTimestamp:
    """Tests for timestamp function."""

    def test_timestamp_format(self):
        """Test that timestamp follows expected format."""
        result = timestamp()
        # Format: YYYYMMDD_HHMMSS
        assert len(result) == 15
        assert result[8] == "_"
        assert result.isdigit() or result.replace("_", "").isdigit()

    def test_timestamp_uniqueness(self):
        """Test that timestamps are unique (within test time)."""
        import time

        ts1 = timestamp()
        time.sleep(1.1)  # Wait just over 1 second
        ts2 = timestamp()
        assert ts1 != ts2


# ============ TestRunCommand ============


class TestRunCommand:
    """Tests for run_command function."""

    def test_success(self, mocker, capsys):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""

        mocker.patch("subprocess.run", return_value=mock_result)

        result = run_command(["echo", "test"], verbose=True)

        assert result is not None
        captured = capsys.readouterr()
        assert "Command" in captured.out

    def test_failure_returns_none(self, mocker, capsys):
        """Test that failure returns None."""
        mock_error = CalledProcessError(returncode=1, cmd=["test"])
        mock_error.stdout = ""
        mock_error.stderr = "error"

        mocker.patch("subprocess.run", side_effect=mock_error)

        result = run_command(["test"], verbose=True)

        assert result is None
        captured = capsys.readouterr()
        assert "Error running command" in captured.out

    def test_timeout(self, mocker, capsys):
        """Test timeout handling."""
        from subprocess import TimeoutExpired

        mocker.patch(
            "subprocess.run", side_effect=TimeoutExpired(cmd=["test"], timeout=5)
        )

        result = run_command(["test"], timeout=5, verbose=True)

        assert result is None
        captured = capsys.readouterr()
        assert "Timeout" in captured.out

    def test_file_not_found(self, mocker, capsys):
        """Test command not found handling."""
        mocker.patch("subprocess.run", side_effect=FileNotFoundError())

        result = run_command(["nonexistent_cmd"], verbose=True)

        assert result is None
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_check_parameter(self, mocker):
        """Test check parameter is passed correctly."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=0)

        run_command(["test"], check=False)

        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["check"] is False


# ============ TestLoadFastaSequence ============


class TestLoadFastaSequence:
    """Tests for load_fasta_sequence function."""

    def test_load_valid_fasta(self, egfr_sequence_path):
        """Test loading valid FASTA file."""
        if not egfr_sequence_path.exists():
            pytest.skip("EGFR sequence file not found")

        header, sequence = load_fasta_sequence(egfr_sequence_path)

        assert header is not None
        assert len(header) > 0
        assert len(sequence) > 0
        # Should not contain newline or whitespace
        assert "\n" not in sequence
        assert " " not in sequence

    def test_load_nonexistent_file(self, tmp_path):
        """Test handling of missing file."""
        nonexistent = tmp_path / "nonexistent.fasta"

        with pytest.raises(FileNotFoundError):
            load_fasta_sequence(nonexistent)

    def test_load_empty_file(self, tmp_path):
        """Test handling of empty file."""
        empty_file = tmp_path / "empty.fasta"
        empty_file.write_text("")

        with pytest.raises(ValueError, match="Empty"):
            load_fasta_sequence(empty_file)

    def test_load_invalid_format(self, tmp_path):
        """Test handling of invalid FASTA format."""
        invalid_file = tmp_path / "invalid.fasta"
        invalid_file.write_text("No header line\nACGT")

        with pytest.raises(ValueError, match="Invalid FASTA"):
            load_fasta_sequence(invalid_file)

    def test_load_sequence_only_header(self, tmp_path):
        """Test handling of file with only header."""
        header_only = tmp_path / "header_only.fasta"
        header_only.write_text(">header_only")

        with pytest.raises(ValueError, match="No sequence"):
            load_fasta_sequence(header_only)


# ============ TestConstants ============


class TestConstants:
    """Tests for module constants."""

    def test_blast_programs_list(self):
        """Test BLAST programs list is correct."""
        assert "blastp" in BLAST_PROGRAMS
        assert "blastn" in BLAST_PROGRAMS
        assert len(BLAST_PROGRAMS) == 5

    def test_blast_databases_list(self):
        """Test BLAST databases list contains expected values."""
        assert "nr" in BLAST_DATABASES
        assert "nt" in BLAST_DATABASES
        assert "swissprot" in BLAST_DATABASES

    def test_blast_outfmt_dict(self):
        """Test output format mapping."""
        assert BLAST_OUTFMT[6] == "tabular"
        assert BLAST_OUTFMT[5] == "XML"
        assert BLAST_OUTFMT[0] == "pairwise"
