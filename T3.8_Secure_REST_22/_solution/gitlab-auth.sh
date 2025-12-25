#! /bin/bash

# Example bash script to authenticate to GitLab REST API
# to retrieve Contributors on a Project Repository

# As the user for their Personal Access Token
# if not provided as an ENV
if [[ -z "${GITLAB_TOKEN}" ]]; then
  echo "What is your Personal Access Token? (Note: input will be hidden)"
  read -s GITLAB_TOKEN
fi

# Lookup the address for GitLab
# if environment variables are not set
if [[ -z "${GITLAB_ADDRESS}" ]]; then
  echo "What is the address for GitLab? (include https:// or http:// as required)"
  echo "  example: https://gitlab-01.ppm.example.com"
  read GITLAB_ADDRESS
fi

# GitLab Project ID
PROJECT_ID='devnet%2FT3.8_Secure_REST_2'

# Make the API request to GitLab for the Project Contributors
# TODO: Update the CURL request below to pass the provided Personal Access Token in Authorization header
curl -k --silent --header "Authorization: Bearer ${GITLAB_TOKEN}" \
  ${GITLAB_ADDRESS}/api/v4/projects/${PROJECT_ID}/repository/contributors
