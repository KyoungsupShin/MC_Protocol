import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="HslCommunication",
    version="1.0.6",
    author="Richard.Hu",
    author_email="hsl200909@163.com",
    description="An industrial IoT underlying architecture framework, focusing on the underlying technical communications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dathlin/HslCommunication",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)