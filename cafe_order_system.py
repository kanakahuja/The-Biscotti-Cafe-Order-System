import json
from datetime import datetime

# Define the menu with prices in Rs.
menu = {
    "coffee": 250,
    "tea": 50,
    "sandwich": 200,
    "burger": 350,
    "fries": 100,
    "cake": 500
}

# Tax configuration
CGST_RATE = 0.09  # 9%
SGST_RATE = 0.09  # 9%
PACKAGING_COST = 20  # Flat packaging cost for takeout
DATA_FILE = 'orders.json'

class Order:
    def __init__(self, table_number, order_number):
        self.table_number = table_number
        self.order_number = order_number
        self.items = {}
        self.is_active = True
        self.include_packaging = False
        self.order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_items(self, items):
        for item_name, quantity in items.items():
            item_name = item_name.lower()  # Convert item name to lowercase
            if item_name in menu:
                if item_name in self.items:
                    self.items[item_name] += quantity
                else:
                    self.items[item_name] = quantity
                print(f"Added {quantity} {item_name}(s) to the order.")
            else:
                print(f"{item_name.capitalize()} is not available on the menu.")

    def calculate_subtotal(self):
        return sum(menu[item] * quantity for item, quantity in self.items.items())

    def calculate_taxes(self, subtotal):
        cgst = subtotal * CGST_RATE
        sgst = subtotal * SGST_RATE
        return cgst, sgst

    def calculate_total(self):
        subtotal = self.calculate_subtotal()
        cgst, sgst = self.calculate_taxes(subtotal)
        total = subtotal + cgst + sgst
        if self.include_packaging:
            total += PACKAGING_COST
        return total, cgst, sgst

    def close_order(self):
        self.is_active = False
        subtotal = self.calculate_subtotal()
        cgst, sgst = self.calculate_taxes(subtotal)
        total = subtotal + cgst + sgst
        if self.include_packaging:
            total += PACKAGING_COST

        print(f"Order #{self.order_number} for table {self.table_number} closed at {datetime.now()}.\n")
        print(f"Summary for Table {self.table_number}:")
        print(f"{'Item':<10}{'Quantity':<10}{'Unit Price (Rs.)':<15}{'Total (Rs.)':<10}")
        print("-" * 50)
        for item, quantity in self.items.items():
            unit_price = menu[item]
            total_price = unit_price * quantity
            print(f"{item.capitalize():<10}{quantity:<10}{unit_price:<15}{total_price:<10}")
        print("-" * 50)
        print(f"{'Subtotal (Rs.)':<35}{subtotal:<10}")
        print(f"{'CGST (9%) (Rs.)':<35}{cgst:<10}")
        print(f"{'SGST (9%) (Rs.)':<35}{sgst:<10}")
        if self.include_packaging:
            print(f"{'Packaging Cost (Rs.)':<35}{PACKAGING_COST:<10}")
        print("-" * 50)
        print(f"{'Net Total (Rs.)':<35}{total:<10}")

