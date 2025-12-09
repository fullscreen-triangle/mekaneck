"""
Setup script for Blindhorse validation package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "blindhorse" / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "blindhorse" / "requirements.txt").read_text().strip().split("\n")
requirements = [r.strip() for r in requirements if r.strip() and not r.startswith("#")]

setup(
    name="blindhorse",
    version="0.1.0",
    author="Kundai Farai Sachikonye",
    author_email="kundai@fullscreen-triangle.com",
    description="Pharmaceutical Maxwell Demon Validation Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fullscreen-triangle/mekaneck",
    project_urls={
        "Bug Tracker": "https://github.com/fullscreen-triangle/mekaneck/issues",
        "Documentation": "https://github.com/fullscreen-triangle/mekaneck/tree/main/blindhorse",
        "Source Code": "https://github.com/fullscreen-triangle/mekaneck",
    },
    packages=find_packages(include=["blindhorse", "blindhorse.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.4.0",
        ],
        "viz": [
            "plotly>=5.16.0",
            "dash>=2.12.0",
            "pyvis>=0.3.2",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "jupyterlab>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "blindhorse=blindhorse.orchestrator:main",
            "blindhorse-validate=blindhorse.run_validation:main",
        ],
    },
    include_package_data=True,
    package_data={
        "blindhorse": ["*.md", "requirements.txt"],
    },
    zip_safe=False,
    keywords=[
        "pharmaceutical",
        "maxwell-demon",
        "drug-discovery",
        "oscillatory-computing",
        "categorical-state",
        "validation",
        "biophysics",
        "pharmacodynamics",
    ],
)

