import heapq
import pygame
import random
import ast

# velikost 1 je základní podle potřeby zmenšujte nebo zvětšujte
vel = 1

def load_data_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data_str = file.read()

        # Převedení řetězce na slovník pomocí modulu 'ast'
        data_dict = ast.literal_eval(data_str)

        return data_dict
    except FileNotFoundError:
        print(f"Soubor '{file_path}' nebyl nalezen.")
        return {}
    except SyntaxError:
        print(f"Nepodařilo se načíst data ze souboru '{file_path}'. Zkontrolujte formát.")
        return {}

table = load_data_from_file("table.mcl")
graph = load_data_from_file("lenghts.mcl")
citys = load_data_from_file("city.mcl")

def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    queue = [(0, start)]
    predecessors = {}
    predecessors_time = {}
    while queue:
        (current_distance, current_node) = heapq.heappop(queue)
        time = []
        if current_node == end:
            path = []
            current_time = current_node
            while current_node in predecessors:
                path.append(current_node)
                current_node = predecessors[current_node]
            path.append(start)
            path.reverse()
            while current_time in predecessors_time:
                time.append(predecessors_time[current_time])
                current_time = predecessors_time[current_time]
            time.append(0)
            time.reverse()
            return path, time
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))
                predecessors[neighbor] = current_node
                predecessors_time[neighbor] = weight
    return None, None

WIDTH, HEIGHT = 1920, 1440
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Map control for RP')
rflag = pygame.image.load("flag-red.png")
gflag = pygame.image.load("flag-green.png")
font_size = int(18 *vel)
font = pygame.font.SysFont("monocraft", font_size)

barva = (30, 90, 30)
barva2 = (16, 134, 215)

def update_tlacitko_text(name, text):
    for tlacitko in tlacitka:
        if tlacitko["jmeno"] == name:
            tlacitko["text"] = text
            break

def update_tlacitko_barva(name, barva):
    for tlacitko in tlacitka:
        if tlacitko["jmeno"] == name:
            tlacitko["barva"] = barva
            break

def rychlostplus():
    global velocity
    velocity += 1

def rychlostminus():
    global velocity
    velocity -= 1
    if velocity < 0:
        velocity = 0

def skupiny():
    global menu
    if menu == 0:
        menu = 1
    else: 
        menu = 0

def skupiny_tlacitko_barva():
    global menu
    if menu == 1:
        return barva2
    else:
        return barva

def start_mesto():
    global start, klik_mesto
    start = klik_mesto

def cil_mesto():
    global cil, klik_mesto
    cil = klik_mesto

def nevybrano_mesto(vybrano):
    if vybrano != None:
        return barva2
    else:
        return barva

def pustit_skupinu():
    global path, menu, cesty, muzem, time, finished, fractional_steps, positions, current_points, start, cil, malovani_cesty
    if path != None:
        cesty.append((path, time))
        path = None
        start = None
        cil = None
        menu = 0
        muzem = 1
        finished.append(False)
        fractional_steps.append(0.0)
        positions.append((0,0))
        current_points.append(0)
        malovani_cesty = False
        barva = (
            random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)
        )
        barvy.append(barva)

velocity = 1
start = None
cil = None

tlacitka = [
    {"jmeno": "rychlost +", "x": WIDTH - 130*vel, "y": 10*vel, "barva": barva, "sirka": 30 *vel, "vyska": 30*vel, "text": "+", "akce": rychlostplus, "pouziti": [0,1]},
    {"jmeno": "rychlost -", "x": WIDTH - 30*vel, "y": 10*vel, "barva": barva, "sirka": 30*vel, "vyska": 30*vel, "text": "-", "akce": rychlostminus, "pouziti": [0,1]},
    {"jmeno": "rychlost text", "x": WIDTH - 95*vel, "y": 10*vel, "barva": barva, "sirka": 60*vel, "vyska": 30*vel, "text": str(velocity), "akce": 0, "pouziti": [0,1]}, 

    {"jmeno": "pridani skupiny", "x": WIDTH - 130*vel, "y": 40*vel, "barva": barva, "sirka": 130*vel, "vyska": 30*vel, "text": "New group", "akce": skupiny, "pouziti": [0,1]},

    {"jmeno": "start", "x": WIDTH - 130*vel, "y": 80*vel, "barva": barva, "sirka": 130*vel, "vyska": 30*vel, "text": "start", "akce": start_mesto, "pouziti": [1]},
    {"jmeno": "cil", "x": WIDTH - 130*vel, "y": 120*vel, "barva": barva, "sirka": 130*vel, "vyska": 30*vel, "text": "cil", "akce": cil_mesto, "pouziti": [1]},
    {"jmeno": "pustit skupinu", "x": WIDTH - 130*vel, "y": 160*vel, "barva": barva, "sirka": 130*vel, "vyska": 30*vel, "text": "Go group", "akce": pustit_skupinu, "pouziti": [1]},

]

mesta_points = []
cesty = []
barvy = []

pocet_skupin = 0

map_path = "map.jpg"
map_image = pygame.image.load(map_path)
map_rect = map_image.get_rect()
map_rect.center = screen.get_rect().center

current_points = [0] * pocet_skupin
fractional_steps = [0.0] * pocet_skupin
positions = [table[path[0]] for path, _ in cesty]
finished = [False] * pocet_skupin

