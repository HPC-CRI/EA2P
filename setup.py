from setuptools import setup, find_packages

setup(
    name='EA2P',
    version='1.0.1',
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
    description='EA2P (Energy-Aware Application Profiler): A multi-platform profiling tool that offers precise and detailed energy usage measurements for applications, with the ability to adapt to different needs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/HPC-CRI/EA2P',
    classifiers=[
        'Programming Language :: Python :: 3',
        # Add any relevant classifiers
    ],
)
