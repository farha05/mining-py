library(tm)

# 1. create corpus from contents of a directory
# 2. create TermDocumentMatrix and DocumentTermMatrix from corpus
#    a) using term frequency
#    b) using TF/IDF
# 3. output some statistical measures (no of cols, no of rows, etc.)
# 4. output frequent terms
# 5. write matrices to TAB delimited files
#    matrices have to be converted to data frame before they can be written

(ewjcorp <- Corpus(DirSource(directory = "/projects/cch/ncse/corpustxt-20090224/EWJ", encoding = "UTF-8", recursive = TRUE), readerControl = list(reader = readPlain, language = "en_GB", load = TRUE)))

# (ewjcorp <- Corpus(DirSource(directory = "/projects/cch/ncse/corpustxt-20090224/EWJ/1858/04", encoding = "UTF-8", recursive = TRUE), readerControl = list(reader = readPlain, language = "en_GB", load = TRUE)))

print("Converting to lower case")
ewjcorp <- tm_map(ewjcorp, tolower)
print("Removing stopwords")
ewjcorp <- tm_map(ewjcorp, removeWords, stopwords("english"))
print("Removing punctuation")
ewjcorp <- tm_map(ewjcorp, removePunctuation)
print("Removing numbers")
ewjcorp <- tm_map(ewjcorp, removeNumbers)
print("Stripping whitespace")
ewjcorp <- tm_map(ewjcorp, stripWhitespace)
# ewjcorp <- tm_map(ewjcorp, stemDocument)

print("Creating matrix ewjtdmtf")
ewjtdmtf <- TermDocumentMatrix(ewjcorp,
                          control = list(weighting = weightTf,
                                         removePunctuation = TRUE))
print("Creating matrix ewjdtmtf")
ewjdtmtf <- DocumentTermMatrix(ewjcorp,
                          control = list(weighting = weightTf,
                                         removePunctuation = TRUE))

print("Creating matrix ewjtdmtfidf")
ewjtdmtfidf <- TermDocumentMatrix(ewjcorp,
                          control = list(weighting = weightTfIdf,
                                         removePunctuation = TRUE))
print("Creating matrix ewjdtmtfidf")
ewjdtmtfidf <- DocumentTermMatrix(ewjcorp,
                          control = list(weighting = weightTfIdf,
                                         removePunctuation = TRUE))

## ncol(ewjtdmtf)
## ncol(ewjtdmtfidf)
## nrow(ewjtdmtf)
## dim(ewjtdmtfidf)
## nDocs(ewjtdmtfidf)
## nTerms(ewjtdmtfidf)

## findFreqTerms(ewjtdmtf, lowfreq = 10)

# to write the matrix to a file it first has to be converted to a data frame
# ---------
print("Writing matrix ewjtdmtf")
ewjtdmtf.m <- inspect(ewjtdmtf)
ewjtdmtf.df <- as.data.frame(ewjtdmtf.m, stringsAsFactors = FALSE)
write.table(ewjtdmtf.df, file = '/projects/cch/ba-jsps/dat/R/tm/ewjtdmtf.txt', quote = FALSE, sep = '\t')
# ---------
print("Writing matrix ewjtdmtfidf")
ewjtdmtfidf.m <- inspect(ewjtdmtfidf)
ewjtdmtfidf.df <- as.data.frame(ewjtdmtfidf.m, stringsAsFactors = FALSE)
write.table(ewjtdmtfidf.df, file = '/projects/cch/ba-jsps/dat/R/tm/ewjtdmtfidf.txt', quote = FALSE, sep = '\t')
# ---------
print("Writing matrix ewjdtmtf")
ewjdtmtf.m <- inspect(ewjdtmtf)
ewjdtmtf.df <- as.data.frame(ewjdtmtf.m, stringsAsFactors = FALSE)
write.table(ewjdtmtf.df, file = '/projects/cch/ba-jsps/dat/R/tm/ewjdtmtf.txt', quote = FALSE, sep = '\t')
# ---------
print("Writing matrix ewjdtmtfidf")
ewjdtmtfidf.m <- inspect(ewjdtmtfidf)
ewjdtmtfidf.df <- as.data.frame(ewjdtmtfidf.m, stringsAsFactors = FALSE)
write.table(ewjdtmtfidf.df, file = '/projects/cch/ba-jsps/dat/R/tm/ewjdtmtfidf.txt', quote = FALSE, sep = '\t')

print("--== FINISHED ==--")
