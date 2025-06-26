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


#####################################################################
#                                                                   #
#                        CREATION DES VARIABLES                     #
#                                                                   #
#####################################################################

#donc height = true prend par defaut la hauteur egale a celle du parent


ip=0
cpt=0
pages={}
port=5000
stop="yes"
hauteur=True
activeaddres=[]
list_item2=[]
activeaddres1=[]
last_activeaddres1=[]
dic_ipclient={}
nature='unknown'
host='127.0.1.1'
last_click_time=0
dicactiveaddress={}
ipclient='127.0.1.1'
dic_items_to_send={}
total_size_to_send=0
largeur_sidebar = 250
list_item2_selected=[]
run_socket_server=True
largeur_workarea = 1000
system=platform.system()
UPLOAD_FOLDER=Path.home()
DOWNLOAD_DIR = Path.home()
loarding=["-","\\","|","/"]
network_cidr="192.168.0.0/24"
stop_event = threading.Event()
pagewidth,pageheight=1000,1000
showtransfertsvar=False

upload_infos={}
download_infos={}

if not os.path.exists(Path.home()/"steevesharer"):
    os.mkdir(Path.home()/"steevesharer")
    os.mkdir(Path.home()/"steevesharer/Uploads")
if not os.path.exists(Path.home()/"steevesharer/Downloads"):
    os.mkdir(Path.home()/"steevesharer/Downloads")      

UPLOAD_FOLDER=Path.home()/"steevesharer/Uploads"
DOWNLOAD_DIR = Path.home()/"steevesharer/Downloads"

reseau_cidr = "192.168.43.0/24"  # <- Modifiez ici selon votre réseau

# Détection du système d'exploitation pour adapter la commande ping
param_ping = "-n" if platform.system().lower() == "windows" else "-c"

current_dir=curent=Path().home().parent.parent #a la base le dossier courant cest la racine

class Client(Container):
     def __init__(self,name="myself",ip=classes.host,list_items=[],count_items=1,position=0,size_items=0,total_sent_bits=0,family="Courier New",**kwargs):
        super().__init__(**kwargs)
        self.name=name
        self.ip=ip
        self.list_items=list_items #liste des items qui doivent etre envoyé
        self.size_items=size_items
        self.count_items=count_items
        self.position=position
        self.total_sent_bits=total_sent_bits
        self.col={"sm": 12/2, "md": 12/2, "xl": 12/2}
        self.alignment=alignment.center
        self.height=3*pageheight//8 - 50
        self.bgcolor=Colors.BLACK
        self.border=border.all(1,Colors.WHITE12)
        self.margin=margin.all(5)
        self.border_radius=20
        self.shadow=BoxShadow(spread_radius=0.9,color=Colors.WHITE12,offset=Offset(2,2))
        self.content=Column(
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                Text(self.name,color=Colors.BLUE,font_family="Courier New",text_align=TextAlign.CENTER,size=20,),
                Column(
                    scroll="auto",
                    auto_scroll=True,
                    height=3*pageheight//8 - 150,
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    spacing=15,
                    controls=[]
                )
            ] 
        )


