"""Core functionality for renaming files based on dates in their filenames."""

import re
import shutil
from datetime import datetime
from pathlib import Path

class DateFileRenamer:
    def __init__(self, backup_dir=True):
        # backup_dir: True for default backup behavior, False to disable, or a Path for custom location
        self.backup_enabled = backup_dir is not False
        self.backup_dir = backup_dir if isinstance(backup_dir, Path) else None
        self.backup_location = None  # Set when processing starts
        
        # Dictionary of regex patterns and their corresponding datetime format strings
        month_names = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
        self.date_patterns = {
            # YYYY-MM-DD or YYYY_MM_DD
            r'(\d{4})[-_](\d{2})[-_](\d{2})': '%Y%m%d',
            # DD-MM-YYYY or DD_MM_YYYY
            r'(\d{2})[-_](\d{2})[-_](\d{4})': '%Y%m%d',
            # YYYYMMDD (8 consecutive digits, no separators - WhatsApp style)
            r'(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)': '%Y%m%d',  # Must come before MMDDYYYY
            # MMDDYYYY
            r'(?<!\d)(\d{2})(\d{2})(\d{4})(?!\d)': '%Y%m%d',  # Match 8 digits not surrounded by digits
            # DD(Mon)YY or DD-(Mon)-YY
            rf'(\d{{1,2}})[-_]?({month_names})[-_]?(\d{{2}})(?!\d)': '%Y%m%d',
            # (Mon)DD,YY or (Mon)_DD_YY
            rf'({month_names})[-_]?(\d{{1,2}})[-,_]?(\d{{2}})(?!\d)': '%Y%m%d',
        }
        
        # Datetime patterns (checked before date-only patterns)
        self.datetime_patterns = {
            # YYYYMMDD_HHMMSSMMM or YYYYMMDD_HHMMSS (e.g., PXL_20260204_181153683)
            r'(\d{4})(\d{2})(\d{2})[-_](\d{2})(\d{2})(\d{2})(\d{3})?': 'datetime_yyyymmdd_hhmmss',
        }
        
        self.month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        self.renamed_files = []
        self.skipped_files = []
        self.backup_files = []  # Track files that were backed up

    def extract_datetime(self, filename):
        """Extract datetime from filename using datetime patterns.
        
        Returns:
            tuple: (datetime_str, matched_str, has_time) where:
                - datetime_str: ISO 8601 format (e.g., '20260204T181153')
                - matched_str: The original matched portion of the filename
                - has_time: Boolean indicating if time was found
        """
        for pattern in self.datetime_patterns.keys():
            search_text = f" {filename} "
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) >= 6:
                        year, month, day, hour, minute, second = groups[:6]
                        milliseconds = groups[6] if len(groups) > 6 and groups[6] else None
                        
                        # Validate datetime
                        date_str = f"{year}{month}{day}"
                        time_str = f"{hour}{minute}{second}"
                        full_datetime_str = f"{date_str}{time_str}"
                        datetime.strptime(full_datetime_str, '%Y%m%d%H%M%S')
                        
                        # Format as ISO 8601: YYYYMMDDTHHMMSS or YYYYMMDDTHHMMSS.mmm
                        iso_str = f"{year}{month}{day}T{hour}{minute}{second}"
                        if milliseconds:
                            iso_str += f".{milliseconds}"
                        
                        return iso_str, match.group().strip(), True
                except ValueError:
                    continue
        
        return None, None, False

    def extract_date(self, filename):
        """Extract date from filename using various patterns."""
        for pattern in self.date_patterns.keys():
            # Add separators to help with boundary matching
            search_text = f" {filename} "
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    matched_str = match.group()
                    if len(groups) == 3:
                        # Check for text month format (either DD-Mon-YY or Mon-DD-YY)
                        if any(month.upper() in groups[1].upper() for month in self.month_map.keys()):
                            # DD-Mon-YY format
                            month = self.month_map[groups[1].capitalize()]
                            day = groups[0].zfill(2) if len(groups[0]) == 1 else groups[0]
                            year = f"20{groups[2]}" if len(groups[2]) == 2 else groups[2]
                        elif any(month.upper() in groups[0].upper() for month in self.month_map.keys()):
                            # Mon-DD-YY format
                            month = self.month_map[groups[0].capitalize()]
                            day = groups[1].zfill(2) if len(groups[1]) == 1 else groups[1]
                            year = f"20{groups[2]}" if len(groups[2]) == 2 else groups[2]
                        elif '-' in matched_str or '_' in matched_str:
                            # Separator-based patterns (DD-MM-YYYY or YYYY-MM-DD)
                            if len(groups[0]) == 4:
                                # YYYY-MM-DD format
                                year, month, day = groups
                            else:
                                # DD-MM-YYYY format
                                day, month, year = groups
                        else:
                            # No separators - need to determine YYYYMMDD vs MMDDYYYY
                            # Check the length of the first group to disambiguate
                            if len(groups[0]) == 4:
                                # YYYYMMDD format - first group is 4-digit year
                                year, month, day = groups
                            else:
                                # MMDDYYYY format - check if first two digits are valid month (01-12)
                                first_two = int(groups[0])
                                if 1 <= first_two <= 12:
                                    month, day, year = groups
                                else:
                                    day, month, year = groups

                        # Create standardized date string
                        date_str = f"{year}{month.zfill(2)}{day.zfill(2)}"
                        # Validate the date
                        datetime.strptime(date_str, '%Y%m%d')
                        return date_str, match.group().strip()
                except ValueError:
                    continue
        return None, None

    def rename_file(self, filepath):
        """Rename a file based on the date or datetime found in its name."""
        path = Path(filepath)
        if not path.is_file():
            return

        filename = path.name
        
        # Try to extract datetime first (which includes time)
        datetime_str, matched_datetime, has_time = self.extract_datetime(filename)
        
        if datetime_str:
            # Datetime format found - use ISO 8601 format
            date_str = datetime_str
            matched_str = matched_datetime
        else:
            # Fall back to date-only extraction
            date_str, matched_str = self.extract_date(filename)
        
        if not date_str:
            self.skipped_files.append(filename)
            return

        # Split filename and extension
        name_without_ext = filename.rsplit('.', 1)[0]
        ext = filename.split('.')[-1]
        
        # Remove the matched date/datetime from the name
        # Try a series of replacement strategies, from most specific to least
        name_without_date = name_without_ext
        
        # Strategy 1: Remove with separator on both sides
        pattern_with_separators = f'[-_]{re.escape(matched_str)}[-_]'
        name_without_date = re.sub(pattern_with_separators, '_', name_without_date)
        
        # Strategy 2: Remove with separator on left only (replace with nothing)
        if name_without_date == name_without_ext:
            pattern_leading_sep = f'[-_]{re.escape(matched_str)}'
            name_without_date = re.sub(pattern_leading_sep, '', name_without_ext)
        
        # Strategy 3: Remove with separator on right only (replace with nothing)
        if name_without_date == name_without_ext:
            pattern_trailing_sep = f'{re.escape(matched_str)}[-_]'
            name_without_date = re.sub(pattern_trailing_sep, '', name_without_ext)
        
        # Strategy 4: Direct string replacement (handles dots and other cases)
        if name_without_date == name_without_ext:
            name_without_date = name_without_ext.replace(matched_str, '')
        
        # Clean up multiple separators and remove leading/trailing underscores
        name_without_date = re.sub(r'[-_]+', '_', name_without_date).strip('_')
        
        # Create the new filename with datetime/date prefix and original extension
        new_filename = f"{date_str}_{name_without_date}.{ext}"
        new_filepath = path.parent / new_filename

        try:
            # Create backup if enabled
            if self.backup_enabled and self.backup_location:
                backup_path = self.backup_location / filename
                shutil.copy2(path, backup_path)
                self.backup_files.append(filename)
            
            # Rename the file
            path.rename(new_filepath)
            self.renamed_files.append((filename, new_filename))
        except OSError as e:
            print(f"Error renaming {filename}: {e}")

    def process_directory(self, directory, recursive=False):
        """Process all files in the given directory."""
        directory = Path(directory)
        print(f"Processing directory: {directory}")
        
        # Create backup directory if backups are enabled
        if self.backup_enabled:
            if self.backup_dir:
                self.backup_location = self.backup_dir
            else:
                # Default: create .backup subfolder in the target directory
                self.backup_location = directory / ".backup"
            
            self.backup_location.mkdir(parents=True, exist_ok=True)
            print(f"Backup location: {self.backup_location}")
        
        if recursive:
            files = [f for f in directory.rglob('*') if f.is_file()]
        else:
            files = [f for f in directory.iterdir() if f.is_file()]
        
        print(f"Found files: {[f.name for f in files]}")
        
        for file_path in files:
            print(f"Processing file: {file_path}")
            self.rename_file(file_path)
            print(f"Renamed files so far: {self.renamed_files}")
            print(f"Skipped files so far: {self.skipped_files}")

    def print_summary(self):
        """Print a summary of the renaming operation."""
        print("\nRenaming Summary:")
        print("-" * 50)
        
        if self.backup_enabled and self.backup_location:
            print(f"\nBackup location: {self.backup_location}")
            print(f"Files backed up: {len(self.backup_files)}")
        
        if self.renamed_files:
            print("\nSuccessfully renamed files:")
            for old_name, new_name in self.renamed_files:
                print(f"  {old_name} → {new_name}")
            print(f"\nTotal files renamed: {len(self.renamed_files)}")
        
        if self.skipped_files:
            print("\nSkipped files (no valid date found):")
            for filename in self.skipped_files:
                print(f"  {filename}")
            print(f"\nTotal files skipped: {len(self.skipped_files)}")