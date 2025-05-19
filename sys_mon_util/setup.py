from setuptools import setup, find_packages

setup(
    name="system_monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'psutil>=5.9.0',
        'requests>=2.31.0',
        'python-daemon>=3.0.1; platform_system != "Windows"',
        'pywin32>=306; platform_system == "Windows"',
        'schedule>=1.2.0',
        'pyyaml>=6.0.1',
        'cryptography>=41.0.0',
    ],
    entry_points={
        'console_scripts': [
            'system_monitor=system_monitor:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A cross-platform system monitoring utility",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="system monitor security health check",
    url="https://github.com/yourusername/system_monitor",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
