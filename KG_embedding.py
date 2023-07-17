#from platform_core.DataBases.KGraph.KG_extractor import KG_extractor
from KG_construct import KG_construct
from pyspark.sql import functions as F
from sentence_transformers import SentenceTransformer, CrossEncoder, util
import torch
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

MODEL_NAME = 'nq-distilbert-base-v1'
BI_ENCODER = SentenceTransformer(MODEL_NAME)
TOP_K = 3



def search_embeddings(querys:str, table_name:str, user_id=None)-> list:
	"""
	Retrive top similar QA semantic matching sebtences

	Parameters:
	-----------
	querys: string of querys.
	table_name: data base table name.
	user_id: provided user id, default value is None.
	
	Returns:
	-------
	top_results: top semantic matching answer sentences 
	"""
	kg_embedding = KG_embedding()
	candidate_sentences = kg_embedding.retrieve_corpus(table_name, user_id)
	corpus_embedding = kg_embedding.embedding_corpus(sentences=candidate_sentences)

	query_embeddiing = kg_embedding.embedding_corpus(sentences=querys)

	cos_scores = util.cos_sim(query_embeddiing, corpus_embedding)[0]
	top_results = torch.topk(cos_scores, k=3)

	#top_sentences = []
	#top_cos_scores = []

	for score, idx in zip(top_results[0], top_results[1]):
		print(candidate_sentences[idx],"(Score: {:.4f})".format(score))



class KG_embedding(KG_construct):
	"""
	Construct embedding vector database
	"""
	def __init__(self):
		spark = SparkSession.builder.enableHiveSupport().getOrCreate()
		KG_construct.__init__(self, spark)

	def retrieve_corpus(self, table_name:str, user_id=None)-> list:
		"""
		retrive sentence corpus from existing database

		Parameters:
		-----------
		table_name: data base table name.
		user_id: provided user id, default value is None.

		Returns:
		-------
		corpus: retrived corpus list
		"""
		dataframe = self.extract_table().toPandas()

		sources = dataframe['source']
		relation = dataframe['relation']
		target = dataframe['target']
		sentences = []
		for i in range(len(sources)):
			text = sources[i] + ' ' + relation[i] + ' '+ target[i]
			sentences = sentences.append(text)

		return sentences

	def embedding_corpus(self, sentences:list)-> list:
		"""
		embed corpus sentences

		Parameters:
		----------
		sentences: list of sentence of interest

		Returns:
		-------
		embedding_vector: list of embedded sentence vectors
		"""
		corpus_embedding = BI_ENCODER(corpus, convert_to_tensor=True)

		return corpus_embedding


	def query_analyze(self,query_text):
		doc = self.nlp(query_text)
		query_entity = []
		for tok in doc:
			print(tok.head.text,"-->",tok.text,"-->",tok.dep_,"-->",tok.pos_)
			if not tok.pos_ == "PRON" and not tok.pos_ == "DET" \
			and not tok.pos_ == "AUX"\
			and not tok.pos_ == "ADV" and not tok.pos_ == "PUNCT":
				query_entity.append(tok.text)
		print(query_entity)
		self.query_entity = query_entity


	def extract_entities(self, dataframe):
		answer_tables = []
		for entity in self.query_entity:
			answer_df = dataframe.filter(F.col("target").contains(entity)|F.col("source").contains(entity))
			answer_tables.append(answer_df)
		if answer_tables == []:
			return None
		if not len(answer_tables) == 1:
			join_table = answer_tables[0]
			for i in range(len(answer_tables)):
				join_table = join_table.union(answer_tables[i]).dropDuplicates()
			self.answer_table = join_table
		else:
			self.answer_table = answer_tables[0]

		return True

	def return_triple_sentences(self):
		df = self.answer_table.toPandas()
		sources = df['source']
		relation = df['relation']
		target = df['target']
		sentences = ''
		for i in range(len(sources)):
			text = sources[i] + ' ' + relation[i] + ' '+ target[i]
			sentences = sentences + text + '. '

		self.returned_sentences = sentences
		#return sentences

	def keyword_entity_extraction(self, query_text, dataframe):
		self.query_analyze(query_text)
		result = self.extract_entities(dataframe)
		if result == None:
			return None
		else:
			self.return_triple_sentences()
			return True

			






