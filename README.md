# datadevops

## Architecture

## CI/CD

### Build Pipelines

### Release Pipelines

#### Environments
- Dev
- Stg
- Prod

## Data

## Known Issues, Limitations and Workarounds
- Currently, ADLA Gen2 cannot be managed via the az cli 2.0. 
  - **Workaround**: Use the REST API to automate creation of the File System.
- Databricks KeyVault-backed secrets scopes can only be create via the UI, and thus cannot be created programmatically and was not incorporated in the automated deployment of the solution.
  - **Workaround**: Use normal Databricks secrets with the downside of duplicated information.