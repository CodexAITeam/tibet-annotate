import urllib.request
import xml.etree.ElementTree as ET

class StaBiMets(object):

    def __init__(self, ppn):
        with urllib.request.urlopen("https://content.staatsbibliothek-berlin.de/dc/%s.mets.xml" % ppn) as metadata_url:
            self.metadata = ET.parse(metadata_url).getroot()

    #
    # Iter through file groups of a StaBi METS file
    #
    # >>> import codexai.stabi_mets
    # >>> mets = codexai.stabi_mets.StaBiMets('PPN1789694302')
    # >>> for fileGrp in mets.iterfilegroups():
    # ...     print( fileGrp.attrib["USE"] )
    # ... 
    # PRESENTATION
    # THUMBS
    # DEFAULT
    #
    def iterfilegroups(self,group = None):
        for fileGrp in self.metadata.find('{http://www.loc.gov/METS/}fileSec').findall('{http://www.loc.gov/METS/}fileGrp'):
            if group is None or fileGrp.attrib["USE"] == group:
                yield fileGrp

    #
    # Iter through files in a StaBi METS file
    #
    # >>> import codexai.stabi_mets
    # >>> mets = codexai.stabi_mets.StaBiMets('PPN1789694302')
    # >>> for file in mets.iterfiles():
    # ...     print( file.attrib["ID"] )
    # ...     break
    # ... 
    # FILE_0001_PRESENTATION
    #
    def iterfiles(self,group = None):
        for fileGrp in self.iterfilegroups( group ):
            for file in fileGrp.findall('{http://www.loc.gov/METS/}file'):
                yield file

    #
    # Iter through URLs
    #
	# >>> import codexai.stabi_mets
	# >>> mets = codexai.stabi_mets.StaBiMets('PPN1789694302')
	# >>> for url in mets.iterurls():
	# ...     print(url)
	# ...     break
	# ... 
	# https://content.staatsbibliothek-berlin.de/dc/PPN1789694302-00000001/full/max/0/default.jpg
    def iterurls(self,group = 'DEFAULT',mimetype = None):
        for file in self.iterfiles( group ):
            if mimetype is None or file.attrib["MIMETYPE"] == mimetype:
                flocat = file.find('{http://www.loc.gov/METS/}FLocat')
                if flocat.attrib["LOCTYPE"] == 'URL':
                    yield flocat.attrib['{http://www.w3.org/1999/xlink}href']

    #
    # Iter through pages
    #
    # Intended for selection of pages
    #
    # >>> import codexai.stabi_mets
    # >>> mets = codexai.stabi_mets.StaBiMets('PPN1789694302')
    # >>> structMaps=mets.metadata.findall('./{http://www.loc.gov/METS/}structMap[@TYPE="PHYSICAL"]')
    # >>> structMaps
    # [<Element '{http://www.loc.gov/METS/}structMap' at ...]
    # >>> div1s = structMaps[0].findall('./{http://www.loc.gov/METS/}div[@TYPE="physSequence"]')
    # >>> div1s
    # [<Element '{http://www.loc.gov/METS/}div' at ...>]
    # >>> div2s = div1s[0].findall('./{http://www.loc.gov/METS/}div[@TYPE="page"]')
    # >>> fptrs = div2s[0].findall('./{http://www.loc.gov/METS/}fptr')
    # >>> fptrs[0].attrib['FILEID']
    # 'FILE_0001_PRESENTATION'
    # >>> 
    def iterpages(self):
        for structMap in self.metadata.findall('./{http://www.loc.gov/METS/}structMap[@TYPE="PHYSICAL"]'):
            for div1 in structMap.findall('./{http://www.loc.gov/METS/}div[@TYPE="physSequence"]'):
                for div2 in div1.findall('./{http://www.loc.gov/METS/}div[@TYPE="page"]'):
                    image_ids = []
                    for fptr in div2.findall('./{http://www.loc.gov/METS/}fptr'):
                        image_ids.append( fptr.attrib['FILEID'] )
                    # FIXME: Next line assumes we can always translate ORDErR="" into a filename
                    ret = (div2.attrib["ORDERLABEL"],image_ids)
                    yield ret

    #
    # Gets the file location for a specified fileid and group.
    # By specifying the group here we can right away filter out files of groups we are not looking for.
    #
	# >>> import codexai.stabi_mets
	# >>> mets = codexai.stabi_mets.StaBiMets('PPN1789694302')
	# >>> file = mets.getFileByID('FILE_0001_DEFAULT')
	# >>> file
	# <Element '{http://www.loc.gov/METS/}file' at ...>
	# >>> file.attrib["ID"]
	# 'FILE_0001_DEFAULT'
	# >>> file = mets.getFileByID('FILE_0001_DEFAULT','DEFAULT')
	# >>> file.attrib["ID"]
	# 'FILE_0001_DEFAULT'
	# >>> file = mets.getFileByID('FILE_0001_DEFAULT','PRESENTATION')
	# >>> file
	# >>> 
    def getFileByID(self,fileid,group = None):
        groupfilter = ""
        if group is not None:
            groupfilter = '[@USE="%s"]' % group
        return self.metadata.find('./{http://www.loc.gov/METS/}fileSec/{http://www.loc.gov/METS/}fileGrp%s/{http://www.loc.gov/METS/}file[@ID="%s"]' % (groupfilter,fileid) )

	#
    # Get the URL for a file-ID
    #
	#
	# Background:
	#
	# >>> import codexai.stabi_mets
	# >>> mets = codexai.stabi_mets.StaBiMets('PPN1789694302')
	# >>> flocat = mets.getFileByID('FILE_0001_DEFAULT','DEFAULT').find('./{http://www.loc.gov/METS/}FLocat[@LOCTYPE="URL"]')
	# >>> flocat
	# <Element '{http://www.loc.gov/METS/}FLocat' at ...>
	# >>> flocat.attrib
	# {'LOCTYPE': 'URL', '{http://www.w3.org/1999/xlink}href': 'https://content.staatsbibliothek-berlin.de/dc/PPN1789694302-00000001/full/max/0/default.jpg'}
	# >>> 
    #
    # Usage:
    #
	# >>> import codexai.stabi_mets
	# >>> mets = codexai.stabi_mets.StaBiMets('PPN1789694302')
	# >>> mets.getURLByID('FILE_0001_DEFAULT','DEFAULT')
	# 'https://content.staatsbibliothek-berlin.de/dc/PPN1789694302-00000001/full/max/0/default.jpg'
	# >>> 
    def getURLByID(self,fileid,group = None):
        file = self.getFileByID(fileid,group)
        if file is None:
            return None
        return file.find('./{http://www.loc.gov/METS/}FLocat[@LOCTYPE="URL"]').attrib['{http://www.w3.org/1999/xlink}href']

# vim:expandtab
