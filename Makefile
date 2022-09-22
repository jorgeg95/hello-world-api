build: 
	docker build -t hello-world-api .

compose-up: 
	docker compose up -d

compose-down: 
	docker compose down

compose-restart: compose-down compose-up

test: 
	python3 -m unittest test_revolut_code_challenge_server

helm-install:
	helm upgrade --install --set DB_USER=${DB_USER} --set DB_PASSWORD=${DB_PASSWORD} --set DB_NAME=${DB_NAME} hello-world-api kubernetes/helm/ -f kubernetes/helm/values.yml

helm-remove:
	# The || true avoids throwing error when the release is not installed
	# Useful for the make clean
	helm delete hello-world-api || true 

clean: helm-remove compose-down
	docker rmi --force hello-world-api
