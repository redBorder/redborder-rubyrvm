#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the list of gems
GEMS=(
  "ruby-druid-0.1.10.gem"
  "ilo-sdk-1.3.1.gem"
  "redborder-consul-connector-0.0.6.gem"
  "prettyprint-0.0.1.gem"
)

# Define the host URL
GEMINABOX_HOST="https://geminabox.redborder.com/gems/"

# Define the target directory
TARGET_DIR="${SCRIPT_DIR}/SOURCES"

# Create the target directory if it does not exist
mkdir -p "${TARGET_DIR}"

# Loop over the list of gems and download each one to the target directory
for GEM in "${GEMS[@]}"; do
  wget -P "${TARGET_DIR}" "${GEMINABOX_HOST}${GEM}"
done

