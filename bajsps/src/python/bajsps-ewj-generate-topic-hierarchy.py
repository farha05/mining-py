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

freqdic = {}
freqtoklistdic = {}
freqfrqlistdic = {}
unsorttoklistdic = {}
unsorttokperpublist = []

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

def getTopicTermDics(indir, aidlist):
    topictermlistdic = {}
    topictfidflistdic = {}
    for artid in aidlist:
        infile = "%s.txt" % (artid, )
        infilepath = os.path.join(indir, infile)
        fobj = file(infilepath, "r")
        artlist = fobj.readlines()
        # freqdic["all"] = [e.strip().split("\t") for e in alllist]
        topictermlistdic[artid] = [e.strip().split("\t")[0] for e in artlist]
        topictfidflistdic[artid] = [e.strip().split("\t")[1] for e in artlist]
        fobj.close()
    return topictermlistdic, topictfidflistdic

def generateTopicHierarchies(ttedic, ttfdic):
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
    
    # print("Read topics per article.")
    topictermdic, topictfidfdic = getTopicTermDics(indir, artidlist)
        
    if targtermmethod == "castanet1":
        generateTopicHierarchies(topictermdic, topictfidfdic)
    elif targtermmethod == "castanet2":
        generateTopicHierarchies(topictermdic, topictfidfdic)
    elif targtermmethod == "tfidf":
        generateTopicHierarchies(topictermdic, topictfidfdic)
    

    print("--== FINISHED ==--")

