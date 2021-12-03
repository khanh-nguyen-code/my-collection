publish: build
	twine upload --verbose dist/*

build: clean
	python setup.py sdist

clean:
	rm -rf dist khanh_utils.egg-info

