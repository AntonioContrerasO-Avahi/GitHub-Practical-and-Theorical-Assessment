#!/usr/bin/env bash
# 2.2 Conda Environment for ML Stack (~30 min) [Optional]
# Prerequisites: conda must be installed (Anaconda or Miniconda)
set -euo pipefail

conda create -n ml-dev python=3.11 -y
conda activate ml-dev

# Install PyTorch with CUDA (adjust pytorch-cuda version to match your GPU)
conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y
conda install -c conda-forge transformers datasets -y
pip install tensorboard wandb

# Verify CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Export environment
conda env export > environment.yml
conda env export --from-history > environment-minimal.yml

echo ""
echo "environment.yml and environment-minimal.yml created."
echo "To recreate: conda env create -f environment.yml"
