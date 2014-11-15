#!/usr/bin/env python3.4
#-*- coding: UTF-8 -*-


css = """body {
  margin-left: .5em;
  margin-right: .5em;
  text-align: justify;
}

p {
  text-align: justify;
  text-indent: 1em;
  margin-top: 0px;
  margin-bottom: 1ex;
}

h1, h2 {
  font-family: sans-serif;
  font-style: italic;
  text-align: center;
  background-color: #6b879c;
  color: white;
  width: 100%;
}

h1 {
    margin-bottom: 2px;
}

h2 {
    margin-top: -2px;
    margin-bottom: 2px;
}
"""

mimetype = 'application/epub+zip'

book_opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
	<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
		xmlns:opf="http://www.idpf.org/2007/opf"
		xmlns:dcterms="http://purl.org/dc/terms/">
		<dc:title>{title}</dc:title>
		<dc:language>ru</dc:language>
		<dc:identifier id="BookId" opf:scheme="URI">{url}</dc:identifier>
		<dc:description>{description}</dc:description>
		<dc:publisher>http://ficbook.net</dc:publisher>
		<dc:relation>http://ficbook.net</dc:relation>
		<dc:creator opf:file-as="{author}" opf:role="aut">{author}</dc:creator>
		<dc:date>{datetime}</dc:date>
		<dc:source>{url}</dc:source>
	</metadata>

	<manifest>
		<item id="ncx" href="book.ncx" media-type="application/x-dtbncx+xml" />
		<item id="css_css1" href="styles.css" media-type="text/css" />
		{items}
	</manifest>

	<spine toc="ncx">
        {itemrefs}
	</spine>
</package>"""

item = '<item id="chapter{chapter_no}" href="chapter{chapter_no}.html" media-type="application/xhtml+xml"/>'
itemref = '<itemref idref="chapter{chapter_no}"/>'


navPoint = """<navPoint id="{chapter_no}" playOrder="{chapter_no}">
			<navLabel><text>{chapter_name}</text></navLabel>
			<content src="chapter{chapter_no}.html" />
		</navPoint>"""

book_ncx = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
   "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">
	<head>
		<meta name="dtb:uid" content="{url}" />
		<meta name="dtb:depth" content="2" />
		<meta name="dtb:totalPageCount" content="0" />
		<meta name="dtb:maxPageNumber" content="0" />
	</head>

	<docTitle>
		<text>{name}</text>
	</docTitle>

	<docAuthor>
		<text>{author}</text>
	</docAuthor>

	<navMap>
        {navMap}
	</navMap>
</ncx>"""

container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="book.opf" media-type="application/oebps-package+xml" />
	</rootfiles>
</container>
"""

page = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link rel="stylesheet" type="text/css" href="styles.css" />
<title>{ff_name}</title>
</head>
<body>
<h1>{part_name}</h1>
<p>{text}</p></body>
</html>
"""












