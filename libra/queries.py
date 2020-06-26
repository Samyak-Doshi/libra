

#function imports for all query
from libra.query.nlp_queries import image_caption_query, generate_caption, predict_text_sentiment, text_classification_query, get_summary, summarization_query
from libra.query.classification_models import k_means_clustering, train_svm, nearest_neighbors, decision_tree
from libra.query.supplementaries import tune_helper, stats, generate_id
from libra.query.feedforward_nn import regression_ann, classification_ann, convolutional
from libra.query.dimensionality_red_queries import dimensionality_reduc
from libra.data_generation.grammartree import get_value_instruction
from libra.data_generation.dataset_labelmatcher import get_similar_column, get_similar_model
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
import warnings
import os


#supressing warnings for cleaner dialogue box
warnings.simplefilter(action='error', category=FutureWarning)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# function imports from other files

currLog = ""
counter = 0



#clears log when needed - currently not being used
def clearLog():
    global currLog
    global counter

    currLog = ""
    counter = 0


# logging function that creates hierarchial display of the processes of
# different functions. Copied into different python files to maintain
# global variables.
def logger(instruction, found="", slash=''):
    global currLog
    global counter
    if counter == 0:
        currLog += (" " * 2 * counter) + str(instruction) + str(found)
    elif instruction == "->":
        counter = counter - 1
        if slash == '|':
            currLog += (" " * 2 * counter) + slash + str(found)
        else:
            currLog += (" " * 2 * counter) + str(instruction) + str(found)
    else:
        # currLog += (" " * 2 * counter) + "|" + "\n"
        currLog += (" " * 2 * counter) + "|- " + str(instruction) + str(found)
        if instruction == "done...":
            currLog += "\n" + "\n"

    counter += 1
    if instruction == "->":
        print(currLog, end="")
    else:
        print(currLog)
    currLog = ""


