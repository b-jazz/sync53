from setuptools import setup, find_packages

setup(
    name='sync53',
    version='0.1',
    description='Discover your IP address and update the DNS entry hosted on Amazon\'s Route53.',
    url='https://github.com/b-jazz/sync53',
    license='GPLv3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
#    packages=find_packages(where='src'),
    py_modules=['sync53'],
    install_requires=['click', 'requests', 'boto'],
    entry_points = {
        'console_scripts': [
            'sync53=sync53:main',
        ],
    },
)
