from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read dev requirements
dev_requirements = []
with open('requirements-dev.txt', 'r', encoding='utf-8') as f:
    dev_requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="lod-imputation-geochem",
    version="0.1.0",
    author="SAMUEL MEDINA LETELIER",
    author_email="smedinaleteliergmail.com",
    description="Statistical methods for handling left-censored geochemical data (values below LOD)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smedinalet/lod-imputation-geochem",
    project_urls={
        "Bug Tracker": "https://github.com/smedinalet/lod-imputation-geochem/issues",
        "Documentation": "https://github.com/smedinalet/lod-imputation-geochem/blob/main/README.md",
        "Source Code": "https://github.com/smedinalet/lod-imputation-geochem",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    packages=find_packages(exclude=["tests", "scripts", "docs", "examples"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "lod-validate=scripts.04_validar_csv:main",
        ],
    },
    keywords=[
        "geochemistry",
        "LOD",
        "limit-of-detection",
        "imputation",
        "censored-data",
        "compositional-data",
        "CoDa",
        "left-censored",
        "below-detection",
        "geochemical-analysis",
    ],
    include_package_data=True,
    zip_safe=False,
)