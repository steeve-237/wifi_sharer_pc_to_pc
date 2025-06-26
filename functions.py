import os
import time
import socket
import shutil
import classes
import getpass
import tempfile 
import requests
import platform
import ipaddress
import threading
import subprocess
from flet import *
from pathlib import *
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, send_from_directory,abort,jsonify,request, Response

current_dir=classes.Path().home().parent.parent

ip=0
cpt=0
pages={}
port=5000
stop="yes"
hauteur=True
list_item2=[]
classes.activeaddres=[]
nature='unknown'
last_click_time=0
largeur_sidebar = 250
largeur_workarea = 1000
UPLOAD_FOLDER="uploads"
classes.host='127.0.1.1'
system=platform.system()
UPLOAD_FOLDER=Path.home()
DOWNLOAD_DIR = Path.home()
loarding=["-","\\","|","/"]
classes.list_item2_selected=[]
pagewidth,pageheight=1000,1000


if not os.path.exists(Path.home()/"steevesharer"):
    os.mkdir(Path.home()/"steevesharer")
    os.mkdir(Path.home()/"steevesharer/Uploads")
if not os.path.exists(Path.home()/"steevesharer/Downloads"):
    os.mkdir(Path.home()/"steevesharer/Downloads")      

UPLOAD_FOLDER=Path.home()/"steevesharer/Uploads"
DOWNLOAD_DIR = Path.home()/"steevesharer/Downloads"

reseau_cidr = "192.168.43.0/24"  # <- Modifiez ici selon votre réseau (c'etait pour un teste)

# Détection du système d'exploitation pour adapter la commande ping
param_ping = "-n" if platform.system().lower() == "windows" else "-c"

current_dir=curent=Path().home().parent.parent #a la base le dossier courant cest la racine


#####################################################################
#                                                                   #
#                        CREATION DES FONCTIONS                     #
#                                                                   #
#####################################################################

# dans ce fichier il faut maintenant gerer:
# 0. mettre une icone sur le nom de chaque item en cours de telechargement dans la zone de chaque client (dans chaque alertdialoge)
# 1. la connection et deconnection dun client avec les alert snackbar 
# les options (supprimer,renommer,copier,couper et coller sur chaque items),et puis faire le drag and drop
# 2. le pourcentage denvoi total de chaque utilisateur
# 3. la repatition des client dans les alerts dialoge en fonction du nombre de client
# 4. laffichage des items qui seront telecharge dans la liste de telechargement propre a chaque utilisateur#

