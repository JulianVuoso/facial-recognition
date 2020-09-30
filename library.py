
# imports used packages
from pathlib import Path
import numpy as np
import os
import glob

# saves the image given as a matrix in the correspondig dir
# face is a matrix of N x N 
# name is the name of the person on the image
# dir is the database path
def save_face(face, name, dir):

    # creates the directory if the path does not exist
    path = os.path.join(dir, name, 'faces')
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # counts the files on the path
    files_count = len(os.listdir(path))
	
    # saves the matrix as a vector
    np.save(path + str(files_count), face.flatten())


##################################################################


# creates the matrix A for eigenvals to calculate later
# also saves the mean and index list for later use
# dir, the path to the database
def create_A(dir):
    # create the matrix a transposed
    a = []
    index = []
    for face in glob.glob(dir + '/persons/*/*.npy'):
        a.append(np.load(face))
        index.append(face)
    
    # calculates mean between rows and saves mean and index
    m = np.mean(a, axis=0)
    np.save(dir + '/mean', m)
    np.save(dir + '/index', index)
    
    # substracts to each row the mean and returns transposed
    return np.transpose(np.subtract(a, m))


# calculates the eigenvalues and eigenvectos given a matrix
# returns touple (u, s), being u eigenvectors and s the eigenvalues
# TODO to be replaced with our function
def calculate_eigen(a, dir):
    u, s, vh = np.linalg.svd(np.dot(np.transpose(a), a), full_matrices=True)
    # u --> eigenvectors in 3 x 3 matrix, s --> eigenvalues in vector
   
    u = np.dot(a, u)
    for i in range(0, len(u[0])):
        u[:,i] = np.transpose(np.array(u[:,i]/np.linalg.norm(u[:,i], 2)))
    # u --> eigenvector matrix of the covariance, with ||u||=1
    # s --> eigenvalues in vector

    # saves to files the eigen values and vectors
    np.save(dir + '/eigenvector', u)
    np.save(dir + '/eigenvalues', s)
    return (u, s)

# fi is an N^2 vector, Fi = ri - Y
# eigenvectors is an N^2 x K, the K best eigenvectors
# returns omh = K vector with K weights
def calculate_weights(fi, eigenvectors):
    return np.dot(np.transpose(eigenvectors), fi)

# creates and saces the ohm space
# a the A matrix N^2 x M
# u the eigenvectors N^2 x K
# dir the dir to save
# returns the ohm space
def create_ohm_space(a, u, dir):
    o = []

    # for each col get the weights
    for i in range(0, len(a[0])):
        ohmi = calculate_weights(np.transpose(a)[i], u)
        o.append(ohmi)

    # calculate ohm space and save
    res = np.transpose(o)
    np.save(dir + '/ohm-space', res)
    return res


######################################################################


# ohm1 is a K vector with K weights
# ohm2 is a K vector with K weights
# eigenvalues is a K vector with K eigenvalues
# returns face space distance between ohm1 and ohm2
def vector_distance(ohm1, ohm2, eigenvalues):
    if (len(ohm1) != len(ohm2)):
        raise Exception("Vectors must have the same lengths")
    sum = 0
    for i in range(0, len(ohm1)):
        sum += (ohm1[i] - ohm2[i]) ** 2 / eigenvalues[i]
    return sum

# ohm is a K vector with K weights from a particular image
# dir the path for the ohm space and eigenvalues
# threshold is the max distance to recognize image
# returns image number recognized (minimum vector distance) 
#  or -1 if unknown
def face_space_distance(ohm_img, dir, threshold=float('Inf')):

    ohm_space = np.load(dir + '/ohm-space.npy')
    eigenvalues = np.load(dir + '/eigenvalues.npy')


    index = -1
    min_err = float('Inf')
    for i in range(0, len(ohm_space[0])):
        dist = vector_distance(ohm_img, ohm_space[:,i], eigenvalues)
        if (dist < threshold and dist < min_err):
            index = i
            min_err = dist
    print("Min error ",min_err)
    return index


# given an image and a dir calculates its ohm
# face the matrix of the image
# dir the direction of the mean and eigenvector to load
def get_ohm_image(face, dir):

    # loads mean already calculated and eigenvector
    m = np.load(dir + '/mean.npy')
    u = np.load(dir + '/eigenvector.npy')

    # substracts and returns the calculated weights
    return calculate_weights(np.subtract(face.flatten(), m), u)

# loads and gets the path of the index list
# index the index that matched the face
# dir the path to the list of indexes
def get_matching_path(index, dir):

    # loads the index list of the persons
    dir_list = np.load(dir + '/index.npy')

    # returns the corresponding path
    return dir_list[index]

