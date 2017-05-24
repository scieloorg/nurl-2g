clean:
	@ rm -f dist/*

build:
	@python setup.py bdist_wheel

build_image: clean build
	@docker build -t nurl:latest .

.PHONY: clean build build_image
