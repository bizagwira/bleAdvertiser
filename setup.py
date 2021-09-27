from setuptools import setup
setup(
	name='ble',
	version='0.1.0',
	description='ble package provides the API tools based on ble112 for the BLE dongle',
	url='#',
	author='Honoré BIZAGWIRA',
	author_email='devios.honore@gmail.com',
	license='MIT',
	packages=['ble'],
	zip_safe=False,
    install_requires=[
		'Pillow==8.3.1',
		'pyserial==3.5',
		'serial==0.0.97'
    ]
)
