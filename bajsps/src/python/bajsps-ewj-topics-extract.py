#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: look into nltk.text and its methods to explore

from __future__ import print_function
import sys
import string
import re
import types
import os, os.path
import cPickle
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

def removeStopWords(tl):
    cl = [w for w in tl if w.lower() not in stopwords]
    return cl

def removeHapaxLegomena(tl):
    # from gensim: remove words that appear only once
    # ATTENTION !!!
    # unlike removeStopWords this function processes a list of list (of tokens)
    # print("LEN:", len(tl))
    # print("X", len(tl))
    # print("X", len(tl[0]))
    # sys.exit()
    allTokens = sum(tl, [])
    tokensOnce = set(word for word in set(allTokens) if allTokens.count(word) == 1)
    # tl = [[word for word in text if word not in tokensOnce]
    #          for text in tl]
    # print(type(tokensOnce))
    # tl = [word for word in tl if word not in tokensOnce]
    tl = [[word for word in text if word not in tokensOnce]
             for text in tl]
    return tl

def OLDprintDistributionPlot(tokunsortedlist, fdist):
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
    

def printDistributionPlot(tokunsortedlist, distplotlist):
    #
    # dispersion plot
    nltk.draw.dispersion.dispersion_plot(tokunsortedlist, distplotlist)

def processGensim(tokunsortedlist):
    # LSA (gensim)
    # remove stopwords
    gensimlogfile = "bajsps-gensim-%s.log" % ("ewj", )
    gensimlogfilepath = os.path.join(gensimoutdir, gensimlogfile)
    logging.basicConfig(filename = gensimlogfilepath, filemode = 'w', format = '%(asctime)s : %(levelname)s : %(message)s', level = logging.INFO)
    print('=' * 30)
    print("CONFLICT:", "gensim")
    dictionaryfilepath = os.path.join(gensimoutdir, "gensim-%s.dict" % ("ewj", ))
    corpusmmfilepath = os.path.join(gensimoutdir, "gensim-%s.mm" % ("ewj", ))
    # 
    # print(type(tokunsortedlist))
    # print(type(tokunsortedlist[0]))
    # print(type(tokunsortedlist[0][0]))
    # print(len(tokunsortedlist))
    # print(len(tokunsortedlist[0]))
    # print(len(tokunsortedlist[1]))
    # print(stopwords)
    # for word in tokunsortedlist:
    #     print(word)
    # tokunsortedlist is list of lists
    tlist = [[word for word in textlist if word not in stopwords]
         for textlist in tokunsortedlist]
    # tlist = [word for word in tokunsortedlist if word not in stopwords]
    # print("X", len(tlist))
    # print("X", len(tlist[0]))
    tlist = removeHapaxLegomena(tlist)
    # print("Y", len(tlist))
    # print("Y", len(tlist[0]))
    # for n, tx in enumerate(tlist):
    #     print("LEN of text %d: %d" % (n, len(tx)))
    dictionary = corpora.Dictionary(tlist)
    dictionary.save(dictionaryfilepath) # store the dictionary, for future reference
    # print("DICTIONARY:")
    # print(dictionary)
    # print("DICTIONARY.TOKEN2ID:")
    # print(dictionary.token2id)
    corpus = [dictionary.doc2bow(text) for text in tlist]
    corpora.MmCorpus.saveCorpus(corpusmmfilepath, corpus) # store to disk, for later use
    # print(corpus)
    # Creating a transformation
    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    # Or to apply a transformation to a whole corpus:
    corpus_tfidf = tfidf[corpus]
    # for doc in corpus_tfidf:
    #     print(doc)
    # Transformations can also be serialized, one on top of another, in a sort of chain:
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary.id2word, numTopics=300) # initialize an LSI transformation
    corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
    # Let's inspect with :func:`models.LsiModel.printTopics`:
    logging.info('------------------------------------')
    logging.info('PRINT TOPICS')
    lsi.printTopics(2)
    logging.info('------------------------------------')

    # print topics and their tokens
    print('====================================')
    print(lsi.numTopics)
    print("PRINT TOPIC:")
    for nt in range(lsi.numTopics):
        print("TOPIC NO.",nt)
        print(lsi.printTopic(nt, topN = 10).encode("UTF-8"))
    print('====================================')

    # load previously save model, in this example from Dirichlet allocation:
    lda = models.LdaModel.load("/data/docs/textmining/ncsetest/gensim/ldamodel")

    logging.info('------------------------------------')
    logging.info('PRINT DEBUG')
    lsi.printDebug(numTopics=5, numWords=10)
    logging.info('------------------------------------')

    # print(len(dictionary))
    # print(str(dictionary))

    # print("CORPUS_TFIDF:", corpus_tfidf)
    # print("       TFIDF:", tfidf)
    # for c in corpus_tfidf:
    #     print(len(c))
    #     print(c)


