.PHONY: build dev test tests up-dev bash prod up-dev up-prod


build: prod

prod:
	docker-compose build prod

up-prod:
	docker run -p 80:80 ocrpytesseract/ocrpytesseract:latest-prod

bash:
	docker-compose run --entrypoint=bash dev