class Myprogressbar(Container):
    def __init__(self,name="",ip=classes.host,list_items=[],evolution=0.5,size_items=0,total_sent_bits=0,family="Courier New",**kwargs):
        super().__init__(**kwargs)
        self.name=name
        self.ip=ip
        self.list_items=list_items
        self.size_items=size_items
        self.evolution=evolution
        self.total_sent_bits=total_sent_bits
        self.alignment=alignment.center
        path=Path(name)
        if path.is_dir():
            self.icon=Icon(name=Icons.FOLDER,color=Colors.AMBER,size=25)
        else:
            ext = Path(name).suffix.lower()
            iconname=Icons.INSERT_DRIVE_FILE
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                iconname=Icons.IMAGE
            elif ext in ['.mp3', '.wav', '.ogg']:
                iconname=Icons.AUDIOTRACK
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                iconname=Icons.MOVIE
            elif ext == '.pdf':
                iconname=Icons.PICTURE_AS_PDF
            elif ext in ['.doc', '.docx']:
                iconname=Icons.TEXT_SNIPPET
            elif ext in ['.xls', '.xlsx', '.csv']:
                iconname=Icons.TABLE_CHART
            elif ext in ['.zip', '.rar', '.tar', '.gz']:
                iconname=Icons.ARCHIVE
            elif ext in ['.py', '.js', '.cpp', '.java', '.html','.c','.sql','.php','.css']:
                iconname=Icons.CODE

            self.icon=Icon(name=iconname,color=Colors.GREEN,size=25)
        # self.bgcolor=Colors.RED
        # self.height=70


        self.progressbar = ProgressBar(
            width=400,
            height=20,
            border_radius=8,
            color=Colors.GREEN,
        )

        self.progressbarevolution=Text(
            width=400,
            text_align=TextAlign.CENTER,
            value=f"{evolution} %",
        )
        size_items_toMO=self.size_items/(1024**2)
        self.progressbarlabel=Text(
            value=f"{self.name} + \n {size_items_toMO:.2f} Mo",
            color=Colors.WHITE,
            text_align=TextAlign.CENTER,
            max_lines=3)
        self.progressbarcontainer=Container(
            alignment=alignment.center,
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                alignment=MainAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    Stack(
                        alignment=alignment.center,
                        controls=[
                            self.progressbar,
                            self.progressbarevolution,
                        ]
                    ),
                    Row(
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                        self.icon,
                        self.progressbarlabel,
                        ]
                    ),
                    
                ]  
            )
        )

        self.content=self.progressbarcontainer


# Conteneur 1 + poignée interne
poignee2 = GestureDetector(
    mouse_cursor=MouseCursor.RESIZE_LEFT_RIGHT,
    on_pan_update=None,  # on remplit plus tard
    content=Container(
        margin=margin.all(4),
        width=4,
        height=hauteur,
        bgcolor=Colors.TRANSPARENT,
        border_radius=4,
    ),
)

#poignee1.on_pan_update = resize1

backbutton=IconButton(
    icon=Icons.UNDO,
    icon_color=Colors.BLUE,
    icon_size=30,
    tooltip='back',
    rotate=20,
)

titlesidebar=Container(
    padding=padding.only(left=20,right=5),
    content=Text(
        value= "\U0001F4C1 {}".format(current_dir),
        color=Colors.GREEN_ACCENT_200,
        size=20,
        font_family="Times New Roman",
        text_align=TextAlign.START,
        max_lines=1,
    )
)

titlesidebarcontainer=Container(
    padding=padding.only(left=5),
    content=Row(
        controls=[
            backbutton,
            Row(
                width=350,
                scroll='auto',
                controls=[
                    titlesidebar,
                ]
            ),
        ]
    )
)

sendbutton=IconButton(
    icon=Icons.UPLOAD,
    icon_color=Colors.BLUE,
    icon_size=30,
    tooltip='envoyer',
)

researchicon=IconButton(
    icon=Icons.SEARCH,
    icon_size=30,
    icon_color=Colors.BLUE,
    tooltip="rechercher",
    on_click=lambda e:print("ok"),
)

researchfield=TextField(
    bgcolor=Colors.TRANSPARENT,
    color=Colors.BLUE,
    width=300,
    border_radius=20,
    border_color=Colors.TRANSPARENT,
    hint_text="rechercher",
    text_size=20,
    focus_color=Colors.BLUE,
    label_style=TextStyle(color=Colors.BLUE,font_family="Courier New",size=20),
    hint_style=TextStyle(color=Colors.BLUE,font_family="Courier New",size=20),
)

researchzone=Container(
    padding=padding.only(left=2,right=2),
    margin=margin.only(bottom=5,right=15,top=5),
    border_radius=30,
    border=border.all(1,Colors.BLUE),
    bgcolor=Colors.TRANSPARENT,
    content=Row(
        controls=[
            researchicon,
            researchfield,
        ]
    )
)
optionbar=Container(
    bgcolor=Colors.TRANSPARENT,
    margin=margin.only(left=2,right=20),
    height=60,
    border_radius=50,
    border=border.only(bottom=BorderSide(2,Colors.BLUE)),
    alignment=alignment.center,
    content=Row(
        alignment=MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=VerticalAlignment.CENTER,
        controls=[
            titlesidebarcontainer,
            sendbutton,
            researchzone,
        ]
    )
)

