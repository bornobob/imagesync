from imagesyncer import ImageSyncer

if __name__ == '__main__':
    ImageSyncer('[PATH HERE]', [{'reddit': '[REDDIT HERE]',
                                           'sort': 'all',
                                           'limit': 100,
                                           'min_score': 100}]).sync()
