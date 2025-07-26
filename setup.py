from os.path import abspath
import sys
import setuptools

sys.path.insert(0, abspath(__file__))

with open("README.md", "r", encoding='utf-8') as f:
    readme = f.read()
with open('requirements.txt', "r", encoding='utf-8') as f:
    reqs = f.read()

setuptools.setup(
    name="reso",
    version='0.0.0',
    author="Reso-team",
    description="omit",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["test", "docs", "frontend"]),
    install_requires=reqs.strip().split('\n'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        # 'console_scripts': [
            # 'xxxxxx = xxxxx.cli:main',
        # ],
    },
    python_requires='>=3.10',
)
