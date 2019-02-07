
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


set -o errexit
set -o pipefail
set -o nounset
set -o xtrace # For debugging

# Set path
dir_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$dir_path"


###################
# USER PARAMETERS
release_id="${1-}"
cluster_name="${2-}"
mount_data_path="${3-}"
mount_data_container="${4-}"
database="${5-}"


# Deploy clusters
full_cluster_name=${cluster_name}_${release_id}
cluster_config=$(cat ./config/cluster.config.template.json |
    sed "s~__REPLACE_CLUSTER_NAME__~${full_cluster_name}~g" |
    sed "s~__REPLACE_MOUNT_DATA_PATH__~${mount_data_path}~g" |
    sed "s~__REPLACE_MOUNT_DATA_CONTAINER__~${mount_data_container}~g" |
    sed "s~__REPLACE_DATABASE__~${database}~g")
databricks clusters create --json "$cluster_config"

# Upload dependencies
echo "Uploading libraries dependencies..."
databricks fs cp ./libs/ "dbfs:${mount_data_path}/libs/$release_id" --recursive --overwrite

# Install Library dependencies
echo "Installing 3rd party library depedencies..."
cluster_id=$(databricks clusters list | awk '/'$full_cluster_name'/ {print $1}')
databricks libraries install \
    --jar "dbfs:${mount_data_path}/libs/azure-cosmosdb-spark_2.3.0_2.11-1.2.2-uber.jar" \
    --cluster-id $cluster_id