#from KG_embedding import *
#from pyspark import SparkContext, SparkConf
#from pyspark.sql import SparkSession
from KG_construct import KG_construct
from KG_embedding import *
from KG_extractor import KG_extractor
from sentence_transformers import SentenceTransformer, util
import torch

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Corpus with example sentences
corpus = ['A man is eating food.',
          'A man is eating a piece of bread.',
          'The girl is carrying a baby.',
          'A man is riding a horse.',
          'A woman is playing violin.',
          'Two men pushed carts through the woods.',
          'A man is riding a white horse on an enclosed ground.',
          'A monkey is playing drums.',
          'A cheetah is running behind its prey.'
          ]
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

kg_embedding = KG_embedding()
corpus = kg_embedding.retrieve_corpus('graph_database.triple_relation')

# Query sentences:
#queries = ['who is playing drums','A man is eating pasta.', 'Someone in a gorilla costume is playing a set of drums.', 'A cheetah chases prey on across a field.']
queries = ["what is lab test"]


# Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
top_k = min(5, len(corpus))
for query in queries:
    query_embedding = embedder.encode(query, convert_to_tensor=True)

    # We use cosine-similarity and torch.topk to find the highest 5 scores
    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=top_k)

    print("\n\n======================\n\n")
    print("Query:", query)
    print("\nTop 5 most similar sentences in corpus:")

    for score, idx in zip(top_results[0], top_results[1]):
        print(corpus[idx], "(Score: {:.4f})".format(score))



"""
def init_spark_context():
    # load spark context

    # IMPORTANT: pass aditional Python modules to each worker
    #global service 
    #global sc
    global spark

    #sc = SparkContext(conf=conf, pyFiles=['./platform_core/MayaEngine.py', './platform_core/WebServer/WebServer.py'])
    spark = SparkSession.builder.enableHiveSupport().getOrCreate()


init_spark_context()
kg_embedding = KG_embedding(spark)

"""