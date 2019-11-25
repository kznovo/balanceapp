from setuptools import setup, find_packages

with open("./requirements.txt") as f:
    install_requires = f.read()

with open("./requirements.dev.txt") as f:
    extras_require = f.read()

setup(
    name="balanceapi",
    version="0.1",
    packages=find_packages(where="./balanceapi"),
    install_requires=install_requires,
    extras_require={"dev": extras_require},
)
