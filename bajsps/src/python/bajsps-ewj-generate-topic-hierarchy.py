#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: look into nltk.text and its methods to explore

from __future__ import print_function
import sys
import string
import re
import types
import os, os.path
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
    # ---------------------------------------------
    # for topicleaf in atlist:
    for topicleaf in atlist[:30]:#<<<<-------------- CHANGE!!!
    # ---------------------------------------------
        # topicsynsets = wordnet.synsets(topicleaf)
        # only choose nouns instead
        topicsynsetslist = wordnet.synsets(topicleaf, pos=wordnet.NOUN)
        if len(topicsynsetslist) > 0:
            topicsynset = topicsynsetslist[0]
            print("-" * 30)
            print(topicsynset)
            # print(topicsynset.hypernym_distances())
            # print(topicleaf, topicsynset.hypernyms())
            # print(topicleaf, topicsynset.root_hypernyms())
            print(topicleaf, topicsynset.hypernym_paths())
            hypernympathsdic[topicleaf] = topicsynset.hypernym_paths()
        # else:
            # print(topicleaf)
    # print(len(hypernympathsdic.keys()))
    return hypernympathsdic

def testPermute(hypnympathsdic):
    pass

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
    

    print("--== FINISHED ==--")

