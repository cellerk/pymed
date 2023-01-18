import json
import datetime

from typing import TypeVar
from typing import Optional

from .helpers import getContent


class PubMedBookArticle(object):
    """ Data class that contains a PubMed article.
    """

    __slots__ = (
        "pubmed_id",
        "booktitle",
        "articletitle",
        "abstract",
        "publication_date",
        "publication_date_string",
        "authors",
        "editors",
        "copyrights",
        "doi",
        "isbn",
        "language",
        "publication_type",
        "sections",
        "publisher",
        "publisher_location",
    )

    def __init__(
        self: object,
        xml_element: Optional[TypeVar("Element")] = None,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """ Initialization of the object from XML or from parameters.
        """

        # If an XML element is provided, use it for initialization
        if xml_element is not None:
            self._initializeFromXML(xml_element=xml_element)

        # If no XML element was provided, try to parse the input parameters
        else:
            for field in self.__slots__:
                self.__setattr__(field, kwargs.get(field, None))
    
    # Original function _extractPubMedId (returned many results)
    #def _extractPubMedId(self: object, xml_element: TypeVar("Element")) -> str:
    #    path = ".//ArticleId[@IdType='pubmed']"
    #    return getContent(element=xml_element, path=path)

    # New function _extractPubMedId (written by me)
    def _extractPubMedId(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//BookDocument/PMID"
        return getContent(element=xml_element, path=path)

    def _extractBookTitle(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//BookTitle"
        return getContent(element=xml_element, path=path)
    
    def _extractArticleTitle(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//ArticleTitle"
        return getContent(element=xml_element, path=path)

    def _extractAbstract(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText"
        return getContent(element=xml_element, path=path)

    def _extractCopyrights(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//CopyrightInformation"
        return getContent(element=xml_element, path=path)

    def _extractDoi(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//ArticleId[@IdType='doi']"
        return getContent(element=xml_element, path=path)

    def _extractIsbn(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Isbn"
        return getContent(element=xml_element, path=path)

    def _extractLanguage(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Language"
        return getContent(element=xml_element, path=path)

    def _extractPublicationType(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//PublicationType"
        return getContent(element=xml_element, path=path)

    def _extractPublicationDate(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//PubDate/Year"
        #path = ".//ContributionDate"
        return getContent(element=xml_element, path=path)

    def _extractPublisher(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Book/Publisher/PublisherName"
        return getContent(element=xml_element, path=path)

    def _extractPublisherLocation(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Book/Publisher/PublisherLocation"
        return getContent(element=xml_element, path=path)

    def _extractEditors(self: object, xml_element: TypeVar("Element")) -> list:
        return [
            {
                "lastname": getContent(editor, ".//LastName", None),
                "firstname": getContent(editor, ".//ForeName", None),
                "initials": getContent(editor, ".//Initials", None),
                #"affiliation": getContent(editor, ".//AffiliationInfo/Affiliation", None),
                "affiliation": [ getContent(aff_info, ".//Affiliation", None) for aff_info in editor.findall(".//AffiliationInfo") ],
                #"affiliation": self._extractAffiliation(xml_element.findall(".//Author")),
                "collective_name": getContent(editor, ".//CollectiveName", None),               # New addition added by me! 03.10.2022
            }
            for editor in xml_element.findall(".//AuthorList[@Type='editors']/Author")
        ]

    def _extractAuthors(self: object, xml_element: TypeVar("Element")) -> list:
        return [
            {
                "lastname": getContent(author, ".//LastName", None),
                "firstname": getContent(author, ".//ForeName", None),
                "initials": getContent(author, ".//Initials", None),
                #"affiliation": getContent(author, ".//AffiliationInfo/Affiliation", None),
                "affiliation": [ getContent(aff_info, ".//Affiliation", None) for aff_info in author.findall(".//AffiliationInfo") ],
                #"affiliation": self._extractAffiliation(xml_element.findall(".//Author")),
                "collective_name": getContent(author, ".//CollectiveName", None),               # New addition added by me! 03.10.2022
            }
            for author in xml_element.findall(".//AuthorList[@Type='authors']/Author")
        ]

    def _extractSections(self: object, xml_element: TypeVar("Element")) -> list:
        return [
            {
                "title": getContent(section, path=".//SectionTitle"),
                "chapter": getContent(element=section, path=".//LocationLabel"),
            }
            for section in xml_element.findall(".//Section")
        ]
    
    def _extractPublicationDateString(
        self: object, xml_element: TypeVar("Element")
    ) -> str:
        # Get the publication date as a string
        
        try:
            # Get the publication elements
            #publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
            publication_date = xml_element.find(".//ContributionDate")

            if publication_date is not None:
                publication_year = int(getContent(publication_date, ".//Year", None))
                publication_month = self.extract_publication_month(publication_date)
                publication_day = int(getContent(publication_date, ".//Day", "1"))
            
            # Construct a datetime object from the info
            publication_date_datetime = datetime.date(year=publication_year, month=publication_month, day=publication_day)
            return publication_date_datetime.strftime("%Y %b %d")

        # Unable to parse the datetime
        except Exception as e:
            print(e)
            return None

    def extract_publication_month(self, publication_date):
        month_str = getContent(publication_date, ".//Month", "1")
        try:
            return int(month_str)
        except ValueError:
            return monthToNum(month_str.lower())

    def _initializeFromXML(self: object, xml_element: TypeVar("Element")) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        # Parse the different fields of the article
        self.pubmed_id = self._extractPubMedId(xml_element)
        self.booktitle = self._extractBookTitle(xml_element)
        self.articletitle = self._extractArticleTitle(xml_element)
        self.abstract = self._extractAbstract(xml_element)
        self.copyrights = self._extractCopyrights(xml_element)
        self.doi = self._extractDoi(xml_element)
        self.isbn = self._extractIsbn(xml_element)
        self.language = self._extractLanguage(xml_element)
        self.publication_date = self._extractPublicationDate(xml_element)
        self.publication_date_string = self._extractPublicationDateString(xml_element)
        self.editors = self._extractEditors(xml_element)
        self.authors = self._extractAuthors(xml_element)
        self.publication_type = self._extractPublicationType(xml_element)
        self.publisher = self._extractPublisher(xml_element)
        self.publisher_location = self._extractPublisherLocation(xml_element)
        self.sections = self._extractSections(xml_element)

    def toDict(self: object) -> dict:
        """ Helper method to convert the parsed information to a Python dict.
        """

        return {
            key: (self.__getattribute__(key) if hasattr(self, key) else None)
            for key in self.__slots__
        }

    def toJSON(self: object) -> str:
        """ Helper method for debugging, dumps the object as JSON string.
        """

        return json.dumps(
            {
                key: (value if not isinstance(value, datetime.date) else str(value))
                for key, value in self.toDict().items()
            },
            sort_keys=True,
            indent=4,
        )
    


def monthToNum(shortMonth):
    return {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9, 
        'oct': 10,
        'nov': 11,
        'dec': 12
    }[shortMonth]
