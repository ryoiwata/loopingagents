#!/bin/bash
# obsynapse Environment Setup Script
# This script creates a conda environment with all dependencies needed for the obsynapse project

# Deactivate any currently active conda environment
conda deactivate

# Create conda environment with Python 3.12 (compatible with DBT)
# Using local path ./obsynapse instead of global environment
conda create -p ./loopingagents python=3.12 --yes

# Activate the newly created environment
conda activate ./loopingagents

# Install python-dotenv: Library for loading environment variables from .env files
conda install conda-forge::python-dotenv --yes

# Install openai: Official OpenAI Python library for interacting with OpenAI's API
conda install conda-forge::openai --yes