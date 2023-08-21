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


###driver= Iniciar_driver()
###
####Actualizar_links()
###
###df=pd.read_csv("pags_web.csv")
###for link in df["href"]:
###    driver.get(link)
###    Apply()
    
##sleep(5)


##driver,s = Iniciar_driver("https://www.dice.com/jobs/detail/3d318313fc798cb60ebd59bb3fb8d4cc?searchlink=search%2F%3Fq%3Dpython%2C%2520Data%2520scientist%26countryCode%3DUS%26radius%3D30%26radiusUnit%3Dmi%26page%3D89%26pageSize%3D20%26filters.isRemote%3Dtrue%26language%3Den%26eid%3DS2Q_&searchId=57aba60a-d4ea-41c3-a6cc-0dd321ef27f4")
###driver,s = Iniciar_driver("https://www.dice.com/jobs/detail/b8f7058f122fd66e409a7868340ef325?searchlink=search%2F%3FcountryCode%3DUS%26radius%3D30%26radiusUnit%3Dmi%26page%3D1%26pageSize%3D20%26language%3Den%26eid%3DS2Q_%2CgKQ_&searchId=b5049236-097d-438d-abbe-99dd32b56e24")
##sleep(5)
##
###Aceptar Cookies
##pyautogui.click(x=997, y=574)

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


#Palabras interesantes
#counts=counts.drop(["business","experience","work","years","software","development","data","working","knowledge","technical","solutions",
#                        "strong","skills","ability","using","design","tools","support","systems","engineering","understanding","security",
#                        "engineer","including","new","services","contract","management","&","all","technologies","technology","by",
#                        "application","develop","remote","computer","related","job","teams","information","build","platform",
#                        "required","degree","code","applications","best","requirements","infrastructure","provide","product","building",
#                        "complex","developing","environment","across","big","communication","full","architecture","performance","like",
#                        "role","more","w2","more","database","testing","design","lead","enterprise","system","learning","quality",
#                        "one","their","machine","client","project","agile","and/or","company","practices","good",
#                        "integration","test","time","processes","developer","position","large","opportunity","implement","help",
#                        "ensure","within","excellent","into","hands-on","models","based","process","preferred","create","well",
#                        "multiple","projects","looking","engineers","expertise","etc","customer","able","service","any","implementation",
#                        "employment","healthcare","high","continuous","production","maintain","deployment","modeling","highly","delivery",
#                        "plus","advanced","analytical","responsible","products","various","least","familiarity","key","industry",
#                        "understand","problems","monitoring","drive","both","us","location","architect","processing","what","has",
#                        "written","equal","responsibilities","candidate","customers","independent","issues","if","improve",
#                        "deliver","status","but","level","identify","equivalent","change","stack","manage","responsibilities","they",
#                        "concepts","responsibilities","professional","implementing","field","000","part","collaborate","standards",
#                        "solution","operations","12","should","qualifications","demonstrated","expert","internal","clients","perform",
#                        "needs","user","may","financial","need","corp-to-corp","learn","writing","health","experience","also","please",
#                        "environments",")","(e","members","g","techniques","employer","organization","apply","stakeholders","docker",
#                        "disability","100%","intelligence","benefits","existing","national","minimum","leading","documentation",
#                        "leadership","reporting","scalable","modern","employees","scale","model","qualifications","distributed",
#                        "qualifications","reporting","creating","qualifications","research","gender","skills","applicants","up",
#                        "candidates","home","operational","seeking","people","some","verbal","control","end","relational","identity",
#                        "opportunities","communicate","sources","relevant","include","procedures","developers","proficiency","critical",
#                        "monthsdepends","them","terraform","storage","how","coding","language","participate","make","join","origin",
#                        "race","providing","closely","rest","hands","following","without","timedepends","without","proven","do","meet",
#                        "core","planning","life","vision","supporting","warehouse","which","protected","description","orientation","global",
#                        "problem","patterns","background","maintaining","power","digital","proficient","when","companies","medical",
#                        "s3","configuration","sexual","religion","focus","different","education","activities","solve","transformation",
#                        "2","tasks","effectively","source","qualified","functions","functional","reports","capabilities","innovative",
#                        "veteran","culture","program","assist","analyze","reviews","age","managing","components","current","statistical",
#                        "compliance","needed","color","open","6","3","experienced","insights","partner","similar","framework","consulting",
#                        "net","public","successful","most","duration","variety","methodologies","duration","out","access","while",
#                        "description","duties","hire","computing","solid","areas","results","5","consideration","strategy","databricks",
#                        "react","users","principles","sets","insurance","tests","collaboration","visualization","value","these",
#                        "maintenance","enable","write","architectures","regard","sex","available","plan","own","where","deploy","months",
#                        "extensive","features","risk","training","manager","experiencetravel","jobs","operating","solving","range",
#                        "administration","its","documentation","document","others","impact","future","independently","review",
#                        "queries","appropriate","group","travel","ansible","direct","federal","lake","delivering","optimization","great",
#                        "https","streaming","diverse","inc","s","partners","define","unit","growth","com","would","governance","state",
#                        "effective","warehousing","networking","desired","external","success","basic","migration","day","lifecycle",
#                        "contribute","paid","splunk","action","deploying","require","long","tech","methods","provides","problem-solving",
#                        "mission","decisions","structures","take","making","right","title","receive","+","better","//www","goals","staffing",
#                        "plans","individual","covid-19","prior","over","efficient","world","domain","designs","o","office","reliability",
#                        "law","mentor","diversity","term","subject","than","strategic","only",
#                        "collaborative","certification","microservices","relationships","applicable","vaccination","initiatives","1",
#                        "query","pay","programs","driven","set","around","roles","works","metrics","growing","specifications",
#                        "changes","no","standard","nice","integrations","resume","spring","top","availability","cases","here",
#                        "certifications","you'll","interpersonal","managers","utilizing","exposure","so","local","glue","optimize",
#                        "automate","datasets","monitor","strategies","committed","mobile","used","salary","additional","focused",
#                        "offer","improvement","improvements"                        
#                        ])

