import os
from distutils.core import setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()


setup(
    name='update_helper',
    version=__import__('update_helper').__version__,
    description='an update helper',
    long_description=readme,
    author='adorsk',
    url='http://github.com/adorsk/update_helper',
    py_modules=['update_helper'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
