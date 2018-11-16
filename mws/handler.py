from mws import mws
import pymysql
import xmltodict
import json
import logging
import sys
import os
import settings
import boto3
from utils import to_amazon_timestamp
from datetime import datetime, timedelta

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

client = boto3.client(
    'lambda',
    region_name='us-east-1'
)

def main(event, context):
    """
    This function testing
    """
    item_count = 0;

    #logger.info(event)
    #logger.info(context)

    try:
        orders_api = mws.Orders(os.environ['MWS_ACCESS_KEY'], os.environ['MWS_SECRET_KEY'], event['seller_id'], event['region'], auth_token = event['auth_token'])
        logger.info("SUCCESS: orders_api")

        service_status = orders_api.get_service_status()
        logger.info("SUCCESS: service_status")

        if(service_status.parsed.Status != 'GREEN'):
            logger.error("ERROR: MWS API is having problems")
            sys.exit()
        else:
            logger.info("SUCCESS: MWS API is GREEN")


        # updated 8h ago
        updated_after = to_amazon_timestamp(datetime.now() - timedelta(hours=8))

        response = orders_api.list_orders(marketplaceids=event['marketplaceids'], lastupdatedafter=updated_after, max_results='25')

        xml_data = xmltodict.parse(response.original, process_namespaces=True, namespaces={'https://mws.amazonservices.com/Orders/2013-09-01': None, '@xmlns': None})
        
        data = xml_data.get("ListOrdersResponse", {}).get("ListOrdersResult", {})
        
        orders = []
        orders.extend(data.get("Orders", {}).get("Order", []))

        with conn.cursor() as db:
            for order in orders:
                item_count += 1
                logger.debug("GOT ORDER %s", (order['SellerOrderId']))

                number_of_rows = db.execute('SELECT `id`, `syncronized`, `failed` FROM `orders` WHERE `seller_id` = %s AND `seller_order_id` = %s AND `order_status` = %s', (event['seller_id'], order['SellerOrderId'], order['OrderStatus']))
                db_order = db.fetchone()

                if(db_order == None and number_of_rows == 0):
                    db.execute('INSERT INTO `orders` (`seller_id`, `seller_order_id`, `order_status`, `payload`, `created_at`, `updated_at`) values (%s, %s, %s, %s, NOW(), NOW());', (event['seller_id'], order['SellerOrderId'], order['OrderStatus'], json.dumps(order)))
                    id = db.lastrowid

                    logger.info("SUCCESS: NEW ORDER %s", (id))
                    call_webhook(id, url = event.get('url'))
                elif(db_order != None and db_order[1] == 0 and db_order[2] <= 3):
                    logger.info("SUCCESS: EXISTING ORDER %d BUT NOT SYNCED", (db_order[0]))
                    call_webhook(db_order[0], url = event.get('url'))
                else:
                    logger.info("SUCCESS: EXISTING ORDER %d", (db_order[0]))

        logger.info("SUCCESS: COMPLETED CYCLE")

    except Exception as e:
        logger.error(sys.exc_info()[-1].tb_lineno)
        logger.error(type(e).__name__)
        logger.error(e)

    finally:
        return "Added %d items to MySQL table" %(item_count)

def call_webhook(id, url):

    client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:XXXXX:function:mws-webhook-dev-webhook',
        InvocationType='Event',
        LogType='None',
        Payload=json.dumps({"id": id, "url": url})
    )
