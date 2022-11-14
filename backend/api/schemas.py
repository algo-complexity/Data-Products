from datetime import date
from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel

from api import models


class Coauthor(BaseModel):
    container_type: str
    filled: list
    scholar_id: str
    source: str
    name: str
    affiliation: str


class GSBib(BaseModel):
    title: str
    pub_year: Optional[str] = None
    citation: str


class GSBibFilled(BaseModel):
    title: str
    author: list[str]
    pub_year: str
    venue: str
    abstract: str


class GSPublicationFilled(BaseModel):
    container_type: str
    source: str
    bib: GSBibFilled
    filled: bool
    gsrank: int
    pub_url: str
    author_id: list[str]
    url_scholarbib: str
    url_add_sclib: str
    num_citations: int
    citedby_url: str
    url_related_articles: str
    eprint_url: str


class GSPublication(BaseModel):
    container_type: str
    source: str
    bib: GSBib
    filled: bool
    author_pub_id: str
    num_citations: int
    citedby_url: Optional[str] = None
    cites_id: Optional[list[str]] = None
    public_access: Optional[bool] = None


class PublicAccess(BaseModel):
    available: int
    not_available: int


class GoogleScholar(BaseModel):
    container_type: str
    filled: list[str]
    source: str
    scholar_id: str
    url_picture: str
    name: str
    affiliation: str
    email_domain: str
    interests: list[str]
    citedby: int
    organization: Optional[int]
    homepage: Optional[str]
    citedby5y: int
    hindex: int
    hindex5y: int
    i10index: int
    i10index5y: int
    cites_per_year: Dict[int, int]
    coauthors: list[Coauthor]
    publications: list[GSPublication]
    public_access: PublicAccess


class Researcher(BaseModel):
    name: str
    email: Optional[str]
    citations: Optional[int]
    scholar_id: str
    faculty: Optional[str]
    interests: list[str]
    co_authors: list[str]
    publications: list[str]

    @classmethod
    def from_orm(cls, researcher: models.Researcher):
        return cls(
            name=researcher.name,
            email=researcher.email,
            citations=researcher.citations,
            scholar_id=researcher.scholar_id,
            faculty=researcher.faculty.name if researcher.faculty else None,
            interests=[item.name for item in researcher.interests.all()[:10]],
            co_authors=[item.name for item in researcher.co_authors.all()[:10]],
            publications=[item.title for item in researcher.publications.all()[:10]],
        )


class ResearcherStub(BaseModel):
    name: str

    @classmethod
    def from_orm(cls, researcher: models.Researcher):
        return cls(
            name=researcher.name,
        )


class Website(BaseModel):
    url: str

    @classmethod
    def from_orm(cls, website: models.Website):
        return cls(
            url=website.url,
        )


class ResearcherWebsite(BaseModel):
    url: str
    type: str

    @classmethod
    def from_orm(cls, researcher_site: models.ResearcherWebsites):
        return cls(url=researcher_site.website.url, type=researcher_site.type)


class Citation(BaseModel):
    year: date
    count: int

    @classmethod
    def from_orm(cls, citation: models.Citation):
        return cls(year=citation.year, count=citation.count)


class Publication(BaseModel):
    title: str
    abstract: str
    num_citations: int
    year: Optional[date]
    paper_url: Optional[str]
    conference: Optional[str]

    @classmethod
    def from_orm(cls, publication: models.Publication):
        return cls(
            title=publication.title,
            abstract=publication.abstract,
            num_citations=publication.num_citations,
            year=publication.year,
            paper_url=publication.paper_url.url if publication.paper_url else None,
            conference=publication.conference.name if publication.conference else None,
        )


class InterestNode(BaseModel):
    id: str
    name: str
    type: Literal["interest"]

    @classmethod
    def from_orm(cls, interest: models.Interest):
        return cls(id=interest.name, name=interest.name, type="interest")


class ProfNode(BaseModel):
    id: str
    name: str
    data: Researcher
    type: Literal["prof"]

    @classmethod
    def from_orm(cls, prof: models.Researcher):
        return cls(
            id=prof.name, name=prof.name, data=Researcher.from_orm(prof), type="prof"
        )


class Link(BaseModel):
    source: str
    target: str


class Graph(BaseModel):
    nodes: list[Union[ProfNode, InterestNode]]
    links: list[Link]