responsivezone=ResponsiveRow(
    spacing=0,
    run_spacing=0,
    controls=[
        
    ]
)

showsendingbutton=IconButton(
    icon=Icons.UPLOAD,
    icon_color=Colors.BLUE,
    icon_size=30,
    bgcolor=Colors.RED,
    tooltip=Tooltip(
        message="\" Show sending \"",
        text_align=TextAlign.CENTER,
        bgcolor=Colors.TRANSPARENT,
        text_style=TextStyle(color=Colors.RED_200,font_family="Courier New")
    ),
    content=Container(
    )
)

showrecivingbutton=IconButton(
    icon=Icons.DOWNLOAD,
    icon_color=Colors.BLUE,
    icon_size=30,
    bgcolor=Colors.RED,
    tooltip=Tooltip(
        message="\" Show reciving \"",
        text_align=TextAlign.CENTER,
        bgcolor=Colors.TRANSPARENT,
        text_style=TextStyle(color=Colors.RED_200,font_family="Courier New")
    ),
    content=Container(
    )
)

zoneshowtransfertsbutton=Container(
    expand=True,
    bottom=75,
    right=75,
    content=Row(
        alignment=MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            showsendingbutton,
            showrecivingbutton,
        ]
    )
)

workareascrollable=Container(
    margin=margin.only(left=2,right=30),
    height=pageheight-100,
    content=Stack(
        controls=[
            Column(
                scroll='auto',
                alignment=alignment.center,
                controls=[
                    responsivezone,
                ]
            ),
            zoneshowtransfertsbutton,
        ]
    )
)

workarea=Container(
    border=border.all(1,Colors.WHITE),
    height=True,
    width=1000,
    border_radius=25,
    expand_loose=True,
    content=Row(
        controls=[
            poignee2,
            Container(
                bgcolor=Colors.TRANSPARENT,
                margin=margin.only(left=2,right=2),
                height=True,
                expand=True,
                content=Column(
                    spacing=2,
                    controls=[
                        optionbar,
                        workareascrollable,
                    ]
                )
            )
        ]
    )
)



sidebar=Container(
    height=pageheight,
    border_radius=25,
    border=border.all(1,Colors.WHITE),
    bgcolor=Colors.TRANSPARENT,
    width=250,
    content=Column(
        scroll='auto',
        spacing=2,
        expand=True,
        expand_loose=True,
        alignment=MainAxisAlignment.START,
        horizontal_alignment=CrossAxisAlignment.START,
        controls=[
        ]
    )
)

accueil=Container(
    expand=True,
    border_radius=25,
    bgcolor=Colors.GREY_900,
    content=Row(
        spacing=5,
        controls=[
            sidebar,
            workarea,
        ]
    ),
)

dismiss_selecreciver_button=Container(
    alignment=alignment.center,
    padding=padding.all(5),
    content=IconButton(
        content=Text(
            size=25,
            value="  quiter...  ",
            max_lines=2,
            text_align=TextAlign.CENTER,
            font_family="Times New Roman",
            color=Colors.RED,
        ),
    )
)

main1_selectreciver=Container(
    expand=3,
    alignment=alignment.center,
    height=pageheight//3,
    content=Column(
        scroll='auto',
        height=3*pageheight//4 - 200,
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=5,
        controls=[
            
        ]
    )
)



main2_selectreciver=Row(
    width=True,
    expand=1,
    height=100,
    alignment=MainAxisAlignment.END,
    vertical_alignment=VerticalAlignment.CENTER,
    controls=[
        classes.dismiss_selecreciver_button,
    ]
)

