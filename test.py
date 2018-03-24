#!/usr/bin/python
import yaml
import yodl

with open('./test.yml', 'r') as stream:
    # data = yaml.load(stream)
    data = yaml.load(stream, yodl.OrderedDictYAMLLoader)
    for key, module in data['modules'].iteritems():
        print key, module['path'], module['owner']
