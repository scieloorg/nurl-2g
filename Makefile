clean:
	@ rm -f dist/*

build:
	@python setup.py bdist_wheel

build_image: clean build
	@docker build -t nurl:latest .
	@docker tag nurl scieloorg/nurl

upload_image:
	@docker push scieloorg/nurl

.PHONY: clean build build_image upload_image