selectreciver=AlertDialog( 
    bgcolor=Colors.TRANSPARENT,
    #bgcolor=colors.WHITE24,
    #content_padding=padding.only(0,0,0,0), 
    
    alignment=alignment.center,
    content=Container(
        height=pageheight*3/4,
        border_radius=30,
        width=pagewidth//3,
        opacity=0.9,
        alignment=alignment.center,
        bgcolor=Colors.BLUE_ACCENT_200,
        border=border.all(2,Colors.BLUE),
        padding=padding.only(top=10,bottom=10,left=5,right=5),
        content=Column(
            horizontal_alignment=CrossAxisAlignment.CENTER,
            height=3*pageheight//4 - 10,
            spacing=5,
            controls=[
                main1_selectreciver,
                main2_selectreciver,
            ]
        ),
    ),
#on_di
# smiss=lambda e:print("fermer")
)



responsivetransferts_sendcontent=ResponsiveRow(
    spacing=0,
    run_spacing=0,
    controls=[
    ]
)

transferts_sendcontent=Column(
    horizontal_alignment=CrossAxisAlignment.CENTER,
    height=3*pageheight//4 - 10,
    spacing=5,
    scroll='auto',
    controls=[
        responsivetransferts_sendcontent,
    ]
)

transferts_send=AlertDialog( 
    bgcolor=Colors.TRANSPARENT,
    #bgcolor=colors.WHITE24,
    #content_padding=padding.only(0,0,0,0),
    title = Row(
        alignment=MainAxisAlignment.CENTER,
        controls=[
        Icon(name=Icons.UPLOAD, color="blue",size=60),
        Text("En cours de transfert...", size=30, color=Colors.AMBER,font_family="Times New Roman"),
        ]
    ),
    
    alignment=alignment.center,
    content=Container(
        height=pageheight*3/4,
        border_radius=30,
        width=pagewidth,
        opacity=0.9,
        alignment=alignment.center,
        #bgcolor=Colors.BLUE_ACCENT_200,
        bgcolor=Colors.BLACK,
        border=border.all(2,Colors.WHITE12),
        padding=padding.only(top=10,bottom=10,left=5,right=5),
        content=transferts_sendcontent,
    ),
#on_dismiss=lambda e:print("fermer")
)

responsivetransferts_recivecontent=ResponsiveRow(
    spacing=0,
    run_spacing=0,
    controls=[
    ]
)

transferts_recivecontent=Column(
    horizontal_alignment=CrossAxisAlignment.CENTER,
    height=3*pageheight//4 - 10,
    spacing=5,
    scroll='auto',
    controls=[
        responsivetransferts_recivecontent,
    ]
)

transferts_recive=AlertDialog( 
    bgcolor=Colors.TRANSPARENT,
    #bgcolor=colors.WHITE24,
    #content_padding=padding.only(0,0,0,0), 
    title = Row(
        alignment=MainAxisAlignment.CENTER,
        controls=[
            Icon(name=Icons.DOWNLOAD, color="blue",size=60),
            Text("En cours de reception...", size=30, color=Colors.AMBER,font_family="Times New Roman")
        ]
    ),
    alignment=alignment.center,
    content=Container(
        height=pageheight*3/4,
        border_radius=30,
        width=pagewidth,
        opacity=0.9,
        alignment=alignment.center,
        #bgcolor=Colors.BLUE_ACCENT_200,
        bgcolor=Colors.BLACK,
        border=border.all(2,Colors.WHITE12),
        padding=padding.only(top=10,bottom=10,left=5,right=5),
        content=transferts_recivecontent,
    ),
#on_dismiss=lambda e:print("fermer")
)

pages={
    "/accueil":View(
        route="/",
        bgcolor=Colors.BLACK,
        controls=[
            accueil,
        ],
    ),
}

