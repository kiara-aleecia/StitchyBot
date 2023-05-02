import nltk as nltk
from nltk.corpus import sentiwordnet as swn
from allennlp.predictors.predictor import Predictor

class UserModel(object):

    def __init__(self, name):
        self.name = name
        self.likes = open((name + "_likes.csv"), "a")
        self.dislikes = open((name + "_dislikes.csv"), "a")

    def parse(self, statement):
        """
        Parses statement to find what it is that the user has strong opinions on
        """
        predictor = Predictor.from_path(
            "https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")
        results = predictor.predict(
            sentence = statement
        )
        for i in range(len(results['verbs'])):
            desc = results['verbs'][i]['description']
            arg1start = desc.find('ARG1: ')
            arg0start = desc.find('ARG0: ')

            if arg1start > -1:
                arg1end = arg1start + len('ARG1: ')
                arg1 = desc[arg1end: desc.find(']',arg1end)]
                return arg1
            elif arg0start > -1:
                arg0end = arg0start + len('ARG0: ')
                arg0 = desc[arg0end: desc.find(']', arg0end)]
                return arg0

    def addDislike(self, argument):
        """
        Adds what user dislikes to user model
        """
        self.dislikes.write(argument + ",")

    def addLike(self, argument):
        """
        Adds what user likes to user model
        """
        self.likes.write(argument + ",")

    def analyze(self, statement):
        """
        Analyzes statement to find likes or dislikes
        """
        neg = 0
        pos = 0
        tokens = statement.split()
        for token in tokens:
            syn_list = list(swn.senti_synsets(token))
            if syn_list:
                syn = syn_list[0]
                neg += syn.neg_score()
                pos += syn.pos_score()

        if neg >= 0.6:
            argument = self.parse(statement)
            self.addDislike(argument)
        if pos >= 0.6:
            argument = self.parse(statement)
            self.addLike(argument)
    
    def addSkill(self, statement):
        """
        Adds to user's skill repository
        """
        skill = statement.split(' ')[2]
        third_word = statement.split(' ')[3]
        if third_word != 'now':
            skill = skill + third_word
        self.skills.write(skill + ",")