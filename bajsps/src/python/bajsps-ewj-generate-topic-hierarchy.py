#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: look into nltk.text and its methods to explore

from __future__ import print_function
import sys
import string
import re
import types
import os, os.path
from pprint import pprint
import itertools
# import etree
import xml.etree.ElementTree as ET
# import cPickle
from operator import itemgetter, attrgetter
from optparse import OptionParser
print("NLTK import start")
# import nltk
from nltk.corpus import stopwords
from nltk.corpus import words
from nltk.corpus import wordnet
import nltk.util
print("NLTK import end")
import logging

stopwords = nltk.corpus.stopwords.words('english')

topichierdic = {}

def makeOutDir(basedir, subdir):
    leafdir = os.path.join(basedir, subdir)
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    if not os.path.exists(leafdir):
        os.mkdir(leafdir)
    return leafdir

def getArtidList(indir):
    print("Read frequency lists.")
    infile = "artids.txt"
    infilepath = os.path.join(indir, infile)
    fobj = file(infilepath, "r")
    artidlist = fobj.readlines()
    artidlist = [artid.strip() for artid in artidlist]
    fobj.close()
    return artidlist

def getArtidListFromFileList(indir):
    filelist = os.listdir(indir)
    aidlist = [ f[:-4] for f in filelist if f.endswith(".txt")]
    return aidlist

def getTopicTermDics(indir, aidlist, ntt):
    topictermlistdic = {}
    topictfidflistdic = {}
    alltopicslist = []
    for artid in aidlist:
        nttuse = ntt
        infile = "%s.txt" % (artid, )
        infilepath = os.path.join(indir, infile)
        fobj = file(infilepath, "r")
        artlist = fobj.readlines()
        ttlistlen = len(artlist)
        if ttlistlen < ntt:
            nttuse = ttlistlen
        else:
            nttuse = ntt
        # freqdic["all"] = [e.strip().split("\t") for e in alllist]
        topictermlistdic[artid] = [e.strip().split("\t")[0] for e in artlist[:nttuse]]
        topictfidflistdic[artid] = [e.strip().split("\t")[1] for e in artlist[:nttuse]]
        for l in topictermlistdic[artid]:
            alltopicslist.append(l)
        fobj.close()
    alltopicsset = set(alltopicslist)
    alltopicslist = list(alltopicsset)
    return topictermlistdic, topictfidflistdic, alltopicslist

def generateHolonyms(atlist):
    # explore holonyms
    # not very helpful
    holonymsmemberdic = {}
    holonymspartdic = {}
    holonymssubstancedic = {}
    for topicleaf in atlist:
        # topicsynsets = wordnet.synsets(topicleaf)
        # only choose nouns instead
        topicsynsetslist = wordnet.synsets(topicleaf, pos=wordnet.NOUN)
        if len(topicsynsetslist) > 0:
            topicsynset = topicsynsetslist[0]
            holonymsmemberdic[topicleaf] = topicsynset.member_holonyms()
            holonymspartdic[topicleaf] = topicsynset.part_holonyms()
            holonymssubstancedic[topicleaf] = topicsynset.substance_holonyms()
        else:
            print(topicleaf)
    print("Holonyms member")
    for h in holonymsmemberdic.keys():
        if len(holonymsmemberdic[h]) > 0:
            print(h, holonymsmemberdic[h])
    print("Holonyms part")
    for h in holonymspartdic.keys():
        if len(holonymspartdic[h]) > 0:
            print(h, holonymspartdic[h])
    print("Holonyms substance")
    for h in holonymssubstancedic.keys():
        if len(holonymssubstancedic[h]) > 0:
            print(h, holonymssubstancedic[h])
    return holonymsmemberdic, holonymspartdic, holonymssubstancedic

def generateTopicHierarchies(atlist):
    # see: api/nltk.corpus.reader.wordnet.Synset-class.html
    # see: api/nltk.corpus.reader.wordnet._WordNetObject-class.html
    hypernympathsdic = {}
    # print(len(atlist))
    testset = set()
    # ---------------------------------------------
    for topicleaf in atlist:
    # for topicleaf in atlist[:50]:#<<<<------------------------------------------ CHANGE!!!
    # ---------------------------------------------
        # topicsynsets = wordnet.synsets(topicleaf)
        # only choose nouns instead
        topicsynsetslist = wordnet.synsets(topicleaf, pos=wordnet.NOUN)
        topicsynsetslistlen = len(topicsynsetslist)
        if topicsynsetslistlen > 0:
            # use first synset that has a hypernympath longer than 1, otherwise
            #     don't use this synset at all 
            # explore if later we could use all synsets
            for topicsynset in topicsynsetslist:
                hyppaths = getHypernymPaths(topicsynset)
                hyppathslen = len(hyppaths)
                if hyppathslen > 1:
                    hypernympathsdic[topicleaf] = hyppaths
                    break
    return hypernympathsdic

