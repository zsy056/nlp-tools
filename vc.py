#!/usr/bin/env python

import sys
import lxml.etree
import find

en_v = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
cn_v = ['VA', 'VC', 'VE', 'VV']

cn_vi = {'CNVi1': ['NR+V'],
         'CNVi2': ['NN+V'],
         'CNVi3': ['PN+V'],
         'CNVi4': ['JJ+NR+V'],
         'CNVi5': ['JJ+NN+V'],
         'CNVi6': ['JJ+NN+V', 'JJ+JJ+NN+V'],
         'CNVi7': ['JJ+DEG+NN+V', 'JJ+DEG+JJ+NN+V'],
         'CNVi8': ['NR+NN+V'],
         'CNVi9': ['NR+NN+DEG+NN+VC'],
         'CNVi10': ['CD+NN+V'],
         'CNVi11': ['CD+M+NN+V', 'CD+M+NR+NN+V'],
         'CNVi12': ['DT+NN+V', 'DT+M+NN+V'],
         'CNVi13': ['DT+VV+D+EC+NN+V', 'DT+M+VV+D+EC+NN+V'],
         'CNVi14': ['LC+NN+V', 'LC+DEG+NN+V'],
         'CNVi15': ['NN+DEG+NN+V'],
         'CNVi16': ['PN+NN+V', 'PN+DEG+NN+V'],
         'CNVi17': ['VA+DEG+V'],
         'CDNVi1': ['PN+V', 'NR+V'],
         'CPrepVi1': ['P+PN+V', 'P+NR+V'],
         'CPrepVi2': ['P+DT+NN+V', 'P+DT+CD+NN+V', 'P+DT+CD+M+NN+V',
            'P+DT+CD+M+VA+DEC+NN+V', 'P+DT+M+NN+V',
            'P+DT+M+VA+DEC+NN+V', 'P+DT+VA+DEC+NN+V'],
         'CViPrep1': ['V+P+DT+NN', 'V+P+DT+CD+NN', 'V+P+DT+CD+M+NN',
             'V+P+DT+CD+M+VA+DEC+NN', 'V+P+DT+M+NN',
             'V+P+DT+M+VA+DEC+NN', 'V+P+DT+VA+DEC+NN'],
         'CPrepVi3': ['BA+NN+V+P+NN+NN'],
         'CPrepVi4': ['BA+NN+V+P+NN+VV'],
         'CPrepVi5': ['CD+M+NN', 'CD+M+NR+DEG+NN', 'CD+M+NN+DEG+NN']}

en_vi = {'ENVi1': ['WP+V'],
         'ENVi2': ['DT+NN+V', 'DT+NNS+V', 'DT+JJ+NN+V', 'DT+JJR+NN+V',
             'DT+JJS+NN+V', 'DT+JJ+NNS+V', 'DT+JJR+NNS+V',
             'DT+JJS+NNS+V'],
         'ENVi3': ['DT+JJ+V'],
         'ENVi4': ['DT+NNP+V', 'DT+NNPS+V'],
         'ENVi5': ['DT+NN+IN+PRP$+NN+V', 'DT+NN+IN+PRP$+NNP+V'],
         'ENVi6': ['NR+V'],
         'ENVi7': ['JJ+NNS+V', 'JJR+NNS+V', 'JJS+NNS+V'],
         'ENVi8': ['CD+NNS+V', 'CD+JJ+NNS+V', 'CD+JJR+NNS+V',
             'CD+JJS+NNS+V'],
         'ENVi9': ['PRP+V'],
         'ENVi10': ['PRP$+NN+V', 'PRP$+JJ+NN+V', 'PRP$+JJR+NN+V',
             'PRP$+JJS+NN+V'],
         'ENVi11': ['NNP+V+JJ', 'PRP+V+JJ'],
         'ENVi12': ['PDT+DT+NNS+PRP+V', 'PDT+DT+NNS+PRP+MD+V'],
         'EViPrep1': ['V+TO+NNP+NN', 'V+TO+DT+NN', 'V+TO+NNP+NNS',
             'V+TO+DT+NNS', 'V+TO+NNP+JJ+NN', 'V+TO+NNP+JJ+NNS',
             'V+TO+DT+JJ+NN', 'V+TO+DT+JJ+NNS', 'V+TO+NNP+JJR+NN',
             'V+TO+NNP+JJR+NNS', 'V+TO+DT+JJR+NN', 'V+TO+DT+JJR+NNS',
             'V+TO+NNP+JJS+NN', 'V+TO+NNP+JJS+NNS', 'V+TO+DT+JJS+NN',
             'V+TO+DT+JJS+NNS'],
         'EViPrep2': ['V+IN+DT+NN'],
         'EViPrep3': ['V+TO+DT+NN+NN']}

