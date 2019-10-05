#-----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
#-----------------------------------------------------------------------------------------
FROM python:3

# Install pylint
RUN pip install pylint databricks-cli

# Configure apt
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils 2>&1

# Install git, process tools, lsb-release (common in install instructions for CLIs)
RUN apt-get -y install git procps lsb-release jq

# Install any missing dependencies for enhanced language service
RUN apt-get install -y libicu[0-9][0-9]

# Instal az cli
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install java
RUN apt-get install -y openjdk-8-jdk
ENV JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64

RUN mkdir /workspace
WORKDIR /workspace

# Install Python dependencies from requirements.txt if it exists
COPY src/ddo_transform/requirements.txt* src/ddo_transform/requirements_dev.txt* /workspace/
RUN pip install -r requirements_dev.txt \
    && rm requirements_dev.txt* \
    && pip install -r requirements.txt \ 
    && rm requirements.txt*

# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

# Databricks dev env
ENV DATABRICKS_TOKEN=dapid5fd5daf58dd0125bd5e84810668d5c3
ENV DATABRICKS_HOST=https://australiaeast.azuredatabricks.net
ENV DATABRICKS_CLUSTER_ID=1001-093620-hitch722
ENV DATABRICKS_DBFS_UPLOAD_PATH=dbfs:/mnt/datalake
ENV DATABRICKS_WORKSPACE_UPLOAD_PATH=/notebooks


# Set the default shell to bash rather than sh
ENV SHELL /bin/bash
