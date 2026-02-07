"""Tests for the DateFileRenamer class."""


import pytest
from pathlib import Path
from datetime import datetime
from date_renamer.renamer import DateFileRenamer

@pytest.fixture
def renamer() -> DateFileRenamer:
    """Create a DateFileRenamer instance for testing."""
    return DateFileRenamer()

@pytest.fixture
def temp_directory(tmp_path: Path) -> Path:
    """Create a temporary directory with test files."""
    test_files = [
        "invoice_12-03-2024.pdf",
        "report_Mar_8_21.txt",
        "data_2023-12-25_raw.csv",
        "summary_08Dec2022.xlsx",
        "2024_01_15_meeting.docx",
        "no_date_file.txt"
    ]
    
    # Create test files with some content to ensure they exist
    for filename in test_files:
        file_path = tmp_path / filename
        with open(file_path, 'w') as f:
            f.write('test content')
    
    return tmp_path

@pytest.mark.parametrize("input_file,expected_date,expected_match", [
    ("data_2023-12-25_raw.csv", "20231225", "2023-12-25"),
    ("report_Mar_8_21.txt", "20210308", "Mar_8_21"),
    ("report_03152024.txt", "20240315", "03152024"),
    ("IMG-20260204-WA0002.jpeg", "20260204", "20260204"),  # YYYYMMDD format (WhatsApp)
    ("photo_20250815_archived.jpg", "20250815", "20250815"),  # YYYYMMDD format
])
def test_extract_date_formats(renamer, input_file, expected_date, expected_match):
    """Test extracting dates in various formats."""
    date_str, matched_date = renamer.extract_date(input_file)
    assert date_str == expected_date
    assert matched_date == expected_match

def test_invalid_date(renamer):
    """Test handling invalid dates."""
    filename = "report_13-45-2024.txt"  # Invalid month and day
    date_str, matched_date = renamer.extract_date(filename)
    assert date_str is None
    assert matched_date is None

def test_no_date(renamer):
    """Test handling files without dates."""
    filename = "no_date_file.txt"
    date_str, matched_date = renamer.extract_date(filename)
    assert date_str is None
    assert matched_date is None

def test_process_directory(renamer, temp_directory):
    """Test processing a directory with multiple files."""
    initial_files = set(f.name for f in temp_directory.iterdir())
    renamer.process_directory(temp_directory)
    final_files = set(f.name for f in temp_directory.iterdir())
    
    # Verify total file count remains same
    assert len(initial_files) == len(final_files)

    # Check that files with dates were renamed
    assert not (temp_directory / "invoice_12-03-2024.pdf").exists()
    assert (temp_directory / "20240312_invoice.pdf").exists()

    # Check that files without dates were not renamed
    assert (temp_directory / "no_date_file.txt").exists()

    # Check summary counts
    assert len(renamer.renamed_files) == 5  # All files with dates
    assert len(renamer.skipped_files) == 1  # no_date_file.txt

def test_multiple_dates(renamer):
    """Test handling filenames with multiple date patterns."""
    filename = "2024-01-15_report_Mar-8-21.txt"
    date_str, matched_date = renamer.extract_date(filename)
    # Should use the first valid date found
    assert date_str == "20240115"
    assert matched_date == "2024-01-15"


@pytest.mark.parametrize("input_file,expected_datetime,expected_match", [
    ("PXL_20260204_181153683.MP.jpg", "20260204T181153.683", "20260204_181153683"),
    ("photo_20240315_120530.jpg", "20240315T120530", "20240315_120530"),
    ("original_066327a2-b97c-416a-b6db-b6296a669edf_PXL_20260204_181153683.MP.jpg", 
     "20260204T181153.683", "20260204_181153683"),
])
def test_extract_datetime_formats(renamer, input_file, expected_datetime, expected_match):
    """Test extracting datetime in various formats."""
    datetime_str, matched_str, has_time = renamer.extract_datetime(input_file)
    assert datetime_str == expected_datetime
    assert matched_str == expected_match
    assert has_time is True


def test_no_datetime(renamer):
    """Test handling files without datetime."""
    filename = "report_2023-12-25.txt"  # Only has date, not datetime
    datetime_str, matched_str, has_time = renamer.extract_datetime(filename)
    assert datetime_str is None
    assert has_time is False


def test_rename_file_with_datetime(renamer, tmp_path):
    """Test renaming a file with datetime in the filename."""
    # Create test file
    test_file = tmp_path / "PXL_20260204_181153683.MP.jpg"
    test_file.write_text("test content")
    
    # Rename it
    renamer.rename_file(test_file)
    
    # Check that file was renamed correctly
    expected_file = tmp_path / "20260204T181153.683_PXL.MP.jpg"
    assert expected_file.exists()
    assert not test_file.exists()
    assert len(renamer.renamed_files) == 1


def test_rename_file_with_datetime_and_prefix(renamer, tmp_path):
    """Test renaming a file with datetime and UUID prefix."""
    # Create test file
    test_file = tmp_path / "original_066327a2-b97c-416a-b6db-b6296a669edf_PXL_20260204_181153683.MP.jpg"
    test_file.write_text("test content")
    
    # Rename it
    renamer.rename_file(test_file)
    
    # Check that file was renamed correctly (hyphens in UUID are converted to underscores by cleanup)
    expected_file = tmp_path / "20260204T181153.683_original_066327a2_b97c_416a_b6db_b6296a669edf_PXL.MP.jpg"
    assert expected_file.exists()
    assert not test_file.exists()
    assert len(renamer.renamed_files) == 1