cn_vt = {'CVtN1': ['V+NN'],
         'CVtN2': ['VA+V+NN'],
         'CVtN3': ['VV+NN+VV+V+NN', 'VV+NN+VC+V+NN', 'VV+NN+VE+V+NN'],
         'CVtDN1': ['PN+DEG+VV+V+NN', 'PN+DEG+VV+V+NN+NN',
             'NR+DEG+VV+V+NN', 'NR+DEG+VV+V+NN+NN', 'NN+DEG+VV+V+NN',
             'NN+DEG+VV+V+NN+NN'],
         'CVtDN2': ['V+NN+NN'],
         'CVtQ1': ['V+CD+M', 'V+DT+M', 'V+CD+M+NR', 'V+DT+M+NR',
             'V+CD+M+NN', 'V+DT+M+NN', 'V+CD+M+NR+NN', 'V+DT+M+NR+NN'],
         'CVtQ2': ['V+CD+AD+M'],
         'CVtDe1': ['V+LC+DEG+NN'],
         'CVtDe2': ['V+PN+M+MSP+VV+DEC', 'V+PN+M+NR+MSP+VV+DEC',
             'V+PN+NR+NN+MSP+VV+DEC', 'V+PN+NR+NN+MSP+VV+DEC+NN',
             'V+NR+M+MSP+VV+DEC', 'V+NR+M+NR+MSP+VV+DEC',
             'V+NR+M+NR+NN+MSP+VV+DEC', 'V+NR+M+NR+NN+MSP+VV+DEC+NN',
             'V+CD+M+MSP+VV+DEC', 'V+CD+M+NR+MSP+VV+DEC',
             'V+CD+NR+NN+MSP+VV+DEC', 'V+CD+NR+NN+MSP+VV+DEC+NN',
             'V+DT+M+MSP+VV+DEC', 'V+DT+M+NR+MSP+VV+DEC',
             'V+DT+NR+NN+MSP+VV+DEC', 'V+DT+NR+NN+MSP+VV+DEC+NN'],
         'CVtDe3': ['V+NN+VV+CD+DEC', 'V+NN+VV+CD+DEC+NN'],
         'CVtP1': ['V+PN'],
         'CVtP2': ['V+PN+PN'],
         'CVtV1': ['V+VV'],
         'CVtVP1': ['V+VV+NN'],
         'CVtVP2': ['V+VV+NN+VV'],
         'CVtVP3': ['V+VV+PN+DEG+NN'],
         'CVtVP4': ['V+NN+V+VV+NN', 'V+NN+V+VC+NN', 'V+NN+V+VE+NN'],
         'CVtAdj1': ['V+JJ+NN'],
         'CVtAdj2': ['V+VA'],
         'CVtPA1': ['M+NN+LB+NN+V', 'DT+M+NN+LB+NN+V',
            'DT+CD+M+NN+LB+NN+V', 'CD+M+NN+LB+NN+V'],
         'CVtPrep1': ['V+P+NN+DEG+NN+NN'],
         'CVtPrep2': ['P+NN+LC+V+NN', 'P+NN+NN+LC+V+NN'],
         'CVtC1': []}

