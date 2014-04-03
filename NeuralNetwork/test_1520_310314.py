__author__ = 'Martinus Wilhelmus Tegelaers'

from pybrain.structure import FeedForwardNetwork
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection
from pybrain.structure import BiasUnit
from pybrain.tools.xml import NetworkWriter
from pybrain.datasets import ClassificationDataSet

from pybrain.supervised.trainers import BackpropTrainer
from pybrain.utilities import percentError


def read_dataset(path_to_file):
    data_set = ClassificationDataSet(900,
                                     nb_classes=4,
                                     class_labels=['Rectangle',
                                                   'Circle',
                                                   'Heart',
                                                   'Star'])
    return add_to_dataset(data_set, path_to_file)


def add_to_dataset(data_set, path_to_file):
    shape_map = {'r': [0],
                 'c': [1],
                 'h': [2],
                 's': [3]}

    with open(path_to_file, 'r') as raw_data:
        for p, line in enumerate(raw_data.read().split('\n')):
            print p
            shape, raw_features = line.split(':')
            features = map((lambda x: x == " True"), raw_features.split(','))
            data_set.appendLinked(features, shape_map[shape])
    return data_set

#=============================================================================
if __name__ == '__main__':
    hl1 = 150
    hl2 = 150

    # Initialising neural network.
    print "Initialising Neural Network..."
    neural_network = FeedForwardNetwork()
    # Layers
    input_layer = LinearLayer(900)
    hidden_layer_1 = SigmoidLayer(hl1)
    hidden_layer_2 = SigmoidLayer(hl2)
    output_layer = LinearLayer(4)

    neural_network.addInputModule(input_layer)
    neural_network.addModule(hidden_layer_1)
    neural_network.addModule(hidden_layer_2)
    neural_network.addOutputModule(output_layer)

    # Setting up connections between nodes.
    in_to_hidden_1 = FullConnection(input_layer, hidden_layer_1)
    hidden_1_to_hidden_2 = FullConnection(hidden_layer_1, hidden_layer_2)
    hidden_2_to_output = FullConnection(hidden_layer_2, output_layer)

    neural_network.addConnection(in_to_hidden_1)
    neural_network.addConnection(hidden_1_to_hidden_2)
    neural_network.addConnection(hidden_2_to_output)

    b = BiasUnit(name='bias')
    neural_network.addModule(b)

    neural_network.sortModules()
    print "done."
    print "-------------------------------------------"

    #-------------------------------------------------------------------------
    # Build dataset
    print "Building Dataset..."
    data_set = read_dataset("./oracle/ds1.txt")
    data_set = add_to_dataset(data_set, "./oracle/ds2.txt")
    data_set = add_to_dataset(data_set, "./oracle/ds3.txt")
    data_set = add_to_dataset(data_set, "./oracle/ds4.txt")
    data_set = add_to_dataset(data_set, "./oracle/ds5.txt")

    test_data, trainings_data = data_set.splitWithProportion(0.25)
    trainings_data._convertToOneOfMany()
    test_data._convertToOneOfMany()

    print "done."
    print "-------------------------------------------"

    print "Number of training patterns: ", len(trainings_data)
    print "Input and output dimensions: ", trainings_data.indim, trainings_data.outdim
    print "-------------------------------------------"

    print "Setting up training exercises..."
    trainer = BackpropTrainer(neural_network,
                              dataset=trainings_data,
                              momentum=0.15,
                              verbose=True,
                              weightdecay=0.,
                              learningrate=0.05)
    print "done."
    print "-------------------------------------------"

    current_best = 0
    for i in range(1000):
        trainer.trainEpochs(3)
        trnresult = percentError(trainer.testOnClassData(), trainings_data['class'])
        tstresult = percentError(trainer.testOnClassData(dataset=test_data), test_data['class'])
        print "epoch: %4d" % trainer.totalepochs, \
            "  train error: %5.2f%%" % trnresult, \
            "  test error: %5.2f%%" % tstresult
        print "-------------------------------------------"
        if tstresult > current_best and tstresult > 75:
            NetworkWriter.writeToFile(trainer.module,
                                      "network_" + str(hl1) + "_" + str(hl2) + "_" + str(tstresult) + ".xml")







