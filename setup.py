from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastwg",
    version="1.0.2",
    author="wolfDiesel",
    author_email="",
    description="Fast WireGuard server management via CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wolfDiesel/fast-wireguard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "fastwg=fastwg.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
