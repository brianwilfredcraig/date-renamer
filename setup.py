from setuptools import setup, find_packages

setup(
    name="date_renamer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "date-renamer=date_renamer.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A utility to rename files based on dates in their filenames",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/date-renamer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)