# Date Renamer

A Python utility that renames files based on dates found in their filenames. It standardizes the date format to YYYYMMDD_ prefix while preserving the rest of the filename.

[![GitHub](https://img.shields.io/github/license/brian1/date-renamer)](https://github.com/brian1/date-renamer/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/date-renamer)](https://pypi.org/project/date-renamer/)

## Features

- Detects dates in multiple formats within filenames
- Supports various date formats (YYYY-MM-DD, DD-MM-YYYY, MMM-DD-YY, etc.)
- Renames files with standardized YYYYMMDD_ prefix
- Optional recursive directory processing
- Detailed operation summary
- Command-line interface

## Installation

```bash
pip install .
```

## Usage

```bash
# Process current directory
date-renamer

# Process specific directory
date-renamer /path/to/directory

# Process directory and subdirectories recursively
date-renamer /path/to/directory -r
```

## Supported Date Formats

- YYYY-MM-DD, YYYY_MM_DD
- DD-MM-YYYY, DD_MM_YYYY
- MMDDYYYY
- DD-Mon-YY, DDMonYY (e.g., 08-Mar-21, 08Mar21)
- Mon-DD-YY, Mon_DD_YY (e.g., Mar-08-21, Mar_08_21)

## Examples

Input files:
```
invoice_12-03-2024.pdf    → 20240312_invoice.pdf
report_Mar_8_21.txt       → 20210308_report.txt
data_2023-12-25_raw.csv   → 20231225_data_raw.csv
summary_08Dec2022.xlsx    → 20221208_summary.xlsx
2024_01_15_meeting.docx   → 20240115_meeting.docx
```

## Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run tests:
   ```bash
   pytest
   ```

## License

MIT License