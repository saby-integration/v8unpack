import sys

import setuptools

sys.path[0:0] = ['src\\v8unpack']

from version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='v8unpack',
    version=__version__,
    url='https://github.com/saby-integration/v8unpack',
    license='MIT',
    author='Razgovorov Mikhail',
    author_email='1338833@gmail.com',
    description='Unpacking binaries 1C to JSON for GIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: Russian',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        "Operating System :: OS Independent"
    ],
    keywords='1C CF CFE EPF V8UNPACK SABY SBIS СБИС 1С',
    python_requires='>=3.6',
    zip_safe=False,
    packages=setuptools.find_packages(where='src'),
    package_dir={"": "src"},
    install_requires=[
        'tqdm>=4'
    ],
    entry_points={
        'console_scripts':
            [
                'v8unpack = v8unpack:main',
            ]
    }
)
