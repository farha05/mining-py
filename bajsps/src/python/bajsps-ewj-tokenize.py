#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: look into nltk.text and its methods to explore

# output folders:
#                 low = lowercase tokens
#                 stw = lowercase tokens without stop words

from __future__ import print_function
import sys
import string
import re
import types
import os, os.path
import cPickle
import sqlite3
from optparse import OptionParser
print("NLTK import start")
# import nltk
# from nltk.collocations import BigramCollocationFinder
# from nltk.collocations import TrigramCollocationFinder
# from nltk.metrics import BigramAssocMeasures
# from nltk.metrics import TrigramAssocMeasures
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import nltk.util
print("NLTK import end")

# load training data for sentence detection
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

english_stops = set(stopwords.words('english'))

wn_all_lemma_list = [k for k in wordnet.all_lemma_names()]
wn_all_lemma_set = set(wn_all_lemma_list)

ipunct = string.punctuation
letset = set(string.letters + string.digits)


def getInfileList(epath):
    ilist = []
    print("Get source files.")
    for walkroot, walkdirs, walkfiles in os.walk(epath):
        if (walkdirs == []) and (walkfiles != []):
            # print(walkroot, walkdirs, walkfiles)
            walkfilepaths = [os.path.join(walkroot, wf) for wf in walkfiles]
            ilist += walkfilepaths
    ilist = sorted(ilist)
    return ilist

def processTexts(ilist):
    print("Process texts.")
    artidlist = []
    tokendic = {
                "low" : { },
                "stw" : { },
                "wlo" : { },
                "wst" : { }
                }
    tokendic["low"]["all"] = []
    tokendic["stw"]["all"] = []
    tokendic["wlo"]["all"] = []
    tokendic["wst"]["all"] = []
    for ipath in ilist:
        pa, fi = os.path.split(ipath)
        artid, ext = os.path.splitext(fi)
        artidlist.append(artid)
        fobj = file(ipath, "r")
        intext = fobj.read()
        intext = intext.replace(" \n", "\n")
        intext = intext.replace("-\n", "")
        fobj.close()
        # print(artid, len(intext))
        # print(intext)
        # tokenlist = tokenizePunktTokenize(intext, artid)
        # print(len(tokenlist), tokenlist)
        tokenrawlist = tokenizeWordPunctTokenize(intext, artid)
        # print(len(tokenrawlist), tokenrawlist)
        # tokenlist = tokenizePunctWordTokenize(intext, artid)
        # print(tokenlist)
        # tokenlist = tokenizeWordTokenize(intext, artid)
        # print(len(tokenlist), tokenlist)
        # tokenlist = tokenizeRegexpTokenize(intext, artid)
        # print(len(tokenlist), tokenlist)
        tokenlist, tokenstwlist = postProcessTokens(tokenrawlist)
        # tokennopunctlist = [t for t in tokenrawlist if t not in ipunct]
        # print(len(tokennopunctlist), tokennopunctlist)
        # tokenlowerlist = [t.lower() for t in tokennopunctlist]
        # print(len(tokenlowerlist), tokenlowerlist)
        tokengoodocrlist = filterBadOcrUsingWordnetLemmata(tokenlist)
        tokengoodocrstwlist = filterBadOcrUsingWordnetLemmata(tokenstwlist)
        tokendic["low"][artid] = tokenlist
        tokendic["stw"][artid] = tokenstwlist
        tokendic["wlo"][artid] = tokengoodocrlist
        tokendic["wst"][artid] = tokengoodocrstwlist
        tokendic["low"]["all"] += tokenlist
        tokendic["stw"]["all"] += tokenstwlist
        tokendic["wlo"]["all"] += tokengoodocrlist
        tokendic["wst"]["all"] += tokengoodocrstwlist
    # print(tokendic)
    # print(tokendic["stw"]["all"])
    return tokendic, artidlist

def filterBadOcrUsingWordnetLemmata(tlist):
    # far too slow to check against whole WN word list
    # we first use sets and intersection and compare the smaller lists
    # wlist = [t for t in tlist if t in wn_all_lemma_list]
    tset = set(tlist)
    iset = tset.intersection(wn_all_lemma_set)
    ilist = list(iset)
    wlist = [t for t in tlist if t in ilist]
    # print(len(tlist), len(wlist), len(ilist))
    return wlist

def postProcessTokens(tlist):
    # strip punctuation
    tokennopunctlist = [t for t in tlist if t not in ipunct]
    # convert to lower case
    tokenlowerlist = [t.lower() for t in tokennopunctlist]
    # only include tokens longer than one char
    tokennoonecharlist = [t for t in tokenlowerlist if len(t) > 1 ]
    # strip numbers or tokens containing numbers
    tokennonumlist = [t for t in tokennoonecharlist if not re.search(r"\d", t) ]
    # strip non-alphabetic characters, i. e. get rid of bad OCR
    tokennononalphalist = [t for t in tokennonumlist if not re.search(r"[^A-Za-z]", t) ]
    # strip stop words
    tokennostoplist = [t for t in tokennononalphalist if t not in english_stops]
    # print(len(tokennostoplist), tokennostoplist)
    return tokennononalphalist, tokennostoplist
    

