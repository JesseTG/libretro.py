import os.path
import re

import setuptools
import ctypesgen

# TODO: Clone libretro-common here

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

# Inspiration: https://stackoverflow.com/a/7071358/6064135
with open('src/libretro/_version.py', 'r') as version_file:
    version_groups = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_groups:
        version = version_groups.group(1)
    else:
        raise RuntimeError('Unable to find version string!')

REQUIREMENTS = [
    # Add your list of production dependencies here, eg:
    # 'requests == 2.*',
]

DEV_REQUIREMENTS = [
    'bandit == 1.7.*',
    'black == 23.*',
    'build == 0.10.*',
    'ctypesgen == 1.1.*',
    'flake8 == 6.*',
    'isort == 5.*',
    'mypy == 1.5.*',
    'pytest == 7.*',
    'pytest-cov == 4.*',
    'twine == 4.*',
]

THISDIR = os.path.dirname(__file__)
LIBRETRO_COMMON_PATH = os.path.join(THISDIR, 'deps', 'libretro-common')

if not os.path.exists(LIBRETRO_COMMON_PATH):
    raise FileNotFoundError(f"libretro-common not found at {LIBRETRO_COMMON_PATH}; run 'git submodule update --init'")

LIBRETRO_COMMON_INCLUDE = os.path.join(LIBRETRO_COMMON_PATH, 'include')
CTYPESGEN_TARGET = os.path.join(THISDIR, 'src', 'libretro', '_libretro.py')

ctypesoptions = ctypesgen.options.get_default_options()
ctypesoptions.output_file = CTYPESGEN_TARGET
ctypesoptions.headers = [os.path.join(LIBRETRO_COMMON_INCLUDE, 'libretro.h')]

descriptions = ctypesgen.parser.parse(ctypesoptions.headers, ctypesoptions)
ctypesgen.processor.process(descriptions, ctypesoptions)
ctypesgen.printer.WrapperPrinter(CTYPESGEN_TARGET, ctypesoptions, descriptions)

setuptools.setup()
