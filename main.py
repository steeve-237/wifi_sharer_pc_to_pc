import signal
from functions import *

system=classes.platform.system()

def main(page:Page):
    def updateactiveaddres():#met a jour la liste d'addess disponible sur le reseau local
        while not classes.stop_event.is_set():
            if findnetwork():
                network= [str(octet) for octet in classes.host.split(".")[:3]]
                classes.network_cidr= network[0]+"."+network[1]+"."+network[2]+".0/24"
                classes.activeaddres=scann_network(classes.network_cidr,page=page)

    def scann_network(reseau,page):
        # ip_net = ipaddress.ip_network(reseau, strict=False) : crée un objet réseau à partir de ton CIDR.
        # ip_net.hosts() donne toutes les adresses IP utilisables (pas l’IP réseau ni broadcast).
        # ThreadPoolExecutor(max_workers=100) : lance jusqu’à 100 pings en parallèle (accélère beaucoup le scan !)
        # executor.map(ping, ip_net.hosts()) : on ping toutes les IP du réseau
        ip_net = ipaddress.ip_network(reseau, strict=False)
        print(f"Scan en cours sur le réseau : {reseau} ...")

        classes.last_activeaddres1 = []
        classes.last_activeaddres1=classes.last_activeaddres1+classes.activeaddres1
        classes.activeaddres1=[]

        # Utilisation de threads pour accélérer
        with ThreadPoolExecutor(max_workers=100) as executor:
            resultats = executor.map(ping, ip_net.hosts())

        for ip in resultats:
            if ip:
                print(f"[+] Hôte actif : {ip}")
                classes.activeaddres1.append(ip)
                try:
                    r=requests.get(f"http://{ip}:5000/myname",timeout=2)
                    username=r.text
                except:
                    username="inconnu"
                classes.dic_ipclient[ip]=username

                if ip not in classes.last_activeaddres1:
                    if username!="inconnu":
                        classes.activeaddres.append(ip)
                    if ip==classes.host:
                        texte=f" \"{username}\"  (moi-même) à rejoin le resieau...\n {ip}"
                    else:
                        texte=f"\"{username}\" à rejoin le resieau...\n {ip}"
                    
                    page.overlay.append(
                        SnackBar(
                            open=True,
                            duration=7000, #7secondes de latence
                            content=Text(
                                text_align=TextAlign.CENTER,
                                value=texte,
                                color=Colors.AMBER,
                                size=30,
                                font_family="Times New Roman",
                            )
                        )
                    )
                    page.update()

        for ip in classes.last_activeaddres1:
            if ip not in classes.activeaddres1:
                page.overlay.append(
                    SnackBar(
                        open=True,
                        duration=7000, #7secondes
                        content=Text(
                            text_align=TextAlign.CENTER,
                            value=f"\"{classes.dic_ipclient[ip]}\" est parti(e)...\n{ip}",
                            color=Colors.RED,
                            size=30,
                            font_family="Times New Roman",
                        )
                    )
                )
                page.update()
                classes.dic_ipclient.pop(ip,None) #on supprime l'ip du dictionnaire de client retourne none si la cle nexiste pas

        print("\nScan terminé.")
        return classes.activeaddres1

    def changeroute(*agrs):
        page.views.clear()
        page.views.append(
            classes.pages[page.route]
        )
        page.update()
    
    def onclose (*args):
        print("arret des soket et serveur")
        classes.stop_event.is_set()
        requests.post(f"http://{classes.host}:5000/shutdown")

    page.title='filestransfert'
    page.bgcolor='black'
    page.window.height=700
    page.window.width=True

    page.on_resized=lambda e,p=page:updatepage(e,p)
    page.on_route_change=changeroute

    page.theme=Theme(
        scrollbar_theme=ScrollbarTheme(
            track_color={
                ControlState.HOVERED: Colors.WHITE, #je ne sais pas a quoi ca sert
                ControlState.DEFAULT: Colors.TRANSPARENT, #je ne sais pas a quoi ca sert
            },
            track_visibility=True,
            thumb_visibility=True,
            thumb_color={
                ControlState.HOVERED: Colors.BLUE,
                ControlState.DEFAULT: Colors.BLUE,
            },
            thickness=5,
            track_border_color=Colors.BLUE,
            radius=10,
            main_axis_margin=5,
            cross_axis_margin=1,
        ),
    )

    classes.poignee2.on_pan_update = resize2
    classes.poignee2.height=classes.sidebar.height
    classes.workarea.on_hover = on_hover2
    classes.poignee2.on_pan_update = resize2
    classes.poignee2.height=classes.sidebar.height
    classes.workarea.on_hover = on_hover2
    classes.backbutton.on_click=lambda e:loardchilditembackbutton()
    classes.sendbutton.on_click=lambda e,: sendselecteditems()
    classes.showsendingbutton.on_click=lambda e,: showsending()
    classes.transferts_send.on_dismiss=lambda e,: dissmis_showsending()
    classes.showrecivingbutton.on_click=lambda e,: showreciving()
    classes.transferts_recive.on_dismiss=lambda e,: dissmis_showreciving()
    classes.researchfield.on_change=lambda e,:onchangeresearch()
    classes.researchicon.on_click=lambda e,:onchangeresearch()
    classes.dismiss_selecreciver_button.on_click=lambda e,:dismiss_selectreciver()

    #page.add(classes.body)
    
    page.go("/accueil")
    loarddirhome(classes.current_dir)
    page.overlay.append(classes.selectreciver)
    page.overlay.append(classes.transferts_send)
    page.overlay.append(classes.transferts_recive)
    classes.selectreciver.open=False
    classes.transferts_send.open=False
    classes.transferts_recive.open=False
    page.on_close=onclose
    page.update()

    network= [str(octet) for octet in classes.host.split(".")[:3]]
    classes.network_cidr= network[0]+"."+network[1]+"."+network[2]+".0/24"
    classes.activeaddres=scann_network(classes.network_cidr,page=page)

    start_socket_server=threading.Thread(target=launch_socket_server)
    start_update_activeaddres=threading.Thread(target=updateactiveaddres)
    start_socket_server.start()
    start_update_activeaddres.start()

app(target=main)

requests.post(f"http://{classes.host}:5000/shutdown")
classes.stop_event.is_set()
try:
    os.kill(os.getpid(),signal.SIGINT)
except:
    pass
os.system("exit")
