from KG_construct import KG_construct
from KG_embedding import *
from KG_extractor import KG_extractor
from sentence_transformers import SentenceTransformer, util
import torch

#kg_construct = KG_construct()
embedder = SentenceTransformer('all-MiniLM-L6-v2')
TOP_K = 3
kg_embedding = KG_embedding()


def query_embeddings(query: str, corpus: list):
	"""
	query on the existing stored database

	Parameters:
	-----------
	query: the query 
	corpus: candidate sentence list for answering

	Returns:
	--------
	top k answering sentences
	"""

	corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
	query_embedding = embedder.encode(query, convert_to_tensor=True)

	# We use cosine-similarity and torch.topk to find the highest 5 scores
	cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
	top_results = torch.topk(cos_scores, k=top_k)

	print("\n\n======================\n\n")
	print("Query:", query)
	print("Top ", TOP_K,  " most similar sentences in corpus:")

	for score, idx in zip(top_results[0], top_results[1]):
		print(corpus[idx], "(Score: {:.4f})".format(score))

def store_data(conversation: str, userid: int):
	"""
	storage data into spark database

	Parameters:
	-----------
	conversation: str, the input string
	userid: int

	Returns:
	-------
	stored graph database
	"""
	kg_embedding.convert_conversation(userid, conversation)


text = 'The following plan outlines the \
steps for researching the chemical composition of several\
 paintings created in Denmark in the mid-1800s and is intended to ensure the preservation \
 of these pieces. 1. Review the findings from the original research: review the study that \
 discovered beer and cereal grains in the base layer of Danish paintings and is from the mid-1800s.\
  Gather samples from the paintings: contact the relevant museums and obtain permission to gather \
  samples from the paintings studied in the research. Run lab tests: send the gathered samples to a \
  laboratory or hire a lab technician to analyze and identify the chemical composition of each painting.\
   5. Review comparison results: compare the findings of the lab tests of all the paintings studied to \
   systematically class the use of beer, cereal grains, and yeast in the base layer. Outreach to museums and \
   galleries: contact museums, galleries, and other places that house these pieces to provide them with the \
   information required to properly preserve these pieces. Executing these steps will allow us to understand \
   the chemical composition of these paintings, which is essential for their preservation. Additionally, \
   by presenting our findings in a scientific report, we can ensure that other museums, galleries, and art\
    historians can continue the research.'


#store_data(text, 1920)
search_embeddings("what is lab test", 'graph_database.triple_relation')






