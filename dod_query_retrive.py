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
	kg_embedding.convert_conversation(user_id, conversation)
	






