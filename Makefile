#
# Prepare openapi files and run projects in containers.
#
YAML=$(shell find * -name \*yaml)
YAMLSRC=$(shell find openapi -name \*yaml.src)
YAMLGEN=$(patsubst %.yaml.src,%.yaml,$(YAMLSRC))

yaml: $(YAMLGEN)

.ONESHELL:
%.yaml: %.yaml.src
	tox -e yamllint -- $<
	tox -e yaml --  $< $@
	tox -e valid_oas 



yamllint: $(YAML)
	tox -e yamllint -- $?

# Create a simple project starting from OpenAPI v3 spec
#  in simple.yaml.
python-flask-generate: openapi/simple.yaml
	# Convert OpenAPI v3 to a temporary Swagger 2.0 using
	#  docker image ioggstream/api-spec-converter
	./scripts/openapi2swagger.sh openapi/simple.yaml > /tmp/swagger.yaml

	# Generate a flask client from v2 spec using
	#  docker image swaggerapi/swagger-codegen-cli
	./scripts/codegen.sh /tmp/swagger.yaml  ./python-flask/ 2 python-flask 

python-flask: python-flask-generate
	(cd python-flask && docker-compose up --build test )

python-flask-spid: openapi/spid.yaml
	cp openapi/spid.yaml python-flask-spid/spid.yaml
	(cd python-flask-spid && docker-compose up --build simple idp)

python-flask-quickstart: python-flask-generate
	# Test all
	(cd python-flask && docker-compose up --build test )
	# Build and run the application
	(cd python-flask && docker-compose up simple )

