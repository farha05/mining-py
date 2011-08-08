library(tm)

# 1. read in matrix files
# 2. output some statistical measures (no of cols, no of rows, etc.)
# 3. output frequent terms

# BA-JSPS - EWJ

ewjtdmtffile = '/projects/cch/ba-jsps/dat/R/tm/ewjtdmtf.txt'
ewjtdmtfidffile = '/projects/cch/ba-jsps/dat/R/tm/ewjtdmtfidf.txt'
ewjdtmtffile = '/projects/cch/ba-jsps/dat/R/tm/ewjdtmtf.txt'
ewjdtmtfidffile = '/projects/cch/ba-jsps/dat/R/tm/ewjdtmtfidf.txt'


# -----------------------------------------
# READ FILES IN
ewjtdmtf = read.table(ewjtdmtffile,header=T,sep="\t",row.names=1, fileEncoding="UTF-8")
ewjtdmtfidf = read.table(ewjtdmtfidffile,header=T,sep="\t",row.names=1, fileEncoding="UTF-8")
ewjdtmtf = read.table(ewjdtmtffile,header=T,sep="\t",row.names=1, fileEncoding="UTF-8")
ewjdtmtfidf = read.table(ewjdtmtfidffile,header=T,sep="\t",row.names=1, fileEncoding="UTF-8")

## ncol(ewjtdmtf)
## ncol(ewjtdmtfidf)
## nrow(ewjtdmtf)
## dim(ewjtdmtfidf)
## nDocs(ewjtdmtfidf)
## nTerms(ewjtdmtfidf)

## findFreqTerms(ewjtdmtf, lowfreq = 10)

