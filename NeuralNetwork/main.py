from pybrain.structure import FeedForwardNetwork
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection

from pybrain.datasets import ClassificationDataSet

from pybrain.supervised.trainers import BackpropTrainer
from pybrain.utilities import percentError


def read_dataset(path_to_file):
    shape_map = {'r': [0],
                 'c': [1],
                 'h': [2],
                 's': [3]}

    data_set = ClassificationDataSet(400, nb_classes=4, class_labels=['Rectangle', 'Circle',
                                                                     'Heart', 'Star'])

    with open(path_to_file, 'r') as raw_data:
        for line in raw_data.read().split('\n'):
            shape, raw_features = line.split(':')
            features = map((lambda x: float(x)), raw_features.split(',')) #remove last empty line due to way dataset is build
            print "feature length: " + str(len(features))
            data_set.appendLinked(features, shape_map[shape])

    return data_set


#------------------------------------------------------------------------------------
if __name__ == '__main__':
    #--------------------------------------------------------------------------------
    # Initialising neural network.
    print "Initialising Neural Network"
    neural_network = FeedForwardNetwork()
    # Layers
    input_layer = LinearLayer(400)
    hidden_layer_1 = SigmoidLayer(120)
    hidden_layer_2 = SigmoidLayer(40)
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

    neural_network.sortModules()

    #--------------------------------------------------------------------------------
    # Build dataset
    print "Building Dataset"
    data_set = read_dataset("./data_zonder_streep.txt")
    test_data, trainings_data = data_set.splitWithProportion(0.1)

    #FIXME: what does this do
    trainings_data._convertToOneOfMany()
    test_data._convertToOneOfMany()

    print "Number of training patterns: ", len(trainings_data)
    print "Input and output dimensions: ", trainings_data.indim, trainings_data.outdim
    print "First sample (input, target, class):"
    print trainings_data['input'][0], trainings_data['target'][0], trainings_data['class'][0]

    trainer = BackpropTrainer(neural_network, dataset=trainings_data, momentum=0.1, verbose=True, weightdecay=0.01)

    for i in range(20):
        trainer.trainEpochs(5)
        trnresult = percentError(trainer.testOnClassData(), trainings_data['class'])
        tstresult = percentError(trainer.testOnClassData(dataset=test_data), test_data['class'])

        print "--------------------------------------------------------------"
        print "epoch: %4d" % trainer.totalepochs, \
            "  train error: %5.2f%%" % trnresult, \
            "  test error: %5.2f%%" % tstresult
