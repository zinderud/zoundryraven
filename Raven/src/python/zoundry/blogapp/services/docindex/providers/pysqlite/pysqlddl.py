
PYSQL_INDEX_VERSION = u"0.982" #$NON-NLS-1$
PYSQL_DOCINDEX_DDL = u"""

CREATE TABLE MetaData (
    Name TEXT,
    Value TEXT
);


CREATE TABLE Document (
    DocumentId TEXT,
    Title TEXT,
    CreationTime TEXT,
    LastModifiedTime TEXT
);
CREATE INDEX DocIdIndex ON Document (DocumentId);
CREATE INDEX DocTitleIndex ON Document (Title);
CREATE INDEX DocCTIndex ON Document (CreationTime);
CREATE INDEX DocLMTIndex ON Document (LastModifiedTime);


CREATE TABLE PublishedData (
    DocumentId TEXT,
    AccountId TEXT,
    BlogId TEXT,
    BlogEntryId TEXT,
    IssuedTime TEXT,
    SynchTime TEXT,
    Draft INTEGER,
    Permalink TEXT
);
CREATE INDEX PubDocIdIndex ON PublishedData (DocumentId);
CREATE INDEX PubAccIdIndex ON PublishedData (AccountId);
CREATE INDEX PubBlogIdIndex ON PublishedData (BlogId);
CREATE INDEX PubDraftIndex ON PublishedData (Draft);
CREATE TRIGGER DELETE_CASCADE_PUBDATA AFTER DELETE ON Document FOR EACH ROW
   BEGIN
      DELETE FROM PublishedData WHERE PublishedData.DocumentId = OLD.DocumentId;
   END;

CREATE TABLE Link (
    DocumentId TEXT,
    Url TEXT,
    Host TEXT,
    Path TEXT,
    Rel TEXT,
    Title TEXT,
    Content TEXT,
    HitCount INTEGER
);
CREATE INDEX LinkDocIdIndex ON Link (DocumentId);
CREATE INDEX LinkUrlIndex ON Link (Url);
CREATE INDEX LinkHostIndex ON Link (Host);
CREATE TRIGGER DELETE_CASCADE_LINK AFTER DELETE ON Document FOR EACH ROW
   BEGIN
      DELETE FROM Link WHERE Link.DocumentId = OLD.DocumentId;
   END;


CREATE TABLE Tag (
    DocumentId TEXT,
    TagId TEXT,
    TagWord TEXT
);
CREATE INDEX TagIdIndex ON Tag (TagId);
CREATE INDEX TagDocIdIndex ON Tag (DocumentId);
CREATE TRIGGER DELETE_CASCADE_TAG AFTER DELETE ON Document FOR EACH ROW
   BEGIN
      DELETE FROM Tag WHERE Tag.DocumentId = OLD.DocumentId;
   END;


CREATE TABLE Image (
    DocumentId TEXT,
    Url TEXT,
    Host TEXT,
    Path TEXT,
    Title TEXT,
    HitCount INTEGER
);
CREATE INDEX ImageDocIdIndex ON Image (DocumentId);
CREATE INDEX ImageUrlIndex ON Image (Url);
CREATE INDEX ImageHostIndex ON Image (Host);
CREATE TRIGGER DELETE_CASCADE_IMAGE AFTER DELETE ON Document FOR EACH ROW
   BEGIN
      DELETE FROM Image WHERE Image.DocumentId = OLD.DocumentId;
   END;


INSERT INTO MetaData(Name, Value) VALUES ('Version', '%s');

""" % PYSQL_INDEX_VERSION #$NON-NLS-1$
