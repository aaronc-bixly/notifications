import codecs
from os import path

from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="Aaron Cunningham",
    author_email="aa.cunningham@outlook.com",
    description="User notification management for the Django web framework",
    name="notifications",
    long_description=read("README.md"),
    version="0.2.0",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    package_data={
        "notifications": [
            "locale/**/**/*",
        ]
    },
    install_requires=[
        "django-appconf>=1.0.1",
        "django>=1.7",
        "lockfile==0.10.2",
        "celery",
        "django-celery",
    ],
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
