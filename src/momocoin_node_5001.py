#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 02:25:52 2020

@author: momo
"""

# Module 2


import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
from ast import literal_eval

def printty(obj):
    """ 
    Pretty print objects
    """
    print (json.dumps(obj, indent=4))


# Part 1 Building my first blockchain

class Blockchain:
    def __init__(self):

        # Store information about the balance, public Address and socket
        self.node = {'socket': '127.0.0.1:5001',
                     'balance': 500,
                     'publicA': 'Ismael'

                     }
        self.chain = []
        self.transactions = []
        self.createBlock(proof=1, previousHash=0)
        self.nodes = []

    # To create a new block

    def createBlock(self,  proof, previousHash):
        block = {
            'index': len(self.chain) + 1,
            'hash': '00x000',
            'timestamps': str(datetime.datetime.now().timestamp()),
            'proof': proof,
            'previousHash': previousHash,
            'transactions': self.transactions,
        }
        self.transactions = []
        self.chain.append(block)
        return block

    # To get the previous_block
    def getPreviousBlock(self):
        return self.chain[-1]

    # Return the proof of work
    def proofOfWork(self, previousProof):
        # Initialize the new proof to 1
        newProof = 1
        checkProof = False
        while checkProof is False:
            # Take what you want to generate the hash but make sure to have the proof included
            # For format purpose we use the the method encode()
            hashOperation = hashlib.sha256(
                str(newProof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                newProof += 1
        return newProof

     # Encode and return the hash  of the entire block

    def hash(self, block):
        # Encode our block in the right format
        # here we take the entire block and we generate a hash
        encodeBlock = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encodeBlock).hexdigest()

   # Verify the validity of the chain

    def isChainValid(self, chain):
        #  The first block
        previousBlock = chain[0]

        # The index of the first block
        blockIndex = 1
        # self.loadChain()

        while blockIndex < len(chain):
            # The current block
            block = chain[blockIndex]
            # Verify the integrity of the chain's blocks hash
            if block['previousHash'] != self.hash(previousBlock):
                return False
            # Verify if each hash respect the difficulty difined in th proof of work
            previousProof = previousBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(
                str(proof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False
            previousBlock = block
            blockIndex += 1
        return True

    # Store the chain // Store the chain in the file blockchain.json

    def storeChain(self):
        with open(blockchainFile, 'w') as fichier:
            json.dump(str(self.chain), fichier)

    # Load  the chain // Load the chain from the file blockchain.json

    def loadChain(self):
        with open(blockchainFile, 'r') as fichier:
            loadedChain = json.load(fichier)
            self.chain = literal_eval(loadedChain)

    # Add  transaction

    def addTransaction(self, sender, receiver, amount):
        network = self.nodes  # Represent the different nodes in the blockchain

        # For each node we get his current chain
        '''
            To review , don't work as expected
        '''
        # -------------------------------- Permit to modify balance of orther node  for each transaction
        for node in network:
            printty(node["socket"])
            response = requests.get(f'http://{node["socket"]}/getChain')
            nodeInfo = requests.get(f'http://{node["socket"]}/getNodeInfo')
            if response.status_code == 200:
                if nodeInfo.json()['publicA'] == receiver:
                    # To review
                    requests.post(f'http://{node["socket"]}/modifyBalance',amount)
        # ---------------------------------

        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previousBlock = self.getPreviousBlock()
        # Determine the next Block that will receive the transaction similar to the pendent
        return previousBlock['index'] + 1

    # Add coin
    def addCoin(self, amount):
        blockchain.node['balance'] += amount
        return "reussi", 200

    # Add nodes
    def addNode(self, address):

        # use the url parse lib to parse the address
        # Permit to have a unique port for each node
        parseUrl = urlparse(address)
        node = {
            'socket': parseUrl.netloc,
            'balance': 0
        }
        self.nodes.append(node)
    # Get Node

    # replace chain for the consensus

    def replaceChain(self):
        network = self.nodes  # Represent the different nodes in the blockchain
        longestChain = None  # the longest chain
        maxLength = len(self.chain)

        # For each node we get his current chain
        for node in network:
            response = requests.get(f'http://{node["socket"]}/getChain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength = length  # replace with the maxlength
                    longestChain = chain  # replace with the longest chain
        # Verify if the chain has been updated | if it is not none
        if longestChain:
            self.chain = longestChain  # Update the chain to the longest chain
            return True
        return False


# Part 2 - Mining our blockchain
# Creating a web app
app = Flask(__name__)

# Creating an address for the node on port 5000
# We ceate the address for each node in order to send them momocoin whenever he mine a block

# Our first node address , remove all dashes -
nodeAddress = str(uuid4()).replace('-', '')
publicA = 'Mohamed'

# To correct this common error : 'Request' object has no attribute 'is_xhr' add
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a blockchain

blockchain = Blockchain()

# The file name for storing
blockchainFile = 'blockchain.json'

# Mining aa block


@app.route('/mineBlock', methods=['GET'])
def mineBlock():
    # The previous block
    previousBlock = blockchain.getPreviousBlock()

    # The previousProof
    previousProof = previousBlock['proof']
    if len(blockchain.transactions) < 10:
        response = {
            'message': 'Mining is impossible, the transaction lenght must be 10',
            'Current lenght': len(blockchain.transactions)
        }
        return jsonify(response), 400
    else:
    
        # To build a new block we must  have the proof and the previoushash
        proof = blockchain.proofOfWork(previousProof)
        previousHash = blockchain.hash(previousBlock)
        blockchain.addTransaction(sender=nodeAddress, receiver=blockchain.node['publicA'], amount=1)
        blockchain.node['balance'] += 1
        block = blockchain.createBlock(proof, previousHash)

        # Send the response
        response = {'message': 'Congratulation, you just mined a block',
                    'index': block['index'],
                    'timestamps': block['timestamps'],
                    'proof': block['proof'],
                    'previousHash': block['previousHash'],
                    'transactions': block['transactions']}
        return jsonify(response), 200


# Getting the full blockchain
@app.route('/getChain', methods=['GET'])
def getChain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Load the chain from the file
@app.route('/loadFile', methods=['GET'])
def loadFile():
    blockchain.loadChain()
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response)


# Store the chain from the file
@app.route('/storeFile', methods=['GET'])
def storeFile():
    blockchain.storeChain()
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response)


# Verify the validity
@app.route('/isValid', methods=['GET'])
def isValid():
    # blockchain.loadChain()
    isValid = blockchain.isChainValid(blockchain.chain)
    if isValid:
        response = {'message': 'All good . the blockchain is valid'}
    else:
        response = {
            'message': 'Mouston.  We have a problem . The blockchain is invalid'}
    return jsonify(response), 200


# Adding a new transaction to the blockchain
@app.route('/addTransaction', methods=['POST'])
def addTransaction():
    print("Route /addTransaction Adding transaction.... ")

    json = request.get_json()  # the file where are the transactions

    transactions_keys = ['receiver', 'amount']
    # Check if the three fields are present
    if not all(key in json for key in transactions_keys):
        response = {
            'error': 'Some elements of the transaction are missing or the format is not valid',
            'Valid format': '{receiver: string, amount: number}'
        }
        return jsonify(response), 400
    if len(blockchain.transactions) == 12:
        response = requests.get(f'http://{blockchain.node["socket"]}/getChain')
        return jsonify(response), 200
    else:
        # Check if the node have enougth money to send
        if blockchain.node['balance'] < json['amount']:
            return 'You don\'t have enough to send ', 400
        index = blockchain.addTransaction(
            nodeAddress, json['receiver'], json['amount'])
        # Decrease his balance
        blockchain.node['balance'] -= json['amount']
        response = {
            'message': f'This transaction will be added to block {index}'}
        return jsonify(response), 201



# Part 3 Decentralizing our blockchain

# Connect new nodes


@app.route('/connectNodes', methods=['POST'])
def connectNodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.addNode(node)
    response = {'message': 'All the nodes are now connected . The momocoin now contains the all list: ',
                'total_list': list(blockchain.nodes)}
    return jsonify(response), 201


# Replacing the chain by the longest
@app.route('/replaceChain', methods=['GET'])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {'message': 'The node had different chains so the chain was replaced by the longest',
                    'newChain': blockchain.chain}
    else:
        response = {'message': 'All good.  The blockchain is the largest one',
                    'actualChain': blockchain.chain}
    return jsonify(response), 200


# Get account balance
@app.route('/getAccount', methods=['GET'])
def getAccount():
    response = {'balance': blockchain.node['balance']}
    return jsonify(response), 200
# Get node info


@app.route('/getNodeInfo', methods=['GET'])
def getNodeInfo():
    response = {'socket': blockchain.node['socket'],
                'balance':  blockchain.node['balance'],
                'publicA':  blockchain.node['publicA']
                }
    return jsonify(response), 200


# Get Modify balance # To do Don't work as expected
@app.route('/modifyBalance', methods=['POST'])
def modifyBalance():
    amount = request.get_json()
    blockchain.addCoin(amount)
    response = {'modifyBalance': blockchain.node['balance']}
    return jsonify(response), 200


# Running the app
app.run(host='0.0.0.0', port=5001)
