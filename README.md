# MWS Orders Webhooks

Using AWS Lambda to fire webhooks on new MWS Orders. 

The Lambda functions use [Serverless Framework](https://serverless.com/). 
Functions programmed in Python 2.7

## Repositories folders (Lambda functions):

### MWS (Collects MWS Orders to DB)

Recovers new orders from MWS via API on a schedule basis. 

### WEBHOOK (Fires a webhook)

Fires the webhook to a custom URL with the info from the order.

## SQL 

MySQL 5.7.21 (RDS instance).

See the [orders.sql](orders.sql) to create the *orders* table.

# Installation

- Grab your MWS Seller ID and Auth Token in your account.
- Install serverless globally `npm install serverless -g`
- Create the MySQL RDS database called 'mws-webhooks' and a table [orders](orders.sql).
- Deploy the Lambda Functions using `serverless deploy` command.
- Create a schedule (5 minutes) CloudWatch rule to call the mws-orders function.
- In the input payload choose JSON `{"region":"UK","seller_id":"XXXXXXXXXXXXXX","auth_token":"amzn.mws.your-token","marketplaceids":["A1F83G8C2ARO7P","A1PA6795UKMFR9","A1RKKUPIHCS9HS","A13V1IB3VIYZZH","APJ6JRA9NG5V4"],"url":"https://some-url-to-catch-the-webhook"}`
