from setuptools import setup, find_packages

setup(
    name='epub_translator',  # 包名
    version='0.1.0',  # 版本号
    description='A tool for translating EPUB files',  # 简短描述
    long_description=open('README.md').read(),  # 详细描述，通常从README文件中读取
    long_description_content_type='text/markdown',  # 描述内容的格式
    author='Your Name',  # 作者名
    author_email='your.email@example.com',  # 作者邮箱
    url='https://github.com/yourusername/epub_translator',  # 项目主页
    packages=find_packages(where='backend'),  # 自动发现包
    package_dir={'': 'backend'},  # 包所在目录
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',  # Python版本要求
    install_requires=[
        # 列出项目依赖的第三方库
        'somepackage>=1.0.0',
        'anotherpackage>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'epub-translate=backend.main:main',  # 命令行工具的入口
        ],
    },
)