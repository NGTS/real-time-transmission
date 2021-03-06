from setuptools import setup, find_packages

setup(
    name='ngts_transmission',
    author='Simon Walker',
    author_email='s.r.walker101@googlemail.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'astropy',
        'pymysql',
        'numpy',
        'scipy',
        'photutils',
    ],
    package_data={
        '': ['*.json'],
    },
    entry_points={
        'console_scripts': [
            'ngtransmission = ngts_transmission.watching:main',
        ],
    },
)