def getHypernymTree(tsynset):
    hyp = lambda s:s.hypernyms()
    treelist = tsynset.tree(hyp)
    pprint(treelist)
    return treelist

def getHypernymPaths(tsynset):
    pathlist = tsynset.hypernym_paths()[0]
    # pprint(pathlist)
    return pathlist

def putCommonHypernymsInOrder(s, h):
    # as common_hypernyms are unsorted (result of set operations)
    # we order them in the same order as the hypernyms
    # slist = [e for e in s]
    hordered = [e for e in s if e in h]
    return hordered

def testPermuteOld(hypnympathsdic):
    # can be rewritten more elegantly using itertools.permutations
    # see below
    # 
    # for tl in hypnympathsdic:
    #     # print(tl, len(hypnympathsdic[tl][0]), hypnympathsdic[tl][0])
    #     print(tl, len(hypnympathsdic[tl]), hypnympathsdic[tl])
    hnpl = hypnympathsdic.keys()
    # print("-" * 30)
    # print(len((hnpl)))
    # for n, h in enumerate(hnpl):
    #     print(hnpl[n], hnpl[n+1]) 
    #     print(hypnympathsdic[hnpl[n]][0][-1:], hypnympathsdic[hnpl[n+1]][0][-1:])
    #     # how does one call _lcs_by_depth ???
    #     print(wordnet._lcs_by_depth(hypnympathsdic[hnpl[n]][0][-1:][0], hypnympathsdic[hnpl[n+1]][0][-1:][0]))

    combicount = 0         
    for t1 in hypnympathsdic:
        # hypernym path
        # h1 = hypnympathsdic[t1][0]
        h1 = hypnympathsdic[t1]
        # last in list is synset for t1
        s1 = h1[-1]
        for t2 in hypnympathsdic:
            # hypernym path
            # h2 = hypnympathsdic[t2][0]
            h2 = hypnympathsdic[t2]
            # last in list is synset for t2
            s2 = h2[-1]
            if s1 != s2:
                combicount += 1
                ch = s1.common_hypernyms(s2)
                # reverse common hypernyms list to start with root
                chordered = putCommonHypernymsInOrder(h1, ch)
                lh = s1.lowest_common_hypernyms(s2)
                sp = s1.shortest_path_distance(s2)
                # only print cases where more than 3 common hypernyms
                if len(ch) > 0:
                    print("-" * 30)
                    print("%s <--> %s" % (s1.name[:s1.name.index(".")], s2.name[:s2.name.index(".")]))
                    print("H1: " + " --> ".join([s.name[:s.name.index(".")] for s in h1]))
                    print("H2: " + " --> ".join([s.name[:s.name.index(".")] for s in h2]))
                    # print("CH: " + " --> ".join([s.name[:s.name.index(".")] for s in ch]))
                    print("CH: " + " --> ".join([s.name[:s.name.index(".")] for s in chordered]))
                    print("LH: " + " -- ".join([s.name[:s.name.index(".")] for s in lh]))
                    print("SP:", sp)
    print("COMBICOUNT:", combicount)

def testCombine(hypnympathsdic):
    # number of combinations: (topics * (topics - 1))/2
    # 4,759 topics --> 11,321,661 combinations
    hnpl = hypnympathsdic.keys()
    nooftopics = len(hnpl)
    print("NO OF TOPICS:    ", nooftopics)
    combicount = 0         
    actualcombicount = 0         
    for (t1, t2) in itertools.combinations(hnpl, 2):
        h1 = hypnympathsdic[t1]
        s1 = h1[-1]
        h2 = hypnympathsdic[t2]
        s2 = h2[-1]
        combicount += 1
        ch = s1.common_hypernyms(s2)
        # reverse common hypernyms list to start with root
        chordered = putCommonHypernymsInOrder(h1, ch)
        lh = s1.lowest_common_hypernyms(s2)
        sp = s1.shortest_path_distance(s2)
        # only print cases where more than 3 common hypernyms
        if len(ch) > 0:
            actualcombicount += 1
            print("-" * 30)
            print("%s <--> %s" % (s1.name[:s1.name.index(".")], s2.name[:s2.name.index(".")]))
            print("H1: " + " --> ".join([s.name[:s.name.index(".")] for s in h1]))
            print("H2: " + " --> ".join([s.name[:s.name.index(".")] for s in h2]))
            # print("CH: " + " --> ".join([s.name[:s.name.index(".")] for s in ch]))
            print("CH: " + " --> ".join([s.name[:s.name.index(".")] for s in chordered]))
            print("LH: " + " -- ".join([s.name[:s.name.index(".")] for s in lh]))
            print("SP:", sp)
        else:
            print("NOCOMMONHYPERNYMS:", t1, t2)
    print("COMBICOUNT:      ", combicount)
    print("ACTUALCOMBICOUNT:", actualcombicount)
    print("NO OF TOPICS:    ", nooftopics)

