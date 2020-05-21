import time
import datetime
import pyautogui
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from mysql_cryptomarketsdb import MySQLcryptomarketsDB
from selenium_networksetting import *
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# ++++++++++++++++++++ You need to update the following 3 variables ++++++++++++++++++++
# Student Name Abbr
g_sStudentNameAbbr = "al"  # You need to update this
# Your Username and Password for YellowBrick Market
g_sMarketUserName = "OrionStars"  # You need to update this
g_sMarketPassword = "sandiego"  # You need to update this
# You must register your own account in YellowBrick Market.
# If two students use the same username, the website will show the error message:
# "The account is logged in somewhere else"
# This error message will prevent you from scraping further. So use your own account.
# Make sure to keep anonymous when you sign up. Don't use real identity!
# ++++++++++++++++++++ You need to update the above 3 variables ++++++++++++++++++++++++
# No need to change anything else below
# Scraping frequency for 4 kinds of web pages
g_nScrapingFreqDaysProductDesc = 30  # days
g_nScrapingFreqDaysProductRating = 7  # days
g_nScrapingFreqDaysVendorProfile = 30  # days
g_nScrapingFreqDaysVendorRating = 7  # days
# market information
g_sMarketNameAbbr = "db"
# You need to provide the latest market URL by looking up the list in https://dark.fail
g_sMarketURL = "http://darkbayupenqdqvv.onion/"
g_nMarketGlobalID = 26
# local output data directory
# g_sOutputDirectoryTemp = "/home/rob/temp_scrapedhtml/"
g_sOutputDirectoryTemp = "/home/rob/Covid19/UndergroundMarkets/db/"
# time to wait for human to input CAPTCHA
g_nTimeSecToWait = 30 * 24 * 60 * 60  # 30 days
# set it True if you want to use the default username and password
g_bUseDefaultUsernamePasswd = False
g_bTakeScreenshotOrNot = False  # if True, it will take screenshots.

# Choose one of the categories. If you want to scrape new category, please look at the html source code
c1 = 'category/02164500-b00f-11e9-8b8a-6907ed514d60'  # Carded Items
c2 = 'category/183960e0-b010-11e9-aefb-77eff3685e85'  # Security & Hosting
c3 = 'category/395aad00-b00e-11e9-ad2a-f1b9db0180aa'  # Counterfeit Items
c4 = 'category/a0f5ca30-b00f-11e9-b247-abf90d62ea65'  # Services
c5 = 'category/aa3983c0-b00e-11e9-8e2a-c3ca29964ed4'  # Digital Products
c6 = 'category/c0c5d3f0-b009-11e9-aea4-712111355e3c'  # Fraud
c7 = 'category/de55f160-b00f-11e9-b35e-33a425dd7b01'  # Other Listings
c8 = 'category/dff98750-b00e-11e9-b8fd-3190ad2a874f'  # Jewles & Gold
c9 = 'category/ec94d1a0-b009-11e9-b912-d148462df001'  # Drugs
c10 = 'category/ed6c2ca0-b00f-11e9-9397-b98faaa936e4'  # Software & Malware
c11 = 'category/f4120b60-b00d-11e9-8e5c-632a53ce2a83'  # Guides & Tutorials
# g_catCodes = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11]
g_catCodes = [c1]
g_startIndexes = {c1: 1, c2: 1, c3: 1, c4: 1, c5: 1, c6: 1, c7: 1, c8: 1, c9: 1, c10: 1, c11: 1}


def Login(aBrowserDriver):
    aBrowserDriver.get(g_sMarketURL)
    aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
    aWaitNextPage.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'http://darkbayupenqdqvv.onion/signup')]")))
    # fill the username and password
    aInputElementUsername = aBrowserDriver.find_element_by_xpath("//input[contains(@name,'username')]")
    aInputElementUsername.send_keys(g_sMarketUserName)
    aInputElementPassword = aBrowserDriver.find_element_by_xpath("//input[contains(@name,'password')]")
    aInputElementPassword.send_keys(g_sMarketPassword)
    aInputElementCaptcha = aBrowserDriver.find_element_by_xpath("//input[contains(@name,'captcha')]")
    aInputElementCaptcha.send_keys('')
    # Waits till you login
    aWaitNextPage.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'http://darkbayupenqdqvv.onion/profile/cart')]")))


