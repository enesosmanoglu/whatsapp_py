#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="whatsapp_py",
    version="1.0",
    description="Send automated messages with the WhatsApp Web.",
    author="Enes Osmanoğlu",
    author_email="enesosmanoglu@gmail.com",
    url="https://enesosmanoglu.github.io/whatsapp_py/",
    packages=find_packages(),
    install_requires=[
        "selenium == 4.10.0",
        "qrcode == 7.4.2",
        "pyodbc == 4.0.39"
    ],
)