def testPermute(hypnympathsdic):
    hnpl = hypnympathsdic.keys()
    combicount = 0         
    actualcombicount = 0         
    for (t1, t2) in itertools.permutations(hnpl, 2):
        h1 = hypnympathsdic[t1]
        s1 = h1[-1]
        h2 = hypnympathsdic[t2]
        s2 = h2[-1]
        combicount += 1
        ch = s1.common_hypernyms(s2)
        # reverse common hypernyms list to start with root
        chordered = putCommonHypernymsInOrder(h1, ch)
        lh = s1.lowest_common_hypernyms(s2)
        sp = s1.shortest_path_distance(s2)
        # only print cases where more than 3 common hypernyms
        if len(ch) > 3:
            actualcombicount += 1
            print("-" * 30)
            print("%s <--> %s" % (s1.name[:s1.name.index(".")], s2.name[:s2.name.index(".")]))
            print("H1: " + " --> ".join([s.name[:s.name.index(".")] for s in h1]))
            print("H2: " + " --> ".join([s.name[:s.name.index(".")] for s in h2]))
            # print("CH: " + " --> ".join([s.name[:s.name.index(".")] for s in ch]))
            print("CH: " + " --> ".join([s.name[:s.name.index(".")] for s in chordered]))
            print("LH: " + " -- ".join([s.name[:s.name.index(".")] for s in lh]))
            print("SP:", sp)
    print("COMBICOUNT:      ", combicount)
    print("ACTUALCOMBICOUNT:", actualcombicount)

def generateXmlSynsetTree(hypnympathsdic):
    # model the hierarchical hypernympaths, which is a subset of the whole
    #    Wordnet topic tree in XML
    # write the resulting XML tree into a file for checking
    # 
    # test run on complete EWJ - first 10 TF-IDF topics for each article:
    #   generates 8868 topics (if synset list longer than 1) 
    #   3 topics do not start with "entity" - disregarded (e. g. channel_island --> guernsey) 
    root = ET.Element("entity")
    hnpl = hypnympathsdic.keys()
    nooftopics = len(hnpl)
    print("NO OF TOPICS:    ", nooftopics)
    for topic in hnpl:
        # print(topic)
        currelement = root
        topicsynsetlist = hypnympathsdic[topic]
        topicnameslist = [s.name[:s.name.index(".")] for s in topicsynsetlist]
        if topicnameslist[0] != 'entity':
            print("--- hypernympathlist does not start with 'entity'")
            print(" --> ".join(topicnameslist))
        else:
            for htopic in topicnameslist[1:]:
                htopic = htopic.replace("'", ".")
                childelement = currelement.find(htopic) 
                if childelement == None:
                    currelement = ET.SubElement(currelement, htopic)
                else:
                    currelement = childelement
    outobj = file("topics.xml", 'w')
    ET.ElementTree(root).write(outobj)
    outobj.close()
    return root
    

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-b", "--basedir", dest="basedir", default="/data/docs/textmining/ncse",
                      help="Output/input base directory for data - default: %s", metavar="DIRECTORY")
    parser.add_option("-t", "--listtype", dest="listtype",
                      type="choice", choices=["low", "stw", "wlo", "wst"], default="wst",
                      help="What kind of list type to run: low = all tokens lower case, stw = tokens no stop words - default: %default", metavar="PROCESS")
    parser.add_option("-m", "--method", dest="targtermmethod",
                      type="choice", choices=["castanet1", "castanet2", "tfidf"], default="tfidf",
                      help="What kind of method to use to extract target terms: castanet1 (Stoica/Hearst), castanet2 (Hearst), TF/IDF - default: %default", metavar="METHOD")
    parser.add_option("-n", "--nooftargetterms", type="int", dest="nooftargetterms", default=10,
                      help="Number of target terms to consider - default: %s", metavar="NUMBER")

    (options, args) = parser.parse_args()

    basedir = options.basedir
    targtermmethod = options.targtermmethod
    listtype = options.listtype
    nooftargetterms = options.nooftargetterms
    
    srcsubdir = "topics"
    indir = os.path.join(basedir, srcsubdir,  targtermmethod, listtype)

    print("Read article ids - artidlist")
    artidlist = getArtidListFromFileList(indir)
    
    print("Read topics per article.")
    topictermdic, topictfidfdic, alltopicslist = getTopicTermDics(indir, artidlist, nooftargetterms)
        
    if targtermmethod == "castanet1":
        hypernympathsdic = generateTopicHierarchies(alltopicslist)
    elif targtermmethod == "castanet2":
        hypernympathsdic = generateTopicHierarchies(alltopicslist)
    elif targtermmethod == "tfidf":
        hypernympathsdic = generateTopicHierarchies(alltopicslist)
        
    # testPermute(hypernympathsdic)
    # testCombine(hypernympathsdic)
    xmltree = generateXmlSynsetTree(hypernympathsdic)
    

    print("--== FINISHED ==--")

