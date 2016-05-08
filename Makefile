IMAGE=sejvlond/python-ultimate-server
NAME="ultimate-server"

build:
	docker build -t ${IMAGE} .

push:
	docker push ${IMAGE}

run:
	docker run -it -d -P --name ${NAME} ${IMAGE}

run-i:
	docker run -it --rm -P ${IMAGE}

stop:
	docker stop ${NAME}

rm: stop
	docker rm ${NAME}

clean: rm
	find . -name "*.pyc" -or -name "__pycache__" | xargs rm -rf