def tokenizePunktTokenize(t, docid):
    tokenlist = []
    tmptokenlist = []
    # training data already loaded at beginning of file
    # sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    # sents = sent_detector.tokenize(t.strip(), realign_boundaries=True)
    sents = sent_detector.tokenize(t.strip(), realign_boundaries=False)
    for s in sents:
        # tokens = nltk.word_tokenize(s)
        tokens = nltk.PunktWordTokenizer().tokenize(s)
        tokenlist += tokens
    # move sentence end full stops to a separate token
    for tok in tokenlist:
        if (tok.endswith(".") and (len(tok) > 1)):
            tmptokenlist.append(tok[:-1])
            tmptokenlist.append(".")
        else:
            tmptokenlist.append(tok)
    tokenlist = []
    for tok in tmptokenlist:
        if (tok.startswith("'") and (len(tok) > 1)):
            if tok == "'s":
                tokenlist.append(tok)
            else:
                tokenlist.append("'")
                tokenlist.append(tok[1:])
        else:
            tokenlist.append(tok)
    return tokenlist

def tokenizeWordPunctTokenize(t, docid):
    tokens = nltk.wordpunct_tokenize(t)
    tmptokenlist = []
    tokenssort = sorted(tokens)
    # for l in tokenssort:
    #     print(l)
    # print(len(tokenssort))
    for tk in tokens:
        tklen = len(tk)
        if tk[0] in string.punctuation:
            if tklen > 1:
                # print("TKLEN:", tklen, tk[0])
                for i in range(0, tklen):
                    tmptokenlist.append(tk[i])
            else:
                tmptokenlist.append(tk)
        else:
            tmptokenlist.append(tk)
    # return tokens
    return tmptokenlist

def tokenizeWordTokenize(t, docid):
    tokenlist = []
    sents = sent_detector.tokenize(t)
    # pprint.pprint(sents)
    for s in sents:
        # conts = re.findall(r"\w+'\w+", s)
        # print(conts)

        tokens = nltk.word_tokenize(s)

        # word_tokenize
        # A word tokenizer that tokenizes sentences using the conventions
        # used by the Penn Treebank.  Contractions, such as "can't", are
        # split  in to two tokens.  E.g.:
        # 
        # - can't S{->} ca n't
        # - he'll S{->} he 'll
        # - weren't S{-} were n't
        
        tokenlist += tokens
    return tokenlist
    
def tokenizeRegexpTokenize(t, docid):
    tokenlist = []
    pattern = r'''(?x)    # set flag to allow verbose regexps
                  ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
                | \w+(-\w+)*        # words with optional internal hyphens
                | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
                | \.\.\.            # ellipsis
                | [][.,;"'?():-_`]  # these are separate tokens
    ''' # ''' this is to fix Aquamacs syntax highlighting

    sents = sent_detector.tokenize(t)
    for s in sents:
        tokens = nltk.regexp_tokenize(s, pattern)    
        tokenlist += tokens
    return tokenlist

def freqTest(tokendic):
    # print(tokendic["low"]["EWJ-1858-05-01-Ar04902"])
    # print(tokendic["stw"]["EWJ-1858-05-01-Ar04902"])
    # FreqDist: see nltk.probability.FreqDist
    # ewjfreqdist = nltk.FreqDist(tokendic["low"]["EWJ-1858-05-01-Ar04902"])
    # ewjfreqdist = nltk.FreqDist(tokendic["stw"]["EWJ-1858-05-01-Ar04902"])
    # ewjfreqdist = nltk.FreqDist(tokendic["stw"]["all"])
    # print(ewjfreqdist)
    # print(ewjfreqdist.samples())
    # print(len(ewjfreqdist.samples()))
    # print(ewjfreqdist.N())
    # print(ewjfreqdist.B())
    # print(ewjfreqdist.items())
    ewjlowfreqdist = nltk.FreqDist(tokendic["low"]["all"])
    fobj = file(os.path.join(basedir, "freq/low-freq-all.txt"), "w")
    for itms in ewjlowfreqdist.items():
        print("%s\t%s" % (itms[0], itms[1]), file=fobj)
    fobj.close()
    ewjstwfreqdist = nltk.FreqDist(tokendic["stw"]["all"])
    fobj = file(os.path.join(basedir, "freq/stw-freq-all.txt"), "w")
    for itms in ewjstwfreqdist.items():
        print("%s\t%s" % (itms[0], itms[1]), file=fobj)
    fobj.close()
    # ewjfreqdist.tabulate()
    # ewjfreqdist.plot()
    # res = printDistributionPlot(tokendic["stw"]["all"], ewjfreqdist)
    
def generateFreqDist(tokdic):
    freqdic = {}
    for listtype in tokdic.keys():
        freqdic[listtype] = {}
        for listid in tokdic[listtype].keys():
            freqdic[listtype][listid] = nltk.FreqDist(tokdic[listtype][listid]).items()
    return freqdic 

