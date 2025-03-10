import os
from setuptools import setup
from django_exchange import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: Django',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

REQUIREMENTS = [
    'django>=1.11',
    'exchangelib>=5.5.0',
]

setup(
    name='django-exchange',
    packages=['django_exchange'],
    version=__version__,
    description='EmailBackend for Django to work with Microsoft Exchange Server',
    long_description=read('README.md'),
    license='MIT',
    author='Robert Stein',
    author_email='robert@blueshoe.de',
    url='https://github.com/Blueshoe/django-exchange',
    install_requires=REQUIREMENTS,
    keywords=['django', 'Outlook', 'Microsoft', 'Exchange', 'Blueshoe'],
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False
)