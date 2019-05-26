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

### Environments

- **Dev** - Development collaboration branch which mirrors master branch
- **QA** - Environment where all integration tests are run
- **Staging** - A mirror of the production job, along with state and data. Deploying to staging first give the ability to "mock" a realistic release into production.
- **Production**

In addition to these environment, each developer may choose to have their own Development(s) environment for their individual use.

### Build Pipelines

1. **Build - Quality Assurance**
  - Purpose: Ensure code quality and integrity
  - Trigger: Pull Request to Master
  - Steps:
     1. Build Python packages
     2. Run units tests 
     3. Code Coverage
     4. Linting
2. **Build - Artifacts**
  - Purpose: To produce necessary artifacts for Release
  - Trigger: Commit to Master
  - Steps:
     1. Build and create Python Wheel
     2. Publish artifacts:
        - Python Wheel
        - Databricks Notebooks and cluster configuration
        - Data Factory pipeline definitions
        - IaC - ARM templates, Bash scripts
        - 3rd party library dependencies (JARs, etc)
  
### Release Pipelines

Currently, there is one multi-stage release pipeline with the following stages. Each stage deploys to a different environment.
  
1. **On-demand Integration Testing (QA) environment** - **TODO**
   1. Deploy Azure resources with ARM templates + Bash scripts
   2. Store sensitive configuration information in shared QA KeyVault
   3. Download integration test data from shared Storage to newly deployed ADAL Gen2.
   4. Configure Databricks workspace
      - Setup Data mount
      - Create Databricks secrets
   5. Deploy Data Application to Databricks
      - Deploy cluster given configuration
      - Upload Jars, Python wheels to DBFS
      - Install libraries on cluster
   6. Deploy ADF pipeline
   7. Run integration tests
      - Trigger ADF Pipeline
      - Databricks job to run integration test notebook

2. **Deploy to Staging**
   - NOTE: *Staging environment should be a mirror of Production and thus already have a configured Databricks workspace (secrets, data mount, etc), ADAL Gen2, ADF Pipeline, KeyVault, etc.*
   1. Hydrate data with latest production data
   2. Deploy Data Application to Databricks
      - Deploy cluster given configuration
      - Upload Jars, Python wheels to DBFS
      - Install libraries on cluster
   3. Deploy ADF Pipeline and activate triggers
   4. Run integration tests

3. **Deploy to Production**
   1. Deploy Data Application to Databricks
      - Deploy cluster given configuration
      - Upload Jars, Python wheels to DBFS
      - Install libraries on cluster
   2. Deploy ADF Pipeline
   3. Swap between existing deployment and newly released deployment

 
## Testing

- Unit Testing - Standard unit tests which tests small pieces of functionality within your code.

- Integration Testing - This includes end-to-end testing of the ETL pipeline.

- Data Testing  
    1. Structure - Test for correct schema, expected structure.
    2. Content - Can be tested through quantitative summary statistics and qualitative data quality graphs within the notebook.

## Monitoring

TODO

### Databricks

### Data Factory

## Deploy the solution

**IN PROGRESS**

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

