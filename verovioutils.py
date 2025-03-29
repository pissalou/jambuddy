import verovio

tk = verovio.toolkit()
tk.loadFile('verovio.mei.xml')
tk.setOptions({
    "spacingStaff": 0,  # adjust spacing between f-clef and g-clef staff so middle-c is equidistant from both staves
})
tk.getPageCount()
tk.renderToSVGFile('verovio.mei.svg')
