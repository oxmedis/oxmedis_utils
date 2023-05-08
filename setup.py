import setuptools

print(":)")
print(setuptools.find_packages(where="src"))
print(setuptools.find_packages(where="src"))
print(setuptools.find_packages(where="src"))
print(":)")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as fp:  # add and read requirements.txt
    install_reqs = [
        r.rstrip() for r in fp.readlines() if not r.startswith("#")
    ]


setuptools.setup(
    name="oxmedis_utils",
    version="0.0.0",
    author="Allison Clement",
    author_email="",
    description="utils and general functions for oxmedis gorup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    license="",
    install_requires=install_reqs,
)
