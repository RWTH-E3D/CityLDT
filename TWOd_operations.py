# import of libraries
import math



def calc_center(points):
    """calculating center of a 2d area"""
    # checking if start points equals endpoint and deleting it if so
    if points[0] == points[-1]:
        del points[-1]
    else:
        # last point is unequal to first point -> no need to delete point
        pass
    return [sum([p[0] for p in points])/len(points), sum([p[1] for p in points])/len(points)] 


def angle(p1, p2):
    """calculating bearing of a vector consisting of two points"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dy == 0 and dx > 0:
        return 90
    elif dy == 0 and dx < 0:
        return 270
    else:
        ang = math.degrees(math.atan(dx/dy))
        if dy < 0:
            return (ang + 180) % 360
        elif dx < 0:
            return (ang + 360) % 360
        else:
            return ang

            

def distance(p1, p2):
    """calculating the distance between two points"""
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )



def normedDirectionVector(p1, p2):
    """calculating the normed direction vector between two points"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.sqrt( dx**2 + dy**2)
    return [dx * 1 / length, dy * 1 / length]



def rotationDirection(center, p1, p2):
    """determening if given two points are rotated clockwise or counterclockwise around center point"""
    # calculating crossproduct
    z = ((p1[0]-center[0])*(p2[1]-p1[1])) - ((p1[1]-center[1])*(p2[0]-p1[0]))
    if z < 0:
        return 'CW'
    else:
        return 'CCW'



def correct_angle(angle, direction):
    """calculating outwardfacing orthogonale from angle and roation direction"""
    if direction == 'CW':
        return (360 + angle - 90) % 360
    else:
        return (360 + angle + 90) % 360



def has_duplicates2(seq):
    """checking if list contains duplicates source:https://github.com/nkmk/python-snippets/blob/6fe3d898263f521439ecfb3629a7fb690f9d3996/notebook/list_duplicate_check.py#L16-L19"""
    seen = []
    unique_list = [x for x in seq if x not in seen and not seen.append(x)]
    return len(seq) != len(unique_list)