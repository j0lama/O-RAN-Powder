#!/bin/bash

echo "Starting RIC installation..."

cd ~

# Step 1
git clone http://gerrit.o-ran-sc.org/r/it/dep -b bronze
cd dep/
git submodule update --init --recursive --remote

# Step 2
cd tools/k8s/etc
sed -i 's/2.12.3/2.17.0/g' infra.rc
cd ../bin/
./gen-cloud-init.sh

# Step 3
mv k8s* k8s_install.sh
sed -i 's/https:\/\/storage.googleapis.com\/kubernetes-helm\/helm-v/https:\/\/get.helm.sh\/helm-v/g' k8s_install.sh
sed -i 's/4.15.0-45-lowlatency/$(uname -r)/g' k8s_install.sh
./k8s_install.sh

# Step 4
cd ~
sed -i 's/kong-docker-kubernetes-ingress-controller.bintray.io\/kong-ingress-controller/kong\/kubernetes-ingress-controller/g' ~/dep/ric-dep/helm/infrastructure/subcharts/kong/values.yaml
cd dep/bin/
./deploy-ric-platform -f ../RECIPE_EXAMPLE/PLATFORM/example_recipe.yaml
# Fix Tiller
KUBE_EDITOR="sed -i 's/gcr.io\/kubernetes-helm\/tiller:v2.12.3/ghcr.io\/helm\/tiller:v2.17.0/g'" kubectl edit deploy deployment-tiller-ricxapp -n ricinfra

# Step 5
cd ..
echo '{ "config-file.json_url": "https://gerrit.o-ran-sc.org/r/gitweb?p=ric-app/hw.git;a=blob_plain;f=init/config-file.json;hb=HEAD" }' > onboard.hw.url
curl --location --request POST "http://$(hostname):32080/onboard/api/v1/onboard/download"  --header 'Content-Type: application/json' --data-binary "@./onboard.hw.url"

# Step 6
curl --location --request POST "http://$(hostname):32080/appmgr/ric/v1/xapps"  --header 'Content-Type: application/json'  --data-raw '{"xappName": "hwxapp"}'

echo "RIC installation completed!"