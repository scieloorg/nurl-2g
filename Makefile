APP_VERSION := $(shell python setup.py --version)
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF := $(strip $(shell git rev-parse --short HEAD))

clean:
	@ rm -f dist/*

build:
	@python setup.py bdist_wheel

build_image: clean build
	@docker build \
		-t scieloorg/nurl:$(VCS_REF) \
		--build-arg WEBAPP_VERSION=$(APP_VERSION) \
		--build-arg VCS_REF=$(VCS_REF) \
		--build-arg BUILD_DATE=$(BUILD_DATE) .
	@docker tag scieloorg/nurl:$(VCS_REF) scieloorg/nurl:latest
	@docker tag scieloorg/nurl:$(VCS_REF) scieloorg/nurl:$(APP_VERSION)

upload_image:
	@docker push scieloorg/nurl

.PHONY: clean build build_image upload_image
