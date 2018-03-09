#!/usr/bin/python
# FILE: configure.py
# VERS: Python 2
# DESC: Configures qdrouterd.conf file with the attribute
#       values specified by the environmental variables
#
###########################################################
import os
import sys

fname = "/etc/qpid-dispatch/qdrouterd.conf"
out = sys.argv[1]

SECTION_VARS = ["ROUTER", "SSL_PROFILE", "AUTH_SERVICE_PLUGIN", "LISTENER", "CONNECTOR", "LOG",
                "ADDRESS", "LINK_ROUTE", "AUTO_LINK", "CONSOLE", "POLICY", "VHOST"]

autogen_warning="""#\n# AUTOGENERATED FILE - Generated by /opt/interconnect/bin/launch/configure.py.\n"""
config = []
comments = []

SECT = 0
ATTR = 1
ATTR_NAME = 0
ATTR_VALUE = 1

ENV = [e for e in os.environ if e.split("_")[SECT] in SECTION_VARS]

def read_config(fname):
  ''' Read Configuration file into multi-dimension list for easier manipulation '''
  in_section = False
  with open(fname, 'r') as fin:
    for line in fin:
      if(line[0] ==  "#"):
        comments.append(line)
      else:
        line = line.split("\n")
        line = ''.join(filter(lambda x: x != "", line))
        if("{" in line):
          section = [line.split(" ")[0], []]
          in_section = True
        elif("}" in line):
          config.append(section)
          in_section = False
        elif(in_section):
          attr = line.split(":")
          attr = [x.strip() for x in attr]
          section[ATTR].append(attr)
  fin.close()

def split_env_label(e):
  v = ""
  for sv in SECTION_VARS:
    if(sv in e):
      v = sv.lower()  
  return v, e[len(v)+1:].lower()

def update_config():
  ''' Update configuration list with environment variable attributes'''
  for e in ENV:
    esect, eattr = split_env_label(e)
    eattr = "".join(w.capitalize() for w in eattr.split("_"))
    eattr = eattr[0].lower() + eattr[1:]
    for c in config:
      csect = c[SECT]
      if(esect == csect):
        if(eattr in [cattr[ATTR_NAME] for cattr in c[ATTR]]):
          for cattr in c[ATTR]:
            if(eattr == cattr[ATTR_NAME]):
              cattr[ATTR_VALUE] = os.environ.get(e)
        else:
          c[ATTR].append([eattr,os.environ.get(e)])

def write_config(fname):
  ''' Write new qdrouter.conf with update attributes and sections'''
  fh = open(fname, "w")
  for c in comments:
    fh.write(c)
  fh.write(autogen_warning)
  fh.write("\n")
  for c in config:
    fh.write(c[SECT] + " {\n")
    for i in c[ATTR]:
      fh.write("    " + ": ".join(i) + "\n")
    fh.write("}\n\n")
  fh.close()

read_config(fname)
update_config()
write_config(out)

# For debugging purposes
with open(out, 'r') as fin:
    print fin.read()