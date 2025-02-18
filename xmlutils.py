from pugixml import pugi
from typing import Callable

doc = pugi.XMLDocument()


def foreach_node(xml_contents: str, xpath: str, functor: Callable) -> str:
    """ return the modified XML as defined by the xpath and the functor """
    doc.load_string(xml_contents)
    for elem in doc.select_nodes(xpath):
        functor(elem.node())
        # print(f'called {functor} on {elem.node().name()}')
    return _doc2str(doc)


def _doc2str(doc: pugi.XMLDocument) -> str:
    xml_writer = pugi.StringWriter()
    doc.save(writer=xml_writer, flags=pugi.FORMAT_RAW, encoding=pugi.ENCODING_UTF8)
    return xml_writer.getvalue()