def getArtidList(indir):
    print("Read frequency lists.")
    infile = "artids.txt"
    infilepath = os.path.join(indir, infile)
    fobj = file(infilepath, "r")
    artidlist = fobj.readlines()
    artidlist = [artid.strip() for artid in artidlist]
    fobj.close()
    return artidlist

def getFrequencyListsAllTokensFromFile(indir):
    global freqtoklistdic, freqfrqlistdic
    print("Read frequency lists - all tokens.")
    infile = "all.txt"
    infilepath = os.path.join(indir, infile)
    fobj = file(infilepath, "r")
    alllist = fobj.readlines()
    # freqdic["all"] = [e.strip().split("\t") for e in alllist]
    freqtoklistdic["all"] = [e.strip().split("\t")[0] for e in alllist]
    freqfrqlistdic["all"] = [e.strip().split("\t")[1] for e in alllist]
    fobj.close()


def getFrequencyListsPerPubTokensFromFile(indir, artidlist):
    global freqtoklistdic, freqfrqlistdic
    print("Read frequency lists - tokens per pub.")
    for artid in artidlist:
        infile = "%s.txt" % (artid, )
        infilepath = os.path.join(indir, infile)
        fobj = file(infilepath, "r")
        artlist = fobj.readlines()
        # freqdic["all"] = [e.strip().split("\t") for e in alllist]
        freqtoklistdic[artid] = [e.strip().split("\t")[0] for e in artlist]
        freqfrqlistdic[artid] = [e.strip().split("\t")[1] for e in artlist]
        fobj.close()
    
def getLowListsAllTokensFromFile(indir):
    print("Read unsorted lists - all tokens.")
    infile = "all.txt"
    infilepath = os.path.join(indir, infile)
    fobj = file(infilepath, "r")
    alllist = fobj.readlines()
    unsorttoklistdic["all"] = [e.strip() for e in alllist]
    fobj.close()

def getLowListsPerPubTokensFromFile(indir, artidlist):
    global unsorttokperpublist
    print("Read unsorted lists - tokens by pub.")
    for artid in artidlist:
        infile = "%s.txt" % (artid, )
        infilepath = os.path.join(indir, infile)
        fobj = file(infilepath, "r")
        artlist = fobj.readlines()
        # unsorttoklistdic[artid] = [e.strip() for e in alllist]
        unsorttoklistdic[artid] = [e.strip() for e in artlist]
        # create list of lists (list of list of tokens) for gensim
        # unsorttokperpublist += unsorttoklistdic[artid] 
        unsorttokperpublist.append(unsorttoklistdic[artid]) 
        fobj.close()
    # print(len(unsorttokperpublist))
    # sys.exit()

def filterTokensUsingWordnet():
    # for k in wordnet.all_lemma_names():
    #     print(k)
    all_lemma_list = [k for k in wordnet.all_lemma_names()]
    print("WordNet tokens:", len(all_lemma_list))

    # just a first test to see what proportion of tokens is in wordnet
    # this is far too slow - try using sets
    noofewjtokens = len(freqtoklistdic["all"])     
    inwordnet = 0
    print(noofewjtokens)
    for n, f in enumerate(freqfrqlistdic["all"]):
        # if int(f) == 1:
        #     print(f, freqtoklistdic["all"][n])
        if freqtoklistdic["all"][n] in all_lemma_list:
            # print(freqtoklistdic["all"][n])
            inwordnet += 1
    print(inwordnet)

    print("%d of %d EWJ tokens are in wordnet" % (inwordnet, noofewjtokens))
    print("i. e. %d percent" % (inwordwnet*100/noofewjtokens, ))
    
    
    
    
    # for k in wordnet.all_synsets():
    #     print(k)
    # all_synsets_list = [k for k in wordnet.all_synsets()]
    # print(len(all_synsets_list))


