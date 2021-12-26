.PHONY: run build clean

run: build
	python main.py

build: clean
	python -m pip install -e .

clean:
	python -m pip uninstall -y testmodule
	rm -rf build testmodule/*.so testmodule/*.c testmodule.egg-info

