import datetime #<- time abstraction field
import sqlalchemy as sa

from pyramid.security import (
    Allow,
    Everyone,
    )

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode, #<- will provide unicode field
    UnicodeText, #<- will provide unicode text field
    DateTime, #<- time abstraction field
    Boolean,
    func,
    ForeignKey,
    and_,
    )

from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import search

from datetime import datetime
import time 

from math import log

from webhelpers.paginate import PageURL_WebOb, Page
 
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
make_searchable()

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
              ]
    def __init__(self, request):
        pass


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255), unique=True, nullable=False)
    name = Column(Unicode(255), nullable=False)
    email = Column(Unicode(255), unique=True, nullable=False)
    password = Column(Unicode(255), nullable=False)
    description = Column(Unicode(255), default=u'No description has been given.',
                         nullable=False)
    location = Column(Unicode(255), default=u'Not stated', nullable=False)
    url = Column(Unicode(255), default=u'www.answer.tv', nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    subscribers = Column(Integer, default=0)
    qkarma = Column(Integer, default=0)
    akarma = Column(Integer, default=0)
    usralias = Column(Unicode(255), nullable=False)
    following = Column(Unicode(255), nullable=False)
    notifications = Column(Unicode(255), default=u'12')
    emailon = Column(Boolean, unique=False, default=True)
    privAsk = Column(Unicode(255), default=u'public', nullable=False)
    privView = Column(Unicode(255), default=u'public', nullable=False)

    def __init__(self, name, username, email, password, usralias, following, url):
        self.username = username
        self.name = name
        self.password=password
        #self.description = description
        self.email = email
        #self.location = location
        self.url = url
        #self.subscribers = subscribers
        #self.qkarma = qkarma
        #self.akarma = akarma
        self.usralias = usralias
        self.following = following

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    questionasker = Column(Unicode())
    questionmain = Column(Unicode(255), unique = False, nullable=False)
    questiontext = Column(Unicode(255), unique=False, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    qkarma = Column(Integer, unique=False, default=0)
    askedby = Column(Unicode(255), unique=False, nullable=False)
    askedbyname = Column(Unicode(255), unique=False, nullable=False)
    askedtoname = Column(Unicode(255), unique=False, nullable=False)
    askedto = Column(Unicode(255), unique=False, nullable=False)
    alias = Column(Unicode(255), unique=True, nullable=False)
    askedtoalias = Column(Unicode(255), unique=False, nullable=False)
    askedbyalias = Column(Unicode(255), unique=True, nullable=False)
    unixage = Column(Integer, unique=False, default=0)
    searchvector = Column(TSVectorType('questionmain','questiontext'))
    answered = Column(Boolean, default=False)    
    upvoted = Column(Boolean, default=False) 
    views = Column(Integer, unique=False, default=0)
        
    def __init__(self, questionasker, questionmain, questiontext, qkarma,
                 askedby, askedbyname, askedtoname, askedto, alias,
                 askedtoalias, askedbyalias, unixage, views):
        self.questionmain = questionmain
        self.questiontext = questiontext
        self.questionasker = questionasker
        self.qkarma = qkarma
        self.askedby = askedby
        self.askedbyname = askedbyname
        self.askedtoname = askedtoname
        self.askedto = askedto
        self.alias = alias
        self.askedtoalias = askedtoalias
        self.askedbyalias = askedbyalias
        self.unixage = unixage
        self.views = views
        
#        #                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   

    @classmethod
    def get_hot(cls, request,  channellower, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedtoalias == channellower).order_by(sa.desc((Question.qkarma -1) /\
                    func.pow((now - Question.unixage), gravity))), page,
                    url=page_url, items_per_page=20)
           
    @classmethod
    def get_rising(cls, request,  channellower, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedtoalias == channellower).order_by(sa.desc(Question.qkarma)), page,
                    url=page_url, items_per_page=20)

    @classmethod
    def get_latest(cls, request,  channellower, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedtoalias == channellower).order_by(sa.desc(Question.created)).all(),\
                    page, url = page_url, items_per_page=20) 
    
    @classmethod
    def get_explore_trending(cls, request, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedby !="Sebastian").filter(Question.askedby !="sebastian").filter(Question.answered==True).order_by(sa.desc((Question.qkarma -1) /\
                    func.pow((now - Question.unixage), gravity))).limit(20), page,
                    url=page_url, items_per_page=20)
    
    @classmethod
    def get_explore_latest(cls, request, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedby !="Sebastian").filter(Question.askedby !="sebastian").filter(Question.answered==True).order_by(sa.desc(Question.created)).limit(20),\
                    page, url = page_url, items_per_page=20) 
    
    @classmethod
    def get_explore_trending100(cls, request, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedby !="Sebastian").filter(Question.askedby !="sebastian").filter(Question.answered==True).order_by(sa.desc((Question.qkarma -1) /\
                    func.pow((now - Question.unixage), gravity))).limit(100), page,
                    url=page_url, items_per_page=100)
    
    @classmethod
    def get_explore_latest100(cls, request, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedby !="Sebastian").filter(Question.askedby !="sebastian").filter(Question.answered==True).order_by(sa.desc(Question.created)).limit(100),\
                    page, url = page_url, items_per_page=100)
    
    @classmethod
    def get_explore_ourpicks100(cls, request, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedby !="Sebastian").filter(Question.askedby !="sebastian").filter(Question.answered==True).order_by(func.random()).offset(20).limit(100), page,
                    url=page_url, items_per_page=100)
        
    @classmethod
    def get_explore_ourpicks(cls, request, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker,\
                    Qvote.userid == logged_in_alias)).filter(Question.askedby !="Sebastian").filter(Question.askedby !="sebastian").filter(Question.answered==True).order_by(func.random()).offset(20).limit(20), page,
                    url=page_url, items_per_page=20)
        
    @classmethod
    def get_history(cls, request,  channellower, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker, Qvote.userid == logged_in_alias)).filter(Question.askedbyalias == channellower).order_by(sa.desc(Question.created)).all(), page,
                    url=page_url, items_per_page=20)
    
    @classmethod
    def get_ahistory(cls, request,  channellower, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin\
                   (Qvote, and_(Question.questionasker==Qvote.questionasker, Qvote.userid == logged_in_alias)).filter(Question.askedtoalias == channellower).filter(Question.answered == True).order_by(sa.desc(Question.created)).all(), page,
                    url=page_url, items_per_page=20)
    
    @classmethod
    def get_search(cls, request,  searchterm, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        query = DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin(Qvote, and_(Question.questionasker==Qvote.questionasker,Qvote.userid == logged_in_alias))
        query = search(query, searchterm)
        return Page(query, page, url=page_url, items_per_page=20)
        
    @classmethod
    def stream_hot(cls, request,  followinglist, logged_in_alias, page=1):
        page_url = PageURL_WebOb(request)
        try:
            followinglist = followinglist.lower()
            followinglist = followinglist.split()
        except:
            followinglist = ""
        now = int(round(time.time()/60/60)) + 1
        gravity = 1.8
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin(Qvote, and_(Question.questionasker==Qvote.questionasker,Qvote.userid == logged_in_alias)).filter(Question.askedtoalias.in_\
                   (followinglist)).order_by(sa.desc((Question.qkarma -1) /\
                    func.pow((now - Question.unixage), gravity))), page,
                    url=page_url, items_per_page=20)
 
    @classmethod
    def stream_latest(cls, request,  followinglist, logged_in_alias,  page=1):
        page_url = PageURL_WebOb(request)
        try:
            followinglist = followinglist.lower()
            followinglist = followinglist.split()
        except:
            followinglist = ""
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin(Qvote, and_(Question.questionasker==Qvote.questionasker,Qvote.userid == logged_in_alias)).filter(Question.askedtoalias.in_\
                   (followinglist)).order_by(sa.desc(Question.created)), page,
                   url=page_url, items_per_page=20)
   
    @classmethod
    def stream_top(cls, request,  followinglist, logged_in_alias,  page=1):
        page_url = PageURL_WebOb(request)
        try:
            followinglist = followinglist.lower()
            followinglist = followinglist.split()
        except:
            followinglist = ""
        return Page(DBSession.query(Question, Qvote, Images).outerjoin(Images, Images.usralias == Question.askedbyalias).outerjoin(Qvote, and_(Question.questionasker==Qvote.questionasker,Qvote.userid == logged_in_alias)).filter(Question.askedtoalias.in_\
                   (followinglist)).order_by(sa.desc(Question.qkarma)), page,
                    url=page_url, items_per_page=20)
 
 
