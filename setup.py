import setuptools

with open("README.md") as readme:
    long_description = readme.read()

setuptools.setup(
    name="slashes",
    version="0.0.5",
    author="Nathan Turner",
    author_email="nathan@clicksminuteper.net",
    description="A python implementation of discord slash commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Minion3665/slasher",
    project_urls={
        "Bug Tracker": "https://github.com/Minion3665/slasher/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)
