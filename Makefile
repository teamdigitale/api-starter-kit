YAML=$(shell find * -name \*yaml)
YAMLSRC=$(shell find openapi -name \*yaml.src)
YAMLGEN=$(patsubst %.yaml.src,%.yaml,$(YAMLSRC))

yaml: $(YAMLGEN)


%.yaml: %.yaml.src
	. .tox/py36/bin/activate
	yamllint $<
	python ./scripts/openapi_resolver.py $< $@



yamllint: $(YAML)
	. .tox/py36/bin/activate
	yamllint $?

# Create a simple project starting from OpenAPI v3 spec
#  in simple.yaml.
prj-simple-generate: openapi/simple.yaml
	# Convert OpenAPI v3 to a temporary Swagger 2.0 using
	#  docker image ioggstream/api-spec-converter
	./scripts/openapi2swagger.sh openapi/simple.yaml > /tmp/swagger.yaml

	# Generate a flask client from v2 spec using
	#  docker image swaggerapi/swagger-codegen-cli
	./scripts/generate-flask.sh /tmp/swagger.yaml  ./prj-simple/

prj-simple: prj-simple-generate
	(cd prj-simple && docker-compose up --build test )


prj-simple-quickstart: prj-simple-generate
	# Test all
	(cd prj-simple && docker-compose up --build test )
	# Build and run the application
	(cd prj-simple && docker-compose up simple )

