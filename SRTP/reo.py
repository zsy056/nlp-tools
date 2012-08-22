#! /usr/bin/env python
import sys
import xml.dom.minidom

def find_node(node, tag, sel_nodes):
    if node.localName == tag:
        sel_nodes.append(node)
    else:
        for c_node in node.childNodes: 
            if c_node.nodeType!=xml.dom.Node.TEXT_NODE:
                find_node(c_node, tag, sel_nodes)

def get_node_sibling(node):
    while True:
        if node == None: return None
        sib = node.nextSibling
        if sib!=None and sib.nodeType!=xml.dom.Node.TEXT_NODE:
            return sib
        node = sib


def find_tag(nodes, tag):
    ret_nodes = []
    for node in nodes:
        sib = get_node_sibling(node)
        while sib==None and node.parentNode!=None and \
                node.tagName!='ROOT':
            sib = get_node_sibling(node.parentNode)
            node = node.parentNode
        #if sib == None: continue
        if sib==None and node.tagName=='ROOT': continue
        find_node(sib, tag, ret_nodes)
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
    if len(cnodes) > 0: return True
    #for f_node in f_nodes:
    #    sib = get_node_sibling(f_node)
    #    if sib == None: continue
    #    s_nodes = []
    #    find_node(sib, qtags[1], s_nodes)
    #    if len(s_nodes) != 0:
    #        return True
    #return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:\nre.py filename query')
        quit(1)
    doc = xml.dom.minidom.parse(sys.argv[1])
    query = sys.argv[2]
    count = 0
    for node in doc.getElementsByTagName('Sentence'):
        if is_sel(node, query):
            print('Sentence id='+node.attributes.item(0).value)
            count = count + 1
    print('Find '+str(count)+' sentences.');
