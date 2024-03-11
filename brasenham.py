def bresenham_line(x1, y1, x2, y2):
    points = []
    
    # Oblicz różnice
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    # Określ kierunek
    if x1 < x2:
        step_x = 1
    else:
        step_x = -1
    
    if y1 < y2:
        step_y = 1
    else:
        step_y = -1
    
    # Oblicz kroki
    if dx > dy:
        p = 2 * dy - dx
        while x1 != x2:
            points.append((x1, y1))
            if p >= 0:
                y1 += step_y
                p -= 2 * dx
            x1 += step_x
            p += 2 * dy
    else:
        p = 2 * dx - dy
        while y1 != y2:
            points.append((x1, y1))
            if p >= 0:
                x1 += step_x
                p -= 2 * dy
            y1 += step_y
            p += 2 * dx
    
    points.append((x1, y1))
    return points