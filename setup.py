from setuptools import setup

url = "https://github.com/jic-dtool/dtool-irods"
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-irods",
    packages=["dtool_irods"],
    version=version,
    description="Add iRODS support to dtool",
    long_description=readme,
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
    url=url,
    install_requires=[],
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
