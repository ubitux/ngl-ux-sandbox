from setuptools import setup, find_packages

setup(name='ngl-ux-sandbox',
      version='0.1',
      packages=find_packages(),
      package_data={
          '': ['shaders/*'],
      }
)
