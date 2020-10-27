#!/usr/bin/env python
# -*- coding: cp1252 -*-


from selenium.webdriver.common.keys import Keys
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, uuid
from selenium.webdriver.common.action_chains import ActionChains
from distutils.version import StrictVersion
from numbers import Number
import ConfigParser as cfgparser
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC


import MySQLdb
from datetime import date
import time
import datetime
import sys
import os
import random
import glob
import re
import shutil

reload(sys)
sys.setdefaultencoding("cp1252")






def getProductDisponible():


    #prendre l encours pour l'instance en cours

    try:
        prod = MySQLdb.connect (host = "localhost", user = "systeme_u", passwd = "systeme_u", db = "C208")
        curprod= prod.cursor (MySQLdb.cursors.DictCursor)

        cdc_id_dispo=0
        sql="""
                SELECT
                    systemu_pousse.*
                FROM
                    systemu_pousse
                INNER JOIN
                    systemu_export_header
                ON
                    systemu_pousse.cdc_id=systemu_export_header.cdc_id
                WHERE
                    systemu_export_header.cree=1
                    AND systemu_export_header.systemu_template_id=1
                    AND systemu_pousse.flag=1
                    AND systemu_pousse.num_instance=%s
                    AND systemu_pousse.affichette_id=%s
                LIMIT 1
            """%(num_instance,affichette_id)

        print sql
        curprod.execute(sql)
        tproduct=curprod.fetchone()

        if tproduct!=None:

            systemu_pousse_id=tproduct["systemu_pousse_id"]

            sql="""
                    UPDATE
                        systemu_pousse
                    set
                       nb_lancement=nb_lancement+1
                    where
                        systemu_pousse_id=%s
                """%(systemu_pousse_id)
            curprod.execute(sql)
            curprod.execute("COMMIT")

            sql="""
                SELECT
                    *
                FROM
                    systemu_pousse
                WHERE
                    systemu_pousse_id=%s

            """%(systemu_pousse_id)

            curprod.execute(sql)
            tnb_lancement=curprod.fetchone()
            if tnb_lancement["nb_lancement"]>3:

                sql="""
                        UPDATE
                            systemu_pousse
                        set
                            date_fin=now(),
                            flag=3
                        where
                            systemu_pousse_id=%s
                    """%(systemu_pousse_id)
                curprod.execute(sql)
                curprod.execute("COMMIT")
                prod.close()
                return 0
            prod.close()
            return tproduct["cdc_id"]


        sql="""

                SELECT
                    *
                FROM
                   systemu_gestion_arret_robot
                WHERE
                    jour=DAYOFWEEK(DATE(NOW()))
                    AND heure_deb_arret <=TIME(now())
                    AND heure_fin_arret >=TIME(now())
               """
        curprod.execute(sql)
        tarret=curprod.fetchone()
        if tarret!=None:
            print "Arret du robot. Voir la table systemu_gestion_robot "
            prod.close()
            return 0



        print "tonga"
        sql="""

            SELECT
                *
            FROM
                systemu_gestion_robot
            WHERE
                heure_deb_lance <=TIME(NOW())
                AND heure_fin_lance >=TIME(NOW())
                AND nb_robot>=%s
                AND systemu_template_id=1

       """%(num_instance)
        curprod.execute(sql)
        trobot=curprod.fetchone()
        if trobot==None:
            print "Le robot %s ne doit pas être lancé. Voir les paramétres dans la table systemu_gestion_robot"%(num_instance)
            return 0



        sql="""
                SELECT
                    systemu_pousse.cdc_id
                FROM
                    systemu_pousse
                INNER JOIN
                    systemu_export_header
                ON
                    systemu_pousse.cdc_id=systemu_export_header.cdc_id
                WHERE
                    systemu_export_header.cree=1
                    AND systemu_export_header.systemu_template_id=1
                    AND affichette_id=%s
                    AND systemu_pousse.flag=0
                ORDER BY systemu_pousse.systemu_pousse_id
            """%(affichette_id)
        curprod.execute(sql)
        tproduct=curprod.fetchall()
        tab_product=[]
        for  produit in tproduct:
            tab_product.append(produit["cdc_id"])

        print "1",tab_product
        if len(tab_product)==0:
            prod.close()
            return 0

        cdc_id = random.choice(tab_product)

        #curprod.execute("LOCK delhaize_pousse IN SHARE MODE")
    #    curprod.close()
    #    curprod= prod.cursor ()
        curprod.execute("START TRANSACTION")

        sql="""
                SELECT *
                    FROM systemu_pousse
                WHERE
                affichette_id=%s
                AND cdc_id=%s
                AND flag=0
                AND (SELECT COUNT(affichette_id) FROM systemu_pousse WHERE flag=1 AND cdc_id=%s) = 0
                FOR UPDATE

            """%(affichette_id,cdc_id,cdc_id)
        print sql
        curprod.execute(sql)
        if curprod.fetchone()!=None:

            print "3"
            sql="""
                UPDATE
                  systemu_pousse
                SET
                  num_instance=%s,
                  nb_lancement=nb_lancement+1,
                  date_debut=now(),
                  flag=1
                WHERE
                  affichette_id=%s
                  AND flag=0
                  AND cdc_id=%s

            """%(num_instance,affichette_id,cdc_id)
            curprod.execute(sql)
            curprod.execute("COMMIT")


            print "affichette_id",affichette_id
            print "num_instance",num_instance
            print "cdc_id",cdc_id


            print str(cdc_id)+"-"+str(affichette_id)+"-"+str(num_instance)
    #        curprod.close()
    #        curprod= prod.cursor (MySQLdb.cursors.DictCursor)
            sql="""
                SELECT
                    cdc_id
                FROM
                    systemu_pousse
                WHERE
                affichette_id=%s
                AND flag=1
                AND cdc_id=%s
                AND num_instance=%s
                LIMIT 1
                """%(affichette_id,cdc_id,num_instance)
            print "9999"
            print sql
            curprod.execute(sql)

            tproduit=curprod.fetchone()
            if tproduit!=None:
                print tproduit["cdc_id"]
                prod.close()
                return tproduit["cdc_id"]
            prod.close()
            return 0
        prod.close()
        return 0
    except Exception as inst:
        try:
            curprod.execute("ROLLBACK")
        except:
            pass
        #erreur= str(u""+inst).replace("'","''")
        print inst
        prod.close()
        return 0


def attente_pj(nom):

    ret = False
    xp = '//a[@title="%s"]' % (u""+nom)
    bok = False
    iter = 0
    while not bok:
        iter +=1
        try:
            driver.find_element_by_xpath(xp)
            bok = True
            return True
        except:
            bok = False
            print "Attente 60sec [%s]" %(nom)
            time.sleep(60)
        if iter ==6:
            return False
    return ret


def double_click_object(driver, object_id, ):
    ret = ""
    s_script = """
        var obje ;
        var event = new MouseEvent('dblclick', {
            'view': window,
            'bubbles': true,
            'cancelable': true
          });
        document.getElementById('%s').dispatchEvent(event);
        obje = document.activeElement;
        return obje.id;
    """ % (object_id)
    ret = driver.execute_script(s_script)
    time.sleep(3)
    return ret




def nz(valeur_o,valeur_pardefaut=''):
    if valeur_o=='' or valeur_o==None or valeur_o=='None':
        return valeur_pardefaut
    else:
        return valeur_o



def copy_rename(src_dir, old_file_name, new_file_name,rep_tmp):
    print "6"

    dst_dir= rep_tmp
    src_file = os.path.join(src_dir, old_file_name)
    print "10"
    print "src_file: ", src_file
    print "dst_dir: ", dst_dir
    shutil.copy(u""+src_file,u""+dst_dir)
    print "11"
    dst_file = os.path.join(dst_dir, old_file_name)
    print "12"
    new_dst_file_name = os.path.join(dst_dir, new_file_name)
    print "13"
    os.rename(dst_file, new_dst_file_name)
    print "14"


