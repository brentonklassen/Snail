from main import Snail
s = Snail()

print("Snail v" + s.version)

while True:
    print("\nWhat would you like to do?")
    print("1. Check Dance Shoes Online")
    print("2. Check Betafresh")
    print("3. Check Lighttake")
    print("4. Update db")
    print("5. Display unshipped packages")
    print("6. Print today's unshipped packing slips")
    print("7. Export today's pick list")
    print('8. Edit order')
    print("9. Quit")
    response = input("Choice: ")

    if response == "1":
        s.importDSOL()

    elif response == "2":
        s.importBetafresh()

    elif response == '3':
        s.importLTM()

    elif response == "4":
        s.updateDatabase()

    elif response == "5":
        s.displayUnshippedPackages()                

    elif response == "6":
        s.printPackingSlips()

    elif response == '7':
        s.exportTodaysPickList()

    elif response == '8':
        s.editOrder()

    elif response == '9':
        if s.quitSnail(): break

    else:
        print('\nInvalid selection...')
