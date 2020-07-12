from lxml.etree import Element, fromstring
import re
from argparse import ArgumentParser


def cleanup(text):
    text = re.sub('[\r\n\t]', ' ', text)
    text = re.sub(' +', ' ', text)
    text = re.sub(r'[–—‐−]', '-', text) # controversial!!!
    return text


def inner_text(xml_element: Element) -> str:
    if xml_element is not None:
        return "".join([t for t in xml_element.itertext()])
    else:
        return ""


def restorative_innertext(element: Element, add_after=['.//sd-panel/strong[1]', './/sd-panel/b[1]'], add_before=['.//sd-panel']) -> str:

    def add_space_after(element: Element):
        for xp in add_after:
            for e in element.xpath(xp):
                if e.tail is None:
                    e.tail = ' '
                elif e.tail[0] != ' ':
                    e.tail = ' ' + e.tail

    def add_space_before(element: Element):
        for xp in add_before:
            for e in element.xpath(xp):
                for sub in e[::-1]:
                    if sub.tail is not None:
                        if sub.tail[-1] != ' ':
                            sub.tail += ' '
                        break

    add_space_after(element)
    add_space_before(element)
    innertext = inner_text(element)
    return innertext


# From https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
# The MIT License (MIT)
# Copyright (c) 2016 Vladimir Ignatev
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * (count+1) / float(total)))

    percents = round(100.0 * (count+1) / float(total))
    bar = u'█' * filled_len + '-' * (bar_len - filled_len)

    print(u'\r[%s] %s%s ...%s' % (bar, percents, '%', status), end="")


