set -e
az login
az extension add -n ml -y || true
az ml online-endpoint create --name saifr-retail-endpoint --resource-group <rg-azureaivalidation> --workspace-name <larissacamposcardoso-9427_ai> --file aml_endpoint.yaml
az ml online-deployment create --endpoint-name saifr-retail-endpoint --name saifr-retail-deploy --file aml_deployment.yaml --resource-group <rg-azureaivalidation> --workspace-name <larissacamposcardoso-9427_ai>
az ml online-endpoint get-keys --name saifr-retail-endpoint --resource-group <rg-azureaivalidation> --workspace-name <larissacamposcardoso-9427_ai>