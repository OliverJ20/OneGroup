from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import os
import shlex

DIR = "/usr/local/onegroup"
SYSTEM = "/lib/systemd/system"
SERVICE = "onegroup.service"

class PostDevelopCommand(develop):
    """Post-Installation for development mode"""
    def run(self):
        develop.run(self)

class PostInstallCommand(install):
    """Post-Installation for install"""
    def run(self):
        install.run(self)
        #print(os.path.dirname(os.path.realpath(__file__)))
        subprocess.call(shlex.split('mkdir {}'.format(DIR)))
        subprocess.call(shlex.split('mv {} {}'.format(SERVICE,SYSTEM)))
        subprocess.call(shlex.split('chmod {} {}'.format("644",SYSTEM+"/"+SERVICE)))
        subprocess.call(shlex.split('systemctl {}'.format("daemon-reload")))
        subprocess.call(shlex.split('systemctl {} {}'.format("enable",SERVICE))) 

setup(
    name = 'OneGroup',
    version='1.0.0',
    description='Webclient for OpenVPN',
    long_description='OpenVPN management client for web',
    classifiers=[
        'Development status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='OpenVPN web management client',
    url= 'https://github.com/SebSherry/CapstoneTeam1',
    author='Capstone Group One',
    author_email='CapstoneGroupOne@gmail.com',
    license='MIT',
    packages = ["onegroup"],
    install_requires=[
        'flask',
        'cherrypy',
        'passlib'
    ],
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    include_package_data=True,
    zip_safe=False
)
