import json
import datetime

from xml.etree.ElementTree import Element
from typing import TypeVar
from typing import Optional

from .helpers import getContent


class PubMedArticle(object):
    """ Data class that contains a PubMed article.
    """

    __slots__ = (
        "pubmed_id",
        "title",
        "abstract",
        "keywords",
        "journal",
        "journal_abbr",
        "publication_date",
        "publication_date_string",
        "authors",
        "methods",
        "conclusions",
        "results",
        "copyrights",
        "doi",
        "xml",
        # New additions, by me
        "journal_volume",
        "journal_issue",
        "journal_pagination",
        "publication_type"
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
        #path = ".//ArticleId[@IdType='pubmed']"
        #return getContent(element=xml_element, path=path)

    # New function _extractPubMedId (written by me)
    def _extractPubMedId(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//MedlineCitation/PMID"
        return getContent(element=xml_element, path=path)

    def _extractTitle(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//ArticleTitle"
        return getContent(element=xml_element, path=path)

    def _extractKeywords(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Keyword"
        return [
            keyword.text for keyword in xml_element.findall(path) if keyword is not None
        ]

    def _extractJournal(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Journal/Title"
        return getContent(element=xml_element, path=path)
    
    def _extractJournalAbbr(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Journal/ISOAbbreviation"
        return getContent(element=xml_element, path=path)

    def _extractAbstract(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText"
        return getContent(element=xml_element, path=path)

    def _extractConclusions(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText[@Label='CONCLUSION']"
        return getContent(element=xml_element, path=path)

    def _extractMethods(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText[@Label='METHOD']"
        return getContent(element=xml_element, path=path)

    def _extractResults(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText[@Label='RESULTS']"
        return getContent(element=xml_element, path=path)

    def _extractCopyrights(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//CopyrightInformation"
        return getContent(element=xml_element, path=path)

    def _extractDoi(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//PubmedData/ArticleIdList/ArticleId[@IdType='doi']"
        return getContent(element=xml_element, path=path)

    def _extractJournalVolume(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Journal/JournalIssue/Volume"
        return getContent(element=xml_element, path=path)

    def _extractJournalIssue(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Journal/JournalIssue/Issue"
        return getContent(element=xml_element, path=path)

    def _extractJournalPagination(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Article/Pagination/MedlinePgn"
        return getContent(element=xml_element, path=path)

    def _extractPublicationType(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Article/PublicationTypeList/PublicationType[@UI='D016428']"
        return getContent(element=xml_element, path=path)

    def _extractPublicationDate(
        self: object, xml_element: TypeVar("Element")
    ) -> TypeVar("datetime.datetime"):
        # Get the publication date
        
        try:
            # Get the publication elements
            #publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
            publication_date = xml_element.find(".//MedlineCitation/Article/Journal/JournalIssue/PubDate")

            if publication_date is not None:
                publication_year = int(getContent(publication_date, ".//Year", None))
                publication_month = self.extract_publication_month(publication_date)
                publication_day = int(getContent(publication_date, ".//Day", "1"))
            
            else:
                publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
                publication_year = int(getContent(publication_date, ".//Year", None))
                publication_month = int(getContent(publication_date, ".//Month", 1))
                publication_day = int(getContent(publication_date, ".//Day", "1"))

            # Construct a datetime object from the info
            return datetime.date(
                year=publication_year, month=publication_month, day=publication_day
            )

        # Unable to parse the datetime
        except Exception as e:
            print(e)
            return None

    def _extractPublicationDateString(
        self: object, xml_element: TypeVar("Element")
    ) -> str:
        # Get the publication date as a string
        
        try:
            # Get the publication elements
            #publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
            publication_date = xml_element.find(".//MedlineCitation/Article/Journal/JournalIssue/PubDate")

            if publication_date is not None:
                if xml_element.find(".//MedlineDate") is not None:
                    return getContent(publication_date, ".//MedlineDate", None)
                else:    
                    publication_year = int(getContent(publication_date, ".//Year", None))
                    publication_month = self.extract_publication_month(publication_date)
                    publication_day = int(getContent(publication_date, ".//Day", "1"))
            
            else:
                publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
                publication_year = int(getContent(publication_date, ".//Year", None))
                publication_month = int(getContent(publication_date, ".//Month", 1))
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

    #def _extractAffiliation(self: object, xml_element: TypeVar("Element")) -> list:
    #    return [
    #        {
    #            "affiliation": getContent(affiliation, ".//Affiliation", None),
    #        }
    #       for affiliation in xml_element.findall(".//AffiliationInfo")
    #    ]
    
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
            for author in xml_element.findall(".//Author")
        ]

    def _initializeFromXML(self: object, xml_element: TypeVar("Element")) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        # Parse the different fields of the article
        self.pubmed_id = self._extractPubMedId(xml_element)
        self.title = self._extractTitle(xml_element)
        self.keywords = self._extractKeywords(xml_element)
        self.journal = self._extractJournal(xml_element)
        self.journal_abbr = self._extractJournalAbbr(xml_element)
        self.abstract = self._extractAbstract(xml_element)
        self.conclusions = self._extractConclusions(xml_element)
        self.methods = self._extractMethods(xml_element)
        self.results = self._extractResults(xml_element)
        self.copyrights = self._extractCopyrights(xml_element)
        self.doi = self._extractDoi(xml_element)
        self.publication_date = self._extractPublicationDate(xml_element)
        self.publication_date_string = self._extractPublicationDateString(xml_element)
        self.authors = self._extractAuthors(xml_element)
        self.xml = xml_element
        self.journal_volume = self._extractJournalVolume(xml_element)
        self.journal_issue = self._extractJournalIssue(xml_element)
        self.journal_pagination = self._extractJournalPagination(xml_element)
        self.publication_type = self._extractPublicationType(xml_element)

    def toDict(self: object) -> dict:
        """ Helper method to convert the parsed information to a Python dict.
        """

        return {key: self.__getattribute__(key) for key in self.__slots__}

    def toJSON(self: object) -> str:
        """ Helper method for debugging, dumps the object as JSON string.
        """

        return json.dumps(
            {
                key: (value if not isinstance(value, (datetime.date, Element)) else str(value))
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