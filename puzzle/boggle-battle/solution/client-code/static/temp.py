class X:
    def __init__(self):
        pass

    def line(self, *args, **kwargs):
        x1, y1, x2, y2 = args[0]
        # print(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" />')

    def ellipse(self, x, y, z, *args, **kwargs):
        x1, y1, x2, y2 = args[0]
        cx, cy = (x1 + x2)/2, (y1 + y2)/2
        rx, ry = x2 - cx, y2 - cy
        # print(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" />')
        print(f'{{ x: {x}, y: {y}, z: {z}, cx: {cx}, cy: {cy} }},')

    def text(self, *args, **kwargs):
        print("text", args, kwargs)

def _gen_image():
    # level = 0
    # board = [["#", "#", "#", "#", "#", "#"],["#", "C", "D", "E", "F", "#"],["#", "H", "I", "J", "K", "#"],["#", "N", "O", "P", "Qu", "#"],["#", "S", "T", "U", "V", "#"],["#", "#", "#", "#", "#", "#"]]
    # level = 1
    # board = [["#", "#", "A", "B", "C"], ["#", "E", "F", "G", "H"], ["I", "J", "K", "L", "M"], ["N", "O", "P", "Qu", "#"], ["R", "S", "T", "#", "#"]]
    # level = 2
    # board = [["#", "#", "A", "B", "#", "#"],["#", "C", "D", "E", "F", "#"],["G", "H", "I", "J", "K", "L"],["M", "N", "O", "P", "Qu", "R"],["#", "S", "T", "U", "V", "#"],["#", "#", "W", "X", "#", "#"]]
    level = 3
    board = [[["A", "B", "C"],["D", "E", "F"],["G", "H", "I"]],[["J", "K", "L"],["M", "N", "O"],["P", "Qu", "R"]],[["S", "T", "U"],["V", "W", "X"],["Y", "Z", "A"]]]
    bonus = {}

    BACKGROUND_COLOR = (206,206,156,255)
    NORMAL_COLOR = (156,156,99,255)
    DOUBLE_COLOR = (132,132,255,255)
    TRIPLE_COLOR = (255,132,132,255)
    LINE_COLOR = (0,0,0,255)

    dim = (384,384)
    if level == 3:
        dim = (384,576)

    d = X()
    if level == 0:
        for i in range(36):
            col = NORMAL_COLOR
            x = i//6
            y = i%6
            if (y,x) in bonus:
                if bonus[(y,x)] == 2:
                    col = DOUBLE_COLOR
                if bonus[(y,x)] == 3:
                    col = TRIPLE_COLOR
            if board[x][y] != "#":
                if y != 5 and board[x][y+1] != "#":
                    d.line([64*x+32,64*y+32,64*x+32,64*y+96], fill=LINE_COLOR, width=1)
                if y != 5 and x != 5 and board[x+1][y+1] != "#":
                    d.line([64*x+32,64*y+32,64*x+96,64*y+96], fill=LINE_COLOR, width=1)
                if x != 5 and board[x+1][y] != "#":
                    d.line([64*x+32,64*y+32,64*x+96,64*y+32], fill=LINE_COLOR, width=1)
                if y != 0 and x != 5 and board[x+1][y-1] != "#":
                    d.line([64*x+32,64*y+32,64*x+96,64*y-32], fill=LINE_COLOR, width=1)
                d.ellipse(x, y, [64*x+16,64*y+16,64*x+48,64*y+48], fill=col)
                txt = board[x][y][0].upper()+board[x][y][1:]
                # w, h = d.textsize(txt)
                # d.text((64*x+32-w/2, 64*y+32-h/2), txt, fill=LINE_COLOR)
    elif level == 2:
        for i in range(36):
            col = NORMAL_COLOR
            x = i//6
            y = i%6
            if (y,x) in bonus:
                if bonus[(y,x)] == 2:
                    col = DOUBLE_COLOR
                if bonus[(y,x)] == 3:
                    col = TRIPLE_COLOR
            if board[x][y] != "#":
                if (0 <= x+1 <= 5 and 0 <= y+2 <= 5) and board[x+1][y+2] != "#":
                    d.line([64*x+32,64*y+32,64*x+96,64*y+160], fill=LINE_COLOR, width=1)
                if (0 <= x+2 <= 5 and 0 <= y+1 <= 5) and board[x+2][y+1] != "#":
                    d.line([64*x+32,64*y+32,64*x+160,64*y+96], fill=LINE_COLOR, width=1)
                if (0 <= x+2 <= 5 and 0 <= y-1 <= 5) and board[x+2][y-1] != "#":
                    d.line([64*x+32,64*y+32,64*x+160,64*y-32], fill=LINE_COLOR, width=1)
                if (0 <= x+1 <= 5 and 0 <= y-2 <= 5) and board[x+1][y-2] != "#":
                    d.line([64*x+32,64*y+32,64*x+96,64*y-96], fill=LINE_COLOR, width=1)
                d.ellipse(x, y, [64*x+16,64*y+16,64*x+48,64*y+48], fill=col)
                txt = board[x][y][0].upper()+board[x][y][1:]
                # w, h = d.textsize(txt)
                # d.text((64*x+32-w/2, 64*y+32-h/2), txt, fill=LINE_COLOR)
    elif level == 1:
        for i in range(25):
            col = NORMAL_COLOR
            x = i//5
            y = i%5
            if (y,x) in bonus:
                if bonus[(y,x)] == 2:
                    col = DOUBLE_COLOR
                if bonus[(y,x)] == 3:
                    col = TRIPLE_COLOR
            if board[x][y] != "#":
                if (0 <= x <= 4 and 0 <= y+1 <= 4) and board[x][y+1] != "#":
                    d.line([get_xcoord((x,y),1),get_ycoord((x,y),1),get_xcoord((x,y+1),1),get_ycoord((x,y+1),1)], fill=LINE_COLOR, width=1)
                if (0 <= x+1 <= 4 and 0 <= y <= 4) and board[x+1][y] != "#":
                    d.line([get_xcoord((x,y),1),get_ycoord((x,y),1),get_xcoord((x+1,y),1),get_ycoord((x+1,y),1)], fill=LINE_COLOR, width=1)
                if (0 <= x+1 <= 4 and 0 <= y-1 <= 4) and board[x+1][y-1] != "#":
                    d.line([get_xcoord((x,y),1),get_ycoord((x,y),1),get_xcoord((x+1,y-1),1),get_ycoord((x+1,y-1),1)], fill=LINE_COLOR, width=1)
                d.ellipse(x, y, [get_xcoord((x,y),1)-16,get_ycoord((x,y),1)-16,get_xcoord((x,y),1)+16,get_ycoord((x,y),1)+16], fill=col)
                txt = board[x][y][0].upper()+board[x][y][1:]
                # w, h = d.textsize(txt)
                # d.text((get_xcoord((x,y),1)-w/2, get_ycoord((x,y),1)-h/2), txt, fill=LINE_COLOR)
    elif level == 3:
        for i in range(27):
            col = NORMAL_COLOR
            x = i//9
            y = i//3%3
            z = i%3
            if board[x][y][z] != "#":
                if (0 <= x <= 2 and 0 <= y <= 2 and 0 <= z+1 <= 2) and board[x][y][z+1] != "#":
                    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x,y,z+1),3),get_ycoord((x,y,z+1),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x <= 2 and 0 <= y+1 <= 2 and 0 <= z+1 <= 2) and board[x][y+1][z+1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x,y+1,z+1),3),get_ycoord((x,y+1,z+1),3)], fill=LINE_COLOR, width=1)
                if (0 <= x <= 2 and 0 <= y+1 <= 2 and 0 <= z <= 2) and board[x][y+1][z] != "#":
                    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x,y+1,z),3),get_ycoord((x,y+1,z),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x <= 2 and 0 <= y+1 <= 2 and 0 <= z-1 <= 2) and board[x][y+1][z-1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x,y+1,z-1),3),get_ycoord((x,y+1,z-1),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y <= 2 and 0 <= z+1 <= 2) and board[x+1][y][z+1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y,z+1),3),get_ycoord((x+1,y,z+1),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y+1 <= 2 and 0 <= z+1 <= 2) and board[x+1][y+1][z+1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y+1,z+1),3),get_ycoord((x+1,y+1,z+1),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y+1 <= 2 and 0 <= z <= 2) and board[x+1][y+1][z] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y+1,z),3),get_ycoord((x+1,y+1,z),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y+1 <= 2 and 0 <= z-1 <= 2) and board[x+1][y+1][z-1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y+1,z-1),3),get_ycoord((x+1,y+1,z-1),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y <= 2 and 0 <= z-1 <= 2) and board[x+1][y][z-1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y,z-1),3),get_ycoord((x+1,y,z-1),3)], fill=LINE_COLOR, width=1)
                if (0 <= x+1 <= 2 and 0 <= y <= 2 and 0 <= z <= 2) and board[x+1][y][z] != "#":
                    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y,z),3),get_ycoord((x+1,y,z),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y-1 <= 2 and 0 <= z+1 <= 2) and board[x+1][y-1][z-1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y-1,z+1),3),get_ycoord((x+1,y-1,z+1),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y-1 <= 2 and 0 <= z <= 2) and board[x+1][y-1][z] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y-1,z),3),get_ycoord((x+1,y-1,z),3)], fill=LINE_COLOR, width=1)
                #if (0 <= x+1 <= 2 and 0 <= y-1 <= 2 and 0 <= z-1 <= 2) and board[x+1][y-1][z-1] != "#":
                #    d.line([get_xcoord((x,y,z),3),get_ycoord((x,y,z),3),get_xcoord((x+1,y-1,z-1),3),get_ycoord((x+1,y-1,z-1),3)], fill=LINE_COLOR, width=1)

        for i in range(27):
            col = NORMAL_COLOR
            x = i//9
            y = i//3%3
            z = i%3
            if (z,y,x) in bonus:
                if bonus[(z,y,x)] == 2:
                    col = DOUBLE_COLOR
                if bonus[(z,y,x)] == 3:
                    col = TRIPLE_COLOR
            if board[x][y][z] != "#":
                d.ellipse(x, y, z, [get_xcoord((x,y,z),3)-16,get_ycoord((x,y,z),3)-16,get_xcoord((x,y,z),3)+16,get_ycoord((x,y,z),3)+16], fill=col)
                txt = board[x][y][z][0].upper()+board[x][y][z][1:]
                # w, h = d.textsize(txt)
                # d.text((get_xcoord((x,y,z),3)-w/2, get_ycoord((x,y,z),3)-h/2), txt, fill=LINE_COLOR)
    # img.show()     


def get_xcoord(coords,l):
    if l == 1:
        return 64*coords[1]+32*coords[0]
    if l == 3:
        return coords[0]*64+coords[2]*64+64


def get_ycoord(coords,l):
    if l == 1:
        return 55*coords[0]+82
    if l == 3:
        return coords[1]*64+coords[2]*192+32


_gen_image()