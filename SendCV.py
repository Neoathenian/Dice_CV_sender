from pickle import TRUE
from bs4 import BeautifulSoup as bs
import requests
from time import sleep
from random import random
from lxml import html
from math import ceil
from bs4 import BeautifulSoup
import sys
import pandas as pd

#from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException,TimeoutException,ElementNotInteractableException
from fake_useragent import UserAgent
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui



def Descansa():
    x=random()*10
    if x<1:
        sleep(1)
    elif x>5:
        sleep(5)
    else:
        sleep(x)
    return

Info_df=pd.read_csv("password.txt",sep="\t").set_index("Info")
User=Info_df.at["User","Value"]
Password=Info_df.at["Password","Value"]

def Iniciar_driver(url="https://www.dice.com/dashboard/login",ultima_semana=False):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    # options.add_argument("--headless")
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    #These options are for the autofill and for the popup to keep the password
    prefs = {"credentials_enable_service": False,"profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)

    s=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options,service=s)
    driver.get(url)
    #Ahora aceptaremos las cookies (para ello necesitamos acceder al shadow element (un pain in the ass))
    sleep(5)
    root=WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.ID,"cmpwrapper"))
    )
    shadow_root=expand_shadow_element(driver,root)
    shadow_root.find_element(By.ID,"cmpbntyestxt").click()

    #Safety measure if you try to access a non dice page
    if url!="https://www.dice.com/dashboard/login":
        return driver
    #Ahora metemos los datos de login
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.ID,"email"))
    ).send_keys(User)

    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.ID,"password"))
    ).send_keys(Password)

    #Pretty sure this is to click the sign in button
    WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.XPATH,'//button[@class="btn btn-primary btn-lg btn-block"]'))
    ).click()

    #Creo que esto es de un pop-up que me aparecía por no tener el perfil visible a la gente
    #WebDriverWait(driver,20).until(
    #    EC.presence_of_element_located((By.XPATH,'//div[@class="fe-popup-cross"]'))
    #)

    WebDriverWait(driver,20).until(
        EC.presence_of_element_located((By.XPATH,'//input[@id="typeaheadInput"]'))
    ).send_keys("python, Data scientist\n")

    #Filtramos para solo remoto
    WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.XPATH,'//button[@aria-label="Filter Search Results by Remote Only"]'))
    ).click()
    ####
    #Tiene que esperar un rato para actualizar los trabajos
    sleep(5)

    if ultima_semana:
        #Filtramos por trabajos que han aparecido la última semana
        Header=WebDriverWait(driver,20).until(
                EC.element_to_be_clickable((By.XPATH,'//button[@data-cy-index="3"]'))
            ).click()
        Descansa()

    #Filtremos por Easy Apply, primero hay que abrir esa pestaña
    Easy_apply_header=WebDriverWait(driver,20).until(
            EC.element_to_be_clickable((By.XPATH,'//div[@class="facet-group-header ng-tns-c71-9"]'))
        )
    if Easy_apply_header.get_attribute("data-cy-accordion-is-expanded")=="false":
        Easy_apply_header.click()

    #Ahora si le damos al boton de Easy Apply
    WebDriverWait(driver,20).until(
            EC.element_to_be_clickable((By.XPATH,'//button[@aria-label="Filter Search Results by Easy Apply"]'))
        ).click()

    return driver



def Next_page(driver):
    WebDriverWait(driver,5).until(
        EC.element_to_be_clickable((By.XPATH,'//li[@class="pagination-next page-item ng-star-inserted"]'))
    ).click()

#Funcion necesaria para acceder shadow elements
def expand_shadow_element(driver,element):
  shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
  return shadow_root

