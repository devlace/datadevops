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
- **QA** - Environment where all integration tests are run (*not yet implmented*)
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

### Pre-requisites:
1. Github Account
2. Azure DevOps Account + Project
3. Azure Account

### Software pre-requisites:
1. For Windows users, [Windows Subsystem For Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
2. [az cli 2.x](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
3. [Python 3+](https://www.python.org/)
4. [databricks-cli](https://docs.azuredatabricks.net/dev-tools/databricks-cli.html)
5. [jq](https://stedolan.github.io/jq/)

NOTE: This deployment was tested using WSL (Ubuntu 16.04) and Debian GNU/Linux 9.9 (stretch)

### Deployment Instructions

1. Fork this repository. Forking is necessary if you want to setup git integration with Azure Data Factory.
2. **Deploy Azure resources.** 
    1. Clone the forked repository and `cd` into the root of the repo
    2. Run `./deploy.sh`.
        - This will deploy three Resource Groups (one per environment) each with the following Azure resources.
            - Data Factory (empty) - *next steps will deploy actual data pipelines*.
            - Data Lake Store Gen2 and Service Principal with Storage Contributor rights assigned.
            - Databricks workspace - notebooks uploaded, SparkSQL tables created, and ADLS Gen2 mounted using SP.
            - KeyVault with all secrets stored.
        - This will create a local `.env.{environment_name}` files containing essential configuration information.
        - All Azure resources are tagged with correct Environment.
        - IMPORTANT: Due to a limitation of the inability to generate Databricks PAT tokens automatically, you will be prompted generate and enter this per environment. See [here](https://docs.azuredatabricks.net/dev-tools/databricks-cli.html#set-up-authentication) for more information.
        - The solution is designed such that **all** starting environment deployment configuration should be specified in the arm.parameters files. This is to centralize configuration.

3. **Setup ADF git integration in DEV Data Factory**
    1. In the Azure Portal, navigate to the Data Factory in the **DEV** environment.
    2. Click "Author & Monitor" to launch the Data Factory portal.
    3. On the landing page, select "Set up code repository". For more information, see [here](https://docs.microsoft.com/en-us/azure/data-factory/source-control).
    4. Fill in the repository settings with the following:
        - Repository type: **Github**
        - Github Account: ***your_Github_account***
        - Git repository name: **forked Github repository**
        - Collaboration branch: **master**
        - Root folder: **/adf**
        - Import Existing Data Factory resource to respository: **Unselected**
    5. Navigating to "Author" tab, you should see all the pipelines deployed.
    6. Select `Connections` > `Ls_KeyVault`. Update the Base Url to the KeyVault Url of your DEV environment.
    7. Select `Connections` > `Ls_AdlsGen2_01`. Update URL to the ADLS Gen2 Url of your DEV environment.

4. **Setup Build Pipelines.** You will be creating two build pipelines, one which will trigger for every pull request which will run Unit Testing + Linting, and the second one which will trigger on every commit to master and will create the actual build artifacts for release.
    1. In Azure DevOps, navigate to `Pipelines` > `Builds`. Select new Build Pipeline.
    2. Under "Where is your code?", select Github (YAML) and select the correct forked repository.
        - If you have not yet already, you maybe prompted to connect your Github account. See [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/repos/github?view=azure-devops&tabs=yaml#grant-access-to-your-github-repositories) for more information.
    3. Under "Configure your pipeline", select Existing Azure Pipelines YAML file.
        - Branch: master
        - Path: `/src/ddo_transform/azure-pipelines-ci-qa.yaml`
    4. Select `Run`.
    5. Repeat for `/src/ddo_transform/azure-pipelines-ci-artifacts`

5. **Setup Release Pipelines**

    **TODO**


## Known Issues, Limitations and Workarounds
- Currently, ADLS Gen2 cannot be managed via the az cli 2.0. 
  - **Workaround**: Use the REST API to automate creation of the File System.
- Databricks KeyVault-backed secrets scopes can only be create via the UI, and thus cannot be created programmatically and was not incorporated in the automated deployment of the solution.
  - **Workaround**: Use normal Databricks secrets with the downside of duplicated information.
- Databricks Personal Access Tokens can only be created via the UI.
  - **Workaround**: User is asked to supply the tokens during deployment, which is unfortunately cumbersome.
- Data Factory Databricks Linked Service does not support dynamic configuration, thus needing a manual step to point to new cluster during deployment of pipeline to a new environment.
  - **Workaround**: Alternative is to create an on-demand cluster however this may introduce latency issues with cluster spin up time. Optionally, user can manually update Linked Service to point to correct cluster.

## Data

### Physical layout

ADLS Gen2 is structured as the following:
------------

    datalake                    <- filesystem
        /libs                   <- contains all libs, jars, wheels needed for processing
        /data
            /lnd                <- landing folder where all data files are ingested into.
            /databricks_delta   <- final tables 


------------


All data procured here: https://www.melbourne.vic.gov.au/about-council/governance-transparency/open-data/Pages/on-street-parking-data.aspx
