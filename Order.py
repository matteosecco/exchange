class Order:
    def __init__(self, price, quantity, uid, typ):
        # init object variables

        self.price = price
        self.quantity = quantity
        self.uid = uid
        if typ in ("bid", "ask"):
            self.typ = typ  # "bid" or "ask
        else:
            raise TypeError

    def __repr__(self):
        return "Order({}, {}, uid, {})".format(self.price, self.quantity, self.typ)
    
    def edit(self, q):
        self.quantity += q