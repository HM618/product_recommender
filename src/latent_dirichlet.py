import pandas as pd
from recommender import make_tfidf_matrix, get_recommendations
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from nltk.corpus import stopwords
import numpy as np
from src.recommender import get_indices

def print_top_words(model, feature_names, n_top_words=10):
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()

def run_lda(df):
    '''Perform LDA on a given dataframe'''
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words=stopwords.words('english'))
    tf = tf_vectorizer.fit_transform(df)
    lda = LatentDirichletAllocation(batch_size=1000, n_jobs=-1, max_iter=5, learning_method='online', random_state=0)
    lda_matrix = lda.fit_transform(tf)
    # print("\nTopics in LDA model:")
    tf_feature_names = tf_vectorizer.get_feature_names()
    # print_top_words(lda, tf_feature_names)
    return lda_matrix

def get_lda_recs(df,col,row_indices, index_of_item,index_df,num=5):
    '''Get recommendations based on the LDA clustering'''
    matrix = run_lda(df[col].iloc[row_indices])
    cos_sim = cosine_similarity(matrix,matrix)
    item = df['vendor_variant_id'].iloc[index_of_item]
    print('LDA:\n')
    print("Recommending " + str(num) + " products similar to " + df['product_title'].iloc[index_of_item] + "...")
    print("-------")
    return get_recommendations(df,item,index_of_item,index_df, cos_sim)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)
    products = pd.read_csv('/Users/Kelly/galvanize/capstones/mod2/data/products_combo.csv')
    products.drop('Unnamed: 0',axis=1, inplace=True)
    row_indices, index_of_item, index_df = get_indices(products,20000)
    get_lda_recs(products,'combo',row_indices,index_of_item, index_df,num=10)
