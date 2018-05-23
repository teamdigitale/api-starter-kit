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

