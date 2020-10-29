import setuptools

setuptools.setup(
    name="badoo-expert-system",
    version="1.0.0",
    author="Maxim Fominykh and Arseny Anciferov",
    author_email="fominykh.max@gmail.com",
    url="https://github.com/maxifom/badoo-expert-system",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'avatar_saver=badoo_expert_system.cmd.avatar_saver:main',
            'face_detector=badoo_expert_system.cmd.face_detector:main',
            'html_parser=badoo_expert_system.cmd.html_parser:main',
            'web_markuper=badoo_expert_system.cmd.web_markuper:main'
        ]
    },
    python_requires='>=3.9',
)
