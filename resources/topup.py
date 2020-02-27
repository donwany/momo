from flask import request, jsonify
from flask_restful import Resource

from common.util import getNetworkName, verifyCredentials, cashWithUser, updateAccount, transaction_id, date_time, \
    generateReturnDictionary, transactionFee

from common.config import app, mail, api, mongo
# _, mongo,_,_ = flask_run()

class TopUp(Resource):
    def post(self):
        # get json data
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        money = postedData["amount"]
        phone = postedData["fromPhone"]
        network = getNetworkName(phone)

        retJson, error = verifyCredentials(phone, password)
        if error:
            return jsonify(retJson)

        if money <= float(0):
            return jsonify(generateReturnDictionary(304, "The money amount entered must be greater than 0", "FAILURE"))

        cash = cashWithUser(phone)
        # Transaction fee
        fees = transactionFee(money)
        money = round(money - fees, 2)

        # Add transaction fee to bank account
        bank_cash = cashWithUser("0240000000")
        updateAccount("0240000000", round(float(bank_cash + fees), 2))
        # Add remaining money to user account
        updateAccount(phone, round(float(cash + money), 2))

        # Insert data into TopUp Collection
        mongo.db.TopUps.insert_one({
            "Username": username,
            "Amount": round(float(money), 2),
            "Network": network,
            "Phone": phone,
            "TransactionID": transaction_id(),
            "DateTime": date_time()
        })
        return jsonify(generateReturnDictionary(200, "Amount Added Successfully to account", "SUCCESS"))