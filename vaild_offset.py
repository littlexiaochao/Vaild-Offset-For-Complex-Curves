'''
This compnent generates vaild offset polyline curves

Args:
    C: Curve
    D: Distance
    P: Plane
    A: Accraucy
Returns:
    Curves: Offset curves
    Count: The number of layer
'''

__author__ = "littlechao PC"
__version__ = "2023.12.30"

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import ghpythonlib.components as gh
import ghpythonlib.treehelpers as th


def deivideAccuracy(A):
    accuracy = round(0.02 / A)
    if accuracy < 1:
        accuracy = 1
    return accuracy

def gereenEquation(pts): # this equation is to judge the direction of the curve.
    sum = 0
    for i in range(len(pts) - 1):
        pt1 = pts[i]
        pt2 = pts[i+1]
        sum += -0.5 * (pt2.Y + pt1.Y) * (pt2.X - pt1.X)
    if sum <= 0:
        return 1
    else: return -1

def OffsetCurve(C, D, P):
    accuracy = deivideAccuracy(A)
    C_len = rs.CurveLength(C)
    DividePts = rs.DivideCurve(C, round(C_len) * accuracy)
    dir = gereenEquation(DividePts)
    DivideParmers = rs.DivideCurve(C, round(C_len) * accuracy, return_points=False)
    OffsetPts = []
    for i in range(len(DivideParmers)):
        tangent = rs.CurveTangent(C, DivideParmers[i])
        direction = rs.VectorUnitize(rs.VectorCrossProduct(tangent, P.ZAxis)) * dir
        OffsetPt = DividePts[i] + direction * D
        OffsetPts.append(OffsetPt)
    OffsetPts.append(OffsetPts[0])
    polyline = rg.Polyline(OffsetPts)
    return polyline

def splitCurveBySelf(C):
    selfPaemers = gh.CurveXSelf(C)[1]
    if selfPaemers != None:
        splitCurves = gh.Shatter(C, selfPaemers)
        return splitCurves
    else:
        return [rg.PolylineCurve(C)]

def removeFasleCurves(last_Cs, Cs, D, tolerance):
    midPts = gh.CurveMiddle(Cs)
    distances = gh.CurveClosestPoint(midPts, last_Cs)[2]
    # remove open curves with near by last curves
    selectCs = []
    for i in range(len(distances)):
        if distances[i] > D - (D * tolerance):
            selectCs.append(Cs[i])
    if len(selectCs) > 1:
        selectCs = rs.JoinCurves(selectCs)
    
    # remove closed small knot curves
    validCs = []
    for i in range(len(selectCs)):
        c_len = rs.CurveLength(selectCs[i])
        if c_len > D * tolerance * 20:
            validCs.append(selectCs[i])
    return validCs




if C != None:
    if D == None or D == 0:
        D = 1
    if P == None:
        P = rs.WorldXYPlane()
    if A == None:
        A = 0.004
    
    time = 1
    IsOutput = True
    curves = []
    
    
    while IsOutput is True and time < 100:
        offsetCurve = OffsetCurve(C, D*time, P)
        splitCurves = splitCurveBySelf(offsetCurve)
        if len(splitCurves) == 1:
            curves.append(splitCurves)
        else:
            vaildCurves = removeFasleCurves(C, splitCurves, D*time, A)
            if len(vaildCurves) == 0:
                IsOutput = False
            else:
                curves.append(vaildCurves)
        time += 1
    
    
    Curves = th.list_to_tree(curves)
    Count = len(curves)