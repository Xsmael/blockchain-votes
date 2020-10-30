#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 02:25:52 2020

@author: momo
"""

#Module 2
 

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests 
from uuid import uuid4
from urllib.parse import urlparse



#Part 1 Building my first blockchain

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.createBlock(proof= 1, previousHash = 0)
        self.nodes = set()

    # To create a new block
        
    def createBlock(self,  proof, previousHash):
        block = {
                'index': len(self.chain) + 1,                
                'timestamps': str(datetime.datetime.now()),
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
    def proofOfWork(self,previousProof):
        # Initialize the new proof to 1
        newProof = 1
        checkProof = False
        while checkProof is False:
            #Take what you want to generate the hash but make sure to have the proof included
            #For format purpose we use the the method encode()
            hashOperation = hashlib.sha256(str(newProof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                newProof += 1
        return newProof
    def hash(self, block):
        # Encode our block in the rigth format 
        # here we take the entire block and we generate a hash 
        encodeBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodeBlock).hexdigest()
    
   # Verify the validity of the chain 
    def isChainValid(self, chain):
        #  The first block 
        previousBlock = chain[0]
        
        # The index of the first block
        blockIndex = 1
        
        while blockIndex < len(chain):
            # The current block 
            block = chain[blockIndex]
            #Verify the integrity of the chain's blocks hash
            if block['previousHash'] != self.hash(previousBlock):
                return False 
            #Verify if each hash respect the difficulty difined in th proof of work
            previousProof = previousBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(str(proof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False 
            previousBlock = block 
            blockIndex +=   1
        return True

    #Add  transaction 
    def addTransaction(self, sender, receiver, amount) :
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previousBlock = self.getPreviousBlock()
        return previousBlock['index'] + 1 
     
    #Add nodes 
    def addNode(self, address):        
        
        #use the url parse lib to parse the address
        # Permit to have a unique port for each node
        parseUrl = urlparse(address)
        self.nodes.add(parseUrl.netloc)
        
    #replace chain for the consensus
    def replaceChain(self):
        network = self.nodes #Represent the different nodes in the blockchain
        longestChain = None # the longest chain
        maxLength = len(self.chain)
        
        #For each node we get his current chain
        for node in network:
            response = requests.get(f'http://{node}/getChain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength = length # replace with the maxlength
                    longestChain = chain # replace with the longest chain
        # Verify if the chain has been updated | if it is not none
        if longestChain:
            self.chain = longestChain # Update the chain to the longest chain 
            return True
        return False
            
        
    
    
    
    
# Part 2 - Mining our blockchain 

# Creating a web app
app = Flask(__name__)

# Creating an address for the node on port 5000
# We ceate the address for each node in order to send them momocoin whenever he mine a block

nodeAddress = str(uuid4()).replace('-', '') # Our first node address , remove all dashes -
 
# To correct this common error : 'Request' object has no attribute 'is_xhr' add 
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#Creating a blockchain

blockchain = Blockchain()

# Mining aa block 

@app.route('/mineBlock', methods = ['GET'])

def mineBlock():
    #The previous block 
    previousBlock = blockchain.getPreviousBlock()
    
    #The previousProof
    previousProof = previousBlock['proof']
    
    #To build a new block we must  have the proof and the previoushash
    proof = blockchain.proofOfWork(previousProof)
    previousHash = blockchain.hash(previousBlock)
    blockchain.addTransaction(sender = nodeAddress, receiver = 'Mohamed', amount = 1)
    block = blockchain.createBlock(proof, previousHash)
    
    #Send the response 
    response = {'message': 'Congratulation, you just mined a block',
                 'index': block['index'],
                 'timestamps': block['timestamps'],
                 'proof': block['proof'],
                 'previousHash': block['previousHash'],
                 'transactions': block['transactions']}
    return jsonify(response), 200


# Getting the full blockchain

@app.route('/getChain', methods = ['GET'])
def getChain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Verify the validity 

@app.route('/isValid', methods = ['GET'])
def isValid():
    isValid = blockchain.isChainValid(blockchain.chain)
    if isValid:
        response = {'message': 'All good . the blockchain is valid'}
    else:
         response = {'message': 'Mouston.  We have a problem . The blockchain is invalid'}
    return jsonify(response), 200
        
# Adding a new transaction to the blockchain
@app.route('/addTransaction', methods = ['POST'])
def addTransaction():
    json = request.get_json() # the file where are the transactions
    
    transactions_keys = ['sender','receiver','amount'] 
    if not all (key in json for key in transactions_keys): # Check if the three fields are present
        return 'Some elements of the transaction are missing', 400
    index = blockchain.addTransaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201

# Part 3 Decentralizing our blockchain

# Connect new nodes 
@app.route('/connectNodes', methods = ['POST'])
def connectNodes():
    json = request.get_json() 
    nodes= json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.addNode(node)
    response = {'message': 'All the nodes are now connected . The momocoin now contains the all list: ',
                'total_list': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest


@app.route('/replaceChain', methods = ['GET'])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {'message': 'The node had different chains so the chain was replaced by the longest',
                    'newChain': blockchain.chain}
    else:
         response = {'message': 'All good.  The blockchain is the largest one',
                     'actualChain': blockchain.chain}
    return jsonify(response), 200
        


# Running the app

app.run(host ='0.0.0.0', port = 5001)