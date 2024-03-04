import os.path
import setuptools
import ctypesgen

# TODO: Only run ctypesgen if building a sdist
THISDIR = os.path.dirname(__file__)
LIBRETRO_COMMON_PATH = os.path.join(THISDIR, 'deps', 'libretro-common')

# TODO: Fetch the version dynamically from CHANGELOG.md

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
