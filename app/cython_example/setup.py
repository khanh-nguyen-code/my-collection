import os

import setuptools
from Cython import Distutils

if __name__ == "__main__":
    setuptools.setup(
        install_requires=["cython", ],
        packages=["testmodule", ],
        zip_safe=False,
        name="testmodule",
        author="khanh",
        cmdclass={"build_ext": Distutils.build_ext},
        ext_modules=[
            setuptools.Extension(
                name="testmodule.wrapper",
                sources=[
                    os.path.join("testmodule", "lib", "testmodule.c"),
                    os.path.join("testmodule", "wrapper.pyx")
                ],
                libraries=[],
                include_dirs=[],
                extra_compile_args=[],
            )
        ],

    )
