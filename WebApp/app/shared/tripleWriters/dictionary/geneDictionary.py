def getGenes():
    return aGenes, cgfGenes
def getAGenes():
    return aGenes
def getRGenes():
    return aGenes[aGenes.index("Asp"):aGenes.index("Unc (atpA)")]
def getMLSTGenes():
    return aGenes[aGenes.index("Unc (atpA)"):aGenes.index("MOMP")+1]
aGenes = ['Asp', 'Gln', 'Glt', 'Gly', 'Pgm', 'Tkt', 'Unc (atpA)', 'flaA SVR', 'flaPeptide', 'porA', 'MOMP']
cgfGenes = ['cj0008 (486bp)', 'cj0033 (206bp)', 'cj0035 (541bp)', 'cj0057 (175bp)', 'cj0177 (399bp)', 'cj0181 (486bp)', 'cj0264 (406bp)', 'cj0297c (300bp)', 'cj0298c (198bp)', 'cj0307 (347bp)', 'cj0421c (127bp)', 'cj0483 (612bp)', 'cj0486 (301bp)', 'cj0566 (558bp)', 'cj0569 (399bp)', 'cj0570 (405bp)', 'cj0625 (498bp)', 'cj0728 (296bp)', 'cj0733 (441bp)', 'cj0736 (205bp)', 'cj0755 (101bp)', 'cj0860 (282bp)', 'cj0967 (301bp)', 'cj1134 (152bp)', 'cj1136 (510bp)', 'cj1141 (413bp)', 'cj1294 (160bp)', 'cj1324 (440bp)', 'cj1329 (307bp)', 'cj1334 (462bp)', 'cj1427c (613bp)', 'cj1431c (307bp)', 'cj1439 (307bp)', 'cj1550c (188bp)', 'cj1551 (241bp)', 'cj1552 (222bp)', 'cj1585 (630bp)', 'cj1679 (529bp)', 'cj1721 (415bp)', 'cj1727c (369bp)']

