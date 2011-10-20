from setuptools import setup, find_packages

setup(
    name='django-multiblogs',
    version=__import__('multiblogs').__version__,
    license="BSD",

    install_requires = [],

    description='An application for managing multiple blogs, and even *gasp* blog "sets".',
    long_description=open('README').read(),

    author='Colin Powell',
    author_email='colin@onecardinal.com',

    url='http://github.com/powellc/django-multiblogs',
    download_url='http://github.com/powellc/django-multiblogs/downloads',

    include_package_data=True,

    packages=['multiblogs'],

    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
