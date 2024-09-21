deploy:
	kubectl apply -f deployment.yaml

run: build
	docker run -it -u $(shell id -u) \
		-v $(PWD)/messages:/app/messages \
		-v $(PWD)/cache:/cache \
		-v $(PWD)/cache:/app/.nb2workflow \
		-v $(PWD)/cache/urivalue:/tmp/urivalue \
		-v $(PWD)/auth.toml:/.config/hop/auth.toml \
		-e NB2W_CACHE=/cache \
		-e HERMES_API_KEY=aa \
		-e MATRIX_IMMA_CHANNEL_REAL="" \
		-e MATRIX_IMMA_CHANNEL_TEST="" \
		-e MATRIX_TOKEN="" \
		-e ILVK_GCN_KAFLA_ID=gcn-kafla-id \
		-e ILVK_GCN_KAFLA_SECRET=gcn-kafla-id \
			odahub/integral-lvk 

build:
	docker build . -t odahub/integral-lvk --push


secrets:
	kubectl create secret generic auth-toml --from-file=auth.toml=auth.toml --dry-run=client -o yaml | kubectl apply -f -
	kubectl create secret generic matrix --from-literal=token=matrix --dry-run=client -o yaml | kubectl apply -f -
	kubectl create secret generic hermes --from-literal=api_key=matrix --dry-run=client -o yaml | kubectl apply -f -