class Item2(Container):
    def openfile(self,*args):
        if self.type!="dir":
            if system=="Windows":
                os.startfile(self.father/self.name)
            elif system=="Darwin": #pour macOs 
                subprocess.run(["open",self.father/self.name])
            elif system=="Linux":
                try:
                    subprocess.run(["xdg-open",self.father/self.name])
                except Exception as e:
                    print("erreur!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",e)

    def loardchilditems2(self,e,*args):
        global current_dir,list_item2,last_click_time,list_item2_selected,total_size_to_send
        curent_lick_time=time.time()
        if curent_lick_time - last_click_time > 0.5:

            fullname=str(self.father/self.name)
            if self.selected=="yes":
                self.bgcolor=Colors.TRANSPARENT
                self.selected="no"
                list_item2_selected.remove(fullname)
            else:
                list_item2_selected.append(fullname)
                if len(list_item2_selected)==1:
                    #signifie que cest le premier item a etre selectionne 
                    # donc total_size_to_send repasse a 0
                    # et on vide la liste des transfert en cours (le transferts_sendcontent)
                    # classes.responsivetransferts_sendcontent.controls=[]
                    # classes.responsivetransferts_sendcontent.update()
                    pass

                #total_size_to_send+=self.size
                self.bgcolor=Colors.BLUE_100
                self.selected="yes"
            #print(len(list_item2_selected))
            #print(f"********{total_size_to_send}*************")
            self.update()
        else:
            if self.type=="dir": #sil est un dossier
                
                list_dir2=[]
                list_file2=[]

                #on noublie pas que lors du doubleclique le premier clique se fait toujours
                #a plus de demis seconde apres le precedent
                #donc apres un doubleclique sur un dossier on doit lui refaire le jeu du clique
                #puisque le premier clique du doubleclique a change son etat

                fullname=str(self.father/self.name)
                if self.selected=="yes":
                    self.bgcolor=Colors.TRANSPARENT
                    self.selected="no"
                    list_item2_selected.remove(fullname)
                else:
                    list_item2_selected.append(fullname)
                    self.bgcolor=Colors.BLUE_100
                    self.selected="yes"
                #print(len(list_item2_selected))
                self.update()

                current_dir=self.father/self.name
                str_curent_dir=str(current_dir)

                titlesidebar.content.value="\U0001F4C1 "+ str_curent_dir
                titlesidebar.update()

                for element in current_dir.iterdir(): #on les gardent d'abord dans deux listes afin de les trier par ordre alphabetique
                    if str(current_dir/element.name) in list_item2_selected:
                        selected="yes"
                    else:
                        selected="no"
                    if element.is_dir() and not element.name.startswith("."):
                        list_dir2.append(Item2(name=element.name,father=current_dir,color=Colors.BLUE,selected=selected,type="dir"))
                    elif element.is_file() and not element.name.startswith("."):
                        list_file2.append(Item2(name=element.name,father=current_dir,color=Colors.BLUE,selected=selected,type="file"))

                #on fati le trie sur le nom du item

                list_dir2=sorted(list_dir2,key=lambda item:item.name)
                list_file2=sorted(list_file2,key=lambda item:item.name)
                list_item2=list_dir2+list_file2

                responsivezone.controls=[
                    Container(
                        col={"sm": 12/5, "md": 12/10, "xl": 12/15},
                        padding=padding.all(5),
                        content=Column(
                            spacing=2,
                            controls=[
                            item2,
                            ]
                        )
                    ) for item2 in list_item2
                ]
            else:
                self.openfile()

        last_click_time=curent_lick_time
        responsivezone.update()


    def __init__(self,name:str,father:Path,type:str,color:Colors,selected="no",family="Courier New",**kwargs):
        super().__init__(**kwargs)
        self.name=name
        self.father=father
        self.type=type
        self.size=os.path.getsize(self.father/self.name)
        self.color=color
        self.border_radius=10
        self.selected=selected
        if self.selected=="yes":
            self.bgcolor=Colors.BLUE_100
        else:
            self.bgcolor=Colors.TRANSPARENT
        self.tooltip=Tooltip(
            message=self.name[:20]+"..."+self.name[-8:],
            bgcolor=Colors.TRANSPARENT,
            text_align=TextAlign.CENTER,
            text_style=TextStyle(color=Colors.BLUE),
        )
        if len(self.name)<29:
            self.tooltip.message=self.name

        self.title=Text(
            value=self.name,
            size=12,
            color=Colors.BLUE,
            max_lines=1,
            width=50,
            text_align=TextAlign.CENTER,
        )

        if (self.type=="dir"):
            self.mainicon=Icon(name=Icons.FOLDER,color=Colors.AMBER,size=30)
        else:
            ext = Path(name).suffix.lower()
            iconname=Icons.INSERT_DRIVE_FILE
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                iconname=Icons.IMAGE
            elif ext in ['.mp3', '.wav', '.ogg']:
                iconname=Icons.AUDIOTRACK
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                iconname=Icons.MOVIE
            elif ext == '.pdf':
                iconname=Icons.PICTURE_AS_PDF
            elif ext in ['.doc', '.docx']:
                iconname=Icons.TEXT_SNIPPET
            elif ext in ['.xls', '.xlsx', '.csv']:
                iconname=Icons.TABLE_CHART
            elif ext in ['.zip', '.rar', '.tar', '.gz']:
                iconname=Icons.ARCHIVE
            elif ext in ['.py', '.js', '.cpp', '.java', '.html','.c','.sql','.php','.css']:
                iconname=Icons.CODE
            self.mainicon=Icon(name=iconname,color=Colors.GREEN,size=25)
            
        # shema possible avec les informations sous forme de menu deroulant sur l'item2
        # self.content=IconButton(
        #     on_click=lambda e, objet=self:self.loardchilditems2(e,objet),
        #     content=Column(
        #         spacing=2,
        #         horizontal_alignment=CrossAxisAlignment.CENTER,
        #         alignment=alignment.center,
        #         controls=[
        #             Row(
        #                 alignment=MainAxisAlignment.CENTER,
        #                 controls=[
        #                     self.mainicon,
        #                     Icon(name=Icons.MORE_VERT,color=Colors.BLUE,size=20,),
        #                 ]
        #             ),
        #             self.title,
        #         ]
        #     ),
        # )

        self.content=IconButton(
            on_click=lambda e, objet=self:self.loardchilditems2(e,objet),
            content=Column(
                spacing=2,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                alignment=alignment.center,
                controls=[
                    self.mainicon,
                    self.title,
                ]
            ),
        )