#interesting_variables=["cloud","aws","python","sql","azure","analytics","automation","programming","web","science","analysis","pipelines",
#                        "etl","devops","spark","google","senior","scripting","api","network","languages","platforms","databases",
#                        "javascript","5+","designing","linux","kubernetes","ci/cd","snowflake","frameworks","deep","java","kafka",
#                        "tableau","bi","oracle","apis","3+","pipeline","algorithms","server","hadoop","git","bachelor's","microsoft",
#                        "automated","jenkins","nosql","2+","apache","scala","amazon","scientist","troubleshooting","r","ml","analyst",
#                        "airflow","backend","js","c#","redshift","shell","c++","scripts","scientists","statistics","tuning","scrum",
#                        "lambda","mysql","ai","sr","powershell","postgresql","angular","json","ui","unix","10+","c","html","excel",
#                        "mining","github","perl","gitlab","django","python","selenium","pandas","dashboard","pyspark","qa","mathematics",
#                        "windows","hive","jira","ruby","4+"]
#import numpy as np
#counts=sol.value_counts()
#counts=counts[4:]
#import matplotlib.pyplot as plt
#inic=3000
#fin=18000
#a_plot=counts[inic:fin]
#plt.plot(np.arange(inic,fin),a_plot)
#plt.show()
#

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







#Bajar_Hasta_Abajo(driver)









#Intentos = 0
#SeEncontro = False
#
#while Intentos<50 and not SeEncontro:
#    print("Bajemos")
#    
#    #document.body.scrollHeight
#    #new_height = driver.execute_script("return document.body.scrollHeight")
#    #if new_height==last_height:
#    #    print("TERMINAMOS")
#    #    quit()
#
#    sleep(0.1)
#    #Buscamos el boton de "Siguiente"
#    #boton = WebDriverWait(driver,1).until(
#    #    EC.visibility_of_element_located((By.XPATH,'//span[@class="sui-AtomButton-text"]'))
#    #    )
#    #
#    #print(boton.text)
#    print("AAAAAAA",flush=True)        
#    #Que NO se haya encontrado un boton de CargarMas, NO significa que no se hayan cargado mas por haber scrolled down
#    
#    
#    #print(len(driver.find_elements(By.XPATH,'//ul[@class="ij-ComponentList"]//li[@class="ij-ComponentList-item"]')))
#    #for elem in driver.find_elements(By.XPATH,'//ul[@class="ij-ComponentList"]//li[@class="ij-ComponentList-item"]'):
#    #    try:
#    #        print(elem.find_element(By.XPATH,'.//h2//a[@class="ij-OfferCardContent-description-title-link"]').text,flush=True)
#    #    except:
#    #        pass
#    #boton=driver.find_element((By.XPATH,'//span[@class="sui-AtomButton-text"]'))
#    #boton=driver.find_element(By.XPATH,'//span[@class="sui-AtomButton-text"]/parent::button')
#    ##boton=WebDriverWait(driver,1).until(
#    ##    EC.element_to_be_clickable((By.XPATH,'//span[@class="sui-AtomButton-text"]'))
#    ##)
#    #boton.click()
#    #SeEncontro = True
#    #print("Se Ha encontrado",flush=True)
#    #try:
#    #    boton=WebDriverWait(driver,1).until(
#    #        EC.element_to_be_clickable((By.XPATH,'//span[@class="sui-AtomButton-text"]/../../../button'))
#    #    )
#    #    boton.click()
#    #    SeEncontro = True
#    #    print("Se Ha encontrado",flush=True)
#    #except:
#    #    Intentos+=1
##
##print(len(driver.find_elements(By.XPATH,'//ul[@class="ij-ComponentList"]//li[@class="ij-ComponentList-item"]')))
##for elem in driver.find_elements(By.XPATH,'//ul[@class="ij-ComponentList"]//li[@class="ij-ComponentList-item"]'):
###    try:
###        print(elem.find_element(By.XPATH,'.//h2//a[@class="ij-OfferCardContent-description-title-link"]').text)
###    except:
##        print("NEXTT")