# class to store all query information. Currently, old_models is not being used.
class client:
    def __init__(self, data):
        logger("creating object...")
        self.dataset = data
        logger("Loading dataset...")
        self.models = {}
        self.old_models = {}
        logger("done...")
        clearLog()

    # returns models with a specific string - currently deprecated, should not be used. 
    def get_models(self, model_requested):
        logger("Getting model...")
        return get_similar_model(model_requested, self.models.keys())
        clearLog()

    # param modelKey: string representation of the model to make prediction
    # param data: dataframe version of desired prediction set
    def predict(self, modelKey, data):
        modeldict = self.models[modelKey]
        data = modeldict['preprocesser'].transform(data)
        print(data)
        predictions = modeldict['model'].predict(data)
        if modeldict.get('interpreter'):
            predictions = modeldict['interpreter'].inverse_transform(
                predictions)
        return predictions

    def neural_network_query(self,
                             instruction,
                             mca_threshold=None,
                             drop=None,
                             preprocess=True,
                             test_size=0.2,
                             random_state=49,
                             epochs=50,
                             generate_plots=True,
                             callback_mode='min',
                             maximizer="val_loss",
                             save_model=False,
                             save_path=os.getcwd()):

        data = pd.read_csv(self.dataset)

        if preprocess:

            remove = get_similar_column(
                get_value_instruction(instruction), data)
            if (data[remove].dtype.name == 'object'):
                callback_mode = 'max'
                maximizer = "val_accuracy"
                self.classification_query_ann(
                    instruction,
                    mca_threshold=mca_threshold,
                    preprocess=preprocess,
                    test_size=test_size,
                    random_state=random_state,
                    epochs=epochs,
                    generate_plots=generate_plots,
                    callback_mode=callback_mode,
                    maximizer=maximizer,
                    save_model=save_model,
                    save_path=save_path)
            else:
                self.regression_query_ann(
                    instruction,
                    mca_threshold=mca_threshold,
                    preprocess=preprocess,
                    test_size=test_size,
                    random_state=random_state,
                    epochs=epochs,
                    generate_plots=generate_plots,
                    callback_mode=callback_mode,
                    maximizer=maximizer,
                    drop=drop,
                    save_model=save_model,
                    save_path=save_path)

    # single regression query using a feed-forward neural network
    # instruction should be the value of a column
    def regression_query_ann(
            self,
            instruction,
            drop=None,
            mca_threshold=None,
            preprocess=True,
            test_size=0.2,
            random_state=49,
            epochs=50,
            generate_plots=True,
            callback_mode='min',
            maximizer="val_loss",
            save_model=True,
            save_path=os.getcwd()):

        self.models['regression_ANN'] = regression_ann(
            instruction=instruction,
            mca_threshold=.25 if mca_threshold is None else mca_threshold,
            dataset=self.dataset,
            drop=drop,
            preprocess=preprocess,
            test_size=test_size,
            random_state=random_state,
            epochs=epochs,
            generate_plots=generate_plots,
            callback_mode=callback_mode,
            maximizer=maximizer,
            save_model=save_model,
            save_path=save_path)

    # query for multilabel classification query, does not work for
    # binaryclassification, fits to feed-forward neural network
    def classification_query_ann(
            self,
            instruction,
            mca_threshold=None,
            preprocess=True,
            callback_mode='min',
            drop=None,
            random_state=49,
            test_size=0.2,
            epochs=50,
            generate_plots=True,
            maximizer="val_loss",
            save_model=False,
            save_path=os.getcwd()):

        self.models['classification_ANN'] = classification_ann(
            instruction=instruction,
            dataset=self.dataset,
            mca_threshold=.25 if mca_threshold is None else mca_threshold,
            drop=drop,
            preprocess=preprocess,
            test_size=test_size,
            random_state=random_state,
            epochs=epochs,
            generate_plots=generate_plots,
            callback_mode=callback_mode,
            maximizer=maximizer,
            save_model=save_model,
            save_path=save_path)

    def kmeans_clustering_query(self,
                                preprocess=True,
                                generate_plots=True,
                                drop=None,
                                base_clusters=1):

        self.models['k_means_clustering'] = k_means_clustering(
            dataset=self.dataset,
            preprocess=preprocess,
            generate_plots=generate_plots,
            drop=drop,
            base_clusters=base_clusters)

    def svm_query(self,
                  instruction,
                  test_size=0.2,
                  kernel='linear',
                  preprocess=True,
                  drop=None,
                  cross_val_size=0.3):

        self.models['svm'] = train_svm(instruction,
                                       dataset=self.dataset,
                                       test_size=test_size,
                                       kernel=kernel,
                                       preprocess=preprocess,
                                       drop=drop,
                                       cross_val_size=cross_val_size)

    def nearest_neighbor_query(
            self,
            instruction=None,
            preprocess=True,
            drop=None,
            min_neighbors=3,
            max_neighbors=10):
        self.models['nearest_neigbor'] = nearest_neighbors(
            instruction=instruction,
            dataset=self.dataset,
            preprocess=preprocess,
            drop=drop,
            min_neighbors=min_neighbors,
            max_neighbors=max_neighbors)

    def decision_tree_query(
            self,
            instruction,
            preprocess=True,
            test_size=0.2,
            drop=None):

        self.models['decision_tree'] = decision_tree(instruction,
                                                     dataset=self.dataset,
                                                     preprocess=True,
                                                     test_size=0.2,
                                                     drop=None)

    def tune(self,
             model_to_tune,
             max_layers=10,
             min_layers=2,
             min_dense=32,
             max_dense=512,
             executions_per_trial=3,
             max_trials=1,
             activation='relu',
             loss='categorical_crossentropy',
             metrics='accuracy',
             epochs=10,
             objective='val_accuracy',
             seed=42,
             directory='my_dir'):

        self.models = tune_helper(
            model_to_tune=model_to_tune,
            dataset=self.dataset,
            models=self.models,
            max_layers=max_layers,
            min_layers=min_layers,
            min_dense=min_dense,
            max_dense=max_dense,
            executions_per_trial=executions_per_trial,
            max_trials=max_trials,
            activation=activation,
            loss=loss,
            metrics=metrics,
            epochs=epochs,
            objective=objective,
            seed=seed,
            directory=directory,
        )

    def stat_analysis(self, column_name="none", drop=None):
        stats(
            dataset=self.dataset,
            drop=drop,
            column_name=column_name
        )

        return

    def convolutional_query(self,
                            instruction=None,
                            read_mode=None,
                            new_folders=True,
                            image_column=None,
                            training_ratio=0.8):

        # storing values the model dictionary
        self.models["convolutional_NN"] = convolutional(
            instruction=instruction,
            read_mode=read_mode,
            data_path=self.dataset,
            new_folders=new_folders,
            image_column=image_column,
            training_ratio=training_ratio)

    # Sentiment analysis predict wrapper
    def predict_text_sentiment(self, text):
        return predict_text_sentiment(self=self, text=text)

    # sentiment analysis query
    def text_classification_query(self, instruction):

        # storing values the model dictionary
        self.models["Text Classification LSTM"] = text_classification_query(
            self=self, instruction=instruction)

    # Document summarization predict wrapper
    def get_summary(self, text):
        return get_summary(self=self, text=text)

    # text summarization query
    def summarization_query(self, instruction,
                            preprocess=True,
                            test_size=0.2,
                            random_state=49,
                            epochs=1,
                            generate_plots=True):

        self.models["Document Summarization"] = summarization_query(
            self=self, instruction=instruction)

    # Image caption prediction
    def generate_caption(self, image):
        caption = generate_caption(self=self, image=image)
        return ' '.join(caption[:len(caption) - 1])

    # Image Caption query
    def image_caption_query(self, instruction, epochs, random_state,
                            preprocess=True,
                            generate_plots=True):
        self.models["Image Caption"] = image_caption_query(
            self=self,
            epochs=epochs,
            instruction=instruction,
            random_state=random_state,
            preprocess=preprocess,
            generate_plots=generate_plots)

    def dimensionality_reducer(self, instruction):
        dimensionality_reduc(instruction, self.dataset)

    def show_plots(self, model):
        print(self.models[model]['plots'].keys())

    # shows the keys in the models dictionary
    def model_data(self, model):
        if model in self.models:
            data = [key for key in self.models[model].keys()]
            print(data)
        else:
            raise Exception(
                "The requested model has not been applied to the client.")

    # returns all operators applicable to the client's models dictionary
    def operators(self, model):
        defined = ['plots', 'accuracy', 'losses']
        operations = [
            func +
            "()" for func in self.models[model].keys() if func in defined]
        if len(operations) > 0:
            print(operations)
        else:
            raise Exception(
                "There are no built-in operators defined for this model. Please refer to the models dictionary.")

    # show accuracy scores for client's model

    def accuracy(self, model):
        if 'accuracy' in self.models[model].keys():
            return self.models[model]['accuracy']
        elif 'cross_val_score' in self.models[model].keys():
            return {'cross_val_score': self.models[model]['cross_val_score']}
        else:
            raise Exception("Accuracy is not defined for {}".format(model))

    # show losses for client's model
    def losses(self, model):
        if 'losses' in self.models[model].keys():
            return self.models[model]['losses']
        else:
            raise Exception("Losses are not defined for {}".format(model))


# Easier to comment the one you don't want to run instead of typing them
# out every time

newClient = client('/Users/palashshah/Desktop')
newClient.convolutional_query()
newClient.tune('convolutional_NN', epochs=1)
# newClient.neural_network_query("Model median house value")
# newClient = client('tools/data/structured_data/landslides_after_rainfall.csv').neural_network_query(instruction='Model distance',
# drop=['id', 'geolocation', 'source_link', 'source_name'])
