# DataDevOps

## Background

The following solution was based on a number of two recent customer engagements with CSE.

## Architecture


## CI/CD

### Build Pipelines

### Release Pipelines

#### Environments
- Dev
- Stg
- Prod

- Tagging appropriate resources

## Deploy

This will deploy three resource groups, one per environment (dev, stg, prod). Only the dev resource group will have the databricks environment fully configured with the solution. 

Note that this deployment will create a Service Principle per environment.

Deploy Build and Release pipelines to deploy to the remaining stg and prod resource group.

## Data


## Known Issues, Limitations and Workarounds
- Currently, ADLA Gen2 cannot be managed via the az cli 2.0. 
  - **Workaround**: Use the REST API to automate creation of the File System.
- Databricks KeyVault-backed secrets scopes can only be create via the UI, and thus cannot be created programmatically and was not incorporated in the automated deployment of the solution.
  - **Workaround**: Use normal Databricks secrets with the downside of duplicated information.
- Databricks Personal Access Tokens can only be created via the UI.
  - **Workaround**: User is asked to supply the tokens during deployment, which is unfortunately cumbersome.