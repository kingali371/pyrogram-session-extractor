from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyrogram-session-extractor",
    version="1.0.0",
    author="Your Name",
    description="استخراج جلسة Pyrogram من حساب تليجرام",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kingali371/pyrogram-session-extractor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyrogram>=2.0.0",
        "tgcrypto>=1.2.3",
    ],
    entry_points={
        "console_scripts": [
            "session-extractor=extractor:main",
        ],
    },
)
