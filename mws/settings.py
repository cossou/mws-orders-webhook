import os

os.environ['DB_HOST'] = 'your_database.host.rds.amazonaws.com'
os.environ['DB_USER'] = 'TestUser123'
os.environ['DB_PASS'] = 'TestPass123'
os.environ['DB_PORT'] = 3306
os.environ['DB_DATABASE'] = 'mws-webhooks'
os.environ['MWS_ACCESS_KEY'] = 'YOURMWSACCESSKEY'
os.environ['MWS_SECRET_KEY'] = 'YOURMWSSECRET'