class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    questiontext = Column(Unicode(255), unique = False, nullable=False) 
    akarma = Column(Integer, unique=False, default=0)
    created = Column(DateTime, default=datetime.utcnow)
    answeredby = Column(Unicode(255), unique = False, nullable=False)
    question = Column(Unicode(255), unique=False, nullable=False)
    embedcode = Column(Unicode(800), unique = False, nullable=False)
    channel = Column(Unicode(255), unique = False, nullable=False)
    unixage = Column(Integer, unique=False, default=0)
  
    
    def __init__(self, questiontext, question, akarma, embedcode, answeredby,
                 channel, unixage):
        self.questiontext = questiontext
        self.question = question
        self.akarma = akarma
        self.embedcode = embedcode
        self.answeredby = answeredby
        self.channel = channel
        self.unixage = unixage

class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key = True)
    usralias = Column(Unicode(), unique = True)
    profilepic = Column(Unicode())
    backgroundpic = Column(Unicode())
    
    def __init__(self, usralias, profilepic, backgroundpic):
        self.usralias = usralias
        self.profilepic = profilepic
        self.backgroundpic = backgroundpic
     

class Qvote(Base):
    __tablename__ = 'qvotes'
    id = Column(Integer, primary_key=True)
    questionasker = Column(Unicode())
    userid = Column(Unicode(255), unique=False)
    questionid = Column(Unicode(255))
    upvote = Column(Integer, unique=False)
    downvote = Column(Integer, unique=False)
    
    
    def __init__(self, questionasker, userid, questionid, upvote, downvote):
        self.userid = userid
        self. questionasker = questionasker
        self.questionid = questionid
        self.upvote = upvote
        self.downvote = downvote

