# Databricks notebook source
import os

# Set mount path
storage_mount_data_path = os.environ['MOUNT_DATA_PATH']
storage_mount_container = os.environ['MOUNT_DATA_CONTAINER']

# Unmount if existing
for mp in dbutils.fs.mounts():
  if mp.mountPoint == storage_mount_data_path:
    dbutils.fs.unmount(storage_mount_data_path)

# Refresh mounts
dbutils.fs.refreshMounts()

# COMMAND ----------

# Retrieve storage credentials
storage_account = dbutils.secrets.get(scope = "storage_scope", key = "storage_account")
storage_sp_id = dbutils.secrets.get(scope = "storage_scope", key = "storage_sp_id")
storage_sp_key = dbutils.secrets.get(scope = "storage_scope", key = "storage_sp_key")
storage_sp_tenant = dbutils.secrets.get(scope = "storage_scope", key = "storage_sp_tenant")

# Mount
configs = {"fs.azure.account.auth.type": "OAuth",
           "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
           "fs.azure.account.oauth2.client.id": storage_sp_id,
           "fs.azure.account.oauth2.client.secret": storage_sp_key,
           "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/" + storage_sp_tenant + "/oauth2/token"} 

# Optionally, you can add <your-directory-name> to the source URI of your mount point.
dbutils.fs.mount(
  source = "abfss://" + storage_mount_container + "@" + storage_account + ".dfs.core.windows.net/",
  mount_point = storage_mount_data_path,
  extra_configs = configs)

# Refresh mounts
dbutils.fs.refreshMounts()
