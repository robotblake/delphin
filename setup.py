from setuptools import setup, find_packages

setup(
    name='delphin',
    author='Blake Imsland',
    author_email='blake@retroco.de',
    license='MIT',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=['botocore>=1.5.52', 'sqlparse'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'delphin=delphin.cli:main',
        ]
    },
)