def menu_draw(menu):
    for tlacitko in tlacitka:
        if menu in tlacitko["pouziti"]:
            rectangle = pygame.Rect(tlacitko["x"], tlacitko["y"], tlacitko["sirka"], tlacitko["vyska"])
            pygame.draw.rect(screen, tlacitko["barva"], rectangle)
            button_text = font.render(tlacitko["text"], True, (255, 255, 255),)
            screen.blit(button_text, (tlacitko["x"] + 10*vel, tlacitko["y"] + 8*vel))

def pohyb_tecek():
        global positions, current_points, finished, fractional_steps,path,table,velocity
        # Pohyb teček
        for i, (path, _) in enumerate(cesty):
            if finished[i]:
                continue
            if current_points[i] < len(path) - 1:
                current_point_name = path[current_points[i]]
                next_point_name = path[current_points[i] + 1]

                current_x, current_y = table[current_point_name]
                next_x, next_y = table[next_point_name]

                distance = ((next_x - current_x) ** 2 + (next_y - current_y) ** 2) ** 0.5

                direction_x = (next_x - current_x) / distance
                direction_y = (next_y - current_y) / distance

                if distance > 0:
                    fractional_steps[i] += velocity / distance
                    if fractional_steps[i] >= 1.0:
                        current_points[i] += 1
                        fractional_steps[i] = 0.0
                    x = current_x + fractional_steps[i] * (next_x - current_x)
                    y = current_y + fractional_steps[i] * (next_y - current_y)
                    positions[i] = (x, y)
            elif current_points[i] == len(path) - 1:
                current_point_name = path[current_points[i]]
                current_x, current_y = table[current_point_name]
                positions[i] = (current_x, current_y)

def button_text_refresh():
    update_tlacitko_text("rychlost text", str(int(velocity)))

def klikmestobarva(tlac):
    for tlacitko in tlacitka:
        if tlacitko == tlac:
            tlacitko["barva"] = barva2
        

def button_color_refresh(): 
    for tlacitko in tlacitka:
        tlacitko["barva"] = barva
        if tlacitko["jmeno"] == klik_mesto:
            update_tlacitko_barva(tlacitko["jmeno"], barva2)

    update_tlacitko_barva("pridani skupiny", skupiny_tlacitko_barva())
    update_tlacitko_barva("start",nevybrano_mesto(start))
    update_tlacitko_barva("cil",nevybrano_mesto(cil))

mesta = []

for nazev in table:
    if nazev in citys:
        x,y = table[nazev][0], table[nazev][1]
        tlacitka.append({"jmeno": str(nazev), "x": x, "y": y, "barva": barva, "sirka": 40*vel, "vyska": 30*vel, "text": str(nazev), "akce": 1, "pouziti": [1]},)

def mesto_draw():
    global table, klik_mesto, menu
    for nazev in table:
        if nazev in citys:
            x, y = table[nazev]
            if menu in [0,2]:
                label_surface = font.render(nazev, True, (255, 255, 255))
                screen.blit(label_surface, (x + 10*vel, y - 20*vel))
            
            if nazev == start:
                screen.blit(gflag, (x - 20, y - 20))
            elif nazev == cil:
                screen.blit(rflag, (x - 20, y - 20))

def kresleni_cesty(od_bodu, kam_bodu):
    tloustka = int(5*vel)
    pygame.draw.line(screen, (70,80,90), table[od_bodu], table[kam_bodu], tloustka)

def klik_na_kolecko(x, y, skupina):
    print(f"Kliknuto na kolečko na pozici ({x}, {y}) ze skupiny {skupina}")

# Hlavní smyčka programu
running = True
menu = 0
klik_mesto = None
path = None
muzem = 0
malovani_cesty = False
skupiny = []
clock = pygame.time.Clock()

while running:
    # Zpracování událostí
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Levé tlačítko myši
                for tlacitko in tlacitka:
                    if pygame.Rect(tlacitko["x"], tlacitko["y"], tlacitko["sirka"], tlacitko["vyska"]).collidepoint(event.pos):
                        if tlacitko["akce"] == 1:
                            klik_mesto = tlacitko["jmeno"]
                        elif tlacitko["akce"] != 0:
                            tlacitko["akce"]()
                            button_text_refresh()

                for kolecko in skupiny:
                    x, y, skupina = kolecko["x"], kolecko["y"], kolecko["skupina"]
                    if pygame.Rect(x - 10*vel, y - 10*vel, 20*vel, 20*vel).collidepoint(event.pos):
                        klik_na_kolecko(x, y, skupina)

    # Vykreslení pozadí
    screen.blit(map_image, map_rect)

    menu_draw(menu)
    button_text_refresh()
    button_color_refresh()
    
    velocity = velocity *0.1
    pohyb_tecek()
    velocity = velocity *10

    if start != None and cil != None:
        path, time = dijkstra(graph,start,cil)
        malovani_cesty = True

    if path != None and menu in [1,2] and malovani_cesty:
        for i in range(len(path) - 1):
            kresleni_cesty(path[i], path[i + 1])

    mesto_draw()        

    # Vykreslení teček
    for i, position in enumerate(positions):
        color = barvy[i % len(barvy)]  # Získání barvy pro každý bod na základě indexu
        pygame.draw.circle(screen, color, (int(position[0]), int(position[1])), 15*vel)

        skupiny.append({"x": int(position[0]), "y": int(position[1]), "skupina": i})

    # Aktualizace obrazovky
    pygame.display.flip()

    clock.tick(60)  # Omezení snímkové frekvence na 60 FPS

# Ukončení programu
pygame.quit()