con_config = {
    'port': 3100,
    'database': {
        'url': 'mongodb://root:example@mongo:27017/notification_manager?authSource=admin',
        'options': {
            'connect': True,
            'serverSelectionTimeoutMS': 5000
        }
    },
    'redis': {
        'host': 'localhost',
        'port': '6379'
    }
}