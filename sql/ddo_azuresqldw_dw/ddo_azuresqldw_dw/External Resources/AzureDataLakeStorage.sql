CREATE EXTERNAL DATA SOURCE [AzureDataLakeStorage]
    WITH (
    TYPE = HADOOP,
    LOCATION = N'abfss://datalake@ddostordevvnhf6tvx.dfs.core.windows.net',
    CREDENTIAL = [ADLSCredentialKey]
    );









