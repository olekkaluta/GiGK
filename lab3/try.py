import sys
#import numpy as np
#import matplotlib.pyplot as plt
from geometry_lib.io_operations import parse_file,TestOutputWriter
from geometry_lib.data_representation import Point, Segment, Color, Side, PointList
from geometry_lib.elementary_functions import WhichSide, CCW, Orientation, orientation

  
def Leftindex(point_lst):
    minn = 0
    b = point_lst[minn]
    b:Point
    for i in range(1, len(point_lst)):
        a = point_lst[i]
        a:Point
        if a.x < point_lst[minn].x:
            minn = i
        elif a.x == point_lst[minn].x:
            if a.y > point_lst[minn].y:
                minn=i
    return minn


def GiftWrapping(point_lst: PointList):
    n = len(point_lst)
    if len(point_lst) < 3:
        return
    
    l = Leftindex(point_lst)
    hull=[]
    p=l
    q=0
    for i in range(n):
        point_lst[i]: Point

    while(True):
        hull.append(p)
        q = (p + 1) % n
        for i in range(n):
            if(CCW(point_lst[p], point_lst[i], point_lst[q]) == True):
                q = i
        p = q
        if(p == l):
            break
    
    res=[]
    res2=[]
    for each in hull:
        a = point_lst[each]
        a:Point
        res2.append(a.x)
        res2.append(a.y)
        res.append(res2)
        res2=[]
    
    return res

  
def convex_hull_naive(point_lst):
    print("[Warning] naive convex hull algorithm complicity is O(n^3)")
    chull=set()
    for p1 in point_lst:
        for p2 in point_lst:
            if p1==p2:
                continue
            sides=set()
            for p3 in point_lst:
                if p3==p1 or p3==p2:
                    continue
                seg=Segment(p1,p2,Color.NONE)
                sides.add(WhichSide(seg,p3))
            if len(sides)==1 or (len(sides)==2 and Side.NONE in sides):
                chull.add(p1)
                chull.add(p2)
    return sorted(list(chull))

def main():
    file="D:/biblioteka/sem1/GiGK/Biblioteka/Pomocny/pr4/test2.txt"
    data = parse_file(file)
    points = data['points']
    z=[]
    for x in points:
      i=0
      y=Point.getPoint(x)
      temp=[]
      i+=1
      for tuple in y:
          temp.append(float(tuple))
      z.append(temp)
    
    tab=[Point(x[0],x[1]) for x in z]

    b=convex_hull_naive(points)
    e=GiftWrapping(tab)

    
    writer1=TestOutputWriter()
    writer1.add_section('data')
    writer1.add_section_value('data', "Algorytm naiwny")
    writer1.add_section_value('data', "Liczba punktów wejściowych: %d" % len(points))
    writer1.add_section_value('data', "Liczba punktów otoczki wypukłej %d" % len(b))
    writer1.add_section('points 0')
    for x in b:
        writer1.add_section_value('points 0', x)
    writer1.print_to_file(file + "_convexhullnaive.txt")
    
    for i in range(len(e)):
        Point.setPoint_x(points[i],e[i][0])
        Point.setPoint_y(points[i],e[i][1])
    writer2=TestOutputWriter()
    writer2.add_section('data')
    writer2.add_section_value('data', "Algorytm GiftWrapping")
    writer2.add_section_value('data', "Liczba punktów wejściowych: %d" % len(points))
    writer2.add_section_value('data', "Liczba punktów otoczki wypukłej %d" % len(e))
    writer2.add_section('points 0')
    for x in points[0:len(e)]:
        writer2.add_section_value('points 0', x)
    writer2.print_to_file(file + "_convexhullgift.txt")
    




if __name__ == '__main__':
  main()