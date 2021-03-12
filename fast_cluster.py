"""
This is a more complex example on performing clustering on large scale dataset.
This examples find in a large set of sentences local communities, i.e., groups of sentences that are highly
similar. You can freely configure the threshold what is considered as similar. A high threshold will
only find extremely similar sentences, a lower threshold will find more sentence that are less similar.
A second parameter is 'min_community_size': Only communities with at least a certain number of sentences will be returned.
The method for finding the communities is extremely fast, for clustering 50k sentences it requires only 5 seconds (plus embedding comuptation).
In this example, we download a large set of questions from Quora and then find
similar questions in this set.
"""

import pickle
from sentence_transformers import SentenceTransformer, util
import numpy as np
import os
import time
from config import itsm_data_dir
from text_format import itsm_tbl_clean


def community_detection(embeddings, threshold=0.9, init_max_size=400):
    # Compute cosine similarity scores
    cos_scores = util.pytorch_cos_sim(embeddings, embeddings)
    # length
    n = list(cos_scores.size())[0]

    extracted_communities = []
    for i in range(n):
        new_cluster = []

        # Only check top k most similar entries
        top_val_large, top_idx_large = cos_scores[i].topk(k=init_max_size, largest=True)
        top_idx_large = top_idx_large.tolist()
        top_val_large = top_val_large.tolist()

        if top_val_large[-1] < threshold:
            for idx, val in zip(top_idx_large, top_val_large):
                if val < threshold:
                    break

                new_cluster.append(idx)
        else:
            # Iterate over all entries (slow)
            for idx, val in enumerate(cos_scores[i].tolist()):
                if val >= threshold:
                    new_cluster.append(idx)

        extracted_communities.append(new_cluster)

    # Largest cluster first
    extracted_communities = sorted(extracted_communities, key=lambda x: len(x), reverse=True)

    # Step 2) Remove overlapping communities
    unique_communities = []
    extracted_ids = set()

    for community in extracted_communities:
        add_cluster = True
        for idx in community:
            if idx in extracted_ids:
                add_cluster = False
                break

        if add_cluster:
            unique_communities.append(community)
            for idx in community:
                extracted_ids.add(idx)

    return unique_communities


def embedding_cache():
    embedding_cache_path = f'{itsm_data_dir}/itsm-embeddings-cache.pkl'
    # Check if embedding cache path exists
    if not os.path.exists(embedding_cache_path):
        model = SentenceTransformer('hfl/chinese-bert-wwm-ext')
        sentences, labels = itsm_tbl_clean()
        print("Encode the itsm text. This might take a while")
        embeddings = model.encode(sentences, show_progress_bar=True, convert_to_numpy=True)
        print("Store file on disc")
        data = {'sentences': sentences, 'embeddings': embeddings,'labels':labels}
        with open(embedding_cache_path, "wb") as fOut:
            pickle.dump(data, fOut)
    else:
        print("Load pre-computed embeddings from disc")
        with open(embedding_cache_path, "rb") as fIn:
            data = pickle.load(fIn)
    return data

if __name__ == '__main__':
    cache_data = embedding_cache()
    sentences = cache_data['sentences']
    embeddings = cache_data['embeddings']
    labels = cache_data['labels']

    print("Start clustering")
    start_time = time.time()
    # Two parameter to tune:
    # min_cluster_size: Only consider cluster that have at least 25 elements (30 similar sentences)
    # threshold: Consider sentence pairs with a cosine-similarity larger than threshold as similar
    clusters = community_detection(embeddings, threshold=0.95,init_max_size=400)
    f = open(f'{itsm_data_dir}/itsm_tbl_origin_example.txt','a')
    for i, cluster in enumerate(clusters):
        text = "Cluster {},{} Elements ##".format(i + 1, len(cluster))
        print(text)
        for sentence_id in cluster:
            text += f'{sentences[sentence_id]}#'

        for sentence_id in cluster:
            text += f'#{labels[sentence_id]}'
        f.write(text + '\n')
    f.close()
    print("Clustering done after {:.2f} sec".format(time.time() - start_time))
