CREATE EXTERNAL DATA SOURCE [AzureDataLakeStorage]
    WITH (
    TYPE = HADOOP,
    LOCATION = N'abfss://CONTAINER@STORAGEACCOUNT.dfs.core.windows.net',
    CREDENTIAL = [ADLSCredentialKey]
    );







