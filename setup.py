from setuptools import setup, find_packages

setup(
    name="fastwg",
    version="1.0.0",
    author="wolfDiesel",
    author_email="wolfdiesel@example.com",
    description="Fast WireGuard server management via CLI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wolfDiesel/fast-wireguard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "cryptography>=42.0.0",
        "pyqrcode>=1.2.1",
        "pypng>=0.20220715.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "fastwg=fastwg.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
