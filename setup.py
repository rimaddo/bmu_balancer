from setuptools import setup, find_packages

setup(
    name='bmu_balancer',
    version='0.0.1',
    description='BMU Assignment Engine',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points="""\
    [paste.app_factory]
    main = bmu_balancer:main
    [console_scripts]
    bmu_balancer = bmu_balancer.cli:cli
    """
)
