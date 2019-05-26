
#!/bin/bash

# Access granted under MIT Open Source License: https://en.wikipedia.org/wiki/MIT_License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, # and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions 
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

#
# A Databricks Environment typically consists of:
# 1. Notebooks in workspace
# 2. Libraries in DBFS
# 3. Cluster information
#

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace # For debugging

# Set path
dir_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$dir_path"


###################
# Requires the following to be set:
#
# RELEASE_ID=
# CLUSTER_NAME=
# MOUNT_DATA_PATH=
# MOUNT_DATA_CONTAINER=
# DATABASE=
# WHEEL_FILE_PATH=


# Deploy clusters
full_cluster_name=${CLUSTER_NAME}_${RELEASE_ID}
cluster_config=$(cat ./config/cluster.config.template.json |
    sed "s~__REPLACE_CLUSTER_NAME__~${full_cluster_name}~g" |
    sed "s~__REPLACE_MOUNT_DATA_PATH__~${MOUNT_DATA_PATH}~g" |
    sed "s~__REPLACE_MOUNT_DATA_CONTAINER__~${MOUNT_DATA_CONTAINER}~g" |
    sed "s~__REPLACE_DATABASE__~${DATABASE}~g")
databricks clusters create --json "$cluster_config"

# Set DBFS libs path
dbfs_libs_path=dbfs:${MOUNT_DATA_PATH}/libs/release_${RELEASE_ID}

# Upload dependencies
echo "Uploading libraries dependencies to DBFS..."
databricks fs cp ./libs/ "${dbfs_libs_path}" --recursive

echo "Uploading app libraries to DBFS..."
databricks fs cp $WHEEL_FILE_PATH "${dbfs_libs_path}"

# Install Library dependencies
echo "Installing 3rd party library depedencies into cluster..."
cluster_id=$(databricks clusters list | awk '/'$full_cluster_name'/ {print $1}')
databricks libraries install \
    --jar "${dbfs_libs_path}/azure-cosmosdb-spark_2.3.0_2.11-1.2.2-uber.jar" \
    --cluster-id $cluster_id

echo "Installing app libraries into cluster..."
wheel_file=$(basename $WHEEL_FILE_PATH)
databricks libraries install \
    --jar "${dbfs_libs_path}/${wheel_file}" \
    --cluster-id $cluster_id

# Upload notebooks to workspace
echo "Uploading notebooks to workspace..."
databricks workspace import_dir "notebooks" "/releases/release_${RELEASE_ID}/"