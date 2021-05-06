import setuptools

setuptools.setup(
    name="ihdw",
    version="0.1.6",
    description="ihdw",
    long_description="i hate dynamic website",
    url="https://github.com/Hantlowt/ihdw",
    packages=setuptools.find_packages(),
    py_modules=['ihdw'],
    install_requires=['jinja2', 'singleton-decorator', 'git+https://github.com/Hantlowt/ihdb', 'git+https://github.com/Hantlowt/ihf'],
    include_package_data=True
)
