from setuptools import find_packages, setup

setup(
    name="etl_base",
    version="0.1.0",
    packages=find_packages(include=["etl_base", "etl_base.*"]),
    install_requires=[
        "boto3",
        "pandas",
        "pyarrow",
    ],
    python_requires=">=3.8",
)
