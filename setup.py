from setuptools import setup, find_packages

setup(
    name='ngts-transmission',
    author='Simon Walker',
    author_email='s.r.walker101@googlemail.com',
    version="0.0.2",
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

