from setuptools import setup, find_packages

setup(
    name='growfin',
    version='0.1.0',
    description='Fetch historical and live NSE stock data with Groww API',
    author='Subham Giri',
    author_email='your_email@example.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'pytz',
        'tzlocal'
    ],
    python_requires='>=3.7',
)

