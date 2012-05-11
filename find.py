#! /usr/bin/env python
import sys
import lxml.etree

# find the bigning of the query, put the list in the sel_nodes
def find_node(node, tag, sel_nodes, path):
    if node == None: return
    if node.tag == tag:
        if path != None:
            path.append(node)
        else:
            path = [node]
        sel_nodes.append(path)
    else:
        for c_node in list(node):
            find_node(c_node, tag, sel_nodes, path)

def find_in_first_child(node, tag, sel_nodes, path):
    while True:
        if node == None: break
        if node.tag == tag: 
            path.append(node)
            sel_nodes.append(path)
            break
        lst = list(node)
        if len(lst)>0: node = lst[0]
        else: break

def find_in_sibs(node, tag, ret_nodes, path):
    if node == None: return
    while True:
        sib = node.getnext()
        if sib == None: break
        find_node(sib, tag, ret_nodes, path)
        node = sib

# Strict mode, the syntax structure must be adjcent
def find_tag_strict(nodes, tag):
    ret_nodes = []
    for node in nodes:
        sib = node[-1].getnext()
        t_node = node[-1]
        while sib==None and t_node.getparent()!=None \
                and t_node.tag!='ROOT':
            t_node = t_node.getparent()
            sib = t_node.getnext()
        if sib==None or t_node.tag=='ROOT': continue
        #find_in_first_child(node, tag, ret_nodes)
        find_in_first_child(sib, tag, ret_nodes, node)
    return ret_nodes

# Not strict mode, needn't be adject
def find_tag_not_strict(nodes, tag):
    ret_nodes = []
    for node in nodes:
        t_node = node[-1]
        find_in_sibs(t_node, tag, ret_nodes, node)
        while t_node!=None and t_node.tag!='ROOT':
            t_node = t_node.getparent()
            find_in_sibs(t_node, tag, ret_nodes) 
    return ret_nodes

def find_tag(nodes, tag, is_strict):
    if is_strict:
        return find_tag_strict(nodes, tag)
    else:
        return find_tag_not_strict(nodes, tag)

def is_sel(node, query, is_strict = True):
    f_nodes = get_last_node(node, query, is_strict)
    return f_nodes!=None and len(f_nodes) > 0

def get_last_node(node, query, is_strict = True):
    query = query.replace(' ', '')
    qtags = query.split('+')
    f_nodes = []
    find_node(node, qtags[0], f_nodes, None)
    cnodes = []
    for qtag in qtags[1:]:
        cnodes = find_tag(f_nodes, qtag, is_strict)
        if len(cnodes) == 0: return []
        f_nodes = cnodes
    if len(f_nodes) > 0: return f_nodes
     

def get_sens(filename):
    return lxml.etree.parse(filename).findall('Sentence')

def get_sen_text(node):
    it = node.itertext()
    ret = ''
    try:
        while True:
            s = next(it).replace('\n', '').replace('$', '').strip()
            if s =='': continue
            ret = ret + s + ' '
    except StopIteration:
        pass
    return ret

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