def NavigateToOnePage(aBrowserDriver, sPageLink):
    # "aBrowserDriver" : web driver
    # "sPageLink" : the link of the web page
    while True:
        aBrowserDriver.get(sPageLink)
        aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
        aWaitNextPage.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'http://darkbayupenqdqvv.onion/profile/cart')]")))
        # Get the page title
        sPageTitle = aBrowserDriver.title
        if '(Privoxy@localhost)' in sPageTitle:
            # 502 - No server or forwarder data received (Privoxy@localhost)
            # 503 - Forwarding failure (Privoxy@localhost)
            # 504 - Connection timeout (Privoxy@localhost)
            aWaitNextPage = WebDriverWait(aBrowserDriver, g_nTimeSecToWait)  # Wait up to x seconds (30 days).
            aWaitNextPage.until(EC.element_to_be_clickable((By.LINK_TEXT, "Privoxy")))
        else:
            break
        # Sleep for a while and then go to next page
        time.sleep(1)
        # Wait for 1 second before scraping next page.
    time.sleep(1)


def NotifyMe(message='DarkBay script Failed!!!', subject='Scraper Alert.'):
    myMailId = 'chickenfrybiryani@gmail.com'
    password = open('password.txt', 'r').read()
    recipients = ['4438089584@mms.att.net']
    # recipients.append('aravuru1@student.gsu.edu')
    msgMultiPart = MIMEMultipart()
    msgMultiPart['from'] = myMailId
    msgMultiPart['To'] = ', '.join(recipients)
    msgMultiPart['Subject'] = subject
    msgMultiPart.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(myMailId, password)
    server.sendmail(myMailId, recipients, msgMultiPart.as_string())
    server.quit()


