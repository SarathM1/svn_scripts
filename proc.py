#!/usr/bin/python
import subprocess
import yaml
import pandas as pd
import re
import yodl



def run_cmd(each_dir):
    cmd = "svn info {}".format(each_dir)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return output, err

def parse(output, pattern):
    match = re.search('(?<=' + pattern + ': ).*$', output, re.MULTILINE)
    if match:
        res = match.group()
        return res
    else:
        print 'No match'

def svn_info(each_dir):
    data_row = {}
    output, err = run_cmd(each_dir)
    data_row['revision_num'] =parse(output, 'Revision')
    data_row['date'] =parse(output, 'Last Changed Date')
    data_row['author'] =parse(output, 'Last Changed Author')
    return data_row

def main():
    with open('./test.yml', 'r') as stream:
        try:
            # dirs = yaml.load(stream)
            dirs = yaml.load(stream, yodl.OrderedDictYAMLLoader)
            data = []
            # for each_dir in dirs:
            for key, module in dirs['modules'].iteritems():
                row = svn_info(module['path'])
                row['path'] = module['path']
                row['owner'] = module['owner']
                data.append(row)
            df = pd.DataFrame(data)
            print "Data: \n", df
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == '__main__':
    main()