def printDistributionPlot(tokunsortedlist, fdist):
    exceptionlist = ["'s", "mr", "said", "would", "also"]
    exceptionlist2 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "$"]
    distplotlist = []
    cnt = 0
    while len(distplotlist) < 21:
        if (fdist.keys()[cnt] not in exceptionlist) and (fdist.keys()[cnt][0] not in exceptionlist2):
            distplotlist.append(fdist.keys()[cnt])
        cnt += 1

    # distplotlist = fdist.keys()[:10]
    # for ty in fdist.keys()[:50]:
    #     print(ty, "\t", fdist[ty], "\t", fdist.freq(ty), "\t", fdist.freq(ty)*100)
    #
    # dispersion plot
    nltk.draw.dispersion.dispersion_plot(tokunsortedlist, distplotlist)

def createPickle(picklefilepath, tokendic, frequencydic):
    pickleoutput = open(picklefilepath, 'wb')
    print("Pickle tokendic")
    cPickle.dump(tokendic, pickleoutput, 2)
    print("Pickle frequencydic")
    cPickle.dump(frequencydic, pickleoutput, 2)
    pickleoutput.close()

def createSqlite(basedir):    
    sqlite3dir = os.path.join(basedir, "db")
    sqlite3filepath = os.path.join(sqlite3dir, "bajsps-ewj.db")
    scon = sqlite3.connect(sqlite3filepath)
    scur = scon.cursor()
    scur.executescript("""
        create table tokenslow(
            id integer primary key,
            seqid integer,
            artid text,
            token text
        );

        create table tokensstw(
            id integer primary key,
            seqid integer,
            artid text,
            token text
        );

        create table typeslow(
            id integer primary key,
            seqid integer,
            artid text,
            token text,
            freq integer
        );

        create table typesstw(
            id integer primary key,
            seqid integer,
            artid text,
            token text,
            freq integer
        );
        """)
    scon.commit()
    scon.close()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-b", "--basedir", dest="basedir", default="/data/docs/textmining/ncse",
                      help="Output/input base directory for data - default: %s", metavar="DIRECTORY")
    # parser.add_option("-r", "--readwrite", dest="readwrite", default="read",
    #                   help="Read: read in previously generated tables, write: write all tables from scratch - default: 'read'", metavar="RW")
    parser.add_option("-p", "--process", dest="processtype",
                      type="choice", choices=["tok", "ngram"], default="tok",
                      help="What kind of process to run: tok, ngram - default: %default", metavar="PROCESS")
    # parser.add_option("-x", "--fileprefix", dest="fileprefix", default="xxx",
    #                   help="Prefix for all created filenames - default: 'xxx'", metavar="PFIX")

    (options, args) = parser.parse_args()

    basedir = options.basedir
    processtype = options.processtype

    # for testing    
    # ewjsubdir = "corpustxt-20090224/EWJ/1858/03"
    ewjsubdir = "corpustxt-20090224/EWJ"
    ewjpath = os.path.join(basedir, ewjsubdir)
    
    # print(ewjpath)
    # print(processtype)

    
    infilelist = getInfileList(ewjpath)
    tokendic, artidlist = processTexts(infilelist)
    frequencydic = generateFreqDist(tokendic)
    
    # for k in tokendic.keys():
    #     # print(k)
    #     for e in artidlist:
    #         print(k, e, len(tokendic[k][e]))
    #     print(k, "all", len(tokendic[k]["all"]))
    
    pickledir = os.path.join(basedir, "pcl")
    picklefilepath = os.path.join(pickledir, "bajsps-ewj.pcl")
        
    basetokdir = os.path.join(basedir, "tok")

    baseunsortdir = os.path.join(basetokdir, "unsort")
    for listtype in tokendic.keys():
        print("Write unsorted: %s" % (listtype, ))
        baselisttypedir = os.path.join(baseunsortdir, listtype)
        outpath = os.path.join(baselisttypedir, "artids.txt")
        fobj = file(outpath, "w")
        for artid in artidlist:
            print(artid, file = fobj)
        fobj.close()
        for listid in tokendic[listtype].keys():
            outfile = listid + ".txt"
            outpath = os.path.join(baselisttypedir, outfile)
            fobj = file(outpath, "w")
            for tok in tokendic[listtype][listid]:
                print(tok, file = fobj)
            fobj.close()

    basefreqdir = os.path.join(basetokdir, "freqsort")
    for listtype in frequencydic.keys():
        print("Write frequency sort: %s" % (listtype, ))
        baselisttypedir = os.path.join(basefreqdir, listtype)
        outpath = os.path.join(baselisttypedir, "artids.txt")
        fobj = file(outpath, "w")
        for artid in artidlist:
            print(artid, file = fobj)
        fobj.close()
        for listid in frequencydic[listtype].keys():
            outfile = listid + ".txt"
            outpath = os.path.join(baselisttypedir, outfile)
            fobj = file(outpath, "w")
            for tup in frequencydic[listtype][listid]:
                print("%s\t%s" % (tup[0], tup[1]), file = fobj)
            fobj.close()
            
    # createPickle(picklefilepath, tokendic, frequencydic)
    # createSqlite(basedir)



    print("--== FINISHED ==--")

