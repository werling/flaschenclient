import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flaschenclient",
    version="0.1.3",
    author="Sebastian Werling",
    author_email="sebastian.werling@gmail.com",
    description="With this python library you can send simple animations to the flaschen taschen server (fork).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/werling/flaschenclient",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
    ],
)
