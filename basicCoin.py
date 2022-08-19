#basic blockchain

import datetime
import hashlib
import json
import flask
from flask import Flask,jsonify
import requests
from uuid import uuid4
from urllib.parse import urlparse
#blockchain class

class Blockchain:
    def __init__(self):
        self.chain=[]
        self.transactions=[]
        self.create_block(proof = 1,prev_hash='0')
        self.nodes=set()
        
    def create_block(self,proof,prev_hash):
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'transactions':self.transactions,
               'prev_hash':prev_hash}
        self.chain.append(block)
        self.transactions=[]
        return block
    
    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,prev_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_value=hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_value[:4]=='0000':
                check_proof=True
            else:
                new_proof +=1
        return new_proof
    
    def hash(self,block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        hashval=hashlib.sha256(encoded_block).hexdigest()
        return hashval
    
    def is_chain_valid(self,chain):
        prev_block=chain[0]
        block_index=1
        while block_index < len(chain):
            block=chain[block_index]
            proof=block['proof']
            prev_proof=prev_block['proof']
            hash_value=hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_value[:4]!='0000':
                return False
            if block['prev_hash']!=self.hash(prev_block):
                return False
            prev_block=block
            block_index += 1
        return True 

    def add_transaction(self,sender,reciever,amount):
        transaction={'sender':sender,
                     'reciever':reciever,
                     'amount':amount}
        self.transactions.append(transaction)
        prev_block=self.get_prev_block()
        return prev_block['index'] + 1 
    
    def add_node(self,address):
        parsed_address=urlparse(address)
        self.nodes.add(parsed_address.netloc)
        
    #nodes are identified by url address    
    def replace_chain(self):
        longestchain=None
        maxlength=len(self.chain)
        network=self.nodes
        for node in network:
            response=requests.get(f'http://{node}/get_chain')
            if response.staus_code==200:
                length=response.json['length']
                chain=response.json['chain']
                if length>maxlength and self.is_chain_valid(chain):
                    maxlength=length
                    longestchain=chain
        if longestchain:
            self.chain=longestchain
            return True
        return False

#create web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#create blockchain
blockchain1 = Blockchain()

#mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block=blockchain1.get_prev_block()
    prev_proof=prev_block['proof']
    proof=blockchain1.proof_of_work(prev_proof)
    prev_hash=blockchain1.hash(prev_block)
    block=blockchain1.create_block(proof, prev_hash)
    respone={'message':'Congratulations you have just mined a new block',
             'index':block['index'],
             'timestamp':block['timestamp'],
             'proof':block['proof'],
             'prev_hash':block['prev_hash']}
    return jsonify(respone) , 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response={'chain':blockchain1.chain,
             'length':len(blockchain1.chain)}
    
    return jsonify(response) , 200

@app.route('/check_chain', methods=['GET'])
def check_chain():    
    valid=blockchain1.is_chain_valid()
    if valid==True:
        response={'message':'The blockchain is valid'}
    else:
        response={'message':'The blockchain is not valid'}
    return jsonify(response) , 200