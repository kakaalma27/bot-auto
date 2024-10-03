from base.browser import Browser
from base.auth.getQuery import Query
from base.auth.getTdata import tData
from base.auth.getInitData import initData
from base.auth.getGradientData import tGradient
from base.px import notPixels
from base.roro import Kuroro
from base.gradient import gradient

def main_menu():
    browser = Browser()  # Default browser instance
    tdata_instance = tData(browser.browser)
    TGradient_instance = tGradient(browser.browser)
    bearer_instance = Query(browser.browser)
    initData_instance = initData(browser.browser)
    notPixels_instance = notPixels(browser.browser)
    Kuroro_instance = Kuroro(browser.browser)
    gradient_instance = gradient(browser.browser)
    proxies = TGradient_instance.load_active_proxies()

    while True:
        print("Telegram Automation by KERJA-RODI")
        print("1. Create Session from Tdata")
        print("2. Get initData using Session")
        print("3. Get Query using Session")
        print("4. Get Auth Gradient using user.txt")
        print("5. Not pixels using initData")
        print("6. Kuroro using Query")
        print("7. Exit")
        
        pilihan = input("Pilih opsi : ")

        try:
            if pilihan == "1":
                tdata_instance.run_get_session()
            elif pilihan == "2":
                initData_instance.run_get_initData()
            elif pilihan == "3":
                bearer_instance.run_get_Bearer()
            elif pilihan == "4":
                if proxies:
                    proxy_browser = Browser(proxy=proxies)
                    TGradient_instance = tGradient(proxy_browser.browser)
                    TGradient_instance.run_get_Gradient()
                else:
                    print("No proxies available, running without proxy.")
                    TGradient_instance.run_get_Gradient()
            elif pilihan == "5":
                notPixels_instance.mainNotPixels()
            elif pilihan == "6":
                Kuroro_instance.mainKuroro()
            elif pilihan == "7":
                print("Keluar dari program.")
                break
            else:
                print("Pilihan tidak valid. Silakan coba lagi.")
        except Exception as e:
            print(f"An error occurred: {e}")

    browser.close()

if __name__ == "__main__":
    main_menu()
