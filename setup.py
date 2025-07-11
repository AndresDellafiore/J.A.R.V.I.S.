@"
from setuptools import setup, find_packages

setup(
    name="jarvis",
    version="0.1",
    packages=find_packages(),
)
"@ | Out-File -FilePath setup.py -Encoding utf8