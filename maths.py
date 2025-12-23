import pygame, math, random, time

width = 500
height = 500
radius = 20
front_color = (255, 255, 255)
back_color = (2, 2, 2)
gravity = pygame.Vector2(0, 0.1)
elasticity = 0.9
friction_float = 0.995  # 1 = sin fricción, 0 = se para en seco
randomness = False
tension = False
number = 20
timer = 0
mouse_radius = 20
fps = 60
string_tolerance = 0
points = [
    {"Position": pygame.Vector2(200, 200), "Velocity": pygame.Vector2(-10, 0), "Connections": [1], "Radius": 20, "Fixed": False, "Gravity": True},
    {"Position": pygame.Vector2(220, 200), "Velocity": pygame.Vector2(0, 0), "Connections": [0,2], "Radius": 20, "Fixed": False, "Gravity": True},
    {"Position": pygame.Vector2(240, 200), "Velocity": pygame.Vector2(0, 0), "Connections": [1,3], "Radius": 20, "Fixed": False, "Gravity": True},
    {"Position": pygame.Vector2(260, 200), "Velocity": pygame.Vector2(0, 0), "Connections": [2,4], "Radius": 20, "Fixed": False, "Gravity": True},
    {"Position": pygame.Vector2(280, 200), "Velocity": pygame.Vector2(0, 0), "Connections": [3,5], "Radius": 20, "Fixed": False, "Gravity": True},
    {"Position": pygame.Vector2(300, 200), "Velocity": pygame.Vector2(0, 0), "Connections": [4], "Radius": 20, "Fixed": False, "Gravity": True},
]

lines = [
    {"1": pygame.Vector2(500, 0), "2": pygame.Vector2(500, 500)},
    {"1": pygame.Vector2(0, -1), "2": pygame.Vector2(500, 0)},
    {"1": pygame.Vector2(-1, 0), "2": pygame.Vector2(0, 500)},
    {"1": pygame.Vector2(0, 500), "2": pygame.Vector2(500, 500)}
]

def draw_point(point, screen):
    pygame.draw.circle(screen, front_color, point["Position"], 3, 5)
    pygame.draw.circle(screen, front_color, point["Position"], point["Radius"], 2)

def draw_line(line, screen):
    pygame.draw.line(screen, front_color, line["1"], line["2"])

def move_point(point_index):
    if points[point_index].get("Fixed", False):
        return  # No se mueve, no hay gravedad
    if points[point_index].get("Gravity", True):
        points[point_index]["Velocity"] += gravity
    points[point_index]["Position"] += points[point_index]["Velocity"] * delta_time


        

def punto_proyeccion(A, C, W):
    W2 = W.length_squared()
    if W2 == 0:
        return A
    t = (C - A).dot(W) / W2
    P = A + W * t
    return P

def apply_tension(point, other, point_index, other_index):
    if other_index in point.get("Connections", []):
        W = other["Position"] - point["Position"]
        distance = W.length()
        if distance >= point["Radius"] + other["Radius"] + string_tolerance:
            if point["Fixed"] == True:
                other["Position"] -= (distance - point["Radius"] - other["Radius"]) * W.normalize()
            elif other["Fixed"] == True:
                point["Position"] += (distance - point["Radius"] - other["Radius"]) * W.normalize()
            else:
                point["Position"] += (distance - point["Radius"] - other["Radius"]) * W.normalize() / 2
                other["Position"] -= (distance - point["Radius"] - other["Radius"]) * W.normalize() / 2
            

        


def correct_overlap(point, other):
    W = other["Position"] - point["Position"]
    distance = W.length()
    if distance <= radius * 2: # Se tocan
        overlap = ((2 * radius) - distance) / 2 # Cuanto se tocan
        # Evitar que se atravisen
        point["Position"] -= overlap * W.normalize()
        other["Position"] += overlap * W.normalize()

def line_colissions(point, line, previous_point):
    strike_point = punto_proyeccion(line["1"], point["Position"], (line["2"] - line["1"]).normalize())
    W = point["Position"] - strike_point
    distance = W.length()
    if distance <= point["Radius"]:
        C = point["Position"] + point["Velocity"]
        P = punto_proyeccion(point["Position"], C, pygame.Vector2(-(line["2"] - line["1"]).y, (line["2"] - line["1"]).x))
        V1point = [pygame.Vector2(P - point["Position"]), pygame.Vector2(C - P)]
        if V1point[0].length() < 0.2:
            print ("Hola")
            V1point = [pygame.Vector2(0, 0), pygame.Vector2(C - P)]
        if V1point[1].length() < 0.2:
            V1point = [pygame.Vector2(P - point["Position"]), pygame.Vector2(0, 0)]
        point["Velocity"] = -elasticity * V1point[0] + V1point[1] * friction_float
    if distance < point["Radius"]:
        overlap = point["Radius"] - distance
        point["Position"] += overlap * W.normalize()

