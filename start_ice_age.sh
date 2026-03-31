#!/usr/bin/env bash
# Start the Ice Age Streamlit app using the ice_age conda environment

# Check for presence of conda package managers
if [ -n "$MAMBA_EXE" ]; then
    CONDA_BIN="$MAMBA_EXE"
elif [ -n "$CONDA_EXE" ]; then
    CONDA_BIN="$CONDA_EXE"
else
    echo "Error: No conda package manager found (mamba, micromamba, or conda)"
    exit 1
fi

$CONDA_BIN run -n ice_age streamlit run ice_age_app.py
