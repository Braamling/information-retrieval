__author__ = 'agrotov'

import itertools
import numpy as np
import lasagne
import theano
import theano.tensor as T
import time
import math
from itertools import count
import query
theano.config.floatX = 'float32'


BATCH_SIZE = 1000
NUM_HIDDEN_UNITS = 100
LEARNING_RATE = 0.00005
# LEARNING_RATE = 0.005
MOMENTUM = 0.95

POINTWISE = 0
PAIRWISE = 1
LISTWISE = 2


# TODO: Implement the lambda loss function
def lambda_loss(output, lambdas):
    x = T.dot(output, lambdas)
    return x

class LambdaRankHW:

    NUM_INSTANCES = count()

    def __init__(self, feature_count, type=PAIRWISE):
        self.feature_count = feature_count
        self.rank_type = type
        self.output_layer = self.build_model(feature_count, 1, BATCH_SIZE)
        self.iter_funcs = self.create_functions(self.output_layer)

    def build_model(self,input_dim, output_dim,
                    batch_size=BATCH_SIZE):
        """Create a symbolic representation of a neural network with `intput_dim`
        input nodes, `output_dim` output nodes and `num_hidden_units` per hidden
        layer.

        The training function of this model must have a mini-batch size of
        `batch_size`.

        A theano expression which represents such a network is returned.
        """
        print "input_dim",input_dim, "output_dim",output_dim
        l_in = lasagne.layers.InputLayer(
            shape=(batch_size, input_dim),
        )

        l_hidden = lasagne.layers.DenseLayer(
            l_in,
            num_units=200,
            nonlinearity=lasagne.nonlinearities.tanh,
        )

        l_out = lasagne.layers.DenseLayer(
            l_hidden,
            num_units=output_dim,
            nonlinearity=lasagne.nonlinearities.linear,
        )

        return l_out

    # Create functions to be used by Theano for scoring and training
    def create_functions(self, output_layer,
                          X_tensor_type=T.matrix,
                          batch_size=BATCH_SIZE,
                          learning_rate=LEARNING_RATE, momentum=MOMENTUM, L1_reg=0.0000005, L2_reg=0.000003):
        """Create functions for training, validation and testing to iterate one
           epoch.
        """
        X_batch = X_tensor_type('x')
        y_batch = T.fvector('y')

        output_row = lasagne.layers.get_output(output_layer, X_batch, dtype="float32")
        output = output_row.T

        output_row_det = lasagne.layers.get_output(output_layer, X_batch, deterministic=True, dtype="float32")

        # TODO: Change loss function
        if self.rank_type is POINTWISE:
            # Point-wise loss function (squared error) - comment it out
            loss_train = lasagne.objectives.squared_error(output, y_batch)
            loss_train = loss_train.mean()
        elif self.rank_type in [PAIRWISE, LISTWISE]:
            # Pairwise loss function - comment it in
            self.bla1 = output
            self.bla2 = y_batch
            loss_train = lambda_loss(output, y_batch)
            loss_train = loss_train.mean()


        # TODO: (Optionally) You can add regularization if you want - for those interested
        # L1_loss = lasagne.regularization.regularize_network_params(output_layer,lasagne.regularization.l1)
        # L2_loss = lasagne.regularization.regularize_network_params(output_layer,lasagne.regularization.l2)
        # loss_train = loss_train.mean() + L1_loss * L1_reg + L2_loss * L2_reg

        # Parameters you want to update
        all_params = lasagne.layers.get_all_params(output_layer)

        # Update parameters, adam is a particular "flavor" of Gradient Descent
        updates = lasagne.updates.adam(loss_train, all_params, learning_rate=LEARNING_RATE)


        # Create two functions:

        # (1) Scoring function, deterministic, does not update parameters, outputs scores
        score_func = theano.function(
            [X_batch],output_row_det,
        )

        # (2) Training function, updates the parameters, outpust loss
        train_func = theano.function(
            [X_batch,y_batch], loss_train,
            updates=updates,
            allow_input_downcast=True
            # givens={
            #     X_batch: dataset['X_train'][batch_slice],
            #     # y_batch: dataset['y_valid'][batch_slice],
            # },
        )

        print "finished create_iter_functions"
        return dict(
            train=train_func,
            out=score_func,
        )

    """ 
    Subtract all combinations of pairs into one matrix with indices u, v
    w_1 and w_2 are vectors of size N.
        """
    def subtract_all_pairs(self, w_1, w_2):
        # Create a matrix with each vector repeated 
        W_1 = np.repeat(w_1, len(w_1)).reshape((len(w_1), len(w_1)))
        # Subtract the matrix by its vector
        return np.subtract(W_1, w_1)

    """ Rescores the original nn outputs with the calculated lambdas. """
    def rescore(self, scores, lambdas):
        # Because our scores are negative, we subtract the lambdas 
        # instead of adding them
        return scores - lambdas


    def score(self, query):
        feature_vectors = query.get_feature_vectors()
        scores = self.iter_funcs['out'](feature_vectors)
        return scores

    """
    We calculate the delta NDCG for each document pair as 1/log(i + 1) - 1/log(j + 1)
    """
    def calculate_delta_ndcg(self, scores):
        # Get the ranking from each scores and keep track of original indicies
        sorted_scores = sorted(enumerate(scores, 1), key=lambda x: -x[1])

        ranking = np.zeros(len(sorted_scores))

        for i, x in enumerate(sorted_scores):
            ranking[i] = x[0] 


        ndcg_components = 1 / np.log2(ranking + 1)

        delta_ndcg = self.subtract_all_pairs(ndcg_components, ndcg_components)
        # print delta_ndcg

        return delta_ndcg.T


    # TODO: Implement the aggregate (i.e. per document) lambda function
    def lambda_function(self, labels, scores, lambdarank=False):

        # TODO(bram) optimize label scoring with theano?

        # Calculate the label score by label_u - label_v (labels are 0 or 1)
        label_scores = self.subtract_all_pairs(labels, labels)

        # Calculate all f(u) - f(v) combinations
        nn_scores = self.subtract_all_pairs(scores, scores)

        # Calculate Lambda u,v
        denominator = 1 + np.exp(nn_scores)
        positive_label_scores = np.float32((0 < label_scores))
        lambda_uv = (.5 * (1 - label_scores)) - (1 / denominator)

        if lambdarank:
            delta_ndcg = self.calculate_delta_ndcg(scores)

            delta_ndcg = -delta_ndcg * label_scores

            lambda_uv = np.multiply(lambda_uv, delta_ndcg)

        # Subtract all positive label scored lambdas from the negative label scores lambdas
        lambda_docs = ((0 < label_scores) * lambda_uv) - ((0 > label_scores) * lambda_uv.T)

        # Aggregate each lambda
        # np.sum(lambda_docs, axis=1) + 100.0
        lambdas = np.sum(lambda_docs, axis=1)

        # if lambdarank:
        #     ndcg_1 = self.ndcg(enumerate(scores), labels, len(scores))
        #     scores = self.rescore(scores, lambdas)
        #     ndcg_2 = self.ndcg(enumerate(scores), labels, len(scores))
        #     lambdas = lambdas * (ndcg_2 - ndcg_1)

        return lambdas

    def compute_lambdas_theano(self, query, labels):
        scores = self.score(query).flatten()
        result = self.lambda_function(labels, scores[:len(labels)], self.rank_type is LISTWISE)
        return result

    def train_once(self, X_train, query, labels):

        # TODO: Comment out to obtain the lambdas
        # NOTETOSELF: Comment this in combination with 
        # the batch_train_loss to obtain point-wise
        if self.rank_type in [PAIRWISE, LISTWISE]:
            lambdas = self.compute_lambdas_theano(query,labels)
            lambdas.resize((BATCH_SIZE, ))


        resize_value = BATCH_SIZE
        if self.rank_type is POINTWISE:
            resize_value=min(resize_value,len(labels))
        X_train.resize((resize_value, self.feature_count),refcheck=False)

        # TODO: Comment out (and comment in) to replace labels by lambdas
        if self.rank_type is POINTWISE:
            batch_train_loss = self.iter_funcs['train'](X_train, labels)
        elif self.rank_type in [PAIRWISE, LISTWISE]:
            batch_train_loss = self.iter_funcs['train'](X_train, lambdas)

        return batch_train_loss

    # train_queries are what load_queries returns - implemented in query.py
    def train_with_queries(self, train_queries, num_epochs):
        try:
            now = time.time()
            for epoch in self.train(train_queries):
                if epoch['number'] % 1 == 0:
                    print("Epoch {} of {} took {:.3f}s".format(
                    epoch['number'], num_epochs, time.time() - now))
                    print("training loss:\t\t{:.6f}\n".format(epoch['train_loss']))
                    now = time.time()
                if epoch['number'] >= num_epochs:
                    break
        except KeyboardInterrupt:
            pass

    # train_queries are what load_queries returns - implemented in query.py
    def ndcgs(self, train_queries, n_ndcg):
        ndcgs = []
        for query in train_queries:
            # Retrieve all labels from a query
            labels = query.get_labels()
            # Score and assign internal doc number to each document
            scores = enumerate(self.score(query).flatten()[:len(labels)])

            ndcgs.append(self.ndcg(scores, labels, n_ndcg))
            if sum(ndcgs) < 0.0001:
                print(sum(labels))
                # print(scores)

        return ndcgs

    def ndcg(self, scores, labels, n_ndcg):
        # Sort the documents based on the output score
        ranking = sorted(scores, key=lambda x: -x[1])
        # Sort labels high to low
        sorted_labels = sorted(labels, key=lambda x: -float(x))
        
        # Discard all but the best n_ndcg documents
        ranking = ranking[:n_ndcg]

        dcg = 0
        max_dcg = 0.0
        for i, doc in enumerate(ranking, 1):
            # Calculate each part of the dcg part
            dcg += (2**labels[doc[0]] - 1) / math.log(i + 1, 2)
            max_dcg += (2**sorted_labels[i-1] - 1) / math.log(i + 1, 2)

        # Ignore queries where the max_dcg is 0.0
        # Weird hack because python is inconsistent with division by zero errors
        try:
            if math.isnan(dcg/max_dcg):
                return 0.0
        except ZeroDivisionError as e:
            return 0.0
        
        return dcg/max_dcg

    def train(self, train_queries):
        X_trains = train_queries.get_feature_vectors()

        queries = train_queries.values()

        for epoch in itertools.count(1):
            batch_train_losses = []
            random_batch = np.arange(len(queries))
            np.random.shuffle(random_batch)
            for index in xrange(len(queries)):
                random_index = random_batch[index]
                labels = queries[random_index].get_labels()
                batch_train_loss = self.train_once(X_trains[random_index], queries[random_index], labels)
                # self.bla1.shape.eval({'x' : X_trains[random_index], 'y': queries[random_index]})
                # self.bla2.shape.eval({'x' : X_trains[random_index], 'y': queries[random_index]})
                batch_train_losses.append(batch_train_loss)


            avg_train_loss = np.mean(batch_train_losses)
            yield {
                'number': epoch,
                'train_loss': avg_train_loss,
            }