def points_colissions(point, other):
    W = pygame.Vector2(other["Position"] - point["Position"]) # Vector entre los dos centros
    distance = W.length()
    if distance <= radius * 2: # Se tocan
        overlap = ((2 * radius) - distance) / 2 # Cuanto se tocan
        # Evitar que se atravisen
        point["Position"] -= overlap * W.normalize()
        other["Position"] += overlap * W.normalize()
        collisioning = [point, other]
        ## Cálculo de la velocidad de point respecto de el eje de choque
        C = point["Position"] + point["Velocity"]
        # Hallar el punto P (donde va la altura)
        P = punto_proyeccion(point["Position"], C, W)
        # Hallar las velocidades descompuestas (medida de la altura del triángulo P, C, Position = Vy)
        V1point = [pygame.Vector2(P - point["Position"]), pygame.Vector2(C - P)]
        W = pygame.Vector2(other["Position"] - point["Position"]) # Vector entre los dos centros
        ## Cálculo de la velocidad de other respecto de el eje de choque
        C = other["Position"] + other["Velocity"]
        # Hallar el punto P (donde va la altura)
        P = punto_proyeccion(other["Position"], C, W)
        # Hallar las velocidades descompuestas (medida de la altura del triángulo P, C, Position = Vy)
        V1other = [pygame.Vector2(P - other["Position"]), pygame.Vector2(C - P)]
        ## Creación de nuevas velocidades
        if V1point[0].length() < 0.1:
            V1point[0] = pygame.Vector2(0, 0)
        if V1other[0].length() < 0.1:
            V1other[0] = pygame.Vector2(0, 0)
        V2point = (pygame.Vector2(V1other[0]) + pygame.Vector2(V1point[1]))
        V2other = (pygame.Vector2(V1point[0]) + pygame.Vector2(V1other[1]))
        # Vuelta a las coordenadas globales
        point["Velocity"] = V2point
        other["Velocity"] = V2other

def mouse():
    created = False
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed(num_buttons=3)[0] == True:
                mouse = pygame.Vector2(pygame.mouse.get_pos())
                for i in range(len(points)):
                    W = pygame.Vector2(mouse - points[i]["Position"])
                    distance = W.length()
                    if created == False:
                        for t in range(len(points)):
                            if points[t]["Position"] == mouse:
                                created = True
                    if created == False:
                        if distance <= mouse_radius:
                            points.append({"Position": mouse, "Velocity" : pygame.Vector2(0, 0), "Connections" : [i]})
                            points[i]["Connections"].append(len(points) - 1)
                            break
                    else:
                        points[-1]["Connections"].append(i)
                        points[i]["Connections"].append(len(points) - 1)
    if pygame.mouse.get_pressed(num_buttons=3)[2] == True:
        mouse = pygame.Vector2(pygame.mouse.get_pos())
        for i in range(len(points)):
            W = pygame.Vector2(mouse - points[i]["Position"])
            distance = W.length()
            if distance <= mouse_radius:
                points[i]["Position"] = mouse
                points[i]["Velocity"] = pygame.Vector2(0, 0)
                points[i]["Fixed"] = True
    else:
        for point in points:
            point["Fixed"] = False

def physics():
    global previus_points
    previus_points = []
    for p in points:
        previus_points.append({
    "Position": p["Position"].copy(),
    "Velocity": p["Velocity"].copy(),
    "Connections": p["Connections"][:],
    "Radius": p["Radius"],
    "Fixed": p["Fixed"]
})

    # 3. Colisiones por posición (evitar solapamientos)
    COLLISION_ITERATIONS = 4
    for _ in range(COLLISION_ITERATIONS):
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                correct_overlap(points[i], points[j])

    # 4. Respuesta de colisión (solo si realmente la necesitas)
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            points_colissions(points[i], points[j])
    
    for i in range(len(points)):
        for j in range(len(lines)):
            line_colissions(points[i], lines[j], previus_points[i])
    
    # 2. Restricciones por posición (tensión)
    if tension == True:
        CONSTRAINT_ITERATIONS = 20
        for _ in range(CONSTRAINT_ITERATIONS):
            for i in range(len(points)):
                for j in range(i + 1, len(points)):
                    apply_tension(points[i], points[j], i, j)

    for i in range(len(points)):
        move_point(i)
        points[i]["Gravity"] = True
    

            

    





def main():
    global delta_time
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Simulación física")
    clock = pygame.time.Clock()
    while True:
        global previus_previus_points
        previus_previus_points = []
        for p in points:
            previus_previus_points.append({
    "Position": p["Position"].copy(),
    "Velocity": p["Velocity"].copy(),
    "Connections": p["Connections"][:],
    "Radius": p["Radius"],
    "Fixed": p["Fixed"]
})

        delta_time = clock.tick(fps) / (fps / 4)
        time.sleep(timer)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill(back_color)
        physics()
        for line in lines:
            draw_line(line, screen)
        for point in points:
            mouse()
            draw_point(point, screen)
        pygame.display.flip()


main()


