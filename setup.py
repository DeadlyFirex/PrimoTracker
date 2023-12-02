from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("version.txt", "r", encoding="utf-8") as fh:
    version = fh.read().strip()

setup(
    name='PrimoTracker',
    version=version,
    author="DeadlyFirex",
    author_email="info.deadlyfirex@gmail.com",
    description="Backend for the primo tracking applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DeadlyFirex/PrimoTracker",
    project_urls={
        "Bug Tracker": "https://github.com/DeadlyFirex/PrimoTracker/issues",
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU AGPLv3 License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Flask",
        "python_json_config",
        "SQLAlchemy",
        "Flask-SQLAlchemy",
        "flask-jwt-extended[asymmetric_crypto]",
        "Flask-Limiter",
        "bcrypt"
    ],
    python_requires=">=3.10",
)
