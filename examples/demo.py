"""Example script to demonstrate the usage of DateFileRenamer."""

from pathlib import Path
from datetime import datetime
import shutil

def create_example_files():
    """Create example files with different date formats."""
    example_files = [
        "invoice_12-03-2024.pdf",
        "report_Mar_8_21.txt",
        "data_2023-12-25_raw.csv",
        "summary_08Dec2022.xlsx",
        "2024_01_15_meeting.docx",
        "no_date_file.txt"
    ]
    
    examples_dir = Path("example_files")
    if examples_dir.exists():
        shutil.rmtree(examples_dir)
    
    examples_dir.mkdir()
    
    for filename in example_files:
        (examples_dir / filename).touch()
    
    return examples_dir

if __name__ == "__main__":
    from date_renamer import DateFileRenamer
    
    # Create example files
    example_dir = create_example_files()
    print(f"Created example files in: {example_dir}")
    
    # Process the files
    renamer = DateFileRenamer()
    renamer.process_directory(example_dir)
    renamer.print_summary()