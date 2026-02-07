"""CLI interface for the date renamer utility."""

import argparse
from pathlib import Path
from .renamer import DateFileRenamer

def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Rename files containing dates to a standardized YYYYMMDD_ format."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable backup creation (backups enabled by default)"
    )
    args = parser.parse_args()

    try:
        # Create renamer with backup enabled by default (disabled with --no-backup flag)
        renamer = DateFileRenamer(backup_dir=not args.no_backup)
        renamer.process_directory(args.directory, args.recursive)
        renamer.print_summary()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())