def filterTokensUsingWords():
    print(words.fileids())
    for fid in words.fileids():
        print("Words in '%s': %d" % (fid, len(words.words(fid))))
        print(words.words(fid)[:5], "...", words.words(fid)[-5:])

 

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-b", "--basedir", dest="basedir", default="/data/docs/textmining/ncse",
                      help="Output/input base directory for data - default: %s", metavar="DIRECTORY")
    parser.add_option("-g", "--gensimoutdir", dest="gensimoutdir", default="/data/docs/textmining/ncse/gensim",
                      help="Output base directory for gensim data - default: %s", metavar="DIRECTORY")
    # parser.add_option("-r", "--readwrite", dest="readwrite", default="read",
    #                   help="Read: read in previously generated tables, write: write all tables from scratch - default: 'read'", metavar="RW")
    parser.add_option("-t", "--listtype", dest="listtype",
                      type="choice", choices=["low", "stw"], default="stw",
                      help="What kind of list type to run: low = all tokens lower case, stw = tokens no stop words - default: %default", metavar="PROCESS")
    parser.add_option("-p", "--process", dest="processtype",
                      type="choice", choices=["disp", "ngram"], default="disp",
                      help="What kind of process to run: disp, ngram - default: %default", metavar="PROCESS")
    # parser.add_option("-x", "--fileprefix", dest="fileprefix", default="xxx",
    #                   help="Prefix for all created filenames - default: 'xxx'", metavar="PFIX")

    (options, args) = parser.parse_args()

    basedir = options.basedir
    gensimoutdir = options.gensimoutdir
    processtype = options.processtype
    listtype = options.listtype
    
    if processtype == "disp":
        srcsubdir = "freqsort"
    elif processtype == "ngram":
        srcsubdir = "unsort"

    basetokdir = os.path.join(basedir, "tok")
    indir = os.path.join(basetokdir, srcsubdir,  listtype)

    pickledir = os.path.join(basedir, "pcl")
    picklefilepath = os.path.join(pickledir, "bajsps-ewj.pcl")

    print("Read article ids - artidlist")
    artidlist = getArtidList(indir)
    
    # print("Read frequency lists - all tokens.")
    getFrequencyListsAllTokensFromFile(indir)
    
    # print("Read frequency lists - tokens per pub.")
    getFrequencyListsPerPubTokensFromFile(indir, artidlist)
 
    # all tokens unsorted
    # print("Read unsorted lists.")
    # indir = os.path.join(basetokdir, "unsort", listtype)
    # print("Read unsorted lists - all tokens.")
    # getLowListsAllTokensFromFile(indir)
    
    # print("Read unsorted lists - tokens by pub.")
    # getLowListsPerPubTokensFromFile(indir, artidlist)
    # print(len(unsorttokperpublist))

    # print(freqtoklistdic["all"][:20])
    # print(freqfrqlistdic["all"][:20])
    # print(freqtoklistdic["EWJ-1858-04-01-Ar05901"][:10])
    # print(freqfrqlistdic["EWJ-1858-04-01-Ar05901"][:10])
    # print(unsorttoklistdic["all"][:10])
    # print(unsorttoklistdic["EWJ-1858-04-01-Ar05901"][:10])
    # sys.exit()

    # for n, f in enumerate(freqfrqlistdic["all"]):
    #     if int(f) > 100:
    #         print(f, freqtoklistdic["all"][n])

    # print(type(freqfrqlistdic["all"]))
    # pickleinput = open(picklefilepath, 'rb')
    # tokendic     = cPickle.load(pickleinput)
    # frequencydic = cPickle.load(pickleinput)
    # pickleinput.close()
    # print(tokendic["stw"]["EWJ-1858-04-01-Ar05901"][:10])
    # print(frequencydic["stw"]["EWJ-1858-04-01-Ar05901"][:10])

    # print("distribution plot")
    # distplotlist = ["women", "men", "governess", "institution", "education", "teacher", "crimea", "nightingale", "blackwell", "christmas"]
    # printDistributionPlot(unsorttoklistdic["all"], distplotlist)   

    # print("processGensim")
    # processGensim(unsorttokperpublist)
    
    filterTokensUsingWordnet()
    filterTokensUsingWords()

    print("--== FINISHED ==--")

