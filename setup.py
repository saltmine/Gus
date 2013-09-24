from setuptools import setup, find_packages

print find_packages()

setup(
    name='gus',
    version='1.0.0',
    author='Mark Tozzi',
    author_email='mark.tozzi@keepholdings.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://keep.com',
    license=open('LICENSE').read(),
    description='Gus schleps code onto boxes',
    long_description=open('README.rst').read(),
    install_requires=open('pip_requirements.txt').readlines(),
    dependency_links=open('dependency_links.txt').readlines(),
)
