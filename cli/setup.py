from setuptools import setup, find_packages

setup(
    name='sandbox-cli',
    version='0.1.0',
    description='CLI tool for AIO Sandbox',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'agent-sandbox>=0.0.30',
    ],
    entry_points={
        'console_scripts': [
            'sandbox=main:main',
        ],
    },
    python_requires='>=3.8',
)