en_vt = {'EVtP1': ['V+DT'],
         'EVtP2': ['V+PRP'],
         'EVtP3': ['V+PRP+JJ'],
         'EVtN1': ['V+PRP$+NN'],
         'EVtN2': ['V+PRP$+NN+NN'],
         'EVtN3': ['V+PRP$+JJ+NN'],
         'EVtN4': ['V+PRP+CC+PRP$+NN'],
         'EVtN5': ['V+JJ+IN+NNS', 'V+JJ+IN+PRP$+NNS'],
         'EVtN6': ['V+NNP'],
         'EVtN7': ['V+NNP+NNP'],
         'EVtN9': ['V+NN+JJ+CC+JJ'],
         'EVtN10': ['V+CD+NN', 'V+DT+NN', 'V+DT+JJ+NN', 'V+CD+JJ+NN',
             'V+DT+JJR+NN', 'V+CD+JJR+NN', 'V+DT+JJS+NN', 'V+CD+JJS+NN',
             'V+DT+NN+IN+PRP$', 'V+CD+NN+IN+PRP$', 'V+DT+NN+IN+NN',
             'V+CD+NN+IN+NN', 'V+DT+NN+IN+NNS', 'V+CD+NN+IN+NNS',
             'V+DT+JJ+NN+IN+PRP$', 'V+CD+JJ+NN+IN+PRP$',
             'V+DT+JJ+NN+IN+NN', 'V+CD+JJ+NN+IN+NN',
             'V+DT+JJ+NN+IN+NNS', 'V+CD+JJ+NN+IN+NNS',
             'V+DT+JJR+NN+IN+PRP$', 'V+CD+JJR+NN+IN+PRP$',
             'V+DT+JJR+NN+IN+NN', 'V+CD+JJR+NN+IN+NN',
             'V+DT+JJR+NN+IN+NNS', 'V+CD+JJR+NN+IN+NNS',
             'V+DT+JJS+NN+IN+PRP$', 'V+CD+JJS+NN+IN+PRP$',
             'V+DT+JJS+NN+IN+NN', 'V+CD+JJS+NN+IN+NN',
             'V+DT+JJS+NN+IN+NNS', 'V+CD+JJS+NN+IN+NNS'],
         'EVtN11': ['V+PRP$+JJ+NN+RB+RBR+JJ'],
         'EVtN12': ['V+JJ+JJ+NN', 'V+JJ+JJ+NNS', 'V+DT+JJ+JJ+NN',
             'V+DT+JJ+JJ+NNS'],
         'EVtN13': ['V+DT+NN+IN+NN'],
         'EVtN14': ['V+NNS', 'V+CD+NNS', 'V+CD+'],
         'EVtN15': ['V+PRP$+NNS'],
         'EVtN16': ['V+PRP$+NN+CC+NN'],
         'EVtN17': ['V+DT+NN+JJ', 'V+DT+NNS+JJ',
             'V+DT+JJ+NN+JJ', 'V+DT+JJ+NNS+JJ',
             'V+DT+JJ+NN+JJR', 'V+DT+JJ+NNS+JJR',
             'V+DT+JJ+NN+JJS', 'V+DT+JJ+NNS+JJS'],
         'EVtN18': ['V+DT+NN+CC+DT+NN', 'V+DT+NN+CC+DT+NNS',
             'V+DT+JJ+NN+CC+DT+NN', 'V+DT+JJ+NN+CC+DT+NNS',
             'V+DT+JJ+NN+CC+DT+JJ+NN', 'V+DT+JJ+NN+CC+DT+JJ+NNS',
             'V+DT+NN+CC+DT+JJ+NN', 'V+DT+NN+CC+DT+JJ+NNS'],
         'EVtN19': ['V+CD+NN+IN+NN', 'V+CD+NN+IN+NNS',
             'V+CD+NN+IN+DT+NN', 'V+CD+NN+IN+DT+NNS',
             'V+CD+NN+IN+CD+NN', 'V+CD+NN+IN+CD+NNS',
             'V+CD+NN+IN+DT+JJ+NN', 'V+CD+NN+IN+DT+JJ+NNS',
             'V+CD+NN+IN+CD+JJ+NN', 'V+CD+NN+IN+CD+JJ+NNS',
             'V+CD+NN+IN+DT+JJR+NN', 'V+CD+NN+IN+DT+JJR+NNS',
             'V+CD+NN+IN+CD+JJR+NN', 'V+CD+NN+IN+CD+JJR+NNS',
             'V+CD+NN+IN+DT+JJS+NN', 'V+CD+NN+IN+DT+JJS+NNS',
             'V+CD+NN+IN+CD+JJS+NN', 'V+CD+NN+IN+CD+JJS+NNS'],
         'EVtN20': ['V+CD+NN+IN+DT+JJ+NN'],
         'EVtN21': ['V+NN+NN+NN', 'V+NN+NN+NNS',
             'V+DT+NN+NN+NN', 'V+DT+NN+NN+NNS'],
         'EVtN22': ['V+DT+NN+IN+WP+TO+VB'],
         'EVtP1': ['V+N+VBG'],
         'EVtP2': ['V+VBG', 'V+NN+VBG', 'V+NP+VBG'],
         'EVtP3': ['V+VBG+DT+NNS'],
         'EVtP4': ['V+VBN+NNS+VBP+JJ', 'V+VBN+NN+VBP+JJ'],
         'EVtTO1': ['V+TO+VB'],
         'EVtTO2': ['V+TO+VB+DT', 'V+TO+VB+PRP$'],
         'EVtTO3': ['V+TO+VB+DT+NN'],
         'EVtTO4': ['V+TO+VB+NNP'],
         'EVtTO5': ['V+TO+VB+NNS+IN+NN', 'V+TO+VB+NNS+IN+JJ+NN'
                 'V+TO+VB+NNS+IN+NNS', 'V+TO+VB+NNS+IN+JJ+NNS'],
         'EVtTO6': ['V+TO+VB+PRP$',
                 'V+TO+VB+PRP$+NN', 'V+TO+VB+PRP$+NNS'],
         'EVtTO7': ['V+TO+VB+PRP$+NNS'],
         'EVtTO8': ['V+TO+VB+VBN'],
         'EVtTO9': ['V+TO+VB+VBN+IN'],
         'EVtTO10': ['V+PRP+TO+VB+PRP$+NN', 'V+PRP+TO+VB+PRP$+NNS'],
         'EVtPA1': ['DT+NN+VBD+VBN+IN+PRP$+NN',
                 'CD+NN+VBD+VBN+IN+PRP$+NN', 'DT+NN+VB+VBN+IN+PRP$+NN',
                 'CD+NN+VB+VBN+IN+PRP$+NN', 'DT+NN+VBD+VBN+IN+PRP$+NNS',
                 'CD+NN+VBD+VBN+IN+PRP$+NNS',
                 'DT+NN+VB+VBN+IN+PRP$+NNS', 
                 'CD+NN+VB+VBN+IN+PRP$+NNS'],
         'EVtPA2': ['PRP+VBD+VBN+TO+VB'],
         'EVtPrep1': ['PRP+V+NN+TO+VB'],
         'EVtPrep2': [''],
         'EVtPrep3': ['V+PRP+IN+VBG+NN'],
         'EVtPrep4': ['V+PRP+IN+PRP$+JJ+NN', 'V+PRP+IN+PRP$+JJ+NNS'],
         'EVtPrep5': ['V+DT+IN+DT'],
         'EVtPrep6': ['V+DT+NN+IN+NNP'],
         'EVtC1': ['V+N+WP'],
         'EVtC2': ['V+WRB'],
         'EVtC3': ['V+IN+WRB']}
        
