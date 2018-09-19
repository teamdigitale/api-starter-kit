#!/bin/bash
# Generate a python-flask app from the swagger.yaml
set -eo pipefail

usage(){
	echo "$0 path_to_swagger.yaml path_to_project_dir"

	echo "Further help via"
}
: {1?Missing infile}
: {2?Missing outdir}
: {3?Missing version}
: {4?Missing framework}}

IMG=ioggstream/swagger-codegen-cli
INFILE=$(readlink -f "$1")
OUTDIR=$(readlink -f "$2")
VERSION="$3"
FRAMEWORK="$4"


docker run --rm \
	--user=$UID:$GID \
	-v $INFILE:/swagger.yaml:z \
	-v $OUTDIR:/outdir:z $IMG \
	$VERSION generate -l $FRAMEWORK


