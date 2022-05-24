from setuptools import setup

setup(
    name='calepin',
    version='0.1.0',
    description='Static website generator',
    url='https://github.com/julienharbulot/calepin',
    author='Julien Harbulot',
    author_email='',
    license='MIT',
    packages=['calepin'],
    install_requires=list(open('./pip-requirements.txt')),
    classifiers=[],
)