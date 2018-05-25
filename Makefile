YAML=$(shell find * -name \*yaml)
YAMLSRC=$(shell find openapi -name \*yaml.src)
YAMLGEN=$(patsubst %.yaml.src,%.yaml,$(YAMLSRC))

yaml: $(YAMLGEN)


%.yaml: %.yaml.src
	. .tox/py36/bin/activate
	yamllint $<
	python ./scripts/yaml-resolver.py $< $@



yamllint: $(YAML)
	. .tox/py36/bin/activate
	yamllint $?

# Create a simple project starting from OpenAPI v3 spec
#  in simple.yaml.
prj-simple: openapi/simple.yaml
	# Convert OpenAPI v3 to a temporary Swagger 2.0 using
	#  docker image ioggstream/api-spec-converter
	./scripts/openapi2swagger.sh openapi/simple.yaml > /tmp/swagger.yaml

	# Generate a flask client from v2 spec using
	#  docker image ioggstream/
	./scripts/generate-flask.sh /tmp/swagger.yaml  ./prj-simple/
	(cd prj-simple && docker-compose up --build)

