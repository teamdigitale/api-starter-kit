YAML=$(shell find * -name \*yaml)
YAMLSRC=$(shell find openapi -name \*yaml.src)
YAMLGEN=$(patsubst %.yaml.src,%.yaml,$(YAMLSRC))

yaml: $(YAMLGEN)

.ONESHELL:
%.yaml: %.yaml.src
	. .tox/py36/bin/activate
	yamllint $<
	python -m openapi_resolver $< $@



yamllint: $(YAML)
	. .tox/py36/bin/activate
	yamllint $?

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


python-flask-quickstart: python-flask-generate
	# Test all
	(cd python-flask && docker-compose up --build test )
	# Build and run the application
	(cd python-flask && docker-compose up simple )


prj-jaxrs-generate: openapi/simple.yaml
	./scripts/codegen.sh openapi/simple.yaml java-jaxrs 3 jaxrs-resteasy-eap
