import os
import pathlib
import re

from setuptools import find_packages, setup

regexp = re.compile(r'.*__version__ = [\'\"](.*?)[\'\"]', re.S)

base_package = 'record_keeper'
base_path = os.path.dirname(__file__)

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    changes = f.read()

with open('PACKAGE_VERSION') as f:
    package_version = f.read().strip()


def parse_requirements(filename):
    ''' Load requirements from a pip requirements file '''
    with open(filename, 'r') as fd:
        print(f"resolve packages dependencies in {filename}")
        lines = []
        for line in fd:
            line = line.strip()
            potential_path_obj = line.split('#')
            potential_path = potential_path_obj[0].strip()

            if os.path.isdir(potential_path):
                """ the folder name needs to match the package name for this to work """
                package_folder = pathlib.PurePath(potential_path)
                package = f'{package_folder.name}'
                if len(potential_path_obj) > 1:
                    version_pin = potential_path_obj[1].strip()
                    package = f'{package}{version_pin}'
                    print(f' - resolved path to package'
                          f'\'{potential_path}\' --> {package} added')
                else:
                    print(f' - resolved path to package'
                          f'\'{potential_path}\' --> {package} (latest) added')
                lines.append(package)
            elif line and not line.startswith("#"):
                print(f' - package \'{potential_path}\' added')
                lines.append(line.strip())
    return lines


requirements = parse_requirements('requirements.local.txt')
requirements.extend(parse_requirements('requirements.txt'))


if __name__ == '__main__':
    setup(
        name='record_keeper',
        description='A description of the package.',
        long_description='\n\n'.join([readme, changes]),
        long_description_content_type='text/markdown',
        license='Not open source',
        url='https://github.com/williamwissemann/foundation',
        version=package_version,
        author='William T. Wissemann',
        author_email='WilliamWissemann@gmail.com',
        maintainer='William T. Wissemann',
        maintainer_email='WilliamWissemann@gmail.com',
        install_requires=requirements,
        keywords=['record_keeper'],
        package_dir={'': 'src'},
        packages=find_packages('src'),
        include_package_data=True,
        zip_safe=False,
        classifiers=['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Programming Language :: Python :: 3.8']
    )
