import glob
from setuptools import setup, find_packages

setup(
    name='WordleAssistant',
    version='2021.01.29',
    description='Python class solving wordle puzzles.',
    author='Danny E.P. Vanpoucke',
    license='MIT',
    keywords='wordle, machine learning, almost artificial intelligence',
    url='https://github.com/DannyVanpoucke/WordleAssistant',
    packages=find_packages(),
	#find_packages(include=['WordleLib'],exclude=['examples', 'examples.*']),
    zip_safe=False,
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Hobby',
        'License :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
#    setup_requires=['pytest-runner',],
#    tests_require=['pytest',],
)