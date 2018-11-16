import pymysql
import requests
import json
import logging
import sys
import os
import settings

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(os.environ['DB_HOST'], port=os.environ['DB_PORT'], user=os.environ['DB_USER'], passwd=os.environ['DB_PASS'], db=os.environ['DB_DATABASE'], connect_timeout=5, autocommit=True)
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    sys.exit()

logger.info("SUCCESS: Connection to MySQL instance succeeded")

def main(event, context):
    """
    This function testing
    """

    try:
        with conn.cursor() as db:
            db.execute('SELECT `id`, `payload` FROM `orders` WHERE `syncronized` = 0 AND `failed` <= 3 AND `id` = %s', (event['id']))
            order = db.fetchone()

            if(order != None):

                logger.info("SUCCESS: Found row %s in DB", (event['id']))

                data = json.loads(order[1].decode('iso-8859-1').encode('utf8'))
                data['RowId'] = order[0]

                logger.info("SUCCESS: POST to %s", (event['url']))

                r = requests.post(event['url'], json=(data))

                if(r.status_code < 300):
                    logger.info("SUCCESS: Got HTTP Status Code: %s", (r.status_code))
                    db.execute('UPDATE `orders` SET `syncronized` = 1, `syncronized_at` = NOW() WHERE `id` = %s', (event['id']))
                else:
                    logger.info("ERROR: Got HTTP Status Code: %s", (r.status_code))
                    db.execute('UPDATE `orders` SET `failed` = `failed` + 1  WHERE `id` = %s', (event['id']))

            else:
                logger.info("ERROR: Row %s not found in DB", (event['id']))

    except Exception as e:
        logger.error('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    finally:
        return True

