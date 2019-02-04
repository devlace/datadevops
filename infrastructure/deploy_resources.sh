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
# set -o xtrace # For debugging

###################
# SETUP

# Check if required utilities are installed
command -v jq >/dev/null 2>&1 || { echo >&2 "I require jq but it's not installed. See https://stedolan.github.io/jq/.  Aborting."; exit 1; }
command -v az >/dev/null 2>&1 || { echo >&2 "I require azure cli but it's not installed. See https://bit.ly/2Gc8IsS. Aborting."; exit 1; }

# Globals
timestamp=$(date +%s)
deploy_name="deployment${timestamp}"
env_file="../.env"

# Constants
RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m'

# Set path
dir_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$dir_path"

# Check if user is logged in
[[ -n $(az account show 2> /dev/null) ]] || { echo "Please login via the Azure CLI: "; az login; }


###################
# USER PARAMETERS

env_name="${1-}"
rg_name="${2-}"
rg_location="${3-}"
sub_id="${4-}"

storage_fs=datalake # fixed

while [[ -z $env_name ]]; do
    read -rp "$(echo -e ${ORANGE}"Enter environment (dev, stg or prod): "${NC})" env_name
    # TODO validate if dev, stg, prod
done

while [[ -z $rg_name ]]; do
    read -rp "$(echo -e ${ORANGE}"Enter Resource Group name: "${NC})" rg_name
done

while [[ -z $rg_location ]]; do
    read -rp "$(echo -e ${ORANGE}"Enter Azure Location (ei. EAST US 2): "${NC})" rg_location
done

while [[ -z $sub_id ]]; do
    # Check if user only has one sub
    sub_count=$(az account list --output json | jq '. | length')
    if (( $sub_count != 1 )); then
        az account list --output table
        read -rp "$(echo -e ${ORANGE}"Enter Azure Subscription Id you wish to deploy to (enter to use Default): "${NC})" sub_id
    fi
    # If still empty then user selected IsDefault
    if [[ -z $sub_id ]]; then
        sub_id=$(az account show --output json | jq -r '.id')
    fi
done


#####################
# Deploy ARM template

# Set account to where ARM template will be deployed to
echo "Deploying to Subscription: $sub_id"
az account set --subscription $sub_id

# Retrieve KeyVault User Id
upn=$(az account show --output json | jq -r '.user.name')
kvOwnerObjectId=$(az ad user show --upn $upn \
    --output json | jq -r '.objectId')

# Create resource group
echo "Creating resource group: $rg_name"
az group create --name "$rg_name" --location "$rg_location"

# Deploy arm template
echo "Deploying resources into $rg_name"
arm_output=$(az group deployment create \
    --name "$deploy_name" \
    --resource-group "$rg_name" \
    --template-file "./azuredeploy.json" \
    --parameters @"./azuredeploy.parameters.${env_name}.json" \
    --parameters "kvOwnerObjectId=${kvOwnerObjectId}" \
    --output json)

if [[ -z $arm_output ]]; then
    echo >&2 "ARM deployment failed." 
    exit 1
fi


#####################
# Setup ADLS Gen2
# 1. Create Service Principle for ADLS Gen2
# 2. Grant correct RBAC role
# 3. Create File System using REST API

# Retrieve storage account (ADLS Gen2) details
storage_account=$(echo $arm_output | jq -r '.properties.outputs.storName.value')
storage_account_key=$(az storage account keys list \
    --account-name $storage_account \
    --resource-group $rg_name \
    --output json |
    jq -r '.[0].value')
storage_account_id=$(az storage account show \
    --name "$storage_account" \
    --resource-group "$rg_name" \
    --output json |
    jq -r '.id')

# Retrieve service principle name for ADLA Gen2 from arm output
sp_stor_name=$(echo $arm_output | jq -r '.properties.outputs.spStorName.value')

# Create service principle for ADLA Gen2
echo "Creating Service Principal (SP) for access to ADLA Gen2: '$sp_stor_name'"
sp_stor_out=$(az ad sp create-for-rbac --name $sp_stor_name \
    --skip-assignment \
    --output json)
sp_stor_id=$(echo $sp_stor_out | jq -r '.appId')
sp_stor_pass=$(echo $sp_stor_out | jq -r '.password')
sp_stor_tenantid=$(echo $sp_stor_out | jq -r '.tenant')

# Grant "Storage Blob Data Owner (Preview)
echo "Granting 'Storage Blob Data Contributor (Preview)' for '$storage_account' to SP' '$sp_stor_name'"
az role assignment create --assignee "$sp_stor_id" \
    --role "Storage Blob Data Contributor (Preview)" \
    --scope "$storage_account_id"


# Because ADLA Gen2 is not yet supported by the az cli 2.0 as of 2019/02/04
# we resort to calling the REST API directly:
# https://docs.microsoft.com/en-us/rest/api/storageservices/datalakestoragegen2/filesystem
#
# For information on calling Azure REST API, see here: 
# https://docs.microsoft.com/en-us/rest/api/azure/

# Use service principle to generate bearer token
bearer_token=$(curl -X POST -d "grant_type=client_credentials&client_id=${sp_stor_id}&client_secret=${sp_stor_pass}&resource=https%3A%2F%2Fstorage.azure.com%2F" \
    https://login.microsoftonline.com/${sp_stor_tenantid}/oauth2/token |
    jq -r '.access_token')

# Use bearer token to create file system
echo "Creating ADLA Gen2 File System '$storage_fs' in storage account: '$storage_account'"
curl -X PUT -d -H 'Content-Type:application/json' -H "Authorization: Bearer ${bearer_token}" \
    https://${storage_account}.dfs.core.windows.net/${storage_fs}?resource=filesystem


####################
# Retrieve any remaining configuration information

# Ask user to configure databricks cli
# TODO: see if this can be automated
dbricks_name=$(echo $arm_output | jq -r '.properties.outputs.dbricksName.value')
echo -e "${ORANGE}"
echo "Configure your databricks cli to connect to the newly created Databricks workspace: ${dbricks_name}. See here for more info: https://bit.ly/2GUwHcw."
databricks configure --token
echo -e "${NC}"

# Databricks token and details
dbricks_location=$(echo $arm_output | jq -r '.properties.outputs.dbricksLocation.value')
dbi_token=$(awk '/token/ && NR==3 {print $0;exit;}' ~/.databrickscfg | cut -d' ' -f3)
[[ -n $dbi_token ]] || { echo >&2 "Databricks cli not configured correctly. Please run databricks configure --token. Aborting."; exit 1; }

# Retrieve KeyVault details
kv_name=$(echo $arm_output | jq -r '.properties.outputs.kvName.value')


####################
# Build Env file

echo "Appending configuration to .env file."
cat << EOF >> $env_file

# ------ Configuration from deployment ${deploy_name} -----------
SP_STOR_NAME=${sp_stor_name}
SP_STOR_ID=${sp_stor_id}
SP_STOR_PASS=${sp_stor_pass}
SP_STOR_TENANT=${sp_stor_tenantid}
KV_NAME=${kv_name}
DBRICKS_DOMAIN=${dbricks_location}.azuredatabricks.net
DBRICKS_TOKEN=${dbi_token}
BLOB_STORAGE_ACCOUNT=${storage_account}
BLOB_STORAGE_KEY=${storage_account_key}

EOF

echo "Completed deploying Azure resources."