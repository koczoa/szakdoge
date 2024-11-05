#!/bin/sh
date +"%T"
 for i in `seq 1 300`;
do
	java -jar build/libs/app.jar & 
	cd ../python/clients
#	echo "cpd"
	source clients/bin/activate
	python3 asf.py & 
	python3 asf.py
	cd ../../app
	echo "run $i is done"
done
date +"%T"