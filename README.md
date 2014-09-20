Snail
=====

Snail is a database-driven order processing application written in Python to parse order spreadsheets, print pick lists, print packing slips, and print shipping labels. The name was inspired by my friend Troy Fraiser who suggested it as a joke.

Snail runs on top of a SQL Server database and interacts with it via ODBC. The Python module PyPyODBC is used to send queries to the database. The databse includes tabels for orders, items, packages, and shipments.

Snail is designed to import orders from multiple sources that use multiple formats. Merchant-specific parsing modules parse CSV order spreadsheets so that the orders can be loaded into the Snail database.

Orders in the Snail database can be viewed and edited using the Snail GUI application. The GUI is built with Tkinter and includes functionality for viewing unshipped orders and editing their corresponding items, packages, and shipments. The GUI also allows for the printing of pick lists, packing slips, and shipping labels.

Pick lists are exported in CSV format and display items and quantities needed for shipping orders. Packing slips are printed using Seagull Scientific's label printing software via command line. Shipping labels are printed using carrier-specific software (e.g. Endicia-Dazzle for USPS).