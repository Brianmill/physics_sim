from setuptools import Extension, setup

import pybind11

ext_modules = [
    Extension(
        "collision_core",
        ["collision_core.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=["/O2", "/std:c++17"],
    )
]

setup(
    name="collision_core",
    version="0.1.0",
    ext_modules=ext_modules,
)
