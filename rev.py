#!/usr/bin/python
import pysvn
path="/home/sm/project1_work/"
client = pysvn.Client()

entry_list = \
entry = client.info(path)
headrev = entry.get("revision").number
time = entry.get("properties_time")
print  headrev, time

from_revision = pysvn.Revision(pysvn.opt_revision_kind.number, headrev -5)
to_revision = pysvn.Revision( pysvn.opt_revision_kind.head )

for l in log:
    print i.date
    print i.author
