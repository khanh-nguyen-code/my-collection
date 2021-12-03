.PHONY: run build clean

run: build
	python main.py

build: clean
	python setup.py develop

clean:
	rm -rf build testmodule/*.so testmodule/*.c testmodule.egg-info

