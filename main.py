from base.browser import Browser
from base.getQuery import Query
from base.getTdata import tData
from base.getInitData import initData
from base.px import notPixels
from base.roro import Kuroro

def main_menu():
    # Initialize the shared Browser instance
    browser = Browser()

    # Pass the shared browser instance to each class
    tdata_instance = tData(browser.browser)
    bearer_instance = Query(browser.browser)
    initData_instance = initData(browser.browser)
    notPixels_instance = notPixels(browser.browser)
    Kuroro_instance = Kuroro(browser.browser)

    while True:
        print("Telegram Automation by KERJA-RODI")
        print("1. Create Session from Tdata")
        print("2. Get initData using Session")
        print("3. Get Query using Session")
        print("4. Not pixels using initData")
        print("5. Kuroro using Query")
        print("6. Exit")
        
        pilihan = input("Pilih opsi : ")

        if pilihan == "1":
            tdata_instance.run_get_session()
        elif pilihan == "2":
            initData_instance.run_get_initData()
        elif pilihan == "3":
            bearer_instance.run_get_Bearer()
        elif pilihan == "4":
            notPixels_instance.mainNotPixels()
        elif pilihan == "5":
            Kuroro_instance.mainKuroro()
        elif pilihan == "6":
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

    # Close the browser after exiting the menu
    browser.close()

if __name__ == "__main__":
    main_menu()
