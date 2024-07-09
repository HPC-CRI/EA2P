from setuptools import setup, find_packages

setup(
    name='EA2P',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'py-cpuinfo',
        'psutil',
        'requests'
        # Add your dependencies here
    ],
    author='Roblex NANA',
    author_email='nanatchakouteroblex@email.com',
    description='EA2P : A flexible and accurate multi-platforms profiling tool for fine-grained energy measurement of applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/HPC-CRI/EA2P',
    classifiers=[
        'Programming Language :: Python :: 3',
        # Add any relevant classifiers
    ],
)