class Item(Container):#les filtres sur les types de cycle de la side nave
    
    def openfile(self,*args):
        if self.type!="dir":
            if system=="Windows":
                os.startfile(self.father/self.name)
            elif system=="Darwin": #pour macOs 
                subprocess.run(["open",self.father/self.name])
            elif system=="Linux":
                try:
                    subprocess.run(["xdg-open",self.father/self.name])
                except Exception as e:
                    print("erreur!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",e)

    def loardchilditems(self,e,*args):
        global current_dir,list_item2,last_click_time
        curent_lick_time=time.time()
        if curent_lick_time - last_click_time > 0.5:
            list_dir=[]
            list_file=[]
            list_dir2=[]
            list_file2=[]

            if self.type=="dir": #sil est un dossier
                if self.foled=="yes": #s'il n'est pas encore deployé on le deploye
                    current_dir=self.father/self.name
                    str_curent_dir=str(current_dir)

                    titlesidebar.content.value="\U0001F4C1 "+ str_curent_dir
                    titlesidebar.update()
                    self.foledicon.name=Icons.KEYBOARD_ARROW_DOWN

                    if len(self.content.content.content.controls)==1:#s'il na qu'un seul fils (son titre) ca veut dire qu'on ne l'a jamais ouvert
                        for element in current_dir.iterdir(): #on les gardent d'abord dans deux listes afin de les trier par ordre alphabetique
                            if element.is_dir() and not element.name.startswith("."):
                                list_dir.append(Item(name=element.name,father=current_dir,color=Colors.BLUE,type="dir"))
                                list_dir2.append(Item2(name=element.name,father=current_dir,color=Colors.BLUE,type="dir"))
                            elif element.is_file() and not element.name.startswith("."):
                                list_file.append(Item(name=element.name,father=current_dir,color=Colors.BLUE,type="file"))
                                list_file2.append(Item2(name=element.name,father=current_dir,color=Colors.BLUE,type="file"))

                        #on fati le trie sur le nom du item
                        list_dir=sorted(list_dir,key=lambda item:item.name)
                        list_file=sorted(list_file,key=lambda item:item.name)

                        list_dir2=sorted(list_dir2,key=lambda item:item.name)
                        list_file2=sorted(list_file2,key=lambda item:item.name)
                        list_item2=list_dir2+list_file2

                        responsivezone.controls=[
                            Container(
                                col={"sm": 12/5, "md": 12/10, "xl": 12/15},
                                padding=padding.all(5),
                                content=Column(
                                    spacing=2,
                                    controls=[
                                    item2,
                                    ]
                                )
                            ) for item2 in list_item2
                        ]

                        #on insert l'item
                        for dir in list_dir:
                            self.content.content.content.controls.append(
                                dir
                            )

                        for file in list_file:
                            self.content.content.content.controls.append(
                                file
                            )

                    else: #sinon il avait deja ete ouvert auparavant donc on rerend visible tous ses enfants  
                        for elt in self.content.content.content.controls[1:]:
                            elt.visible=True

                    self.foled="no" #on le met a l'etat deployé
                    
                else: #s'il est deja deployé on le referme
                    str_curent_dir=str(current_dir)
                    titlesidebar.content.value="\U0001F4C1 "+ str_curent_dir
                    titlesidebar.update()
                    self.foledicon.name=Icons.CHEVRON_RIGHT


                    self.content.content.content.controls=self.content.content.content.controls[:1]

                    #(self.father/self.name).resolve().relative_to(current_dir.resolve()) # si oui alors le dossier courant est un sous dossier du dossier actuel on ne peut pas le detruire


                    self.foled="yes"
        else:
            self.openfile()

        last_click_time=curent_lick_time
        self.update()
        responsivezone.update()


    def __init__(self,name:str,father:Path,type:str,color:Colors,foled="yes",family="Courier New",**kwargs):
        super().__init__(**kwargs)
        self.name=name
        self.father=father
        self.type=type
        self.foled=foled
        self.color=color
        self.title=Text(self.name,size=15,color=Colors.BLUE)
        #self.on_click=lambda e, objet=self:self.loardchilditems(e,objet)

        if (self.type=="dir"):
            self.mainicon=Icon(name=Icons.FOLDER,color=Colors.AMBER,size=30)
            self.margin=margin.only(left=0)
            if(self.foled=='yes'):
                self.foledicon=Icon(name=Icons.KEYBOARD_ARROW_RIGHT,color=Colors.BLUE,size=20)
        else:
            self.margin=margin.only(left=20)
            ext = Path(name).suffix.lower()
            iconname=Icons.INSERT_DRIVE_FILE
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                iconname=Icons.IMAGE
            elif ext in ['.mp3', '.wav', '.ogg']:
                iconname=Icons.AUDIOTRACK
            elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
                iconname=Icons.MOVIE
            elif ext == '.pdf':
                iconname=Icons.PICTURE_AS_PDF
            elif ext in ['.doc', '.docx']:
                iconname=Icons.TEXT_SNIPPET
            elif ext in ['.xls', '.xlsx', '.csv']:
                iconname=Icons.TABLE_CHART
            elif ext in ['.zip', '.rar', '.tar', '.gz']:
                iconname=Icons.ARCHIVE
            elif ext in ['.py', '.js', '.cpp', '.java', '.html']:
                iconname=Icons.CODE

            self.mainicon=Icon(name=iconname,color=Colors.GREEN,size=25)
            self.foledicon=Container(content=None)

        self.frametitle=IconButton(
            content=Row(
                controls=[
                    self.foledicon,
                    self.mainicon,
                    self.title,
                ]
            ),
        )

        self.frametitle.on_click=lambda e, objet=self:self.loardchilditems(e,objet)

        self.content=Container(
            bgcolor=Colors.TRANSPARENT,
            margin=margin.only(left=10),
            content=Container(
                margin=margin.only(left=0),
                content=Column(
                    controls=[
                        self.frametitle,
                    ]
                )
            )
        )

#-----------------------------------------------------------------------------------------
