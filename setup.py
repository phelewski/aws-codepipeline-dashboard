from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='aws-codepipeline-dashboard',
    version='1.0.0',
    author='Peter Helewski',
    description='A utility for creating a CloudWatch Dashboard for AWS CodePipelines',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/phelewski/aws-codepipeline-dashboard',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['boto3'],
    python_requires='>=3.8'
)
