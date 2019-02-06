All parameters are set in azure.deploy.parameters.<ENV>.json files

.env.<ENV> files are produced after every deployment

## Scripts

deploy_all.sh
└── _deploy_resources.sh        <- deploys resources to a specific Environment
    └──_configure_adlagen2.sh   <- configures the newly deployed ADLA Gen2