class Cafe:
    def __init__(self, num_tables=6):
        self.tables = {i: None for i in range(1, num_tables + 1)}
        self.orders = {}
        self.next_order_number = 1
        self.load_orders()

    def validate_table_number(self, table_number):
        if table_number < 1 or table_number > 6:
            print("Invalid table number. Enter a table number between 1 and 6.")
            return False
        return True

    def open_order(self, table_number):
        if not self.validate_table_number(table_number):
            return
        if self.tables[table_number] is None:
            order = Order(table_number, self.next_order_number)
            self.tables[table_number] = order
            self.orders[self.next_order_number] = order
            print(f"Opened new order for table {table_number} with Order #{self.next_order_number}.")
            self.next_order_number += 1
            self.save_orders()
        else:
            print(f"Table {table_number} already has an active order.")

    def add_items_to_order(self, table_number, items):
        if not self.validate_table_number(table_number):
            return
        order = self.tables[table_number]
        if order is not None and order.is_active:
            order.add_items(items)
            self.save_orders()
        else:
            print(f"No active order for table {table_number} to add items to.")

    def close_order(self, table_number):
        if not self.validate_table_number(table_number):
            return
        order = self.tables[table_number]
        if order is not None and order.is_active:
            while True:
                packaging_choice = input("Do you want packaging for this order (yes/no)? ").strip().lower()
                if packaging_choice in ["yes", "no"]:
                    order.include_packaging = (packaging_choice == "yes")
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
            order.close_order()
            self.tables[table_number] = None
            self.save_orders()
        else:
            print(f"No active order for table {table_number} to close.")

    def save_orders(self):
        with open(DATA_FILE, 'w') as f:
            json.dump({order_number: vars(order) for order_number, order in self.orders.items()}, f, indent=4)

    def load_orders(self):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                for order_number, order_data in data.items():
                    order = Order(order_data['table_number'], int(order_number))
                    order.items = order_data['items']
                    order.is_active = order_data['is_active']
                    order.include_packaging = order_data['include_packaging']
                    order.order_time = order_data['order_time']
                    self.orders[int(order_number)] = order
                    if order.is_active:
                        self.tables[order_data['table_number']] = order
                self.next_order_number = max(self.orders.keys(), default=0) + 1
        except FileNotFoundError:
            pass

    def view_past_orders(self):
        print("\nCompleted Orders:")
        for order_number, order in self.orders.items():
            if not order.is_active:
                print(f"Order #{order_number} for Table {order.table_number} placed on {order.order_time}")

    def view_order_summary(self, order_number):
        if order_number in self.orders:
            order = self.orders[order_number]
            if not order.is_active:
                print(f"\nSummary for Order #{order_number}:")
                print(f"Table: {order.table_number}")
                print(f"Date & Time: {order.order_time}")
                print(f"{'Item':<10}{'Quantity':<10}{'Unit Price (Rs.)':<15}{'Total (Rs.)':<10}")
                print("-" * 50)
                for item, quantity in order.items.items():
                    unit_price = menu[item]
                    total_price = unit_price * quantity
                    print(f"{item.capitalize():<10}{quantity:<10}{unit_price:<15}{total_price:<10}")
                subtotal = order.calculate_subtotal()
                cgst, sgst = order.calculate_taxes(subtotal)
                total = subtotal + cgst + sgst
                if order.include_packaging:
                    total += PACKAGING_COST
                    print(f"{'Packaging Cost (Rs.)':<35}{PACKAGING_COST:<10}")
                print("-" * 50)
                print(f"{'Subtotal (Rs.)':<35}{subtotal:<10}")
                print(f"{'CGST (9%) (Rs.)':<35}{cgst:<10}")
                print(f"{'SGST (9%) (Rs.)':<35}{sgst:<10}")
                print(f"{'Net Total (Rs.)':<35}{total:<10}")
            else:
                print(f"Order #{order_number} is still active.")
        else:
            print(f"Order #{order_number} not found.")

def parse_items_input(items_input):
    items = {}
    for item in items_input.split(','):
        item = item.strip()
        parts = item.split()

        # If item has no quantity, prompt for quantity
        if len(parts) == 1:
            item_name = parts[0].lower()
            while True:
                try:
                    quantity = int(input(f"Enter quantity for {item_name.capitalize()}: "))
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
        else:
            item_name, quantity = parts[0].lower(), int(parts[1])

        items[item_name] = quantity
    return items

def main():
    cafe = Cafe()
    while True:
        print("\nBiscotti Cafe Order System")
        print("1. Open order for a table")
        print("2. Add items to order")
        print("3. Close order")
        print("4. View completed orders")
        print("5. View order summary")
        print("6. Exit")
        choice = input("Enter your choice: ")

        try:
            if choice == '1':
                table_number = int(input("Enter table number (1-6): "))
                cafe.open_order(table_number)
            elif choice == '2':
                table_number = int(input("Enter table number (1-6): "))
                items_input = input("Enter items and quantities (e.g. Coffee 2, Tea 1): ")
                items = parse_items_input(items_input)
                cafe.add_items_to_order(table_number, items)
            elif choice == '3':
                table_number = int(input("Enter table number (1-6): "))
                cafe.close_order(table_number)
            elif choice == '4':
                cafe.view_past_orders()
            elif choice == '5':
                order_number = int(input("Enter order number: "))
                cafe.view_order_summary(order_number)
            elif choice == '6':
                print("Exiting the system. Thank you!")
                break
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Invalid input. Please enter valid data.")

if __name__ == "__main__":
    main()
