from imagesyncer import ImageSyncer

if __name__ == '__main__':
    # an example of how you could set it up hardcoded, you could also save this information in a json file.
    ImageSyncer('[PATH HERE]', [{'reddit': '[REDDIT HERE]',
                                 'time_filter': 'all',
                                 'limit': 100,
                                 'min_score': 100}]).sync()