#Una vez en una página de un coso, lo que hace es darle al boton de apply y enviar el CV
def Apply(driver):
    sleep(5)
    root=WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.XPATH,'//div[@class="col-md-7 col-lg-6 hidden-sm hidden-xs applySec"]//dhi-wc-apply-button'))#'//div[@class="hidden-lg hidden-md col-md-12 col-xs-12 applySec lowerApply"]//dhi-wc-apply-button'))
    )
    shadow_root=expand_shadow_element(driver,root)

    shadow_root=shadow_root.find_element(By.CLASS_NAME,"button-primary")
    if shadow_root.text!="Applied":
        shadow_root.click()

        sleep(20)
        WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH,'//button[@class="btn btn-primary btn-next btn-block"]'))
        ).click()
        try:
            WebDriverWait(driver,10).until(
                EC.element_to_be_clickable((By.XPATH,'//button[@class="btn btn-primary btn-next btn-block"]'))
            ).click()
        except:
            pass

        #selenium.common.exceptions.TimeoutException: Message:  
        WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH,'//button[@class="btn btn-primary btn-next btn-split"]'))
        ).click()
    
def Actualizar_links(driver):
    """Esta función se encarga de actualizar los links de los trabajos para aplicar a ellos
        Para ello hay que estar en la páging de dice.com/jobs. Así, lo que hace es modificar el pags_web.csv
        que es lo que se usará para los links"""
    pags_web=[]
    for i in range(2):
        for elem in driver.find_elements(By.XPATH,'//dhi-search-card[@data-cy="search-card"]'):
            try:
                No_se_ha_hecho=elem.find_element(By.XPATH,'.//span[@class="ribbon-inner"]').text!="applied"
            except:
                No_se_ha_hecho=True
            if No_se_ha_hecho:
                puesto=elem.find_element(By.XPATH,'.//h5//a').text
                href=elem.find_element(By.XPATH,'.//h5//a').get_attribute("href")
                company=elem.find_element(By.XPATH,'.//a[@data-cy="search-result-company-name"]').text
                location=elem.find_element(By.XPATH,'.//span[@class="search-result-location"]').text
                employment_type=elem.find_element(By.XPATH,'.//span[@data-cy="search-result-employment-type"]').text
                posted_date=elem.find_element(By.XPATH,'.//span[@data-cy="card-posted-date"]').text[7:]
                pags_web.append([puesto,posted_date,company,location,employment_type,href])
        sleep(5)
        try:
            Next_page(driver)
        except:
            break
        sleep(5)
    
    pags_web=pd.DataFrame(pags_web,columns=["puesto","posted_date","company","location","employment_type","href"])
    pags_web.to_csv("pags_web.csv")



##Código antiguo
###Aceptar Cookies
##pyautogui.click(x=997, y=574)

#Código antiguo que creo que es para recolectar información de los trabajos
###driver,s = Iniciar_driver("https://www.dice.com")
###
###pags_web=pd.read_csv("pags_web.csv",index_col=0)["href"]
###
###
###sentences=[]
###for url in pags_web:
###    try:
###        driver.get(url)
###        frase=""
###        for elem in driver.find_elements(By.XPATH,'//div[@class="row job-info"]'):
###            try:
###                frase+=elem.text
###            except:
###                pass
###        frase+=driver.find_element(By.XPATH,'//div[@id="jobdescSec"]').text
###        sentences.append(frase)
###    except:
###        print(url)
###    sleep(3)
###    
###sentences=pd.DataFrame(sentences,columns=["sentences"])
###sentences.to_csv("sentences.csv")
###driver.quit()
###sleep(5)
#print(driver.find_element(By.XPATH,'//div[@id="jobdescSec"]').text)

#for elem in driver.find_elements(By.XPATH,'//div[@id="jobdescSec"]//*'):#//p'):
#    print(":)")
#    try:
#        sentences.append(elem.text)
#    except:
#        print("Falle")

#driver.quit()


