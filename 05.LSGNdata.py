import pdb
import cPickle
import numpy as np
from xmlreader_subtree_semeval import *
import json
def offset2tokenid(Keyphrases, fn):
    xmlfn = fn.replace('.ann','.txt.xml')
    xmldoc = minidom.parse(xmlfn)
    sentlist = xmldoc.getElementsByTagName('sentences')[0].getElementsByTagName('sentence')
    line = []
    span0s = []
    span1s = []
    POS = []
    sen_ids = []
    token_ids = []
    heads = []
    head_ids = []
    phraseids = []
    doc = xmlfn.split('/')[-1].split('.')[0]
    sentences = []
    sentences_flat = []
    sentence_ids = []
    for i, sent in enumerate(sentlist):
        idx = int(sent.attributes['id'].value)
        depelem_list, dep_dict = getDeptree(sent)
        tokenelem_dict = getTokens(sent)
        tokenelem_list = integrate(tokenelem_dict, depelem_list)
        line = []
        for token in tokenelem_list:
            sentences_flat.append(token.word)
            line.append(token.word)
            POS.append(token.pos)
            span0s.append(token.offsetbegin)
            span1s.append(token.offsetend)
            sen_ids.append(i)
            token_ids.append(token.idx-1)
            heads.append(token.deptype)
            head_ids.append(token.headidx-1)
            phraseids.append(doc)
            sentence_ids.append(i)
        sentences.append(line)

    tokens = ['O' for m in range(len(line))]
    aspects = []
    rmset = set()
    for phraseID in Keyphrases:
        span0 = int(Keyphrases[phraseID][1][1])
        span1 = int(Keyphrases[phraseID][1][2])
        if span0 not in span0s:
            print span0
            print doc
            rmset.add(phraseID)
            continue
        if span1 not in span1s:
            print span1
            print doc
            rmset.add(phraseID)
            continue
        tokenb = span0s.index(span0)
        tokene = span1s.index(span1)
        Keyphrases[phraseID][1][1] = tokenb
        Keyphrases[phraseID][1][2] = tokene
    for phraseID in rmset:
        del Keyphrases[phraseID]
    return sentences, sentence_ids
def ProcessEntity(phrasedir, sentence_ids):
    ner = [[] for i in range(sentence_ids[-1]+1)]
    for phrase in phrasedir:
        if sentence_ids[phrasedir[phrase][1][1]] != sentence_ids[phrasedir[phrase][1][2]]:
            pdb.set_trace()
        else:
            ent = phrasedir[phrase][1][1:] + [phrasedir[phrase][1][0]]
            ner[sentence_ids[phrasedir[phrase][1][1]]].append(ent)
    for i in range(len(ner)):
        ner[i] = sorted(ner[i])
    return ner
                
def ProcessRelations(phrasedir, relations, sentence_ids):
    rel = [[] for i in range(sentence_ids[-1]+1)]
    for relation in relations:
        cat = relation[0]
        if cat == 'COREF':continue
        if relation[1] not in phrasedir or relation[2] not in phrasedir :
            print fn
            print relation
            continue
        phrase1 = phrasedir[relation[1]][1]
        phrase2 = phrasedir[relation[2]][1]
        if sentence_ids[phrase1[1]] != sentence_ids[phrase2[1]]:
            print fn
            print cat
        else:
            # if phrase1[1] > phrase2[1]:
            #     cat = cat + '_REVERSE'
            #     phrase1,phrase2 = phrase2,phrase1
            cur_rel = phrase1[1:] + phrase2[1:] + [cat]
            rel[sentence_ids[phrase1[1]]].append(cur_rel)

    for i in range(len(rel)):
        rel[i] = sorted(rel[i])
    return rel

def ProcessCorefs(phrasedir, clusters, sentence_ids):
    for i in range(len(clusters)):
        new_lst = []
        for j in range(len(clusters[i])):
            if clusters[i][j] not in phrasedir:
                print fn
                print 'COREF'
                print clusters[i][j]
                continue
            new_lst.append(phrasedir[clusters[i][j]][1][1:])
        new_lst = sorted(new_lst)
        clusters[i] = new_lst

        

def ReadAnn(fn):
    relations = []
    phrasedir = {}
    doc = fn.split('/')[-1].split('.')[0]
    for line in open(fn):
        if line.startswith('T'):
            tokens = line.rstrip().split('\t')
            phrasedir[tokens[0]] = [tokens[-1],tokens[1].split(' ')]
        elif line.startswith('R'):
            tokens = line.rstrip().split('\t')
            rtokens = tokens[-1].split()
            key1 = rtokens[-2].split(':')[-1]
            key2 = rtokens[-1].split(':')[-1]
            relation = rtokens[0]
            relations.append([relation,key1,key2])
    sentences, sentence_ids = offset2tokenid(phrasedir, fn)
    clusters = GetClusters(relations, phrasedir)
    ner = ProcessEntity(phrasedir, sentence_ids)
    rels = ProcessRelations(phrasedir, relations, sentence_ids)
    ProcessCorefs(phrasedir, clusters, sentence_ids)
    
    curdir = {'clusters': clusters, 'relations':rels, 'ner':ner, 'doc_key':doc, 'sentences':sentences}
    # pdb.set_trace()
    return curdir

def GetClusters(relations, phrasedir):
    corefs = {}
    terms = set([])
    for relation in relations:
        if relation[0] == 'COREF':
            terms.add(relation[1])
            terms.add(relation[2])
            
            if relation[1] in corefs:
                corefs[relation[1]].add(relation[2])
            else:
                corefs[relation[1]] = set()
                corefs[relation[1]].add(relation[2])

            if relation[2] in corefs:
                corefs[relation[2]].add(relation[1])
            else:
                corefs[relation[2]] = set()
                corefs[relation[2]].add(relation[1])
                
    clusters = Clusters(corefs, terms)
    return clusters



def Clusters(corefs, terms):
    seen = set([])
    clusters = []
    for term in terms:
        if term not in seen:
            tosee = [term]
            cluster = []
            while tosee:
                ele = tosee.pop()
                cluster.append(ele)
                seen.add(ele)
                for i in corefs[ele]:
                    if i not in seen:
                        tosee.append(i)
            clusters.append(cluster)
    return clusters
relations_train = []
relations_dev = []
relations_test = []
phrases = {}
verdir = '/homes/luanyi/pubanal/data/ScienceKG/version1/'
indir = verdir + 'all'
fns = glob(indir+'/*.ann')
np.random.seed(0)
np.random.shuffle(fns)
i = 0
for fn in fns:
    if i < 350:
        relations_train.append(ReadAnn(fn))
    elif i < 400:
        relations_dev.append(ReadAnn(fn))
    else:
        relations_test.append(ReadAnn(fn))
    i += 1
    
outfn = '/homes/luanyi/ataros/ScientificKG/ScienceKG_train.noreverse.json'
print outfn
with open(outfn,'w') as f:
    for relation in relations_train:
        f.write(json.dumps(relation))
        f.write('\n')
outfn = '/homes/luanyi/ataros/ScientificKG/ScienceKG_dev.noreverse.json'
with open(outfn,'w') as f:
    for relation in relations_dev:
        f.write(json.dumps(relation))
        f.write('\n')
outfn = '/homes/luanyi/ataros/ScientificKG/ScienceKG_test.noreverse.json'
with open(outfn,'w') as f:
    for relation in relations_test:
        f.write(json.dumps(relation))
        f.write('\n')




