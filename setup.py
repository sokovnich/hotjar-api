from setuptools import setup, find_packages
import os


project_dir = os.path.dirname(__file__)

with open(os.path.join(project_dir, "README.md"), encoding="utf8") as readme:
    long_description = readme.read()

with open(
    os.path.join(project_dir, "requirements.txt"), encoding="utf8"
) as requirements:
    install_requirements = requirements.read().split("\n")


setup(
    name="hotjar",
    version="0.0.2",
    packages=find_packages(exclude=["tests*"]),
    author="Sokovnich Yan",
    author_email="x6@live.ru",
    long_description=long_description,
    install_requires=install_requirements,
)
