#!/bin/bash

echo "Starting RIC installation..."

cd ~

# Step 1
sudo -i
git clone http://gerrit.o-ran-sc.org/r/it/dep -b bronze
cd dep/
git submodule update --init --recursive --remote

# Step 2
cd tools/k8s/bin
./gen-cloud-init.sh

# Step 3
# TODO: Patch k8s-1node-cloud-init-k_1_16-h_2_12-d_cur.sh