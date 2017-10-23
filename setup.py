from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import os
import shlex

DIR = "/usr/local/onegroup"
SYSTEM = "/lib/systemd/system"
BIN = "/usr/local/bin"
ETC = "/etc/onegroup"
SERVICE = "onegroup.service"
CONFIG = "onegroup.conf"
STARTUP = "onegroup.py"

class PostDevelopCommand(develop):
    """Post-Installation for development mode"""
    def run(self):
        develop.run(self)
        postInstallProcedure()

class PostInstallCommand(install):
    """Post-Installation for install"""
    def run(self):
        install.run(self)
        postInstallProcedure()

def postInstallProcedure():
    """ 
        Global post install procedure
    """
    #Make system dir
    subprocess.call(shlex.split('mkdir {}'.format(DIR)))
    subprocess.call(shlex.split('mkdir {}'.format(DIR+"/keys")))

    #Make config folder and place config
    subprocess.call(shlex.split('mkdir {}'.format(ETC)))
    subprocess.call(shlex.split('mv {} {}'.format(CONFIG,DIR)))
    
    #If a config file exists, don't over write
    if not os.path.exists(ETC+"/"+CONFIG):
        subprocess.call(shlex.split('cp {} {}'.format(DIR+"/"+CONFIG,ETC)))

    #Create and start service
    subprocess.call(shlex.split('mv {} {}'.format(SERVICE,SYSTEM)))
    subprocess.call(shlex.split('chmod {} {}'.format("644",SYSTEM+"/"+SERVICE)))
    subprocess.call(shlex.split('systemctl {}'.format("daemon-reload")))
    subprocess.call(shlex.split('systemctl {} {}'.format("enable",SERVICE))) 

    #Move startup script to /usr/bin/local
    subprocess.call(shlex.split('mv {} {}'.format(STARTUP,BIN+"/onegroup")))
    


setup(
    name = 'OneGroup',
    version='1.0.0',
    description='Webclient for OpenVPN',
    long_description='OpenVPN management client for web',
    classifiers=[
        'Development status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='OpenVPN web management client',
    url= 'https://github.com/OliverJ20/OneGroup',
    author='Capstone Group One',
    license='MIT',
    packages = ["onegroup"],
    install_requires=[
        'flask',
        'flask-mail',
        'cherrypy',
        'passlib',
        'paste',
        'apscheduler',
        'requests'
    ],
    scripts=[
        'onegroup/scripts/userman',
        'onegroup/scripts/tabler' 
    ],
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    include_package_data=True,
    zip_safe=False
)
