from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='convertable-key-model',
    version='1.0.3',
    author='황용호',
    author_email='jogakdal@gmail.com',
    description='ConvertableKeyModel: Dynamic key conversion for Pydantic models',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jogakdal/standard-api-response',
    install_requires=['pydantic', 'fastapi', 'inflection', 'advanced-python-singleton'],
    packages=find_packages(exclude=[]),
    keywords=['jogakdal', 'standard', 'API', 'response', 'helper', 'pydantic', 'convert', 'key'],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
