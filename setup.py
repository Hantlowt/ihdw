import setuptools

setuptools.setup(
    name="ihdw",
    version="0.1.5",
    description="ihdw",
    long_description="i hate dynamic website",
    url="https://github.com/Hantlowt/ihdw",
    packages=setuptools.find_packages(),
    py_modules=['ihdw'],
    install_requires=['git+https://github.com/Hantlowt/ihdb', 'git+https://github.com/Hantlowt/ihf'],
    include_package_data=True
)
