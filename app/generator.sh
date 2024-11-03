#!/bin/sh

 for i in `seq 1 10`;
do
	java -jar build/libs/app.jar & 
	cd ../python/clients
	echo "cpd"
	source clients/bin/activate
	python3 asf.py & 
	python3 asf.py
	cd ../../app
done

