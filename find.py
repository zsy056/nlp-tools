#! /usr/bin/env python
import sys
import lxml.etree

def find_node(node, tag, sel_nodes):
    if node.tag == tag:
        sel_nodes.append(node)
    else:
        for c_node in list(node):
            find_node(c_node, tag, sel_nodes)

def find_in_first_child(node, tag, sel_nodes):
    while True:
        if node == None: break
        if node.tag == tag: sel_nodes.append(node)
        lst = list(node)
        if len(lst)>0: node = lst[0]
        else: break

def find_tag(nodes, tag):
    ret_nodes = []
    for node in nodes:
        sib = node.getnext()
        while sib==None and node.getparent()!=None and node.tag!='ROOT':
            node = node.getparent()
            sib = node.getnext()
        if sib==None and node.tag=='ROOT': continue
        #find_in_first_child(node, tag, ret_nodes)
        find_in_first_child(sib, tag, ret_nodes)
    return ret_nodes

def is_sel(node, query):
    qtags = query.split('+')
    f_nodes = []
    find_node(node, qtags[0], f_nodes)
    cnodes = []
    for qtag in qtags[1:]:
        cnodes = find_tag(f_nodes, qtag)
        if len(cnodes) == 0: return False
        f_nodes = cnodes
    if len(f_nodes) > 0: return True

def get_sens(filename):
    return lxml.etree.parse(filename).findall('Sentence')

def main(argv):
    if len(argv) != 3:
        print('Usage:\nre.py filename query')
        quit(1)
    sens = get_sens(argv[1])
    query = argv[2]
    count = 0
    for sen in sens:
        if is_sel(sen, query):
            print('Sentence id='+sen.get('id'))
            count = count + 1
    print('Find '+str(count)+' sentences.');

if __name__=='__main__':
    main(sys.argv)
