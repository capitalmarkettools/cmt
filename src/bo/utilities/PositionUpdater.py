'''
Created on Jul 23, 2013

@author: Capital Market Tools
'''
from src.models import Transaction, ModelPosition

class PositionUpdater(object):
    '''
    Class to update positions based on Transaction data
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self):
        #load all transactions that are not reflected in balance
        #loop over transactions
            #for each transaction load corresponding position
            # if there is no position create position and update
            #else update position
            #set flag on transactions that it's processed
            #save position
        transactions = Transaction.objects.filter(reflectedInPosition=False)
        for transaction in transactions:
            positions = transaction.relatedPositions()
            if len(positions) == 0:
                position = ModelPosition(portfolio=transaction.portfolio,
                                          positionType=transaction.positionType,
                                          ticker=transaction.ticker,
                                          asOf=transaction.transactionDate)
                position.amount = 0
                positions.append(position)
            for position in positions:
                transaction.updatePositionAmount(position)
                position.save()
            transaction.reflectedInPosition = True
            transaction.save()
            
def main():
    updater = PositionUpdater()
    updater.run()
if __name__ == "__main__":
    main()        