class TempChannel(Base):
    __tablename__ = 'tempchannels'
    id = Column(Integer, primary_key=True)
    login = Column(Unicode(255), unique = False, nullable=False)
    password = Column(Unicode(255), unique = False, nullable=False)
    email = Column(Unicode(255), unique = False, nullable=False)
    verify = Column(Unicode(255), unique = False, nullable=False)
    useralias = Column(Unicode(255), unique = False, nullable=False)
    unixage = Column(Integer)

    def __init__(self, login, password, email, verify, useralias, unixage):
        self.login = login
        self.password = password
        self.email = email
        self.verify = verify
        self.useralias = useralias
        self.unixage = unixage
        
        
class TempPassword(Base):
    __tablename__ = 'temppasswords'
    id = Column(Integer, primary_key=True)
    emailalias = Column(Unicode(255), unique = False, nullable=False)
    hashcode = Column(Unicode(255), unique = False, nullable=False)
    unixage = Column(Integer)

    def __init__(self, emailalias, hashcode, unixage):
        self.emailalias = emailalias
        self.hashcode = hashcode
        self.unixage = unixage

class TempEmail(Base):
    __tablename__ = 'tempemail'
    id = Column(Integer, primary_key=True)
    oldemail = Column(Unicode(255), unique = False, nullable=False)
    emailalias = Column(Unicode(255), unique = False, nullable=False)
    hashcode = Column(Unicode(255), unique = False, nullable=False)
    unixage = Column(Integer)

    def __init__(self, oldemail, emailalias, hashcode, unixage):
        self.oldemail = oldemail
        self.emailalias = emailalias
        self.hashcode = hashcode
        self.unixage = unixage