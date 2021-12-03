publish: build
	twine upload --verbose dist/*

build: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist khanh_utils.egg-info

