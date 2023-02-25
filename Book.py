import uuid
import Order


def u():
    return uuid.uuid4()


class Book:
    def __init__(self):
        
        """ the structure of the book (both bid and ask) is:
            [price, [Order(price, quantity, uid, typ),
                     Order(price, quantity, uid, typ),
                     Order(price, quantity, uid, typ)
                ]]
        
        """
        self.ask = []
        self.bid = []
        
    
    def __repr__(self):
        ask = self.ask[:5][::-1]
        bid = self.bid[:5]
        
        s = "ASK:\n"
        for el in ask:
            s += str(el[0]) + "\t\t" + str(self._calc_quantity(el[1])) + "\n"
            
        s += "---------\nBID:\n"
        for el in bid:
            s += str(el[0]) + "\t\t" + str(self._calc_quantity(el[1])) + "\n"
        
        return s
        
    
    def limit(self, price, quantity, uid, typ):
        """ Limit order (both bid and ask) """
        
        # creates an order object for better order handling
        new_order = Order(price, quantity, uid, typ)

        if new_order.typ == "bid":
            # BID SIDE
                    
            while len(self.ask) > 0 and new_order.price >= self.ask[0][0] and new_order.quantity != 0:
                # BUY-SIDE: in case in which liquidity is available
                # it checks:
                # 1) that the ask book is not empty
                # 2) that there is liquidity available at the required price
                # 3) that the order has not been completely fulfilled

                # quantity of the first available market
                q = self._calc_quantity(self.ask[0][1])
                
                if new_order.quantity >= q:
                    # if the order is bigger than the first market, it
                    # fulfills it and goes to the next
                    
                    new_order.edit(-q)
                    self.ask.pop(0)
                
                else:
                    # if it is smaller, the first market is enough to fulfill
                    # the order

                    while new_order.quantity > 0:
                        # goes through the orders of the first market until
                        # our order is completely fulfilled

                        # current order at hand
                        curr_ord = self.ask[0][1][0]
                        
                        if new_order.quantity >= curr_ord.quantity:
                            # if the first order of the market is smaller than
                            # ours, it is fulfilled and removed from the book
                            
                            self.ask[0][1].pop(0)
                            new_order.edit(-curr_ord.quantity)
                        
                        else:
                            # if it is bigger, part of it is fulfilled while
                            # ours is done
                            
                            curr_ord.edit(-new_order.quantity)
                            new_order.edit(-new_order.quantity)
                        
            if new_order.quantity > 0:
                # SELL-SIDE: if the order didn't find enough liquidity, it is
                # going to provide for it in the book
                
                # variable to keep track of whether the order price is already
                # on the book or not
                found = False
                
                for i, markets in enumerate(self.bid):
                    # to insert the new order, it iterates through the book  
                    
                    if markets[0] == new_order.price:
                        # if the price is already present

                        for j, old_orders in enumerate(markets[1]):
                            # iterates through the orders of this market to see
                            # if the uid is already present
                            
                            if old_orders.uid == new_order.uid:
                                # in this case you just need to edit the order
                                # object without touching the bid list
                                                        
                                self.bid[j][1][j].edit(new_order.quantity)
                                found = True
                                break

                        else:
                            # it means that the user has no order at this price

                            self.bid[i][1].append(new_order)
                            found = True

                if not found:
                    # if the price was not present in the book, a new market
                    # is created
                    
                    self.bid.append([new_order.price, [new_order]])
                        
                # sort the book
                self.bid = self._sort(self.bid, rev=True)
        
        else:
            # ASK SIDE

            while len(self.bid) > 0 and new_order.price <= self.bid[0][0] and new_order.quantity != 0:
                # BUY-SIDE: in case in which liquidity is available
                # it checks:
                # 1) that the bid book is not empty
                # 2) that there is liquidity available at the required price
                # 3) that the order has not been completely fulfilled
                
                # quantity of the first available market
                q = self._calc_quantity(self.bid[0][1])
                
                if new_order.quantity >= q:
                    # if the order is bigger than the first market, it
                    # fulfills it and goes to the next
                    
                    new_order.edit(-q)
                    self.bid.pop(0)
                
                else:
                    # if it is smaller, the first market is enough to fulfill
                    # the order
                    
                    while new_order.quantity > 0:
                        # goes through the orders of the first market until
                        # our order is completely fulfilled
                        
                        # current order at hand
                        curr_ord = self.bid[0][1][0]
                        
                        if new_order.quantity >= curr_ord.quantity:
                            # if the first order of the market is smaller than
                            # ours, it is fulfilled and removed from the book
                            
                            self.bid[0][1].pop(0)
                            new_order.edit(-curr_ord.quantity)
                        
                        else:
                            # if it is bigger, part of it is fulfilled while
                            # ours is done
                            
                            curr_ord.edit(-new_order.quantity)
                            new_order.edit(-new_order.quantity)
                    

            if new_order.quantity > 0:
                # SELL-SIDE: if the order didn't find enough liquidity, it is
                # going to provide for it in the book
                
                # variable to keep track of whether the order price is already
                # on the book or not
                found = False
                
                for i, markets in enumerate(self.ask):
                    # to insert the new order, it iterates through the book 
                    
                    if markets[0] == new_order.price:
                        # if the price is already present
                        
                        for j, old_orders in enumerate(markets[1]):
                            # iterates through the orders of this market to see
                            # if the uid is already present
                            
                            if old_orders.uid == new_order.uid:
                                # in this case you just need to edit the order
                                # object without touching the bid list     
                        
                                self.ask[j][1][j].edit(new_order.quantity)
                                found = True
                                break
                    
                        else:
                            # it means that the user has no order at this price
                            
                            self.ask[i][1].append(new_order)
                            found = True
                            
                if not found:
                    # if the price was not present in the book, a new market
                    # is created
                    self.ask.append([new_order.price, [new_order]])
                                                
                # sort the book
                self.ask = self._sort(self.ask)
        
        # to see the console
        print(self)
            
    def market(self, quantity, typ):
        """ Market order: it works by putting a limit order with the highest
            price in the book and then removing it after fullfillment """
        
        if typ == "bid":
            # BID SIDE
            
            highest_price = self.ask[-1][0]
            
            self.limit(highest_price, quantity, u(), typ)
            
        elif typ == "ask":
            # ASK SIDE
            
            lowest_price = self.ask[-1][0]
            
            self.limit(lowest_price, quantity, u(), typ)
        
    def remove(self):
        "Remove order"
        
        pass
    
    def _sort(self, l, rev=False):
        """ Sort the bid and ask lists """
        
        return sorted(l, key=lambda x: x[0], reverse=rev)
    
    def _calc_quantity(self, l):
        """ Given a list 'l' of orders, it calculates the total quantity """
        return sum(x.quantity for x in l)


    

b = Book()

b.limit(120, 10, u(), "bid")
b.limit(130, 10, u(), "ask")
b.limit(140, 10, u(), "ask")
b.limit(140, 10, u(), "ask")
b.limit(160, 10, u(), "ask")
b.limit(150, 10, u(), "ask")



    