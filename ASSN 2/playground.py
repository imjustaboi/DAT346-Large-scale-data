#!/usr/bin/env python
#
# File: kmeans.py
# Author: Alexander Schliep (alexander@schlieplab.org)
#
#
from multiprocessing import Pool
from multiprocessing import Process, Queue, JoinableQueue
import logging
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
import time

# Kmeans algorithm:
#   pick k random centroids
#   datapoints get clustered to their closest centroid
#   move the centroids of each cluster to the cluster's center
#   repeat

# building blocks of K means:
    #

def generateData(n, c):
    # Generate n samples and assigned them to c classes
    logging.info(f"Generating {n} samples in {c} classes")
    X, y = make_blobs(n_samples=n, centers=c, cluster_std=1.7, shuffle=False,
                      random_state=2122)
    return X


def nearestCentroid(datum, centroids):
    # Take a datapoint and a list of centroids
    # Return index of closest centroid and smallest distance to the respective datapoint
    # norm(a-b) is Euclidean distance, matrix - vector computes difference
    # for all rows of matrix
    dist = np.linalg.norm(centroids - datum, axis=1)
    return np.argmin(dist), np.min(dist)


def func1(q1, N, data, centroids):
   for i in range(N):
       # Get index of closest centroid and closest distance
       cluster, dist = nearestCentroid(data[i], centroids)
       output = [i, cluster, dist]
       q1.put(output)

def func2():
    None

def kmeans(nP, k, data, nr_iter=100):
    # return total variation and list of centroids
    N = len(data)

    # Choose k random data points as centroids
    centroids = data[np.random.choice(np.array(range(N)), size=k, replace=False)]
    logging.debug("Initial centroids\n", centroids)

    N = len(data)




    # The cluster index: c[i] = j indicates that i-th datum is in j-th cluster
    c = np.zeros(N, dtype=int)

    logging.info("Iteration\tVariation\tDelta Variation")
    total_variation = 0.0

    # time
    t0 = 0
    t1 = 0

    for j in range(nr_iter):
        logging.debug("=== Iteration %d ===" % (j + 1))

        # Assign data points to nearest centroid
        variation = np.zeros(k)
        cluster_sizes = np.zeros(k, dtype=int)

        # multiprocessing vars
        processes = []
        nr_process = 1
        q1 = JoinableQueue()
        q2 = JoinableQueue()

        #{--------------------------Parallelizable--------------------------
        # start measure time for loop 1

        func1(q1, N, data, centroids)
        # stop measure time for loop 1

        #---------------------------Parallelizable--------------------------}
        while not q1.empty():

            start_t1 = time.time()
            result = q1.get()
            end_t1 = time.time()
            t0 += end_t1 - start_t1

            data_index = result[0]
            cluster_index = result[1]
            dist = result[2]

            c[data_index] = cluster_index
            cluster_sizes[cluster_index] += 1
            variation[cluster_index] += dist ** 2

            print("loop")



        delta_variation = -total_variation
        total_variation = sum(variation)
        delta_variation += total_variation
        logging.info("%3d\t\t%f\t%f" % (j, total_variation, delta_variation))

        # Recompute centroids
        centroids = np.zeros((k, 2))  # This fixes the dimension to 2

        #{--------------------------Parallelizable--------------------------
        # start measure time loop 2
        start_t2 = time.time()
        for i in range(N):
            centroids[c[i]] += data[i]
        centroids = centroids / cluster_sizes.reshape(-1, 1)
        end_t2 = time.time()
        # stop measure time loop 2
        t1 += end_t2 - start_t2
        #---------------------------Parallelizable--------------------------}

        logging.debug(cluster_sizes)
        logging.debug(c)
        logging.debug(centroids)



    return total_variation, c, [t0, t1]


def computeClustering(args):
    if args.verbose:
        logging.basicConfig(format='# %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='# %(message)s', level=logging.DEBUG)

    X = generateData(args.samples, args.classes)

    start_time = time.time()
    #
    # Modify kmeans code to use args.worker parallel threads
    total_variation, assignment, t_array = kmeans(args.workers, args.k_clusters, X, nr_iter=args.iterations)
    #
    #
    end_time = time.time()
    logging.info("Clustering complete in %3.2f [s]" % (end_time - start_time))
    print(f"Total variation {total_variation}")

    if args.plot:  # Assuming 2D data
        fig, axes = plt.subplots(nrows=1, ncols=1)
        axes.scatter(X[:, 0], X[:, 1], c=assignment, alpha=0.2)
        plt.title("k-means result")
        # plt.show()
        fig.savefig(args.plot)
        plt.close(fig)

    print("t1 = ", t_array[0], " | t2 = ", t_array[1], " | t3 = ", end_time-start_time)
    print((t_array[0] + t_array[1]) / (end_time-start_time))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compute a k-means clustering.',
        epilog='Example: kmeans.py -v -k 4 --samples 10000 --classes 4 --plot result.png'
    )
    parser.add_argument('--workers', '-w',
                        default='1',
                        type=int,
                        help='Number of parallel processes to use (NOT IMPLEMENTED)')
    parser.add_argument('--k_clusters', '-k',
                        default='3',
                        type=int,
                        help='Number of clusters')
    parser.add_argument('--iterations', '-i',
                        default='100',
                        type=int,
                        help='Number of iterations in k-means')
    parser.add_argument('--samples', '-s',
                        default='10000',
                        type=int,
                        help='Number of samples to generate as input')
    parser.add_argument('--classes', '-c',
                        default='3',
                        type=int,
                        help='Number of classes to generate samples from')
    parser.add_argument('--plot', '-p',
                        type=str,
                        help='Filename to plot the final result')
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Print verbose diagnostic output')
    parser.add_argument('--debug', '-d',
                        action='store_true',
                        help='Print debugging output')
    args = parser.parse_args()
    computeClustering(args)
