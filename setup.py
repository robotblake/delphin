from setuptools import setup, find_packages

setup(
    name='delphin',
    author='Blake Imsland',
    author_email='blake@retroco.de',
    license='MIT',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=['botocore', 'sqlparse'],
    packages=find_packages(),
    package_data={'botocore': ['data/*/*.json']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'delphin=delphin.cli:main',
        ]
    },
)
