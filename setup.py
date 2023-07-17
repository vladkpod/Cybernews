from setuptools import setup, find_packages

setup(
    name="newsfeed-aggregator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "feedparser",
        "pymongo",
        "pandas",
        "nltk",
        "scikit-learn",
        "numpy"
    ],
    entry_points={
        'console_scripts': [
            'run-parser = reader:run_parser',
            'build-model = model:build_model',
        ],
    },
    python_requires='>=3.7',
)
