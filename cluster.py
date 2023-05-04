import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForMaskedLM
from sklearn.cluster import KMeans
from tqdm import tqdm
import logging
import argparse

logging.basicConfig(level=logging.INFO)

MODEL = "roberta-base"
DATASET = "spider"
DATASET_COLUMN = "query"
K = 20
KMEANS_RANDOM_STATE = 42

def main():
    # Load the dataset
    logging.info("Loading the %s dataset...", DATASET)
    dataset = load_dataset(DATASET)

    # load the roBERTa-base-uncased model
    logging.info("Loading the %s model...", MODEL)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForMaskedLM.from_pretrained(MODEL)

    # prepare input: the texts from the spider dataset train and dev splits
    logging.info("Preparing the input from the \"%s\" column of the dataset...", DATASET_COLUMN)
    texts = dataset['train'][DATASET_COLUMN]

    # embed each sentnece in the dataset
    logging.info("Embedding the dataset...")
    embeddings = []
    labels = []
    for text in tqdm(texts):
        encoded_input = tokenizer(text, return_tensors='pt')

        # forward pass
        output = model(**encoded_input)

        # extract the [CLS] embedding
        text_embedding = output[0][0, 0, :].detach().numpy()

        # save the embedding and label
        embeddings.append(text_embedding)
        labels.append(text)

    # Make a dict where the key is the labels and the value is the embeddings
    embeddings_dict = {}
    for i in range(len(labels)):
        embeddings_dict[labels[i]] = embeddings[i]

    # Cluster the embeddings and write the corresponding labels of the clusters to disk in individual txt files (verbose)
    logging.info("Clustering the embeddings with %d clusters and random state %d...", K, KMEANS_RANDOM_STATE)
    kmeans = KMeans(n_clusters=K, random_state=KMEANS_RANDOM_STATE, verbose=1).fit(embeddings)
    
    # Match cluster labels to text labels
    cluster_labels = {}
    for i in range(len(kmeans.labels_)):
        cluster_labels[labels[i]] = kmeans.labels_[i]
    
    # write the cluster labels to disk
    logging.info("Writing the cluster labels to disk...")
    for i in range(K):
        f = open("./output/clusters/cluster"+str(i) + \
                "_d=" + DATASET + \
                "_col=" + DATASET_COLUMN + \
                "_r=" + str(KMEANS_RANDOM_STATE) +".txt", "w")
        for key in cluster_labels:
            if cluster_labels[key] == i:
                f.write(key+"\n")
        f.close()

    logging.info("Done!")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--model", type=str, default=MODEL, help="The model to use for embedding the dataset")
    argparser.add_argument("--dataset", type=str, default=DATASET, help="The dataset to cluster")
    argparser.add_argument("--dataset_column", type=str, default=DATASET_COLUMN, help="The column of the dataset to cluster")
    argparser.add_argument("-k", type=int, default=K, help="The number of clusters to create")
    argparser.add_argument("-r", type=int, default=KMEANS_RANDOM_STATE, help="The random state to use for the kmeans algorithm")
    args = argparser.parse_args()

    MODEL = args.model
    DATASET = args.dataset
    K = args.k
    KMEANS_RANDOM_STATE = args.r
    DATASET_COLUMN = args.dataset_column
    
    main()
