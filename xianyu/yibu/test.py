#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import os
import re

source_dir = './mytemplate'

camel_case_pattern = re.compile(r'[a-zA-Z]+')

converted_files = set()

for root, dirs, files in os.walk(source_dir):
    for filename in files:

        match = camel_case_pattern.search(filename)
        if match and filename not in converted_files:
        # process filename conversion
            converted_filename = filename.replace(match.group(0), match.group(0).lower())
            print('Converting {} to {}'.format(filename, converted_filename))
            shutil.move(os.path.join(root, filename), os.path.join(root, converted_filename))

        converted_files.add(filename)

print('Conversion completed!')
