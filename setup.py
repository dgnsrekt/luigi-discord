import io
import os
import sys


from setuptools import setup, find_packages
# from setuptools.command.text import test as TestCommand

long_description = ''  # TODO: add
install_requires = ['luigi', 'requests']
tests_require = ['pytest']

setup(
    name='luigi-discord',
    version='0.0.1',
    description='Send Discord notifications to report on Luigi pipelines',
    long_description=long_description,
    author='run2dev'
    author_email='run2devtest@gmail.com'
    url='https://github.com/run2dev',
    license='MIT'
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    # cmdclass = {'test': PyTest},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
    ],


)