def resize2(e: DragUpdateEvent):
    global largeur_sidebar,pagewidth
    largeur_sidebar=classes.sidebar.width

    #print(pagewidth, workarea.width)
    nouvelle_largeur = largeur_sidebar + e.delta_x
    if (249<nouvelle_largeur<(pagewidth//4)):
        largeur_sidebar=nouvelle_largeur
        classes.sidebar.width = largeur_sidebar
        classes.workarea.width = classes.workarea.width - e.delta_x
        classes.sidebar.update()
        classes.workarea.update()
        classes.titlesidebar.update()
        classes.responsivezone.update()

classes.poignee2.on_pan_update = resize2
classes.poignee2.height=classes.sidebar.height
#-----------------------------------------------------------------------------------------

def on_hover2(e: HoverEvent):
    if (classes.poignee2.content.bgcolor==Colors.TRANSPARENT):
        classes.poignee2.content.bgcolor=Colors.BLUE
    else:
        classes.poignee2.content.bgcolor=Colors.TRANSPARENT

    classes.poignee2.update()

classes.workarea.on_hover = on_hover2

#-----------------------------------------------------------------------------------------

def updatepage(e,p):
    global pagewidth,pageheight

    pagewidth=p.width
    pageheight=p.height
    classes.sidebar.width=p.width//4
    classes.workarea.width=p.width//4*3
    classes.sidebar.height=pageheight
    classes.workarea.height=pageheight
    classes.workareascrollable.height=pageheight-100
    classes.sidebar.update()
    classes.titlesidebar.update()
    classes.workareascrollable.update()
    classes.workarea.update()
#-----------------------------------------------------------------------------------------

classes.poignee2.on_pan_update = resize2
classes.poignee2.height=classes.sidebar.height
classes.workarea.on_hover = on_hover2

#-----------------------------------------------------------------------------------------
def loarddirhome(path:classes.Path):
    classes.current_dir=path
    classes.sidebar.content.controls=classes.sidebar.content.controls[:1]

    list_dir=[]
    list_file=[]

    #on affiche d'abord les dossiers
    for element in classes.current_dir.iterdir():
        if element.is_dir() and not element.name.startswith("."):
            list_dir.append(classes.Item(name=element.name,father=classes.current_dir,color=Colors.BLUE,type="dir"))
        elif element.is_file() and not element.name.startswith("."):
            list_file.append(classes.Item(name=element.name,father=classes.current_dir,color=Colors.BLUE,type="file"))

    list_dir=sorted(list_dir,key=lambda item:item.name)
    list_file=sorted(list_file,key=lambda item:item.name)

    for dir in list_dir:
        classes.sidebar.content.controls.append(
        dir
        )
    for file in list_file:
        classes.sidebar.content.controls.append(
        file
        )

#-----------------------------------------------------------------------------------------

classes.backbutton.on_click=lambda e:loardchilditembackbutton()

#-----------------------------------------------------------------------------------------
def loardchilditembackbutton(*args):
    global list_item2
    list_dir2=[]
    list_file2=[]

    classes.current_dir=classes.current_dir.parent
    str_curent_dir=str(classes.current_dir)

    classes.titlesidebar.content.value="\U0001F4C1 "+ str_curent_dir
    classes.titlesidebar.update()

    for element in classes.current_dir.iterdir(): #on les gardent d'abord dans deux listes afin de les trier par ordre alphabetique
        if str(classes.current_dir/element.name) in classes.list_item2_selected:
            selected="yes"
        else:
            selected="no"
        if element.is_dir() and not element.name.startswith("."):
            list_dir2.append(classes.Item2(name=element.name,father=classes.current_dir,color=Colors.BLUE,selected=selected,type="dir"))
        elif element.is_file() and not element.name.startswith("."):
            list_file2.append(classes.Item2(name=element.name,father=classes.current_dir,color=Colors.BLUE,selected=selected,type="file"))
    #on fati le trie sur le nom du item

    list_dir2=sorted(list_dir2,key=lambda item:item.name)
    list_file2=sorted(list_file2,key=lambda item:item.name)
    list_item2=list_dir2+list_file2

    classes.responsivezone.controls=[
    Container(
        col={"sm": 12/5, "md": 12/10, "xl": 12/15},
        padding=padding.all(5),
        content=Column(
            spacing=2,
            controls=[item2,]
            )
        ) for item2 in list_item2
    ]

    classes.responsivezone.update()

classes.backbutton.on_click=lambda e:loardchilditembackbutton()

#-----------------------------------------------------------------------------------------
def setipclient(e,ip,*args):
    # classes.upload_infos[ip]={"countdown":0,"countup":0,"length":classes.total_size_to_send,"sent_bits":0,"recived_bits":0}
    # classes.ipclient=ip
    classes.selectreciver.open=False
    classes.selectreciver.update()

    #maintenant on doit chercher a selectioner lutilisateur a qui on veut envoye
    for item in classes.list_item2_selected:
        path=Path(item)
        size=os.path.getsize(path)
        if path.is_dir():
            socket_send_command(ipclient=ip,pre="folder",item=item,size=size)
        else:
            socket_send_command(ipclient=ip,pre="file",item=item,size=size)

    classes.list_item2_selected=[]
    #on finit on update l'item sinon il vas rester blue j'usqu'au prochen changement de la 
    #page
    for elemt in classes.responsivezone.controls:
        if elemt.content.controls[0].selected=="yes":
            elemt.content.controls[0].selected="no"
            elemt.content.controls[0].bgcolor=Colors.TRANSPARENT
            elemt.content.controls[0].update()
#-----------------------------------------------------------------------------------------
def dismiss_selectreciver(*args):
    classes.selectreciver.open=False
    classes.selectreciver.update()
#-----------------------------------------------------------------------------------------
def sendselecteditems(*args):
    if len(classes.list_item2_selected)>0:
        #chaque fois qu'on clique sur le bouton envoi on reinitialise le tableau daffichage de transferts_send
        #classes.upload_infos={}

        #classes.ipclient=classes.activeaddres[len(classes.activeaddres)-1]
        classes.main1_selectreciver.content.controls.clear()
        classes.main1_selectreciver.content.controls.append(
            Text(
                size=25,
                value="selectionnez un destinataire",
                max_lines=2,
                text_align=TextAlign.CENTER,
                font_family="Times New Roman",
                color=Colors.RED,
            ),
        )
        for ip in classes.activeaddres:
            visuel=True
            identifiants=''
            try:
                r=requests.get(f"http://{ip}:5000/myname",timeout=1)
                if ip!=classes.host:
                    identifiants=f"{r.text}\n{ip}"
                else:
                    identifiants=f"{r.text} ( moi-même )\n{ip}"
            except:
                visuel=False
                identifiants=None
            finally:
                classes.main1_selectreciver.content.controls.append(
                    IconButton(
                        visible=visuel,
                        content=Text(
                            value=identifiants,#on affiche le nom mais on utilise lip pour la requette
                            size=20,
                            max_lines=3,
                            expand=True,
                            color=Colors.BLACK,
                            width=pagewidth//3,
                            weight=FontWeight.BOLD,
                            text_align=TextAlign.CENTER,
                            font_family="Times New Roman",
                            #color=Colors.GREEN_ACCENT_200,
                        ),
                    on_click=lambda e,ip=ip:setipclient(e,ip),#ici on utilise bien l'ip pour la requette
                    )
                )
    else:
        classes.main1_selectreciver.content.controls.clear()
        classes.main1_selectreciver.content.controls.append(
            Text(
                size=25,
                value="aucun fichier ou dossier\n n'a ete selectioné",
                max_lines=2,
                text_align=TextAlign.CENTER,
                font_family="Times New Roman",
                color=Colors.GREEN_ACCENT_200,
            ),
        )

    classes.selectreciver.open=True
    classes.selectreciver.update()

classes.sendbutton.on_click=lambda e,: sendselecteditems(e,)
#-----------------------------------------------------------------------------------------
def dissmis_showsending(*args):
    classes.transferts_send.open=False
    classes.transferts_send.update()
    
#-----------------------------------------------------------------------------------------
def showsending(*args):
    classes.transferts_send.open=True
    classes.transferts_send.update()

classes.showsendingbutton.on_click=lambda e,: showsending(e,)

#-----------------------------------------------------------------------------------------
def dissmis_showreciving(*args):
    classes.transferts_recive.open=False
    classes.transferts_recive.update()
    
#-----------------------------------------------------------------------------------------
def showreciving(*args):
    classes.transferts_recive.open=True
    classes.transferts_recive.update()

classes.showrecivingbutton.on_click=lambda e,: showreciving(e,)
#-----------------------------------------------------------------------------------------
def onchangeresearch(*args):
    research_list_item2=[]
    for item in classes.list_item2:
        if (classes.researchfield.value.lower() in item.name.lower()):
            research_list_item2.append(item)

    classes.responsivezone.controls=[
        Container(
            col={"sm": 12/5, "md": 12/10, "xl": 12/15},
            padding=padding.all(5),
            content=Column(
                spacing=2,
                controls=[
                item2,
                ]
            )
        ) for item2 in research_list_item2
    ]
    
    classes.responsivezone.update()

classes.researchfield.on_change=lambda e,:onchangeresearch
classes.researchicon.on_click=lambda e,:onchangeresearch

#-----------------------------------------------------------------------------------------

reseau_cidr = "192.168.43.0/24"  # <- Modifiez ici selon votre réseau

# Détection du système d'exploitation pour adapter la commande ping
param_ping = "-n" if platform.system().lower() == "windows" else "-c"

def findnetwork():
    global cpt 
    while True:
        try:
            # Crée un socket UDP (User Datagram Protocol)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Se connecte à une adresse IP (ici 10.255.255.255) et un port arbitraires.
            # L'important est de ne pas se connecter à l'extérieur,
            # mais de forcer le socket à déterminer l'interface et l'adresse IP locales.
            # 10.255.255.255 est une adresse réservée, peu probable d'être réellement utilisée.
            s.connect(('10.255.255.255', 1))

            # Récupère l'adresse IP locale du socket
            classes.host = s.getsockname()[0]
            print("a new network connection have been detected!")
            s.close()
            break
        except Exception:
            if platform.system() == "Windows":
                os.system("cls")
            else:
                os.system("clear")

            print(f"waitting for network {loarding[cpt]}")
            time.sleep(1)   
            cpt+=1
            if cpt==4:
                cpt=0
            if platform.system() == "Windows":
                os.system("cls")
            else:
                os.system("clear")

    print("\nconnection established with ip: ",classes.host)
    return classes.host

def ping(ip):
    # Cette fonction ping une adresse IP.
    # ["ping", param_ping, "1", "-w", "500", str(ip)] :
    # "1" : on envoie 1 seul paquet
    # -w 500 : temps d’attente maximum (100 ms = 0.1 s)
    # check_output exécute la commande et capture la sortie.
    # Si la machine répond, on retourne l’adresse IP.
    # Si elle ne répond pas (timeout), on attrape l’erreur et retourne None.

    try:
        # Envoie un ping avec 1 paquet
        output = subprocess.check_output(
            ["ping", param_ping, "1", "-w", "100", str(ip)],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        return str(ip)
    except subprocess.CalledProcessError:
        return None

def launch_flask_server():#pour les multiples connections simultanee
    appflask.run(host=classes.host,port=port,threaded=True)

def socketdownload_file(SERVER_URL,filename,size=0):
    path=Path(filename)
    name=path.name
    uploaf_from=path.parent
    file_size=size

    local_path = os.path.join(classes.DOWNLOAD_DIR, name)
    
    try:
        surl=SERVER_URL.split(":") 
        #ip su server se trouve apres le premier ":" apres les "//"
        #et fini juste avant les ":" qui suivent directement
        ipserver=surl[1][2:]

        if ipserver not in classes.download_infos.keys():
            servername="myself"
            if ipserver!=classes.host:
                r=requests.get(f"http://{ipserver}:5000/myname",timeout=2)
                servername=r.text
                sent_bits=0
            list_itmes=[name]
            file_size=size
            size_items=size
            classes.download_infos[ipserver]=classes.Client(ip=ipserver,name=servername,list_items=list_itmes,size_items=size_items,position=len(classes.download_infos))
            classes.download_infos[ipserver].content.controls[1].controls.append(
                classes.Myprogressbar(name=name,ip=ipserver,evolution=0,size_items=file_size)
            )
            classes.responsivetransferts_recivecontent.controls.append(classes.download_infos[ipserver])
        else:
            classes.download_infos[ipserver].content.controls[1].controls.append(
                classes.Myprogressbar(name=name,ip=ipserver,evolution=0,size_items=file_size)
            )
            classes.download_infos[ipserver].count_items+=1
            classes.download_infos[ipserver].total_sent_bits+=file_size
            classes.download_infos[ipserver].list_items.append(name)
            classes.responsivetransferts_recivecontent.controls[len(classes.responsivetransferts_recivecontent.controls)-1]=classes.download_infos[ipserver]

        classes.responsivetransferts_recivecontent.update()
        classes.transferts_recive.update()

        r = requests.get(
            f"{SERVER_URL}/download/",
            params={"parent":uploaf_from,"name":name},
            stream=True,
            )
        r.raise_for_status()
        file_length=int(r.headers.get('Content-Length')) 
        with open(local_path, "wb") as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=32768):
                # r.iter_content: Cette méthode permet de lire la réponse HTTP progressivement par petits morceaux ("chunks"),
                # ce qui est très utile pour les gros fichiers (comme les vidéos, fichiers ZIP, etc.).
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    percent = downloaded / file_length * 100
                    index=classes.download_infos[ipserver]
                    evolution=downloaded/file_length
                    if round(evolution*100,2)==int(evolution*100):
                        percentevolution=int(evolution*100)
                    else:
                        percentevolution=f"{evolution*100:.2f}"
                    percentevolution=float(percentevolution)
                    #la position de lindex dans le tableau est son numero - 1
                    # et surtout on recupere le progressbar de lelement precis pour le rendre mieux maleable#
                    #progressbar=classes.upload_infos[ip_client].content.controls[1].controls[index.count_items-1]
                    progressbar=classes.download_infos[ipserver].content.controls[1].controls[len(classes.download_infos[ipserver].content.controls[1].controls)-1]
                    #on set le progressbar et son label
                    progressbar.progressbar.value=evolution
                    if evolution < 1:
                        progressbar.progressbar.bgcolor=Colors.AMBER
                    else:
                        progressbar.progressbar.bgcolor=Colors.TRANSPARENT

                    progressbar.progressbarevolution.value=f"{percentevolution} %"
                    progressbar.progressbarlabel.value=f"{name} \n (taille:  {file_length/(1024**2):.2f}  Mo)"
                    positionserver=index.position
                    progressbar.update()
                    print("index du progress bar",index.count_items-1)
                    print("progress bar value",progressbar.progressbar.value)
                    print("progress bar label",progressbar.progressbarlabel.value)
                    #classes.responsivetransferts_sendcontent.controls[positionclient].content.controls[1].controls[index.count_items-1]=progressbar
                    #classes.responsivetransferts_sendcontent.controls[positionclient].content.controls[1].controls[index.count_items-1].update()
                    classes.responsivetransferts_recivecontent.controls[positionserver].content.controls[1].controls[len(classes.responsivetransferts_recivecontent.controls[positionserver].content.controls[1].controls)-1]=progressbar
                    classes.responsivetransferts_recivecontent.update()
                    print(f"etat du progressbar {index.count_items-1}:  { classes.responsivetransferts_recivecontent.controls[positionserver].content.controls[1].controls[index.count_items-1].progressbar.value} ")
                    classes.transferts_recive.update()
                    if platform.system() == "Windows":
                        os.system("cls")
                    else:
                        os.system("clear")
                    print(f"Téléchargé: {percent:.2f}%")
        print(f"✅ {filename} téléchargé avec succès")
    except Exception as e:
        pass
    
def socketdownload_folder(SERVER_URL, foldername, size=0):

    path = Path(foldername)
    name = path.name
    upload_from = path.parent
    file_size = size

    zip_name = name + ".zip"
    local_zip_path = os.path.join(classes.DOWNLOAD_DIR, zip_name)

    try:
        # Récupération de l'IP serveur
        surl = SERVER_URL.split(":")
        ipserver = surl[1][2:]

        # Initialisation info téléchargement
        if ipserver not in classes.download_infos.keys():
            servername = "myself"
            if ipserver != classes.host:
                try:
                    r = requests.get(f"http://{ipserver}:5000/myname", timeout=2)
                    servername = r.text
                except Exception:
                    pass

            classes.download_infos[ipserver] = classes.Client(
                ip=ipserver,
                name=servername,
                list_items=[zip_name],
                size_items=file_size,
                position=len(classes.download_infos)
            )

            classes.download_infos[ipserver].content.controls[1].controls.append(
                classes.Myprogressbar(name=zip_name, ip=ipserver, evolution=0, size_items=file_size)
            )
            classes.responsivetransferts_recivecontent.controls.append(classes.download_infos[ipserver])
        else:
            client = classes.download_infos[ipserver]
            client.content.controls[1].controls.append(
                classes.Myprogressbar(name=zip_name, ip=ipserver, evolution=0, size_items=file_size)
            )
            client.count_items += 1
            client.total_sent_bits += file_size
            client.list_items.append(zip_name)
            classes.responsivetransferts_recivecontent.controls[-1] = client

        classes.responsivetransferts_recivecontent.update()
        classes.transferts_recive.update()

        # Téléchargement
        r = requests.get(
            f"{SERVER_URL}/download_folder",
            params={"parent": upload_from, "name": name},
            stream=True,
        )
        r.raise_for_status()
        file_length = int(r.headers.get('Content-Length'))

        with open(local_zip_path, "wb") as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    percent = downloaded / file_length * 100
                    index = classes.download_infos[ipserver]
                    evolution = downloaded / file_length
                    percentevolution = round(evolution * 100, 2)

                    progressbar = index.content.controls[1].controls[-1]
                    progressbar.progressbar.value = evolution
                    progressbar.progressbarevolution.value = f"{percentevolution:.2f} %"
                    progressbar.progressbarlabel.value = f"{zip_name} \n (taille: {file_length / (1024 ** 2):.2f} Mo)"
                    progressbar.progressbar.bgcolor = Colors.AMBER if evolution < 1 else Colors.TRANSPARENT

                    positionserver = index.position
                    classes.responsivetransferts_recivecontent.controls[positionserver].content.controls[1].controls[-1] = progressbar
                    classes.responsivetransferts_recivecontent.update()
                    classes.transferts_recive.update()
                    if platform.system() == "Windows":
                        os.system("cls")
                    else:
                        os.system("clear")
                    print(f"Téléchargé: {percent:.2f}%")

        print(f"✅ {zip_name} téléchargé avec succès (non extrait) dans : {local_zip_path}")

    except Exception as e:
        print(f"❌ Erreur pendant le téléchargement : {e}")

def launch_socket_server():
    global con,address,sockets
    while not classes.stop_event.is_set():
        sockets.listen(1)
        con,address=sockets.accept()
        requete_client=con.recv(1024)
        if requete_client:
            requete_client=requete_client.decode("utf-8")
            split_requete_client=requete_client.split(" ")
            dernier_morceau_requette_client=split_requete_client[len(split_requete_client)-1]
            if split_requete_client[0]=="file":
                print("download file")
                #on extrait normalement lentete du paquet pour etre sur que le filename ne contient pas
                #luimeme un caractere special place dans le split+2 a cause des 2 espaces on sarrete avant le debut du dernier
                # compartiment et le / doit resterpour signaler au pc que cest le chemin d'un dossier
                filename=requete_client[len(split_requete_client[0])+len(split_requete_client[1])+2:-(len(dernier_morceau_requette_client)+1)]
                socketdownload_file(SERVER_URL=split_requete_client[1], filename=filename,size=int(dernier_morceau_requette_client))
            elif split_requete_client[0]=="folder":
                print("download folder")
                filename=requete_client[len(split_requete_client[0])+len(split_requete_client[1])+2:-(len(dernier_morceau_requette_client)+1)]
                socketdownload_folder(SERVER_URL=split_requete_client[1], foldername=filename,size=int(dernier_morceau_requette_client))
        
        con.close()
    print("arret de la socket d'ecoute....")
    sockets.close()

def socket_send_command(ipclient:str,item:str,pre="file",size=0):
    #ici je ne sais pas encore si plusieurs pc peuvent se connecter en meme temps
    #sur le socket_server donc dans le futur on essaira une bucle infinie avec un try
    #ou encore plus on essaira de creer le socket_server en mode multiconnection(en utilisant les threads)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ipclient,5001))
    url=f"http://{classes.host}:5000"
    suf=str(item)
    command=pre+" "+url+" "+suf+" "+str(size)
    s.send(command.encode("utf-8"))
    s.close()

def converttowindows(word:str):
    word=word.split("/")
    tampon=""
    for i in range(len(word)-1):
        tampon=tampon+word[i]+"\\"
    tampon=tampon+word[len(word)-1]
    return tampon

def converttolinux(word:str):
    word=word.split("\\")
    tampon=""
    for i in range(len(word)-1):
        tampon=tampon+word[i]+"/"
    tampon=tampon+word[len(word)-1]
    return tampon
#===================================== Main ====================================  

appflask = Flask(__name__)
os.makedirs(classes.UPLOAD_FOLDER, exist_ok=True)

# notons bien qu'ici on vas utiliser:
# ....le telechargement par streaming pour lenvoi des fichier volumineux
# .... on demmare le serveur en mode thread ( threaded=True ) pour les connections simultanees #

@appflask.route('/shutdown', methods=['POST'])
def shutdown():
    print("arret du serveur...")
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return 'Erreur : le serveur ne peut pas être arrêté depuis ce contexte.'
    func()
    if platform.system() == "Windows":
        os.system("quit")
    else:
        os.system("quit")
    return 'Serveur Flask arrêté proprement.'

@appflask.route("/")
def welcom():
    return "bonjour bro"

@appflask.route("/myname")
def myname():
    #recuperation de l'ip ...

    if request.headers.getlist("X-Forwarded-For"):
        ip_client=request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_client=request.remote_addr
    
    if ip_client not in classes.activeaddres:
        classes.activeaddres.append(ip_client)

    return getpass.getuser()

@appflask.route("/files")
def list_files():
    return jsonify(os.listdir(UPLOAD_FOLDER))

@appflask.route("/download/", methods=['GET'])
def download_file():
    upload_from = request.args.get("parent")
    name = request.args.get("name")

    # Adaptation chemin selon OS
    if platform.system() == "Windows":
        upload_from = converttowindows(upload_from)
        name = converttowindows(name)
    else:
        upload_from = converttolinux(upload_from)
        name = converttolinux(name)

    file_path = Path(upload_from) / name

    if not file_path.is_file():
        return {"error": "Fichier introuvable"}, 404

    #recuperation de l'ip ...

    if request.headers.getlist("X-Forwarded-For"):
        ip_client=request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_client=request.remote_addr

    #recuperation de la taille du fichier
    file_size=os.path.getsize(file_path)
    file_name=name

    #initialisation des informations sur le telechargement
    if ip_client not in classes.upload_infos.keys():
        client_name="myself"
        if ip_client!=classes.host:
            r=requests.get(f"http://{ip_client}:5000/myname",timeout=2)
            client_name=r.text
            sent_bits=0
            total_sent_bits=0
        list_itmes=[file_name]
        size_items=file_size
        classes.upload_infos[ip_client]=classes.Client(ip=ip_client,name=client_name,list_items=list_itmes,size_items=size_items,position=len(classes.upload_infos))
        classes.upload_infos[ip_client].content.controls[1].controls.append(
            classes.Myprogressbar(name=file_name,ip=ip_client,evolution=0,size_items=file_size)
        )
        classes.responsivetransferts_sendcontent.controls.append(classes.upload_infos[ip_client])
    else:
        classes.upload_infos[ip_client].content.controls[1].controls.append(
            classes.Myprogressbar(name=file_name,ip=ip_client,evolution=0,size_items=file_size)
        )
        classes.upload_infos[ip_client].count_items+=1
        classes.upload_infos[ip_client].total_sent_bits+=file_size
        classes.upload_infos[ip_client].list_items.append(file_name)
        classes.responsivetransferts_sendcontent.controls[len(classes.responsivetransferts_sendcontent.controls)-1]=classes.upload_infos[ip_client]

    classes.responsivetransferts_sendcontent.update()
    classes.transferts_send.update()

    #fin ititialisation et debut du travail
    range_header = request.headers.get('Range', None)

    def generate_range(start, end):
        nonlocal sent_bits
        with open(file_path, 'rb') as f:
            f.seek(start)
            bytes_left = end - start + 1
            chunk_size = 32768 #2^15 bits
            sent_bits=0

            while bytes_left > 0:
                read_size = min(chunk_size, bytes_left)
                chunk = f.read(read_size)
                if not chunk:
                    break
                yield chunk
                sent_bits+=len(chunk)
                bytes_left -= len(chunk)
                index=classes.upload_infos[ip_client]
                evolution=sent_bits/file_size
                if round(evolution*100,2)==int(evolution*100):
                    percentevolution=int(evolution*100)
                else:
                    percentevolution=f"{evolution*100:.2f}"
                percentevolution=float(percentevolution)
                #la position de lindex dans le tableau est son numero - 1
                # et surtout on recupere le progressbar de lelement precis pour le rendre mieux maleable#
                #progressbar=classes.upload_infos[ip_client].content.controls[1].controls[index.count_items-1]
                progressbar=classes.upload_infos[ip_client].content.controls[1].controls[len(classes.upload_infos[ip_client].content.controls[1].controls)-1]
                #on set le progressbar et son label
                progressbar.progressbar.value=evolution
                if evolution < 1:
                    progressbar.progressbar.bgcolor=Colors.BLUE
                else:
                    progressbar.progressbar.bgcolor=Colors.TRANSPARENT

                progressbar.progressbarevolution.value=f"{percentevolution} %"
                progressbar.progressbarlabel.value=f"{file_name} \n (taille:  {file_size/(1024**2):.2f}  Mo)"
                positionclient=index.position
                progressbar.update()
                print("index du progress bar",index.count_items-1)
                print("progress bar value",progressbar.progressbar.value)
                print("progress bar label",progressbar.progressbarlabel.value)
                #classes.responsivetransferts_sendcontent.controls[positionclient].content.controls[1].controls[index.count_items-1]=progressbar
                #classes.responsivetransferts_sendcontent.controls[positionclient].content.controls[1].controls[index.count_items-1].update()
                classes.responsivetransferts_sendcontent.controls[positionclient].content.controls[1].controls[len(classes.responsivetransferts_sendcontent.controls[positionclient].content.controls[1].controls)-1]=progressbar
                classes.responsivetransferts_sendcontent.update()
                print(f"etat du progressbar {index.count_items-1}:  { classes.responsivetransferts_sendcontent.controls[positionclient].content.controls[1].controls[index.count_items-1].progressbar.value} ")
                classes.transferts_send.update()

                # Calcul et affichage du pourcentage
                

    if range_header:
        try:
            range_value = range_header.strip().split('=')[1]
            start_str, end_str = range_value.split('-')
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1

            if start >= file_size:
                return abort(416)

            content_length = end - start + 1
            response = Response(generate_range(start, end), status=206, mimetype='application/octet-stream')
            response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Content-Length', str(content_length))
            response.headers.add('Content-Disposition', f'attachment; filename="{name}"')
            return response
        except Exception as e:
            return f"Erreur dans le Range: {str(e)}", 400

    return Response(generate_range(0, file_size - 1),
        mimetype='application/octet-stream',
        headers={
            'Content-Length': str(file_size),
            'Accept-Ranges': 'bytes',
            'Content-Disposition': f'attachment; filename="{name}"'
        }
    )

@appflask.route("/download_folder/", methods=["GET"])
def download_folder():
    upload_from = request.args.get("parent")
    name = request.args.get("name")

# Adaptation chemin selon OS
    if platform.system() == "Windows":
        upload_from = converttowindows(upload_from)
        name = converttowindows(name)
    else:
        upload_from = converttolinux(upload_from)
        name = converttolinux(name)

    folder_path = Path(upload_from) / name
    if not folder_path.is_dir():
        return {"error": "Dossier introuvable"}, 404

    # Création du zip temporaire
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    zip_path = Path(temp_zip.name)
    temp_zip.close()
    shutil.make_archive(zip_path.with_suffix("").as_posix(), 'zip', folder_path.as_posix())
    zip_path = zip_path.with_suffix(".zip")
    file_size = os.path.getsize(zip_path)
    file_name = f"{folder_path.name}.zip"

    # Récupération de l'IP
    if request.headers.getlist("X-Forwarded-For"):
        ip_client = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_client = request.remote_addr

    # Initialisation des infos de transfert
    if ip_client not in classes.upload_infos:
        client_name = "myself"
        if ip_client != classes.host:
            try:
                r = requests.get(f"http://{ip_client}:5000/myname", timeout=2)
                client_name = r.text
            except Exception:
                pass
        classes.upload_infos[ip_client] = classes.Client(
            ip=ip_client,
            name=client_name,
            list_items=[file_name],
            size_items=file_size,
            position=len(classes.upload_infos)
        )
        classes.upload_infos[ip_client].content.controls[1].controls.append(
            classes.Myprogressbar(name="\U0001F4C1 "+file_name, ip=ip_client, evolution=0, size_items=file_size)
        )
        classes.responsivetransferts_sendcontent.controls.append(classes.upload_infos[ip_client])
    else:
        client = classes.upload_infos[ip_client]
        client.content.controls[1].controls.append(
            classes.Myprogressbar(name="\U0001F4C1 "+file_name, ip=ip_client, evolution=0, size_items=file_size)
        )
        client.count_items += 1
        client.total_sent_bits += file_size
        client.list_items.append(file_name)
        classes.responsivetransferts_sendcontent.controls[-1] = client

    classes.responsivetransferts_sendcontent.update()
    classes.transferts_send.update()

    # Streaming avec Range et progression
    range_header = request.headers.get("Range", None)

    def generate_range(start, end):
        nonlocal file_size
        sent_bits = 0
        with zip_path.open("rb") as f:
            f.seek(start)
            bytes_left = end - start + 1
            chunk_size = 32768 #2^15bit

            while bytes_left > 0:
                read_size = min(chunk_size, bytes_left)
                chunk = f.read(read_size)
                if not chunk:
                    break
                yield chunk
                sent_bits += len(chunk)
                bytes_left -= len(chunk)

                # Mise à jour progression
                index = classes.upload_infos[ip_client]
                evolution = sent_bits / file_size
                percentevolution = round(evolution * 100, 2)

                progressbar = index.content.controls[1].controls[-1]
                progressbar.progressbar.value = evolution
                progressbar.progressbarevolution.value = f"{percentevolution:.2f} %"
                progressbar.progressbarlabel.value = f"{file_name} \n (taille: {file_size / (1024 ** 2):.2f} Mo)"
                progressbar.progressbar.bgcolor = Colors.BLUE if evolution < 1 else Colors.TRANSPARENT

                classes.responsivetransferts_sendcontent.controls[index.position].content.controls[1].controls[-1] = progressbar
                classes.responsivetransferts_sendcontent.update()
                classes.transferts_send.update()

        # Nettoyage après envoi complet
        try:
            zip_path.unlink()
        except:
            pass

    # Réponse partielle ou complète
    if range_header:
        try:
            range_value = range_header.strip().split('=')[1]
            start_str, end_str = range_value.split('-')
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1

            if start >= file_size:
                return abort(416)

            content_length = end - start + 1
            response = Response(generate_range(start, end), status=206, mimetype='application/zip')
            response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Content-Length', str(content_length))
            response.headers.add('Content-Disposition', f'attachment; filename="{file_name}"')
            return response
        except Exception as e:
            try:
                zip_path.unlink()
            except:
                pass
            return f"Erreur dans le Range: {str(e)}", 400

    # Réponse complète
    return Response(generate_range(0, file_size - 1),
        mimetype='application/zip',
        headers={
            'Content-Length': str(file_size),
            'Accept-Ranges': 'bytes',
            'Content-Disposition': f'attachment; filename="{file_name}"'
        }
    )

#---------------------------------------------------------------------------------------

if findnetwork():
    #ici on resort une fois avec l'adres ip du pc courant (qui execute la commande)
    #maintenant on se prepare a la connection et a lenvois des fichiers
    
    sockets=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sockets.bind((classes.host,5001))

    start_fask_server=threading.Thread(target=launch_flask_server)
    start_fask_server.start()