from setuptools import find_packages, setup

setup(
    name="seen",
    version="0.1.3",
    description="Lightweight Web crawling framework for everyone.",
    author="cyrbuzz",
    author_email="cyrbuzz@foxmail.com",
    url='https://github.com/HuberTRoy/seen',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'aiohttp',
        'pyquery',
        'requests'
    ],
    license='GNU GPL 3',
    keywords=["crawling", "spider", "Lightweight"],
    packages=find_packages(),
    py_modules=['seen'],
    include_package_data=True
)