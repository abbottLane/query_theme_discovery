venv: venv/touchfile

venv/touchfile: requirements.txt
	pip install virtualenv
	test -d venv || virtualenv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile

build: venv
	. venv/bin/activate;

clusters: build
	python cluster.py \
	    --model roberta-base \
		--dataset spider \
		--dataset_column question \
		-k 20 \
		-r 10

cluster-labels: build
	python label_clusters.py --input_dir ./output/

clean:
	rm -rf venv
	find -iname "*.pyc" -delete