# The main function, the entry point
if __name__ == '__main__':
    try:
        # query the SQL server to retrieve some basic information
        aMySQLcrptmktDB = MySQLcryptomarketsDB()
        aMySQLcrptmktDB.m_sStudentNameAbbr = g_sStudentNameAbbr
        aMySQLcrptmktDB.m_sMarketNameAbbr = g_sMarketNameAbbr
        aMySQLcrptmktDB.m_nScrapingFreqDaysProductDesc = g_nScrapingFreqDaysProductDesc
        aMySQLcrptmktDB.m_nScrapingFreqDaysProductRating = g_nScrapingFreqDaysProductRating
        aMySQLcrptmktDB.m_nScrapingFreqDaysVendorProfile = g_nScrapingFreqDaysVendorProfile
        aMySQLcrptmktDB.m_nScrapingFreqDaysVendorRating = g_nScrapingFreqDaysVendorRating
        aMySQLcrptmktDB.MySQLQueryBasicInfor()
        g_nMarketGlobalID = aMySQLcrptmktDB.m_nMarketGlobalID
        if g_bUseDefaultUsernamePasswd:
            g_sMarketUserName = aMySQLcrptmktDB.m_sMarketUserName
            g_sMarketPassword = aMySQLcrptmktDB.m_sMarketPassword
        # Setup Firefox browser for visiting .onion sites through Tor (AWS proxy)
        aBrowserDriver = selenium_setup_firefox_network()
        # Visit the YellowBrick Market site and Login
        Login(aBrowserDriver)
        print("Login successful")

        # Visit each category in the category list
        for cat_code in g_catCodes:
            sCat_Link = g_sMarketURL + cat_code
            NavigateToOnePage(aBrowserDriver, sCat_Link)
            AllPages = aBrowserDriver.find_elements_by_xpath("//a[contains(@href,'?page=')]")
            LastPageLink = AllPages[len(AllPages) - 2]
            Last = LastPageLink.get_attribute("href")
            maxIndexofPage = int(Last.partition('page=')[2])
            vAllPageLinks = []

            # Scrape Starts from this page. Change index in g_startIndex.
            nIdxOfPage = g_startIndexes[cat_code]
            for i in range(nIdxOfPage, maxIndexofPage + 1):
                sOnePageLink = sCat_Link + "?page=" + str(i)
                if sOnePageLink not in vAllPageLinks:
                    vAllPageLinks.append(sOnePageLink)
            print("Total number of pages: %d" % maxIndexofPage)

            for sOnePageLink in vAllPageLinks:
                nPageIndex = nIdxOfPage
                nIdxOfPage += 1
                print("page %d" % nPageIndex)
                NavigateToOnePage(aBrowserDriver, sOnePageLink)

                # For each product in this page, insert them into the list of all products.
                vElementsProducts = aBrowserDriver.find_elements_by_xpath("//a[contains(@href,'/product/')]")
                vAllProductsInThisPage = []
                for aElementOneProduct in vElementsProducts:
                    sProductHref = aElementOneProduct.get_attribute("href")
                    if sProductHref not in vAllProductsInThisPage:
                        vAllProductsInThisPage.append(sProductHref)
                # For each vendor in this page, insert them into the list of all vendors.
                vElementsVendors = aBrowserDriver.find_elements_by_xpath("//a[contains(@href,'/vendor/')]")
                vAllVendorsInThisPage = []
                for aElementOneVendor in vElementsVendors:
                    sVendorHref = aElementOneVendor.get_attribute("href")
                    if sVendorHref not in vAllVendorsInThisPage:
                        vAllVendorsInThisPage.append(sVendorHref)

                # 1. Scrape the product information
                for sProductHref in vAllProductsInThisPage:
                    sProductMarketID = sProductHref.partition('product/')[2]
                    bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingProductDescription(sProductMarketID)
                    # bWhetherScraping = True
                    if bWhetherScraping:
                        NavigateToOnePage(aBrowserDriver, sProductHref)
                        # Save the html
                        sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                        aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                        sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(2) + \
                                               '_' + sProductMarketID + '_pd'
                        sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                        # Get screen shot of Product Description
                        aBrowserDriver.get_screenshot_as_file(sLocalOutputFileNameFullPath + "_img.png")
                        aFile = open(sLocalOutputFileNameFullPath, "w")
                        aFile.write(aBrowserDriver.page_source)
                        aFile.close()
                        aMySQLcrptmktDB.UpdateDatabaseUploadFileProductDescription(sLocalOutputFileName,
                                                                                   sLocalOutputFileNameFullPath,
                                                                                   sProductMarketID)
                        os.remove(sLocalOutputFileNameFullPath)

                    # Not doing this in stage 1
                    """
                    # scrape product feedback
                    bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingProductRating(sProductMarketID)
                    if bWhetherScraping:
                        sProductFeedbackHref = sProductHref+"/feedback#"
                        sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                        aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                        sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(2) + '_' + \
                                               sProductMarketID + '_pr'
                        sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                        NavigateToOnePage(aBrowserDriver, sProductFeedbackHref)
                        # Save the html
                        aFile = open(sLocalOutputFileNameFullPath, "w")
                        aFile.write(aBrowserDriver.page_source)
                        aFile.close()
                        aMySQLcrptmktDB.UpdateDatabaseUploadFileProductRating(sLocalOutputFileName,
                                                                              sLocalOutputFileNameFullPath,
                                                                              sProductMarketID)
                        os.remove(sLocalOutputFileNameFullPath)
                    """

                print("Products %d" % len(vAllProductsInThisPage))

                # 1. Scrape the vendor profile page
                for sVendorHref in vAllVendorsInThisPage:
                    sVendorMarketID = sVendorHref[sVendorHref.rindex('/') + 1:]
                    bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingVendorProfile(sVendorMarketID)
                    if bWhetherScraping:
                        sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                        aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                        sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(2) + '_' + \
                                               sVendorMarketID + '_vp'
                        sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                        NavigateToOnePage(aBrowserDriver, sVendorHref)
                        # Save the html
                        aFile = open(sLocalOutputFileNameFullPath, "w")
                        aFile.write(aBrowserDriver.page_source)
                        aFile.close()
                        # Move file to server, and update the sql database
                        aMySQLcrptmktDB.UpdateDatabaseUploadFileVendorProfile(sLocalOutputFileName,
                                                                              sLocalOutputFileNameFullPath,
                                                                              sVendorMarketID)
                        sCommandRemoveLocalfiles = 'rm ' + sLocalOutputFileNameFullPath
                        os.system(sCommandRemoveLocalfiles)

                    # Not doing this in stage 1
                    """
                    # scrape vendors feedback
                    bWhetherScraping = aMySQLcrptmktDB.CheckWhetherScrapingVendorRating(sVendorMarketID)
                    if bWhetherScraping:
                        vVendorFeedbackHref = sVendorHref + "/feedback"
                        sCurrentUTCTime = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                        aMySQLcrptmktDB.m_sCurrentUTCTime = sCurrentUTCTime
                        sLocalOutputFileName = sCurrentUTCTime + '_' + str(g_nMarketGlobalID).zfill(2) + '_' + \
                                               sVendorMarketID + '_vr'
                        sLocalOutputFileNameFullPath = g_sOutputDirectoryTemp + sLocalOutputFileName
                        NavigateToOnePage(aBrowserDriver, vVendorFeedbackHref)
                        aFile = open(sLocalOutputFileNameFullPath, "w")
                        aFile.write(aBrowserDriver.page_source)
                        aFile.close()
                        aMySQLcrptmktDB.UpdateDatabaseUploadFileVendorRating(sLocalOutputFileName,
                                                                             sLocalOutputFileNameFullPath,
                                                                             sVendorMarketID)
                        sCommandRemoveLocalfiles = 'rm ' + sLocalOutputFileNameFullPath
                        os.system(sCommandRemoveLocalfiles)
                    """
                print("Vendors %d" % len(vAllVendorsInThisPage))

        print("All jobs are done! Thanks for inputting so many CAPTCHAs!")
        aBrowserDriver.quit()
    except:
        NotifyMe(message='DarkBay script Failed!!!', subject='Scraper Alert.')
        print('Script Failed.')