def main():
    # test_text = '''<fig><sd-panel><b>(B)</b><sd-tag external_database0="NCBI gene" external_id0="110213" id="sdTag272" role="component" type="gene">BI‐1</sd-tag> KO <sd-tag external_database0="CVCL" external_id0="CVCL_9115" id="sdTag273" role="component" type="cell">MEFs</sd-tag> were stably transduced with lentiviral vectors as described in <b>A</b>. Cells were exposed to <sd-tag id="sdTag274" role="component" type="undefined">EBSS</sd-tag> for 3 h, and then <sd-tag external_database0="Uniprot" external_database1="Uniprot" external_id0="Q91VR7" external_id1="Q9CQV6" id="sdTag276" role="assayed" type="protein">LC3</sd-tag> levels were analysed by <sd-tag category="assay" external_database0="BAO" external_id0="BAO_0002424" id="sdTag277">western blot</sd-tag>. Image was assembled from cropped lanes of the same <sd-tag category="assay" external_database0="BAO" external_id0="BAO_0002424" id="sdTag278">western blot</sd-tag> analysis.<graphic href="https://api.sourcedata.io/file.php?panel_id=5247" /></sd-panel><sd-panel><b>(C)</b> Endogenous <sd-tag external_database0="Uniprot" external_database1="Uniprot" external_id0="Q91VR7" external_id1="Q9CQV6" id="sdTag281" role="assayed" type="protein">LC3</sd-tag> distribution was visualized using immunofluorescence and <sd-tag category="assay" external_database0="BAO" external_id0="BAO_0000453" id="sdTag283">confocal microscopy</sd-tag> in <sd-tag external_database0="NCBI gene" external_id0="110213" id="sdTag284" role="component" type="gene">BI‐1</sd-tag> KO/shLuc and <sd-tag external_database0="NCBI gene" external_id0="110213" id="sdTag285" role="component" type="gene">BI‐1</sd-tag> KO/sh<sd-tag external_database0="NCBI gene" external_id0="56208" id="sdTag286" role="intervention" type="gene">Beclin‐1</sd-tag> cells. Quantification represents the visualization of at least 180 cells. Student's <i>t</i>‐test was used to analyse statistical significance. Mean and standard deviation are presented, <sup>*</sup><i>P</i>0.001, NS: non‐significant. <graphic href="https://api.sourcedata.io/file.php?panel_id=5248" /></sd-panel><sd-panel><b>(D)</b><sd-tag external_database0="Uniprot" external_database1="Uniprot" external_id0="Q91VR7" external_id1="Q9CQV6" id="sdTag290" role="assayed" type="protein">LC3</sd-tag> was visualized and quantified in <sd-tag external_database0="NCBI gene" external_id0="110213" id="sdTag291" role="component" type="gene">BI‐1</sd-tag> KO/shLuc and <sd-tag external_database0="NCBI gene" external_id0="110213" id="sdTag292" role="component" type="gene">BI‐1</sd-tag> KO/sh<sd-tag external_database0="NCBI gene" external_id0="78943" id="sdTag299" role="intervention" type="gene">IRE1α</sd-tag> cells described in (<b>B</b>) by immunofluorescence and <sd-tag category="assay" external_database0="BAO" external_id0="BAO_0000453" id="sdTag294">confocal microscopy</sd-tag> analysis. <graphic href="https://api.sourcedata.io/file.php?panel_id=5249" /></sd-panel></fig>'''
    # test_text = '''<p>(<b>A</b>) <sd-tag id="sdTag133">Blood</sd-tag> <sd-tag id="sdTag134">glucose</sd-tag> levels in 6 mo</p>'''
    # test_text = '''<fig><sd-panel><strong>D</strong><span><sd-tag id="sdTag167">In situ hybridisation</sd-tag> for transcripts of</span> <em><sd-tag id="sdTag171">ptch2</sd-tag></em>, <em><sd-tag id="sdTag172">olig2</sd-tag></em> and <em><sd-tag id="sdTag168">nkx2.2</sd-tag></em> in 24hpf <em><sd-tag id="sdTag173">smo</sd-tag></em><em><sup>hi1640</sup></em> mutant <sd-tag id="sdTag174">embryos</sd-tag> injected with mRNA <span>encoding m<sd-tag id="sdTag169">Smo</sd-tag> and m<sd-tag id="sdTag170">Smo</sd-tag>SA (</span>n=6 for each sample). Scale bars, are 100μm (lateral view), 50μm (sections).</sd-panel></fig>'''
    test_text = '''<sd-panel> <p><strong>Figure 3. Virtual <sd-pretag role='component' id='sdPretag1107992230sme' type='tissue' >memory</sd-pretag> and <sd-pretag role='component' id='sdPretag251248034sme' type='cell' >naïve T cells</sd-pretag> use different TCR repertoires.</strong></p> <p>(A) <sd-pretag role='component' id='sdPretag1274695424sme' type='cell' >LN cells</sd-pretag> isolated from <sd-pretag role='intervention' id='sdPretag1814597115sme' type='geneprod' >Vβ5</sd-pretag> <sd-pretag role='component' id='sdPretag816721855sme' type='organism' >mice</sd-pretag> were stained for <sd-pretag role='assayed' id='sdPretag1479536539sme' type='geneprod' >CD8</sd-pretag>, <sd-pretag role='assayed' id='sdPretag1875812564sme' type='geneprod' >CD4</sd-pretag>, <sd-pretag role='assayed' id='sdPretag768303478sme' type='geneprod' >CD44</sd-pretag>, <sd-pretag role='assayed' id='sdPretag306749453sme' type='geneprod' >CD62L</sd-pretag> and <sd-pretag role='assayed' id='sdPretag306074545sme' type='geneprod' >Vα2</sd-pretag> or <sd-pretag role='assayed' id='sdPretag1254695192sme' type='geneprod' >Vα8</sd-pretag>.3 or <sd-pretag role='component' id='sdPretag1413387893sme' type='geneprod' >Vα3</sd-pretag>.2. <sd-pretag role='component' id='sdPretag1470442251sme' type='geneprod' >CD8</sd-pretag><sup>+</sup> <sd-pretag role='component' id='sdPretag70799027sme' type='cell' >T cells</sd-pretag> were gated as <sd-pretag role='assayed' id='sdPretag1487582829sme' type='geneprod' >CD8</sd-pretag><sup>+</sup> <sd-pretag role='assayed' id='sdPretag1729134841sme' type='geneprod' >CD4</sd-pretag><sup>-</sup> and then the percentage of <sd-pretag role='assayed' id='sdPretag1169992340sme' type='geneprod' >CD44</sd-pretag><sup>+</sup> <sd-pretag role='assayed' id='sdPretag1467214542sme' type='geneprod' >CD62L</sd-pretag><sup>+</sup> <sd-pretag role='component' id='sdPretag1852510456sme' type='cell' >memory T cells</sd-pretag> among <sd-pretag role='assayed' id='sdPretag1987382744sme' type='geneprod' >CD8</sd-pretag><sup>+</sup> <sd-pretag role='component' id='sdPretag1202820407sme' type='geneprod' >Vα2</sd-pretag><sup>+</sup> or <sd-pretag role='component' id='sdPretag2095481847sme' type='geneprod' >CD8</sd-pretag><sup>+</sup> <sd-pretag role='component' id='sdPretag1424117582sme' type='geneprod' >Vα8</sd-pretag>.3<sup>+</sup> or <sd-pretag role='intervention' id='sdPretag1281222641sme' type='geneprod' >CD8</sd-pretag><sup>+</sup> <sd-pretag role='intervention' id='sdPretag1207677443sme' type='geneprod' >Vα3</sd-pretag>.2<sup>+</sup> <sd-pretag role='component' id='sdPretag893713056sme' type='cell' >T cells</sd-pretag> was determined by <sd-pretag category='assay' id='sdPretag1939785539sme'>flow cytometry</sd-pretag>. Mean, n=8 <sd-pretag role='component' id='sdPretag129970437sme' type='organism' >mice</sd-pretag> from 8 independent experiments.</p> <p>(B,C) Cells isolated from peripheral LN (B-C), mesenteric LN (C) and the <sd-pretag role='component' id='sdPretag985544651sme' type='tissue' >spleen</sd-pretag> (C) were stained as in (A) with the addition of <sd-pretag role='component' id='sdPretag870284919sme' type='geneprod' >OVA</sd-pretag>-tetramer. The <sd-pretag role='assayed' id='sdPretag650560618sme' type='geneprod' >OVA</sd-pretag>-reactive Vα-specific <sd-pretag role='component' id='sdPretag1440878763sme' type='cell' >CD8</sd-pretag><sup>+</sup> <sd-pretag role='component' id='sdPretag1582009826sme' type='cell' >T cells</sd-pretag> were gated and the percentage of <sd-pretag role='assayed' id='sdPretag1942642533sme' type='geneprod' >CD44</sd-pretag><sup>+</sup> <sd-pretag role='assayed' id='sdPretag2086268199sme' type='geneprod' >CD62L</sd-pretag><sup>+</sup> <sd-pretag role='component' id='sdPretag48418377sme' type='cell' >memory T cells</sd-pretag> was determined by <sd-pretag category='assay' id='sdPretag1172787085sme'>flow cytometry</sd-pretag>. n=9-10 <sd-pretag role='component' id='sdPretag1569738019sme' type='organism' >mice</sd-pretag> from 5 independent experiments.</p> <p>(D) The same experiment as in (A) was performed using germ-free <sd-pretag role='intervention' id='sdPretag1661091934sme' type='geneprod' >Vβ5</sd-pretag> <sd-pretag role='component' id='sdPretag1040845208sme' type='organism' >mice</sd-pretag>. Mean, n=7-9 <sd-pretag role='component' id='sdPretag983115942sme' type='organism' >mice</sd-pretag> from 4 independent experiments.</p> <p>(E) The same experiment as in (B-C) was performed using a mixture of <sd-pretag role='component' id='sdPretag1183896165sme' type='cell' >T cells</sd-pretag> isolated from LNs and the <sd-pretag role='component' id='sdPretag2073288711sme' type='tissue' >spleen</sd-pretag> from germ-free <sd-pretag role='intervention' id='sdPretag1888791058sme' type='geneprod' >Vβ5</sd-pretag> <sd-pretag role='component' id='sdPretag1048290335sme' type='organism' >mice</sd-pretag>. Mean, n=7-9 from 2-3 independent experiments.</p> <p>(F) RNA was isolated from <sd-pretag role='component' id='sdPretag20368287sme' type='tissue' >memory</sd-pretag> (<sd-pretag role='component' id='sdPretag2024108032sme' type='geneprod' >CD44</sd-pretag><sup>+</sup><sd-pretag role='intervention' id='sdPretag1330093244sme' type='geneprod' >CD62L</sd-pretag><sup>+</sup>) and (<sd-pretag role='intervention' id='sdPretag264394135sme' type='geneprod' >CD44</sd-pretag><sup>+</sup><sd-pretag role='intervention' id='sdPretag1904512257sme' type='geneprod' >CD62L</sd-pretag><sup>+</sup>) K<sup>b</sup>-<sd-pretag role='intervention' id='sdPretag563265161sme' type='geneprod' >OVA</sd-pretag><sup>+</sup> 4mer<sup>+</sup> <sd-pretag role='component' id='sdPretag2069081414sme' type='cell' >T cells</sd-pretag> sorted from LNs and the <sd-pretag role='component' id='sdPretag887804404sme' type='tissue' >spleen</sd-pretag> of germ-free <sd-pretag role='intervention' id='sdPretag530404526sme' type='geneprod' >Vβ5</sd-pretag> <sd-pretag role='component' id='sdPretag1488920750sme' type='organism' >mice</sd-pretag>. <sd-pretag role='component' id='sdPretag1077707006sme' type='geneprod' >TCRα</sd-pretag> encoding genes using either <sd-pretag role='component' id='sdPretag2055652052sme' type='geneprod' >TRAV12</sd-pretag> (corresponding to <sd-pretag role='component' id='sdPretag1069500620sme' type='geneprod' >Vα8</sd-pretag>) or <sd-pretag role='component' id='sdPretag1626893466sme' type='geneprod' >TRAV14</sd-pretag> (corresponding to <sd-pretag role='component' id='sdPretag1692149536sme' type='geneprod' >Vα2</sd-pretag>) were cloned and sequenced. 12-20 clones were sequenced in each group/experiment. Clonotypes identified in at least 2 experiments are shown. Mean frequency + SEM, n=4 independent experiments. Statistical significance was determined by Chi-square test (global test) and paired two-tailed T tests as a post test (individual clones). <sd-pretag role='intervention' id='sdPretag1435758740sme' type='geneprod' >CDR3</sd-pretag> sequences of clonotypes enriched in naïve or VM compartments are shown in the <sd-pretag role='component' id='sdPretag855401733sme' type='tissue' >table</sd-pretag>.</p> <p>(G,H) <sd-pretag role='component' id='sdPretag1502094212sme' type='organism' >Retroviral</sd-pretag> vectors encoding selected <sd-pretag role='intervention' id='sdPretag1533591449sme' type='geneprod' >TCRα</sd-pretag> clones were transduced into immortalized <sd-pretag role='intervention' id='sdPretag769855447sme' type='geneprod' >Rag2</sd-pretag><sup>-/-</sup> <sd-pretag role='component' id='sdPretag516530180sme' type='geneprod' >Vβ5</sd-pretag> bone marrow stem cells. These cells were transplanted into an irradiated Ly5.1 recipient. (G) At least 8 weeks after the transplantation, frequency of <sd-pretag role='component' id='sdPretag534810090sme' type='undefined' >virtual memory</sd-pretag> <sd-pretag role='component' id='sdPretag131941877sme' type='cell' >T cells</sd-pretag> among LN <sd-pretag role='component' id='sdPretag586622077sme' type='cell' >donor T cells</sd-pretag> (<sd-pretag role='intervention' id='sdPretag477195769sme' type='geneprod' >CD45</sd-pretag>.2<sup>+</sup> <sd-pretag role='intervention' id='sdPretag1115040145sme' type='geneprod' >CD45</sd-pretag>.1<sup>-</sup> <sd-pretag role='reporter' id='sdPretag1241808532sme' type='geneprod' >GFP</sd-pretag><sup>+</sup>) was analyzed. Mean+SEM; n=10-21 <sd-pretag role='component' id='sdPretag135605830sme' type='organism' >mice</sd-pretag> from 2-7 independent experiments. Statistical significance was tested using <span class='anchor' id='OLE_LINK3'></span>Kruskal-Wallis test. (H) <sd-pretag role='assayed' id='sdPretag2052920424sme' type='geneprod' >CD5</sd-pretag> levels on naïve monoclonal <sd-pretag role='component' id='sdPretag2012166673sme' type='cell' >T cells</sd-pretag> were detected by <sd-pretag category='assay' id='sdPretag1865680739sme'>flow cytometry</sd-pretag>. Representative <sd-pretag role='component' id='sdPretag1903457800sme' type='organism' >mice</sd-pretag> out of 9-14 in total from 2-4 independent experiments.</p> <p>Data information: (A, C-E) Statistical significance was determined by 2-tailed Wilcoxon signed-rank test.</p> </sd-panel>'''
    # test_text = '''<fig><caption><title>This is the title.</title><p>(A). This is the caption.</p></caption></fig>'''
    argparse = ArgumentParser(description="space keeping innertext")
    argparse.add_argument('xml_string', nargs="?", default=test_text, type=str, help="the xml string to process")
    args = argparse.parse_args()
    xml_string = args.xml_string
    xml = fromstring(xml_string)
    inner_text = restorative_innertext(xml)
    print(inner_text)


if __name__ == "__main__":
    main()
