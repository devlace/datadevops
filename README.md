[![Build Status](https://dev.azure.com/devlacepub/DataDevOps/_apis/build/status/ddo_transform-ci-artifacts?branchName=master)](https://dev.azure.com/devlacepub/DataDevOps/_build/latest?definitionId=3&branchName=master)

# DataDevOps

The purpose of this repository is to demonstrate how DevOps principles can be applied Data Pipeline Solution. 

## Architecture

The following shows the overall architecture of the solution.

![Architecture](images/architecture.PNG?raw=true "Architecture")

### Design Considerations

- **Data Transformation logic belongs in packages, not Notebooks**
  - All main data transformation code should be packaged up within a Python package/JAR/etc. These packages are then uploaded to DBFS and installed on a specifically configured cluster, along with all other third-party dependencies (ei. azure-cosmosdb-spark jar). Notebooks then simply import the package(s) and calls any relevant functions. Effectively, Notebooks become a lightweight wrapper around the packages. This ensures seperation of concerns and promotes code reuse, testability, and code quality.
- **Data should be tested**
  - Two different tests should be performed: 
    - **Structure** (Is the data in the expected shape / schema?)
    - **Content** (Are there unexpected nulls? Are the summary statistics in expected ranges?)
- **Data should have lineage**
  - Just as application deployments should have lineage in order to track which code commit produced which artifacts and deployments, each final loaded data record should be tagged with the appropriate ETL pipeline run id. Not only does this ensure traceability, it also helps with recovery from any potential failed / half-run data loads.

## Build and Release Pipeline

The following shows the overall CI/CD process end to end.

![CI/CD](images/CI_CD.PNG?raw=true "CI/CD")

Both Build and Release Pipelines are built using [AzureDevOps](https://dev.azure.com/) (Public instance) and can be view using the following links:
- [Build Pipelines](https://dev.azure.com/devlacepub/DataDevOps/_build)
- [Release Pipeline](https://dev.azure.com/devlacepub/DataDevOps/_release)

More information [here](docs/CI_CD.md).
### Environments

- **Dev** - Development collaboration branch
- **QA** - Environment where all integration tests are run
- **Staging/UAT** - A mirror of the production job, along with state and data. Deploying to staging first give the ability to "mock" a realistic release into production.
- **Production**

In addition to these environment, each developer may choose to have their own Development(s) environment for their individual use.
 
## Testing

- Unit Testing - Standard unit tests which tests small pieces of functionality within your code. Data transformation code should have unit tests.

- Integration Testing - This includes end-to-end testing of the ETL pipeline.

- Data Testing  
    1. Structure - Test for correct schema, expected structure.
    2. Content - Can be tested through quantitative summary statistics and qualitative data quality graphs within the notebook.

## Monitoring

### Databricks
- [Monitoring Azure Databricks with Azure Monitor](https://docs.microsoft.com/en-us/azure/architecture/databricks-monitoring/)
- [Monitoring Azure Databricks Jobs with Application Insights](https://msdn.microsoft.com/en-us/magazine/mt846727.aspx)

### Data Factory
- [Monitor Azure Data Factory with Azure Monitor](https://docs.microsoft.com/en-us/azure/data-factory/monitor-using-azure-monitor)
- [Alerting in Azure Data Factory](https://azure.microsoft.com/en-in/blog/create-alerts-to-proactively-monitor-your-data-factory-pipelines/)

## Deploy the solution

**WORK IN PROGRESS**

To deploy the solution, 

1. cd into the base directory
2. Run `./deploy.sh`
   - This will create `.env.{environment_name}` files containing essential configuration information.
   - Important: Due to a limitation of the inability to generate Databricks PAT tokens automatically, you **must** manually generate these and fill in the appropriate .env files before proceeding.
3. Run `./databricks/configure_databricks.sh`

The deployment will perform the following:
1. Deploy base infrastructure.
2. Deploy solutions infrastructure to three resource groups (one per environment with the exception of QA -- as this get spun up on demand by the Release pipeline).
3. (Currently manual) - Deploy CI/CD pipeline given yaml and json definitions. **TODO**
 
Notes:
- Base infrastructure contains shared infrastructure such as QA KeyVault and Storage Account with integration testing data **TODO**
- The solution is designed such that **all** starting environment deployment configuration should be specified in the arm.parameters files. This is to centralize configuration.
- All resources are appropriately tagged with the relevant Environments.
- Each environment has a KeyVault specific to the environment where All sensitive configuration information is stored.
- The deployment will create a Service Principle per environment.

## Known Issues, Limitations and Workarounds
- Currently, ADLA Gen2 cannot be managed via the az cli 2.0. 
  - **Workaround**: Use the REST API to automate creation of the File System.
- Databricks KeyVault-backed secrets scopes can only be create via the UI, and thus cannot be created programmatically and was not incorporated in the automated deployment of the solution.
  - **Workaround**: Use normal Databricks secrets with the downside of duplicated information.
- Databricks Personal Access Tokens can only be created via the UI.
  - **Workaround**: User is asked to supply the tokens during deployment, which is unfortunately cumbersome.
- Data Factory Databricks Linked Service does not support dynamic configuration, thus needing a manual step to point to new cluster during deployment of pipeline to a new environment.
  - **Workaround**: Alternative is to create an on-demand cluster however this may introduce latency issues with cluster spin up time. Optionally, user can manually update Linked Service to point to correct cluster.
## Data

### Physical layout

ADLA Gen2 is structured as the following:
------------

    datalake                    <- filesystem
        /libs                   <- contains all libs, jars, wheels needed for processing
        /data
            /lnd                <- landing folder where all data files are ingested into.
            /databricks_delta   <- final tables 


------------






All data procured here: https://www.melbourne.vic.gov.au/about-council/governance-transparency/open-data/Pages/on-street-parking-data.aspx