def DLookup(FieldName , TableName ,connexion, criteria=None):
    cur = connexion.cursor()
    r= "SELECT DISTINCT "+FieldName+" FROM "+TableName+" "
    if(criteria!=None):
        r+=" WHERE "+criteria+" "

    cur.execute(r)

    tres = cur.fetchone()
    if(tres==None):
        return ''
    else:
        return tres[0]


def test_apres_virgule(s):
    try:
        x=s
        isinstance(x, int)

        if str(int(float(x)))==x:
            return True
        else:
            return False
    except:
        return False



try:
    if os.path.exists(os.path.basename(__file__)+'.lock')==False:

        tab=""
        chapter="Traçabilité"
        nom_champ=""
        valeur_champ=""
        section=""
        row_desc=""
        isaffichette_termine=True

        fichierlock=open(os.path.basename(__file__)+'.lock','w')
        fichierlock.close()

        config = cfgparser.ConfigParser()
        config.read("param.ini")
        num_instance=config.get("travail", "num_instance")
        #num_instance=1
        print "num_instance: ", num_instance
        affichette_id=9

        #---Connexion à la base MySql--
        #prod = MySQLdb.connect("164.132.160.87", "systeme_u", "systeme_u", "C208")
        prod = MySQLdb.connect("localhost", "systeme_u", "systeme_u", "C208") #linux
        curprod = prod.cursor(MySQLdb.cursors.DictCursor)

        cdc_id=getProductDisponible() #linux
        #cdc_id=1330 #windows
        #nom_cdc=DLookup("nom_cdc", "systemu_export_header", prod,"cdc_id="+str(cdc_id))
        print "------------19 10 2016--------"
        print u"----------cdc_id extracté: ", cdc_id

        print "10"
        if cdc_id==0 or cdc_id==None:
            if os.path.exists(os.path.basename(__file__)+'.lock')==True:
                os.remove(os.path.basename(__file__)+'.lock')
            #print "------pas de cdc disponible-------"
            sys.exit(0)

        prod = MySQLdb.connect("localhost", "systeme_u", "systeme_u", "C208") #linux
        curprod = prod.cursor(MySQLdb.cursors.DictCursor)



        print "11"
        #linux
        #repertoire_image=r"/home/traceone/SYSTEME_U_FILES/PIECES_JOINTES_INIT_20160222/"+rep+"/"
        repertoire_base=r"/home/traceone/SYSTEME_U_FILES/PIECES_JOINTES_INIT_20160222/"  #linux

        #repertoire_base="D:\\traceone\SYSTEME_U_FILES\PIECES_JOINTES_INIT_20160222\\" #windows
        #repertoire_base=r"\\mctana\prod$\SYSTEMU\PJ\\"

        #-------------Début de traitement selenium-------------
        print "binary"
        binary = FirefoxBinary('/home/traceone/firefox/firefox') #linux
        print "driver"
        driver = webdriver.Firefox(firefox_binary=binary) #linux
        #driver=webdriver.Firefox()  #windows
        driver.implicitly_wait(30)
        print "wait"
        wait = ui.WebDriverWait(driver,20)
        print "get"
        driver.get("https://www.traceone.net/drupal/en")
        driver.maximize_window()

        #clic sur frame
        iframe = driver.find_elements_by_tag_name('iframe')[0]
        driver.switch_to_frame(iframe)
        print "clic sur case en haut"
        driver.find_element_by_id("rdbLoginPassword").click()

        #connexion

        sql="""
            SELECT partage FROM systemu_export_header
            WHERE cdc_id=%s
        """%(cdc_id)

        curprod.execute (sql)
        tproduit= curprod.fetchone()
        partage=tproduit["partage"]


        if partage==1:
            login='migrationsu.fournisseur@traceone.com'
            password='RESU2016'
        elif partage==2:
            login='migrationsu.fournisseur2@traceone.com'
            password='REMP2016'
        elif partage==3:
            login='migrationsu.fournisseur3@traceone.com'
            password='REMP2017'
        elif partage==4:
            login='migrationsu.fournisseur4@traceone.com'
            password='REMP2017'
        elif partage==5:
            login='migrationsu.fournisseur5@traceone.com'
            password='REMP2017'
        elif partage==6:
            login='migrationsu.fournisseur6@traceone.com'
            password='REMP2017'






        s_script= "document.getElementById('tbxlogin').setAttribute('value', '%s')"%(login)
        print "entree login"
        driver.execute_script(s_script)

        s_script= "document.getElementById('tbxPassword').setAttribute('value', '%s')"%(password)
        print "entree mdp"
        driver.execute_script(s_script)
        print "clic sur authentification"
        driver.find_element_by_id("linkLogin").click()

        if partage==1:
            #espace systemu
            systemu=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div/aside/div/div[1]/div/form/div/ul/li[4]/ul/li[2]/a")))
            systemu.click()

        #cliquer portail qualité
        driver.find_element_by_xpath("/html/body/div[3]/div/aside/div/div[2]/div/form/div/ul/li[4]/a").click()

        curprod.execute("select CDC_COMMON_ID,FOURNISSEUR_ID, NOM from CAHIER_DES_CHARGES_MDD where ID=%s"%(cdc_id))
        cdc_mdd=curprod.fetchone()
        fournisseur_id=cdc_mdd["FOURNISSEUR_ID"]
        nom_cdc=cdc_mdd["NOM"]

        sql_emb="""
                SELECT
                    emballage_id
                FROM
                    systemu_pousse_emballage
                WHERE
                    cdc_id=%s and section_type='cara'
            """%(cdc_id)

        curprod.execute(sql_emb)
        semballage=""
        temballage= curprod.fetchall()
        for zemballage in temballage:
            semballage+="_"+str(zemballage["emballage_id"])

        ref_produit="*_"+ str(fournisseur_id)+"_"+str(cdc_id)+semballage
        ref_produit=DLookup("filtre","systemu_export_header",prod,"cdc_id="+str(cdc_id))
        #ref_produit="TEST 2"  #windows
        print "------------------nom cdc filtre: ", ref_produit

        #filtre, rechercher produit
        element=wait.until(EC.element_to_be_clickable((By.XPATH ,"/html/body/form/span/div/div[2]/div/div/div/div/div/div[3]/span[2]/div/table/thead/tr[3]/td[4]/input[2]")))

        script="""
        var mapath = "/html/body/form/span/div/div[2]/div/div/div/div/div/div[3]/span[2]/div/table/thead/tr[3]/td[4]/input[2]";
        var iterator = document.evaluate(mapath, document, null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null );
        var obje = iterator.iterateNext();
        obje.setAttribute('value', '%s');

        """%(u""+ref_produit)

        driver.execute_script(script)
        #print "a"
        time.sleep(5)
        #print "b"
        element.send_keys(Keys.RETURN)
        #print "c"
        time.sleep(5)
        #print "d"
        # clic le lien produit
        try:
            wait.until(EC.text_to_be_present_in_element((By.XPATH ,"/html/body/form/span[1]/div/div[2]/div/div/div/div/div/div[3]/span[2]/div/table/tbody/tr/td[4]/a"),u""+ref_produit))
        except:
            pass
        #print "e"
        #element.click()
        driver.find_element_by_xpath("/html/body/form/span[1]/div/div[2]/div/div/div/div/div/div[3]/span[2]/div/table/tbody/tr/td[4]/a").click()
        #print "f"
        #clic sur traçabilité
        parent_gauche = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[11]/span/span[2]')))
        parent_gauche.click()

        main_window_handle = driver.current_window_handle

        #clic sur bouton "saisir les sections"
        wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/a[1]/span"))).click()

        wait.until(lambda d: len(d.window_handles) == 2)

        #print "window_handles", driver.window_handles

        window_after = driver.window_handles[1]

        #print "window_after", window_after

        driver.switch_to_window(window_after)

        curprod.execute("select TRACABILITE_ID from CDC_COMMON where ID=%s"%(cdc_mdd["CDC_COMMON_ID"]))
        cdc_common=curprod.fetchone()

        curprod.execute("select * from TRACABILITE where ID=%s"%(cdc_common["TRACABILITE_ID"]))
        liste_champs=curprod.fetchone()

        sql="select emballage_id, emballage_name from systemu_pousse_emballage where cdc_id=%s and section_type='cara'"%(cdc_id)
        print "sql systemu_pousse_emballage: ", sql
        curprod.execute(sql)
        sections=curprod.fetchall()
        print "sections: ", sections

        #----sans emballage-----
        if len(sections)==0:
            for x in range(1):
                #type section
                if x<=1:
                    xpath_type="/html/body/form/div["+str(x+4)+"]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[1]"
                else:
                    xpath_type="/html/body/form/div[5]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[1]"
                type=wait.until(EC.element_to_be_clickable((By.XPATH,xpath_type)))

                type.click()
                if x==0:
                    type0=type

                print "clic type "+str(x)

                time.sleep(3)

                xpath_option="/html/body/select/option[text()='Traçabilité']"
                driver.find_element_by_xpath(u""+xpath_option).click()
                print "choisir liste type"

                #section
                if x<=1:
                    xpath="/html/body/form/div["+str(x+4)+"]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[2]"
                else:
                    xpath="/html/body/form/div[5]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[2]"
                section_1=wait.until(EC.element_to_be_clickable((By.XPATH,xpath)))


                #print "methodes section: ", dir(section_1)
                section_1.click()
                section_1.click()
                print "clic section "+str(x)

                time.sleep(5)

                #xpath2=xpath+"/input"
                #driver.find_element_by_xpath(xpath2).clear()
                section="Traçabilité"

                #td_section_id = "ctl00xcphContentxwebGridRecette_rc_0_1"
                #td_section_id = td_section_id.replace("_0_", "_%s_" % (x))
                td_section_id=section_1.get_attribute("id")
                print "td_section_id"

                tmp_new_id = double_click_object(driver,td_section_id)
                s_script= """document.getElementById("%s").value='%s'"""%(tmp_new_id,u'%s'%(section.replace("'","\\'")))
                driver.execute_script(s_script)

                print "section: ", u""+section

                time.sleep(10)

                if x<=len(sections)-2:
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#ctl00xcphContentxwebGridRecette_rc_"+str(x+1)+"_2 > img"))).click()
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.text"))).click()
                    #print "clic sur inserer "+"#ctl00xcphContentxwebGridRecette_rc_"+str(x+1)+"_2 > img"


            type0.click()
            time.sleep(10)
            print "clic sur OKok  pour fermer la saisie des sections"
            driver.find_element_by_id("ctl00_OkButton").click()

            time.sleep(10)

            driver.switch_to_window(main_window_handle)

            #Rafraichir sur clic sur traçabilité
            parent_gauche = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[11]/span/span[2]')))
            parent_gauche.click()

            time.sleep(10)

            #-----onglet Définition-----
            tab="Définition"

            #Parcours de chaque section créée
            for y in range(1):
                section_cree = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[12]/div["+str(y+1)+"]/span/span[2]")))
                section_cree.click()
                time.sleep(5)

                #clic sur définition
                driver.find_element_by_css_selector("#ctl00_cphContent_ctl14_SpecTabView_ctl01 > span.wrap > span.innerWrap").click()
                time.sleep(15)

                #print "---tracabilite_id: ", liste_champs["ID"]

                if liste_champs!=None:
                    print "tracabilite definition id existant"
                    #definition lot
                    xpath_def_lot="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[2]/div/div/div/div[2]/textarea"

                    driver.find_element_by_xpath(xpath_def_lot).clear()
                    nom_champ="DEFINITION_LOT"
                    valeur_champ=u""+str(nz(liste_champs["DEFINITION_LOT"]))
                    driver.find_element_by_xpath(xpath_def_lot).send_keys(valeur_champ)
                    print "saisie DEFINITION_LOT"
                    #mode identification
                    xpath_mode_ident="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[3]/div/div/div/div[2]/textarea"
                    driver.find_element_by_xpath(xpath_mode_ident).clear()
                    nom_champ="EXPLICATION_CODAGE"
                    valeur_champ=u""+str(nz(liste_champs["EXPLICATION_CODAGE"]))
                    driver.find_element_by_xpath(xpath_mode_ident).send_keys(valeur_champ)

                    #taille lot
                    xpath_taille="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[4]/div/div/div/div[2]/textarea"
                    driver.find_element_by_xpath(xpath_taille).clear()
                    nom_champ="TAILLE_LOT"
                    valeur_champ=u""+str(nz(liste_champs["TAILLE_LOT"]))
                    driver.find_element_by_xpath(xpath_taille).send_keys(valeur_champ)

                    #nombre de lots
                    xpath_nombre_lots="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[5]/div/div/div/div[2]/textarea"
                    driver.find_element_by_xpath(xpath_nombre_lots).clear()
                    nom_champ="PREVISION_NB_LOT"
                    valeur_champ=u""+str(nz(liste_champs["PREVISION_NB_LOT"]))
                    driver.find_element_by_xpath(xpath_nombre_lots).send_keys(valeur_champ)

                    curprod.execute("select URL from DOCUMENT where ID_LISTE=%s"%(liste_champs["LISTE_DOCUMENTS_ID"]))
                    id_listes=curprod.fetchall()
                    z=0
                    for id_liste in id_listes:

                        print "1"
                        sfile1=id_liste["URL"].replace("\\", "/")
                        if sfile1.find("/")==-1:
                            tmp=sfile1
                            match = re.findall(r'^liste_[0-9]+', tmp)
                            if len(match)==0:
                                continue

                            tmp2=tmp.replace(match[len(match)-1], "")
                            rep=match[len(match)-1]
                            rep=rep.strip()

                            url=tmp2.strip()
                        else:
                            a=sfile1.split("/")
                            url=a[len(a)-1]
                            rep=sfile1.replace(url, "").strip().strip("/")
                            #rep=rep.replace("/","\\")
                        print "2"
                        #print "rep: ", rep
                        #print "url: ", url

                        #procédure de traçabilité
                        repertoire_image=repertoire_base+rep+"/" #linux
                        #repertoire_image=repertoire_base+rep+"\\" #windows

                        nom_champ="url"

                        p_j=os.path.join(repertoire_image,url)

                        valeur_champ=p_j
                        #print "repertoire url: ", repertoire_image+url
                        #print "pièce jointe: ", p_j
                        print "3"


                        #------test >60-----
                        tfilename=[] #chemin complet
                        tfile1=[] #base
                        path="/home/traceone/SYSTEME_U_FILES/PIECES_JOINTES_INIT_20160222"
                        extension=""
                        avant_extension=p_j
                        iapres_point=p_j.rfind(".")
                        if iapres_point!=-1:
                            extension=p_j[iapres_point+1:]
                            avant_extension=p_j[0:iapres_point]
                        print "extension",extension

                        if extension.upper().find("ZIP")!=-1:
                            print "niditra 1"
                            if os.path.isfile(avant_extension+"_1."+extension) ==True:
                                nom_fic1=avant_extension+"_1."+extension
                                tfilename.append(nom_fic1)
                                tfile1.append(nom_fic1.replace(path,""))
                                print "niditra 2"
                                if os.path.isfile(avant_extension+"_2."+extension) ==True:
                                    nom_fic2=avant_extension+"_2."+extension
                                    tfilename.append(nom_fic2)
                                    tfile1.append(nom_fic2.replace(path,""))
                                    print "niditra 3"
                                    if os.path.getsize(u""+nom_fic1) >=61440000 or os.path.getsize(u""+nom_fic2) >=61440000 :
                                       isaffichette_termine==False
                                       sql="""
                                           INSERT INTO
                                                    systemu_affichette_log_sys
                                                       (
                                                           affichette_id,
                                                           num_instance,
                                                           chapter,
                                                           tab,
                                                           nom_champ,
                                                           valeur_champ,
                                                           exeption,
                                                           cdc_id
                                                       )
                                                    VALUES
                                                       (
                                                           9,
                                                           %s,
                                                           'Tracabilite',
                                                           'Definition',
                                                           'url',
                                                           '%s',
                                                           '%s',
                                                            %s


                                                       )
                                           """%(num_instance,nom_fic1+ "ou "+nom_fic2+ ">=60Mo","Fichier",cdc_id)

                                       curprod.execute (sql)
                                       bfilename_sup_60mo=True
                                       continue





                                else:
                                    print "tsy nahita"
                                    isaffichette_termine==False
                                    sql="""
                                       INSERT INTO
                                                systemu_affichette_log_sys
                                                   (
                                                       affichette_id,
                                                       num_instance,
                                                       chapter,
                                                       tab,
                                                       nom_champ,
                                                       valeur_champ,
                                                       exeption,
                                                       cdc_id
                                                   )
                                                VALUES
                                                   (
                                                       9,
                                                       %s,
                                                       'Tracabilite',
                                                       'Definition',
                                                       'url',
                                                       '%s',
                                                       '%s',
                                                        %s


                                                   )
                                       """%(num_instance,avant_extension+"_2."+extension,"Fichier non trouvé",cdc_id)

                                    curprod.execute (sql)
                                    continue



                            else:
                                print "aaaaa"
                                if os.path.getsize(u""+p_j) >=61440000:
                                    isaffichette_termine==False
                                    sql="""
                                       INSERT INTO
                                                systemu_affichette_log_sys
                                                   (
                                                       affichette_id,
                                                       num_instance,
                                                       chapter,
                                                       tab,
                                                       nom_champ,
                                                       valeur_champ,
                                                       exeption,
                                                       cdc_id
                                                   )
                                                VALUES
                                                   (
                                                       9,
                                                       %s,
                                                       'Tracabilite',
                                                       'Definition',
                                                       'url',
                                                       '%s',
                                                       '%s',
                                                        %s


                                                   )
                                       """%(num_instance, sfile1+ ">=60Mo","Fichier",cdc_id)

                                    curprod.execute (sql)
                                    continue

                                tfilename.append(p_j)
                                tfile1.append(sfile1)

                                print "bbbbb"
                        else:
                            print "ccccccc"
                            if os.path.getsize(u""+p_j) >=61440000:
                                isaffichette_termine==False
                                sql="""
                                   INSERT INTO
                                            systemu_affichette_log_sys
                                               (
                                                   affichette_id,
                                                   num_instance,
                                                   chapter,
                                                   tab,
                                                   nom_champ,
                                                   valeur_champ,
                                                   exeption,
                                                   cdc_id
                                               )
                                            VALUES
                                               (
                                                   9,
                                                   %s,
                                                   'Tracabilite',
                                                   'Definition',
                                                   'url',
                                                   '%s',
                                                   '%s',
                                                    %s


                                               )
                                   """%(num_instance,sfile1+ ">=60Mo","Fichier",cdc_id)

                                curprod.execute (sql)
                                continue

                            tfilename.append(p_j)
                            tfile1.append(sfile1)

                        print "dddddd"
                        #------------------------
                        for p_j1 in tfilename:
                            (filepath, filename) = os.path.split(p_j1)
                            print "filename: ", filename
                            if z==0:
                                xpath0="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/"
                            else:
                                xpath0 = "/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/"

                            xpath1="div[3]/div/div/div[2]/div/div/div/span/div/div[2]/table/tbody/tr["+str(3+z)+"]/td[2]/span/div/span[1]/a[1]"


                            time.sleep(5)

                            xpath=xpath0+xpath1
                            print "xpath: ", xpath
                            driver.find_element_by_xpath(xpath).click()
                            print "clic sur ajout pièce definition"
                            time.sleep(5)

                            #print "window_handles2: ", driver.window_handles

                            #---Frame ajout pièce--
                            driver.switch_to.frame("RadWindowContentFrame_1")
                            print "passage au frame ajout pièce"

                            #time.sleep(4)


                            #----renommer pj-----
                            tmp=""

                            pos_virgule=filename.rfind(",")
                            if pos_virgule!=-1:
                                print "----presence de ,"
                                chaine_apres_virgule=filename[pos_virgule+1:]
                                print "1"
                                if test_apres_virgule(chaine_apres_virgule)==True:
                                    print "2"
                                    erreur = "ok"
                                else:
                                    erreur = "ko"
                                    print "3"

                                if erreur=="ok":
                                    filename2=filename[:-2]
                                    print "4"
                                    src_dir=repertoire_image
                                    old_file_name=u""+filename
                                    new_file_name=u""+filename2
                                    print "5"
                                    rep_tmp = "/home/traceone/SYSTEME_U/alimentaire/tmp/"
                                    copy_rename(src_dir, old_file_name, new_file_name,rep_tmp)
                                    print "15"
                                    tmp=rep_tmp #linux
                                    #tmp=src_dir+"tmp\\" #windows
                                    source=os.path.join(tmp, new_file_name)
                                    print "16"
                                    repertoire_image=source
                                    print "17"
                                    fichier=new_file_name
                                else:
                                    repertoire_image = repertoire_image + filename
                                    fichier=filename
                            else:
                                repertoire_image=repertoire_image + filename
                                fichier=filename
                            #----------------------
                            print "18"
                            driver.find_element_by_id("ctl00_cphContent_fileUpload").clear()
                            driver.find_element_by_id("ctl00_cphContent_fileUpload").send_keys(u""+repertoire_image)
                            print "ajout piece ok"
                            #----------------------

                            time.sleep(10)
                            driver.switch_to.default_content()
                            time.sleep(5)

                            if attente_pj (fichier)==False:
                                isaffichette_termine==False
                                sql="""
                                    INSERT INTO
                                                 systemu_affichette_log_sys
                                                    (
                                                        affichette_id,
                                                        num_instance,
                                                        chapter,
                                                        tab,
                                                       nom_champ,
                                                        valeur_champ,
                                                        exeption,
                                                        cdc_id
                                                    )
                                                 VALUES
                                                   (
                                                        9,
                                                        %s,
                                                        'Tracabilite',
                                                        'Definition',
                                                        'url',
                                                        '%s',
                                                        '%s',
                                                        %s


                                                    )
                                        """%(num_instance,filename,"Message:Erreur upload",cdc_id)

                                curprod.execute (sql)
                                prod.commit()
                                continue

                            print "fichier: ", repertoire_image

                            #---suppr tmp----
                            if tmp!="":
                                os.remove(source)
                            #----------------

                            z+=1

        #------------------------

        for x in range(len(sections)):
            #type section
            if x<=1:
                xpath_type="/html/body/form/div["+str(x+4)+"]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[1]"
            else:
                xpath_type="/html/body/form/div[5]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[1]"
            type=wait.until(EC.element_to_be_clickable((By.XPATH,xpath_type)))

            type.click()
            if x==0:
                type0=type

            print "clic type "+str(x)

            time.sleep(3)

            xpath_option="/html/body/select/option[text()='Traçabilité']"
            driver.find_element_by_xpath(u""+xpath_option).click()
            print "choisir liste type"

            #section
            if x<=1:
                xpath="/html/body/form/div["+str(x+4)+"]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[2]"
            else:
                xpath="/html/body/form/div[5]/div[2]/div/div/div/div/div/table/tbody/tr[2]/td/div/table/tbody/tr["+str(x+1)+"]/td[2]"
            section_1=wait.until(EC.element_to_be_clickable((By.XPATH,xpath)))


            #print "methodes section: ", dir(section_1)
            section_1.click()
            section_1.click()
            print "clic section "+str(x)

            time.sleep(5)

            #xpath2=xpath+"/input"
            #driver.find_element_by_xpath(xpath2).clear()
            section=sections[x]["emballage_name"]

            #td_section_id = "ctl00xcphContentxwebGridRecette_rc_0_1"
            #td_section_id = td_section_id.replace("_0_", "_%s_" % (x))
            td_section_id=section_1.get_attribute("id")
            print "td_section_id"

            tmp_new_id = double_click_object(driver,td_section_id)
            s_script= """document.getElementById("%s").value='%s'"""%(tmp_new_id,u'%s'%(section.replace("'","\\'")))
            driver.execute_script(s_script)

            print "section: ", u""+section

            time.sleep(10)

            if x<=len(sections)-2:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#ctl00xcphContentxwebGridRecette_rc_"+str(x+1)+"_2 > img"))).click()
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.text"))).click()
                #print "clic sur inserer "+"#ctl00xcphContentxwebGridRecette_rc_"+str(x+1)+"_2 > img"


        if len(sections)>0:
            type0.click()
            time.sleep(10)
            print "clic sur OKok  pour fermer la saisie des sections"
            driver.find_element_by_id("ctl00_OkButton").click()

            time.sleep(10)

            driver.switch_to_window(main_window_handle)

            #Rafraichir sur clic sur traçabilité
            parent_gauche = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[11]/span/span[2]')))
            parent_gauche.click()

            time.sleep(10)

            #-----onglet Définition-----
            tab="Définition"

            #Parcours de chaque section créée
            for y in range(len(sections)):
                section=sections[y]["emballage_name"]
                section_cree = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[12]/div["+str(y+1)+"]/span/span[2]")))
                section_cree.click()
                time.sleep(5)

                #clic sur définition
                driver.find_element_by_css_selector("#ctl00_cphContent_ctl14_SpecTabView_ctl01 > span.wrap > span.innerWrap").click()
                time.sleep(15)

                #print "---tracabilite_id: ", liste_champs["ID"]

                if liste_champs!=None:
                    print "tracabilite definition id existant"
                    #definition lot
                    xpath_def_lot="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[2]/div/div/div/div[2]/textarea"

                    driver.find_element_by_xpath(xpath_def_lot).clear()
                    nom_champ="DEFINITION_LOT"
                    valeur_champ=u""+str(nz(liste_champs["DEFINITION_LOT"]))
                    driver.find_element_by_xpath(xpath_def_lot).send_keys(valeur_champ)
                    print "saisie DEFINITION_LOT"
                    #mode identification
                    xpath_mode_ident="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[3]/div/div/div/div[2]/textarea"
                    driver.find_element_by_xpath(xpath_mode_ident).clear()
                    nom_champ="EXPLICATION_CODAGE"
                    valeur_champ=u""+str(nz(liste_champs["EXPLICATION_CODAGE"]))
                    driver.find_element_by_xpath(xpath_mode_ident).send_keys(valeur_champ)

                    #taille lot
                    xpath_taille="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[4]/div/div/div/div[2]/textarea"
                    driver.find_element_by_xpath(xpath_taille).clear()
                    nom_champ="TAILLE_LOT"
                    valeur_champ=u""+str(nz(liste_champs["TAILLE_LOT"]))
                    driver.find_element_by_xpath(xpath_taille).send_keys(valeur_champ)

                    #nombre de lots
                    xpath_nombre_lots="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div[2]/div/div/div[5]/div/div/div/div[2]/textarea"
                    driver.find_element_by_xpath(xpath_nombre_lots).clear()
                    nom_champ="PREVISION_NB_LOT"
                    valeur_champ=u""+str(nz(liste_champs["PREVISION_NB_LOT"]))
                    driver.find_element_by_xpath(xpath_nombre_lots).send_keys(valeur_champ)

                    curprod.execute("select URL from DOCUMENT where ID_LISTE=%s"%(liste_champs["LISTE_DOCUMENTS_ID"]))
                    id_listes=curprod.fetchall()
                    z=0
                    for id_liste in id_listes:

                        print "1"
                        sfile1=id_liste["URL"].replace("\\", "/")
                        if sfile1.find("/")==-1:
                            tmp=sfile1
                            match = re.findall(r'^liste_[0-9]+', tmp)
                            if len(match)==0:
                                continue

                            tmp2=tmp.replace(match[len(match)-1], "")
                            rep=match[len(match)-1]
                            rep=rep.strip()

                            url=tmp2.strip()
                        else:
                            a=sfile1.split("/")
                            url=a[len(a)-1]
                            rep=sfile1.replace(url, "").strip().strip("/")
                            #rep=rep.replace("/","\\")
                        print "2"
                        #print "rep: ", rep
                        #print "url: ", url

                        #procédure de traçabilité
                        repertoire_image=repertoire_base+rep+"/" #linux
                        #repertoire_image=repertoire_base+rep+"\\" #windows

                        nom_champ="url"

                        p_j=os.path.join(repertoire_image,url)

                        valeur_champ=p_j
                        #print "repertoire url: ", repertoire_image+url
                        #print "pièce jointe: ", p_j
                        print "3"


                        #------test >60-----
                        tfilename=[] #chemin complet
                        tfile1=[] #base
                        path="/home/traceone/SYSTEME_U_FILES/PIECES_JOINTES_INIT_20160222"
                        extension=""
                        avant_extension=p_j
                        iapres_point=p_j.rfind(".")
                        if iapres_point!=-1:
                            extension=p_j[iapres_point+1:]
                            avant_extension=p_j[0:iapres_point]
                        print "extension",extension

                        if extension.upper().find("ZIP")!=-1:
                            print "niditra 1"
                            if os.path.isfile(avant_extension+"_1."+extension) ==True:
                                nom_fic1=avant_extension+"_1."+extension
                                tfilename.append(nom_fic1)
                                tfile1.append(nom_fic1.replace(path,""))
                                print "niditra 2"
                                if os.path.isfile(avant_extension+"_2."+extension) ==True:
                                    nom_fic2=avant_extension+"_2."+extension
                                    tfilename.append(nom_fic2)
                                    tfile1.append(nom_fic2.replace(path,""))
                                    print "niditra 3"
                                    if os.path.getsize(u""+nom_fic1) >=61440000 or os.path.getsize(u""+nom_fic2) >=61440000 :
                                       isaffichette_termine==False
                                       sql="""
                                           INSERT INTO
                                                    systemu_affichette_log_sys
                                                       (
                                                           affichette_id,
                                                           num_instance,
                                                           chapter,
                                                           tab,
                                                           nom_champ,
                                                           valeur_champ,
                                                           exeption,
                                                           cdc_id
                                                       )
                                                    VALUES
                                                       (
                                                           9,
                                                           %s,
                                                           'Tracabilite',
                                                           'Definition',
                                                           'url',
                                                           '%s',
                                                           '%s',
                                                            %s


                                                       )
                                           """%(num_instance,nom_fic1+ "ou "+nom_fic2+ ">=60Mo","Fichier",cdc_id)

                                       curprod.execute (sql)
                                       bfilename_sup_60mo=True
                                       continue





                                else:
                                    print "tsy nahita"
                                    isaffichette_termine==False
                                    sql="""
                                       INSERT INTO
                                                systemu_affichette_log_sys
                                                   (
                                                       affichette_id,
                                                       num_instance,
                                                       chapter,
                                                       tab,
                                                       nom_champ,
                                                       valeur_champ,
                                                       exeption,
                                                       cdc_id
                                                   )
                                                VALUES
                                                   (
                                                       9,
                                                       %s,
                                                       'Tracabilite',
                                                       'Definition',
                                                       'url',
                                                       '%s',
                                                       '%s',
                                                        %s


                                                   )
                                       """%(num_instance,avant_extension+"_2."+extension,"Fichier non trouvé",cdc_id)

                                    curprod.execute (sql)
                                    continue



                            else:
                                print "aaaaa"
                                if os.path.getsize(u""+p_j) >=61440000:
                                    isaffichette_termine==False
                                    sql="""
                                       INSERT INTO
                                                systemu_affichette_log_sys
                                                   (
                                                       affichette_id,
                                                       num_instance,
                                                       chapter,
                                                       tab,
                                                       nom_champ,
                                                       valeur_champ,
                                                       exeption,
                                                       cdc_id
                                                   )
                                                VALUES
                                                   (
                                                       9,
                                                       %s,
                                                       'Tracabilite',
                                                       'Definition',
                                                       'url',
                                                       '%s',
                                                       '%s',
                                                        %s


                                                   )
                                       """%(num_instance, sfile1+ ">=60Mo","Fichier",cdc_id)

                                    curprod.execute (sql)
                                    continue

                                tfilename.append(p_j)
                                tfile1.append(sfile1)

                                print "bbbbb"
                        else:
                            print "ccccccc"
                            if os.path.getsize(u""+p_j) >=61440000:
                                isaffichette_termine==False
                                sql="""
                                   INSERT INTO
                                            systemu_affichette_log_sys
                                               (
                                                   affichette_id,
                                                   num_instance,
                                                   chapter,
                                                   tab,
                                                   nom_champ,
                                                   valeur_champ,
                                                   exeption,
                                                   cdc_id
                                               )
                                            VALUES
                                               (
                                                   9,
                                                   %s,
                                                   'Tracabilite',
                                                   'Definition',
                                                   'url',
                                                   '%s',
                                                   '%s',
                                                    %s


                                               )
                                   """%(num_instance,sfile1+ ">=60Mo","Fichier",cdc_id)

                                curprod.execute (sql)
                                continue

                            tfilename.append(p_j)
                            tfile1.append(sfile1)

                        print "dddddd"
                        #------------------------
                        for p_j1 in tfilename:
                            (filepath, filename) = os.path.split(p_j1)
                            print "filename: ", filename
                            if z==0:
                                xpath0="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/"
                            else:
                                xpath0 = "/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/"

                            xpath1="div[3]/div/div/div[2]/div/div/div/span/div/div[2]/table/tbody/tr["+str(3+z)+"]/td[2]/span/div/span[1]/a[1]"


                            time.sleep(5)

                            xpath=xpath0+xpath1
                            print "xpath: ", xpath
                            driver.find_element_by_xpath(xpath).click()
                            print "clic sur ajout pièce definition"
                            time.sleep(5)

                            #print "window_handles2: ", driver.window_handles

                            #---Frame ajout pièce--
                            driver.switch_to.frame("RadWindowContentFrame_1")
                            print "passage au frame ajout pièce"

                            #time.sleep(4)


                            #----renommer pj-----
                            tmp=""

                            pos_virgule=filename.rfind(",")
                            if pos_virgule!=-1:
                                print "----presence de ,"
                                chaine_apres_virgule=filename[pos_virgule+1:]
                                print "1"
                                if test_apres_virgule(chaine_apres_virgule)==True:
                                    print "2"
                                    erreur = "ok"
                                else:
                                    erreur = "ko"
                                    print "3"

                                if erreur=="ok":
                                    filename2=filename[:-2]
                                    print "4"
                                    src_dir=repertoire_image
                                    old_file_name=u""+filename
                                    new_file_name=u""+filename2
                                    print "5"
                                    rep_tmp = "/home/traceone/SYSTEME_U/alimentaire/tmp/"
                                    copy_rename(src_dir, old_file_name, new_file_name,rep_tmp)
                                    print "15"
                                    tmp=rep_tmp #linux
                                    #tmp=src_dir+"tmp\\" #windows
                                    source=os.path.join(tmp, new_file_name)
                                    print "16"
                                    repertoire_image=source
                                    print "17"
                                    fichier=new_file_name
                                else:
                                    repertoire_image = repertoire_image + filename
                                    fichier=filename
                            else:
                                repertoire_image=repertoire_image + filename
                                fichier=filename
                            #----------------------
                            print "18"
                            driver.find_element_by_id("ctl00_cphContent_fileUpload").clear()
                            driver.find_element_by_id("ctl00_cphContent_fileUpload").send_keys(u""+repertoire_image)
                            print "ajout piece ok"
                            #----------------------

                            time.sleep(10)
                            driver.switch_to.default_content()
                            time.sleep(5)

                            if attente_pj (fichier)==False:
                                isaffichette_termine==False
                                sql="""
                                    INSERT INTO
                                                 systemu_affichette_log_sys
                                                    (
                                                        affichette_id,
                                                        num_instance,
                                                        chapter,
                                                        tab,
                                                       nom_champ,
                                                        valeur_champ,
                                                        exeption,
                                                        cdc_id
                                                    )
                                                 VALUES
                                                   (
                                                        9,
                                                        %s,
                                                        'Tracabilite',
                                                        'Definition',
                                                        'url',
                                                        '%s',
                                                        '%s',
                                                        %s


                                                    )
                                        """%(num_instance,filename,"Message:Erreur upload",cdc_id)

                                curprod.execute (sql)
                                prod.commit()
                                continue

                            print "fichier: ", repertoire_image

                            #---suppr tmp----
                            if tmp!="":
                                os.remove(source)
                            #----------------

                            z+=1

            time.sleep(5)
            print "Rafraichir sur clic sur traçabilite"
            parent_gauche = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[11]/span/span[2]')))
            parent_gauche.click()

            time.sleep(15)

            print "rafraichir sur tracabilite pour entrer dans aval"

            #-----onglet Traçabilité aval-----
            tab="Traçabilité aval"

            for a in range(len(sections)):
                curprod.execute("select UVC_ID from CAHIER_DES_CHARGES_EMBALLAGE where ID=%s"%(sections[a]["emballage_id"]))
                cdc_emb=curprod.fetchone()

                if cdc_emb != None:
                    print "test si UVC_ID egal a 0"
                    if nz(cdc_emb["UVC_ID"], 0) != 0:
                        print "apres test, UVC_ID different de 0"
                        curprod.execute("select IDENTIFICATION_UNITE_EMB_ID from UNITE_EMBALLAGE where ID=%s"%(cdc_emb["UVC_ID"]))
                        unite_emb=curprod.fetchone()

                        if nz(unite_emb["IDENTIFICATION_UNITE_EMB_ID"]) != "":
                            curprod.execute("select * from IDENTIFICATION_UNITE_EMBALLAGE where ID=%s"%(unite_emb["IDENTIFICATION_UNITE_EMB_ID"]))
                            identification_unite_emb=curprod.fetchone()

                            section_cree = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[12]/div["+str(a+1)+"]/span/span[2]")))
                            section_cree.click()

                            print "clic sur section"

                            time.sleep(15)

                            #---------onglet traçabilité aval---------
                            driver.find_element_by_css_selector("#ctl00_cphContent_ctl14_SpecTabView_ctl02 > span.wrap > span.innerWrap").click()
                            print "clic sur onglet tracabilite aval"
                            time.sleep(10)
                            print "onglet tracabilite aval ouvert"
                            for e in range(1):
                                #--clic sur saisie element--
                                if e==0:
                                    b=1
                                    xpath_saisie_element1="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/span[1]/div/div[2]/a"
                                else:
                                    b=b+2
                                    xpath_saisie_element1="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/span["+str(b)+"]/div/div[2]/a"

                                #print "debut attente 15s"
                                time.sleep(15)
                                #print "fin attente 15s"

                                wait.until(EC.element_to_be_clickable((By.XPATH,xpath_saisie_element1))).click()
                                print "clic sur lien saisie dans onglet tracabilite aval"

                                time.sleep(5)


                                xpath_element_trace="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/div["+str(e+1)+"]/div/div/div[1]/div/div/div/div[2]/input"

                                driver.find_element_by_xpath(xpath_element_trace).clear()
                                nom_champ="TYPE_D_EMBALLAGE"
                                valeur_champ=u""+str(nz(identification_unite_emb["TYPE_D_EMBALLAGE"]))
                                driver.find_element_by_xpath(xpath_element_trace).send_keys(valeur_champ)
                                #print "saisie sur 1er champ"

                                xpath_type="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/div["+str(e+1)+"]/div/div/div[2]/div/div/div/span/div[2]/div[1]/select"

                                Select(driver.find_element_by_xpath(xpath_type)).select_by_visible_text(u""+str(nz(identification_unite_emb["TYPE_EMBALLAGE"])))

                                xpath_marquage="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/div["+str(e+1)+"]/div/div/div[3]/div/div/div/div[2]/textarea"

                                driver.find_element_by_xpath(xpath_marquage).clear()
                                #----Ajout base TYPE_MARQUAGE-----
                                print "type marquage: ", nz(identification_unite_emb["TYPE_MARQUAGE"])
                                if nz(identification_unite_emb["TYPE_MARQUAGE"])=="":
                                    libelle=""
                                else:
                                    libelle1=nz(DLookup("LIBELLE","TYPE_MARQUAGE",prod,"CODE='"+str(identification_unite_emb["TYPE_MARQUAGE"])+"'"))
                                    if libelle1=="":
                                        libelle = identification_unite_emb["TYPE_MARQUAGE"]
                                    else:
                                        libelle = libelle1
                                print "libelle: ", libelle
                                #---------------------------------
                                mode_marquage=(nz(identification_unite_emb["EMPLACEMENT_MARQUAGE"])+" "+(str(libelle)+" "+(nz(identification_unite_emb["TYPE_MARQUAGE_PRECISION"])+" "+nz(identification_unite_emb["COULEUR"])).strip()).strip()).strip()
                                nom_champ="MARQUAGE CONCATENATION"
                                valeur_champ=u""+str(mode_marquage)
                                driver.find_element_by_xpath(xpath_marquage).send_keys(valeur_champ)
                                print "saisie mode_marquage: ", valeur_champ
                            #xpath_commentaire="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/div[5]/div/div/div[2]/div/div/div/span/div/div/div/div[1]/div[2]/textarea"
                            #driver.find_element_by_xpath(xpath_commentaire).clear()
                            #driver.find_element_by_xpath(xpath_commentaire).send_keys("Commentaire")

                #---------pièce jointe------

                sql="""
                        SELECT
                            (CASE WHEN UVC_ID IS NULL THEN 0 ELSE UVC_ID END) as UVC_ID,
                            (CASE WHEN UL_ID IS NULL THEN 0 ELSE UL_ID END) as UL_ID,
                            (CASE WHEN PALETTE_ID IS NULL THEN 0 ELSE PALETTE_ID END) as PALETTE_ID
                        FROM
                            CAHIER_DES_CHARGES_EMBALLAGE
                        WHERE
                            ID=%s

                    """%(sections[a]["emballage_id"])
                curprod.execute(sql)
                cdc_emb=curprod.fetchone()

                if cdc_emb != None:
                    curprod.execute("select  IDENTIFICATION_UNITE_EMB_ID from UNITE_EMBALLAGE where IDENTIFICATION_UNITE_EMB_ID IS NOT NULL AND ID IN (%s,%s,%s)"%(cdc_emb["UVC_ID"],cdc_emb["UL_ID"],cdc_emb["PALETTE_ID"]))
                    print "tonga eto"
                    tunite_emb=curprod.fetchall()
                    z=0
                    for unite_emb in tunite_emb:

                        curprod.execute("select * from IDENTIFICATION_UNITE_EMBALLAGE where ID=%s"%(unite_emb["IDENTIFICATION_UNITE_EMB_ID"]))
                        identification_unite_emb=curprod.fetchone()
                        if identification_unite_emb!=None:
                            curprod.execute("select URL from DOCUMENT where ID_LISTE=%s"%(identification_unite_emb["LISTE_DOCUMENTS_ID"]))
                            id_listes=curprod.fetchall()

                            for id_liste in id_listes:
                                sfile1=id_liste["URL"].replace("\\", "/")
                                if sfile1.find("/")==-1:
                                    tmp=sfile1
                                    match = re.findall(r'^liste_[0-9]+', tmp)
                                    if len(match)==0:
                                        continue

                                    tmp2=tmp.replace(match[len(match)-1], "")
                                    rep=match[len(match)-1]
                                    rep=rep.strip()

                                    url=tmp2.strip()
                                else:
                                    a=sfile1.split("/")
                                    url=a[len(a)-1]
                                    rep = sfile1.replace(url, "").strip().strip("/")
                                    #rep = rep.replace("/", "\\")

                                #print "tracabilite aval rep: ", rep
                                #print "tracabilite aval url: ", url

                                #procédure de traçabilité
                                repertoire_image=repertoire_base+rep+"/"  #linux
                                #repertoire_image=repertoire_base+rep+"\\"  #windows

                                nom_champ="url"

                                p_j=os.path.join(repertoire_image,url)
                                #(filepath, filename) = os.path.split(p_j)
                                valeur_champ=p_j
                                print "tracabilite aval pj: ",p_j
                                #print "tracabilite aval filename: ",filename

                                #----------------------------------------------------
                                #------test >60-----
                                tfilename=[] #chemin complet
                                tfile1=[] #base
                                path="/home/traceone/SYSTEME_U_FILES/PIECES_JOINTES_INIT_20160222"
                                extension=""
                                avant_extension=p_j
                                iapres_point=p_j.rfind(".")
                                if iapres_point!=-1:
                                    extension=p_j[iapres_point+1:]
                                    avant_extension=p_j[0:iapres_point]
                                print "extension",extension

                                if extension.upper().find("ZIP")!=-1:
                                    print "niditra 1"
                                    if os.path.isfile(avant_extension+"_1."+extension) ==True:
                                        nom_fic1=avant_extension+"_1."+extension
                                        tfilename.append(nom_fic1)
                                        tfile1.append(nom_fic1.replace(path,""))
                                        print "niditra 2"
                                        if os.path.isfile(avant_extension+"_2."+extension) ==True:
                                            nom_fic2=avant_extension+"_2."+extension
                                            tfilename.append(nom_fic2)
                                            tfile1.append(nom_fic2.replace(path,""))
                                            print "niditra 3"
                                            if os.path.getsize(u""+nom_fic1) >=61440000 or os.path.getsize(u""+nom_fic2) >=61440000 :
                                               isaffichette_termine==False
                                               sql="""
                                                   INSERT INTO
                                                            systemu_affichette_log_sys
                                                               (
                                                                   affichette_id,
                                                                   num_instance,
                                                                   chapter,
                                                                   tab,
                                                                   nom_champ,
                                                                   valeur_champ,
                                                                   exeption,
                                                                   cdc_id
                                                               )
                                                            VALUES
                                                               (
                                                                   9,
                                                                   %s,
                                                                   'Tracabilite',
                                                                   'Aval',
                                                                   'url',
                                                                   '%s',
                                                                   '%s',
                                                                    %s


                                                               )
                                                   """%(num_instance,nom_fic1+ "ou "+nom_fic2+ ">=60Mo","Fichier",cdc_id)

                                               curprod.execute (sql)
                                               bfilename_sup_60mo=True
                                               continue





                                        else:
                                            print "tsy nahita"
                                            isaffichette_termine==False
                                            sql="""
                                               INSERT INTO
                                                        systemu_affichette_log_sys
                                                           (
                                                               affichette_id,
                                                               num_instance,
                                                               chapter,
                                                               tab,
                                                               nom_champ,
                                                               valeur_champ,
                                                               exeption,
                                                               cdc_id
                                                           )
                                                        VALUES
                                                           (
                                                               9,
                                                               %s,
                                                               'Tracabilite',
                                                               'Aval',
                                                               'url',
                                                               '%s',
                                                               '%s',
                                                                %s


                                                           )
                                               """%(num_instance,avant_extension+"_2."+extension,"Fichier non trouvé",cdc_id)

                                            curprod.execute (sql)
                                            continue



                                    else:
                                        if os.path.getsize(u""+p_j) >=61440000:
                                            isaffichette_termine==False
                                            sql="""
                                               INSERT INTO
                                                        systemu_affichette_log_sys
                                                           (
                                                               affichette_id,
                                                               num_instance,
                                                               chapter,
                                                               tab,
                                                               nom_champ,
                                                               valeur_champ,
                                                               exeption,
                                                               cdc_id
                                                           )
                                                        VALUES
                                                           (
                                                               9,
                                                               %s,
                                                               'Tracabilite',
                                                               'Aval',
                                                               'url',
                                                               '%s',
                                                               '%s',
                                                                %s


                                                           )
                                               """%(num_instance, sfile1+ ">=60Mo","Fichier",cdc_id)

                                            curprod.execute (sql)
                                            continue

                                        tfilename.append(p_j)
                                        tfile1.append(sfile1)


                                else:
                                    if os.path.getsize(u""+p_j) >=61440000:
                                        isaffichette_termine==False
                                        sql="""
                                           INSERT INTO
                                                    systemu_affichette_log_sys
                                                       (
                                                           affichette_id,
                                                           num_instance,
                                                           chapter,
                                                           tab,
                                                           nom_champ,
                                                           valeur_champ,
                                                           exeption,
                                                           cdc_id
                                                       )
                                                    VALUES
                                                       (
                                                           9,
                                                           %s,
                                                           'Tracabilite',
                                                           'Aval',
                                                           'url',
                                                           '%s',
                                                           '%s',
                                                            %s


                                                       )
                                           """%(num_instance,sfile1+ ">=60Mo","Fichier",cdc_id)

                                        curprod.execute (sql)
                                        continue

                                    tfilename.append(p_j)
                                    tfile1.append(sfile1)


                                #------------------------
                                #----------------------------------------------------

                                #------------------------
                                for p_j1 in tfilename:
                                    (filepath, filename) = os.path.split(p_j1)

                                    xpath_pj="/html/body/form/div[9]/span/div[1]/div[4]/div/div[3]/div/div/div[3]/div/span/div[2]/div/div/div/div/div[6]/div/div/div[2]/div/div/div/span/div/div[2]/table/tbody/tr["+str(2+z)+"]/td[2]/span/div/span[1]/a[1]"

                                    driver.find_element_by_xpath(xpath_pj).click()
                                    print "clic sur Ajouter"
                                    time.sleep(8)

                                    #---Frame ajout pièce--
                                    driver.switch_to.frame("RadWindowContentFrame_1")
                                    #print "passage au frame Ajouter"

                                    time.sleep(4)

                                    #----renommer pj-----
                                    tmp=""
                                    pos_virgule=filename.rfind(",")
                                    if pos_virgule!=-1:
                                        print "----presence de ,"
                                        chaine_apres_virgule=filename[pos_virgule+1:]

                                        if test_apres_virgule(chaine_apres_virgule)==True:
                                            erreur = "ok"
                                        else:
                                            erreur = "ko"

                                        if erreur=="ok":
                                            filename2=filename[:-2]

                                            src_dir=repertoire_image
                                            old_file_name=u""+filename
                                            new_file_name=u""+filename2
                                            rep_tmp = "/home/traceone/SYSTEME_U/alimentaire/tmp/"
                                            copy_rename(src_dir, old_file_name, new_file_name,rep_tmp)
                                            tmp=rep_tmp #linux
                                            #tmp=src_dir+"tmp\\" #windows
                                            source=os.path.join(tmp, new_file_name)
                                            repertoire_image=source
                                            fichier=new_file_name
                                        else:
                                            repertoire_image = repertoire_image + filename
                                            fichier=filename
                                    else:
                                        repertoire_image=repertoire_image + filename
                                        fichier=filename
                                    #----------------------

                                    driver.find_element_by_id("ctl00_cphContent_fileUpload").clear()
                                    driver.find_element_by_id("ctl00_cphContent_fileUpload").send_keys(u""+repertoire_image)
                                    print "pj saisi"
                                    #----------------------

                                    time.sleep(10)
                                    driver.switch_to.default_content()
                                    time.sleep(5)

                                    if attente_pj (fichier)==False:
                                        isaffichette_termine==False
                                        sql="""
                                            INSERT INTO
                                                         systemu_affichette_log_sys
                                                            (
                                                                affichette_id,
                                                                num_instance,
                                                                chapter,
                                                                tab,
                                                               nom_champ,
                                                                valeur_champ,
                                                                exeption,
                                                                cdc_id
                                                            )
                                                         VALUES
                                                           (
                                                                9,
                                                                %s,
                                                                'Tracabilite',
                                                                'Aval',
                                                                'url',
                                                                '%s',
                                                                '%s',
                                                                %s


                                                            )
                                                """%(num_instance,filename,"Message:Erreur upload",cdc_id)

                                        curprod.execute (sql)
                                        prod.commit()
                                        continue

                                    print "pj aval ajoute: ", repertoire_image

                                    #---suppr tmp----
                                    if tmp!="":
                                        os.remove(source)
                                    #----------------

                                    z+=1


        print "Rafraichir sur clic sur traçabilite"
        parent_gauche = wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/form/div[9]/span/div[1]/div[4]/div/div[1]/div/div/div/span/div[1]/div[2]/div/div[2]/div[2]/div[11]/span/span[2]')))
        parent_gauche.click()

        time.sleep(2)

        if isaffichette_termine==True :
            flag=2
        else:
            flag=3

        sql="""
            UPDATE
                systemu_pousse
            SET
                flag=%s,
                date_fin=now()

            WHERE
                cdc_id=%s
                AND affichette_id=9
            """%(flag,cdc_id)
        curprod.execute(sql)
        prod.commit()

        prod.close()

        driver.close()

        if os.path.exists(os.path.basename(__file__)+'.lock')==True:
            os.remove(os.path.basename(__file__)+'.lock')

        print "termine"

        sys.exit(0)


except Exception as inst:
    if os.path.exists(os.path.basename(__file__)+'.lock')==True:
        os.remove(os.path.basename(__file__)+'.lock')

    erreur=str(inst).replace("'","''")
    print "erreur: ", erreur

    flag=3
    sql="""
        UPDATE
            systemu_pousse
        SET
            flag=%s,
            date_fin=now()

        WHERE
            cdc_id=%s
           AND affichette_id=9
        """%(flag,cdc_id)

    curprod.execute(sql)
    prod.commit()

    sql="""
    INSERT INTO systemu_affichette_log_sys
   	(affichette_id,
    	num_instance,
    	chapter,
    	section,
    	tab,
    	nom_champ,
    	valeur_champ,
    	exeption,
    	cdc_id
   	)
    	VALUES
    	(9,
    	'%s',
    	'%s',
    	'%s',
    	'%s',
    	'%s',
    	'%s',
    	'%s',
    	'%s'
    	)
    """%(num_instance,chapter,section,tab,nom_champ,valeur_champ,erreur,cdc_id)

    curprod.execute (sql.encode("cp1252"))
    prod.commit()
    prod.close()

    try:
        driver.close()
    except:
        pass

    sys.exit(0)

