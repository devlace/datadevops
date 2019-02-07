# DataDevOps

*This repository is currently a work in progress.*

The purpose of this repository is to demonstrate how DevOps principles can be applied Data Pipeline Solution. 

## Architecture

The following shows the overall architecture of the solution.

![Architecture](images/architecture.PNG?raw=true "Architecture")

### Design Principles

- **Data Transformation logic belongs in packages, not Notebooks**
  - All main data transformation code is packages within a Python package/JAR/etc. These packages are then uploaded to DBFS and installed on the specifically configured cluster along with all other third party dependencies (ei. azure-cosmosdb-spark jar). Notebooks then import the python package and calls relevant functions. Effectively, the Notebooks become a lightweight wrapper around the notebook. This ensures Unit Test can be easily write for the transformation logic. This also applies to any custom Extraction and Loading logic.
- **Data should be tested**
  - Two different tests should be performed: 
    - **Structure** (is the data in the expected shape / schema?)
    - **Content** (are there unexpected nulls? Are the summary statistics in expected ranges?)
- **Data should have lineage**
  - Just as application deployments should have lineage so you can track which code commit produced the artifacts and deployments, each final loaded data record should be tagged with the appropriate ETL pipeline run id. Not only does this ensure traceability, it also helps with recovery from failed / half-run data loads.


## CI/CD

The following shows the overall CI/CD process end to end.

![CI/CD](images/CI_CD.PNG?raw=true "CI/CD")

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

Currently, there is one multi-stage release pipelines with the following stages, with each stage deploying to a different environment.
  
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
  - 
## Data

All data procured here: https://www.melbourne.vic.gov.au/about-council/governance-transparency/open-data/Pages/on-street-parking-data.aspx

