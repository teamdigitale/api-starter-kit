#!/usr/bin/sh
# Generate a python-flask app from the swagger.yaml
set -eo pipefail

usage(){
	echo "$0 path_to_swagger.yaml path_to_project_dir"

	echo "Further help via"
}
: {1?Missing infile}
: {2?Missing outdir}
docker run --rm \
	-v $(readlink -f "$1"):/swagger.yaml:z \
	-v $(readlink -f "$2"):/outdir:z swaggerapi/swagger-codegen-cli \
	generate -l python-flask -o /outdir -i /swagger.yaml


