from setuptools import setup

setup(
    name='flp2fms',
    version='0.1',
    py_modules=['flp2fms'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        flp2fms=flp2fms:cli
    ''',
)