cn_dvt = {'CDVtN1': ['V+PN+NN', 'V+NR+NN', 'V+PN+NN', 'V+DT+NN', 'V+CD+NN',
            'V+PN+M+NN', 'V+NR+M+NN', 'V+PN+M+NN',
            'V+DT+M+NN', 'V+CD+M+NN'],
          'CDVtN2': ['V+PN+NN+JJ+NN', 'V+NR+NN+JJ+NN', 'V+PN+NN+JJ+NN',
              'V+DT+NN+JJ+NN', 'V+CD+NN+JJ+NN', 'V+PN+M+NN+JJ+NN',
              'V+NR+M+NN+JJ+NN', 'V+PN+M+NN+JJ+NN',
              'V+DT+M+NN+JJ+NN', 'V+CD+M+NN+JJ+NN'],
          'CDVtN3': ['VV+NN+V+PN+NN+NN', 'VV+NN+V+NR+NN+NN',
              'VV+NN+V+PN+NN+NN', 'VV+NN+V+DT+NN+NN', 'VV+NN+V+CD+NN+NN',
              'VV+NN+V+PN+M+NN+NN', 'VV+NN+V+NR+M+NN+NN',
              'VV+NN+V+PN+M+NN+NN', 'VV+NN+V+DT+M+NN+NN',
              'VV+NN+V+CD+M+NN+NN'],
          'CDVtN4': ['V+PN+CD+M', 'V+PN+DT+M', 'V+NR+CD+M', 'V+NR+DT+M',
              'V+PN+CD+M+NR', 'V+PN+DT+M+NR', 'V+NR+CD+M+NR',
              'V+NR+DT+M+NR',
              'V+PN+CD+M+NN', 'V+PN+DT+M+NN', 'V+NR+CD+M+NN',
              'V+NR+DT+M+NN',
              'V+PN+CD+M+NR+NN', 'V+PN+DT+M+NR+NN', 'V+NR+CD+M+NR+NN',
              'V+NR+DT+M+NR+NN'],
          'CDVtN5': ['V+PN+NN+PN', 'V+NR+NN+PN', 'V+PN+NN+PN', 'V+DT+NN+PN',
              'V+CD+NN+PN', 'V+PN+M+NN+PN', 'V+NR+M+NN+PN', 'V+PN+M+NN+PN',
              'V+DT+M+NN+PN', 'V+CD+M+NN+PN'],
          'CDVtN6': ['VV+NN+LC+CD+NN', 'VV+NN+LC+CD+M+NN'],
          'CDVtN7': ['V+PN+NN+VV+NN', 'V+NR+NN+VV+NN', 'V+PN+NN+VV+NN',
              'V+DT+NN+VV+NN', 'V+CD+NN+VV+NN',
              'V+PN+M+NN+VV+NN', 'V+NR+M+NN+VV+NN', 'V+PN+M+NN+VV+NN',
              'V+DT+M+NN+VV+NN', 'V+CD+M+NN+VV+NN'],
          'CDVtN8': ['V+PN+NN+VV', 'V+NR+NN+VV', 'V+PN+NN+VV', 'V+DT+NN+VV',
              'V+CD+NN+VV', 'V+PN+M+NN+VV', 'V+NR+M+NN+VV', 'V+PN+M+NN+VV',
              'V+DT+M+NN+VV', 'V+CD+M+NN+VV'],
          'CDVtN10': ['V+NN+VV+PN+NN+NN', 'V+NN+VV+NR+NN+NN',
              'V+NN+VV+DT+NN+NN', 'V+NN+VV+CD+NN+NN',
              'V+NN+VV+PN+M+NN+NN', 'V+NN+VV+NR+M+NN+NN',
              'V+NN+VV+DT+M+NN+NN', 'V+NN+VV+CD+M+NN+NN'],
          'CDVtPrep1': ['V+PN+NN+P+VV+NN', 'V+NR+NN+P+VV+NN',
              'V+DT+NN+P+VV+NN', 'V+CD+NN+P+VV+NN',
              'V+PN+M+NN+P+VV+NN', 'V+NR+M+NN+P+VV+NN',
              'V+DT+M+NN+P+VV+NN', 'V+CD+M+NN+P+VV+NN'
    }

def conv(sens, v_list, rule_dict):
    for sen in sens:
        for key in rule_dict:
            rules = rule_dict[key]
            for rule in rules:
                for tag in v_list:
                    idx = rule.split('+').index('V')
                    query = rule.replace('+V+', '+'+tag+'+')
                    paths = find.get_last_node(sen, query)
                    if paths == None: continue
                    for path in paths:
                        if path[idx].tag == tag:
                            path[idx].tag = key
                            print('change')

if __name__=='__main__':
    cn_xml = lxml.etree.parse('Result-c.xml')
    cn_sens = cn_xml.findall('Sentence')
    conv(cn_sens, cn_v, cn_vt)
    conv(cn_sens, cn_v, cn_vi)
    conv(cn_sens, cn_v, cn_dvt)
    cn_xml.write('New-c.xml', encoding='utf8')
    
    en_xml = lxml.etree.parse('Result-e.xml')
    en_sens = en_xml.findall('Sentence')
    conv(en_sens, en_v, en_vt)
    conv(en_sens, en_v, en_vi)
    conv(en_sens, en_v, en_dvt)
    en_xml.write('New-e.xml', encoding='utf8')


