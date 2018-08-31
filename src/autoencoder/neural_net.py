from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras import backend as K
from keras.models import load_model
import numpy as np
import glob
import cv2
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg') #for AWS only
import matplotlib.pyplot as plt
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def cnn_autoencoder():
    input_img = Input(shape = (256,256,3))

    #encoder
    encoded1 = Conv2D(128, (3, 3), activation='relu', padding='same')(input_img) #(256, 256, 128)
    pool1 = MaxPooling2D((2, 2), padding='same')(encoded1)
    encoded2 = Conv2D(64, (3, 3), activation='relu', padding='same')(pool1) # (128, 128, 64)
    pool2 = MaxPooling2D((2, 2), padding='same')(encoded2)
    encoded3 = Conv2D(32, (3, 3), activation='relu', padding='same')(pool2)
    encoded = MaxPooling2D((2, 2), padding='same')(encoded3)

    #decoder
    decoded1 = Conv2D(32, (3, 3), activation='relu', padding='same')(encoded)  #(64, 64, 64)
    up1 = UpSampling2D((2, 2))(decoded1)
    decoded2 = Conv2D(64, (3, 3), activation='relu',padding='same')(up1) # (128, 128, 128))
    up2 = UpSampling2D((2, 2))(decoded2)
    decoded3 = Conv2D(128, (3, 3), activation='relu',padding='same')(up2) # (128, 128, 128))
    up3 = UpSampling2D((2, 2))(decoded3)
    decoded = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(up3) #(256, 256, 3))

    autoencoder = Model(input_img, decoded)
    autoencoder.compile(optimizer='adadelta', loss='mean_squared_error')
    return autoencoder

def get_compressed_images(model,X,compressed_layer):
    '''Returns reshaped array of compressed images in prep for clustering.'''
    get_compressed_output = K.function([model.layers[0].input], [model.layers[compressed_layer].output])
    X_compressed = get_compressed_output([X])[0]
    X_compressed = X_compressed.reshape(X_compressed.shape[0],X_compressed.shape[1]*X_compressed.shape[2]*X_compressed.shape[3])
    return X_compressed

def cluster_compressed(X_train_compressed):
    kmeans = KMeans(n_clusters=10, n_jobs=-1)
    kmeans.fit(X_train_compressed)

    labels = kmeans.labels_
    return kmeans, labels

def get_kmeans_rec(item_index, kmeans, og_X, num_recs,filepath=None):
    labels = kmeans.labels_
    cluster_label = kmeans.labels_[item_index]
    cluster_members = og_X[labels == cluster_label]
    indices = np.random.choice(len(cluster_members), num_recs)
    recs = cluster_members[indices]
    return recs

    #show recs
    for rec, i in zip(recs,range(num_recs)):
        plt.imshow(rec.reshape(256,256,3))
        if filepath:
            plt.savefig('{}rec{}.png'.format(filepath,i))
            plt.imshow(og_X[item_index].reshape(256,256,3))
            plt.savefig('{}chosen.png'.format(filepath))

def plot_elbow(X_train_compressed,filename=None):
        distortions = []
        K = range(1,20)
        for k in K:
            kmeans = KMeans(n_clusters=k,max_iter=10, n_jobs=-1)
            kmeans.fit(X_train_compressed)
            distortions.append(kmeans.inertia_)

        # Plot the elbow
        plt.plot(K, distortions)
        plt.grid(True)
        plt.xlabel('k')
        plt.ylabel('Distortion')
        plt.title('The Elbow Method showing the optimal k')
        if filename:
            plt.savefig(filename)

if __name__ == '__main__':
    X_train = np.array([cv2.imread('{}'.format(file)) for file in glob.glob('data/train/*.png')])
    X_train = X_train.reshape(-1, 256, 256, 3)
    X_train = X_train / np.max(X_train)

    X_test = np.array([cv2.imread('{}'.format(file)) for file in glob.glob('data/test/*.png')])
    X_test = X_test.reshape(-1,256,256,3)
    X_test = X_test/ np.max(X_test)

    X_val = np.array([cv2.imread('{}'.format(file)) for file in glob.glob('data/val/*.png')])
    X_val = X_val.reshape(-1,256,256,3)
    X_val = X_val/ np.max(X_val)

    # use for fitting new autoencoder
    autoencoder = cnn_autoencoder()
    autoencoder.fit(X_train,X_train, epochs=6, validation_data=(X_test, X_test))
    autoencoder.save('models/autoencoder5.h5')
    # use to load previous fit autoencoder
    autoencoder = load_model('models/autoencode5.h5')
    restored_imgs = autoencoder.predict(X_val)
    #
    indices = np.random.choice(len(restored_imgs),5)
    for i in indices:
        plt.imshow(X_val[-i].reshape(256, 256,3))
        plt.savefig('images/restored_test5/test{}'.format(i))

        plt.imshow(restored_imgs[-i].reshape(256, 256,3))
        plt.savefig('images/restored_test5/restored{}'.format(i))

    X_train_compressed = get_compressed_images(autoencoder,X_train,6)
    kmeans, train_labels = cluster_compressed(X_train_compressed)
    item_index = np.random.choice(len(X_train))
    get_kmeans_rec(item_index,kmeans,X_train,5, 'images/rec_test5/')
    with open('model.pkl', 'wb') as f:
    # Write the
     model to a file.
    pickle.dump(model, f)