#Código antiguo para saber algo de lo que se pide en los trabajos
##df=pd.read_csv("sentences.csv",index_col=0)
##sol=[]
##for frase in df["sentences"]:
##    sol+=frase.lower().replace(","," ").replace("."," ").replace(":"," ").replace("("," ").replace(")"," ").split()
##
##sol=pd.Series(sol)
##unicos=sol.nunique()
#counts=sol.value_counts().drop(["and","to","of","in","the","with","a","for","or","on","as","is","our","we","you","team","an","are"
#                                    ])
##Hay un carácter raro que no se eliminar
#counts=counts.drop(["-","will","be","that","this","have","*","other","from","such","at","it","must","your","/","not",
#                    "can","who","use","about","through"])
#
#

#Palabras interesantes encontradas en los trabajos
#interesting_variables=["cloud","aws","python","sql","azure","analytics","automation","programming","web","science","analysis","pipelines",
#                        "etl","devops","spark","google","senior","scripting","api","network","languages","platforms","databases",
#                        "javascript","5+","designing","linux","kubernetes","ci/cd","snowflake","frameworks","deep","java","kafka",
#                        "tableau","bi","oracle","apis","3+","pipeline","algorithms","server","hadoop","git","bachelor's","microsoft",
#                        "automated","jenkins","nosql","2+","apache","scala","amazon","scientist","troubleshooting","r","ml","analyst",
#                        "airflow","backend","js","c#","redshift","shell","c++","scripts","scientists","statistics","tuning","scrum",
#                        "lambda","mysql","ai","sr","powershell","postgresql","angular","json","ui","unix","10+","c","html","excel",
#                        "mining","github","perl","gitlab","django","python","selenium","pandas","dashboard","pyspark","qa","mathematics",
#                        "windows","hive","jira","ruby","4+"]

#Código antiguo para cargar mas (no se que carga mas :()
#Busca el boton de "Cargas Mas" y lo pulsa
def CargarMas(driver):
    Intentos = 0
    SeEncontro = False
    while Intentos<50 and not SeEncontro:
        print("Bajemos")
        driver.execute_script("window.scroll(0, window.scrollY + 1000);")#document.body.scrollHeight
        Descansa()
        try:
            #Buscamos el boton de "Siguiente"
            boton = WebDriverWait(driver,1).until(
                EC.element_to_be_clickable((By.XPATH,'//button[@class="sui-AtomButton sui-AtomButton--primary sui-AtomButton--flat sui-AtomButton--center"]'))
            )
            print(boton)
            print("ENCONTRAMOS")
            #boton.click()
            SeEncontro = True
            #print("Se Ha encontrado")
        except:
            #print("Todavía no se ha encontrado")
            print(Intentos)
            Intentos+=1
        print(Intentos)
        print(SeEncontro)
    #Que NO se haya encontrado un boton de CargarMas, NO significa que no se hayan cargado mas por haber scrolled down
    return SeEncontro

#def Cargar_Todo(driver):
#    while CargarMas(driver):
#        pass
#    CargarMas(driver)
#    return

 

#Código antiguo tratando de obtener info de los trabajos
def Descargar_informacion(driver):
    for elem in driver.find_elements(By.XPATH,'//ul[@class="ij-ComponentList"]//li[@class="ij-ComponentList-item"]'):
        try:
            puesto=elem.find_element(By.XPATH,'.//h2//a[@class="ij-OfferCardContent-description-title-link"]').text
            empresa=elem.find_element(By.XPATH,'.//h3//a[@class="ij-OfferCardContent-description-subtitle-link"]').text
            Ubicacion=elem.find_element(By.XPATH,'.//ul//span[@class="ij-OfferCardContent-description-list-item-truncate"]').text
            Sueldo=elem.find_elements(By.XPATH,'.//div[@class="ij-OfferCardContent-description"]//ul[@class="ij-OfferCardContent-description-list"]')[1]#[2].text
            Sueldo=Sueldo.find_elements(By.XPATH,'.//li')[2].text
            print(Sueldo,flush=True)
        except:
            pass





