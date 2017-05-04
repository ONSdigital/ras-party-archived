--liquibase formatted sql
--changeset ras_party:R1_0_0.ras_party_D0001_initial_build.sql

-- R Ingram Initial build 05/04/17

--
-- Schema: ras_party, schema for ras_party microservice
--
DROP SCHEMA IF EXISTS ras_party CASCADE;
CREATE SCHEMA ras_party;

--
-- User: ras_party, user for ras_party microservice
--
DROP USER IF EXISTS ras_party;
CREATE USER ras_party WITH PASSWORD 'password'
  SUPERUSER INHERIT CREATEDB CREATEROLE NOREPLICATION;

--
-- Table: ras_businesses [BUS]
--
DROP TABLE IF EXISTS ras_party.ras_businesses CASCADE;

CREATE TABLE ras_party.ras_businesses
(id              BIGSERIAL                 NOT NULL
,business_ref    CHARACTER VARYING (11)    NOT NULL
,party_id        CHARACTER VARYING (255)   NOT NULL
,name            CHARACTER VARYING (255)   NOT NULL
,trading_name    CHARACTER VARYING (255)
,enterprise_name CHARACTER VARYING (255)
,contact_name    CHARACTER VARYING (255)
,address_line_1  CHARACTER VARYING (35)    NOT NULL
,address_line_2  CHARACTER VARYING (35)
,address_line_3  CHARACTER VARYING (35)
,city            CHARACTER VARYING (35)    NOT NULL
,postcode        CHARACTER VARYING (10)    NOT NULL
,telephone       CHARACTER VARYING (20)
,employee_count  INTEGER
,facsimile       CHARACTER VARYING (20)
,fulltime_count  INTEGER
,legal_status    CHARACTER VARYING (255)
,sic_2003        CHARACTER VARYING (10)
,sic_2007        CHARACTER VARYING (10)
,turnover        INTEGER
,created_on      TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
,CONSTRAINT ras_bus_pk
   PRIMARY KEY (id)
,CONSTRAINT ras_bus_bus_ref_uk
   UNIQUE (business_ref)
,CONSTRAINT ras_bus_party_id_uk
   UNIQUE (party_id)
,CONSTRAINT valid_legal_status
   CHECK (legal_status IN ('COMMUNITY_INTEREST_COMPANY'
                          ,'CHARITABLE_INCORPORATED_ORGANISATION'
                          ,'INDUSTRIAL_AND_PROVIDENT_SOCIETY'
                          ,'GENERAL_PARTNERSHIP'
                          ,'LIMITED_LIABILITY_PARTNERSHIP'
                          ,'LIMITED_PARTNERSHIP'
                          ,'PRIVATE_LIMITED_COMPANY'
                          ,'PUBLIC_LIMITED_COMPANY'
                          ,'UNLIMITED_COMPANY'
                          ,'SOLE_PROPRIETORSHIP'))
);

--
-- Table: ras_respondents [RES]
--
DROP TABLE IF EXISTS ras_party.ras_respondents CASCADE;

-- CREATE TABLE ras_party.ras_respondents
-- (id             BIGSERIAL                 NOT NULL
-- ,party_id       CHARACTER VARYING (255)   NOT NULL
-- ,status         CHARACTER VARYING (30)    NOT NULL
-- ,email_address  CHARACTER VARYING (255)   NOT NULL
-- ,first_name     CHARACTER VARYING (100)   NOT NULL
-- ,last_name      CHARACTER VARYING (100)   NOT NULL
-- ,telephone      CHARACTER VARYING (20)
-- ,created_on     TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
-- ,CONSTRAINT ras_res_pk
--    PRIMARY KEY (id)
-- ,CONSTRAINT ras_bus_partyid_uk
--    UNIQUE (party_id)
-- ,CONSTRAINT ras_bus_emailaddress_uk
--    UNIQUE (email_address)
-- ,CONSTRAINT valid_status
--    CHECK (status IN ('CREATED'
--                     ,'ACTIVE'
--                     ,'SUSPENDED'))
-- );



CREATE TABLE ras_party.ras_respondents
(id             BIGSERIAL                 NOT NULL
,party_id       CHARACTER VARYING (255)   NOT NULL
,status         CHARACTER VARYING (30)    NOT NULL
,email_address  CHARACTER VARYING (255)   NOT NULL
,first_name     CHARACTER VARYING (100)   NOT NULL
,last_name      CHARACTER VARYING (100)   NOT NULL
,telephone      CHARACTER VARYING (20)
,created_on     TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
,CONSTRAINT ras_res_pk
   PRIMARY KEY (id)
,CONSTRAINT ras_res_party_id_uk
   UNIQUE (party_id)
,CONSTRAINT ras_res_emailaddress_uk
   UNIQUE (email_address)
,CONSTRAINT valid_status
   CHECK (status IN ('CREATED'
                    ,'ACTIVE'
                    ,'SUSPENDED'))
);




--
-- Table: ras_business_associations [BUA]
--
DROP TABLE IF EXISTS ras_party.ras_business_associations CASCADE;

CREATE TABLE ras_party.ras_business_associations
(id              BIGSERIAL                 NOT NULL
,business_id     BIGINT                    NOT NULL
,respondent_id   BIGINT                    NOT NULL
--,survey_id       CHARACTER VARYING (255)    NOT NULL
,status          CHARACTER VARYING (30)    NOT NULL
,effective_from  TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
,effective_to    TIMESTAMP WITH TIME ZONE
,created_on      TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
,CONSTRAINT ras_bua_pk
   PRIMARY KEY (id)
,CONSTRAINT ras_bua_bus_fk
   FOREIGN KEY (business_id)
     REFERENCES ras_party.ras_businesses(id)
,CONSTRAINT ras_bua_res_fk
   FOREIGN KEY (respondent_id)
     REFERENCES ras_party.ras_respondents(id)
,CONSTRAINT valid_status
   CHECK (status IN ('ACTIVE'
                    ,'INACTIVE'
                    ,'SUSPENDED'
                    ,'ENDED'))
);

--
-- Index: ras_bua_bus_fk_idx - FK Index
--
CREATE INDEX ras_bua_bus_fk_idx ON ras_party.ras_business_associations(business_id);

--
-- Index: ras_bua_res_fk_idx - FK Index
--
CREATE INDEX ras_bua_res_fk_idx ON ras_party.ras_business_associations(respondent_id);

--
-- Index: ras_bua_surveyid_idx
--
--CREATE INDEX ras_bua_surveyid_idx ON ras_party.ras_business_associations(surveyid);

--
-- Table: ras_enrolments [ENR]
--
DROP TABLE IF EXISTS ras_party.ras_enrolments CASCADE;

CREATE TABLE ras_party.ras_enrolments
(id                       BIGSERIAL                 NOT NULL
,business_association_id  BIGINT
,survey_id                CHARACTER VARYING (255)   NOT NULL
,status                   CHARACTER VARYING (30)    NOT NULL
,created_on               TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
,CONSTRAINT ras_enr_pk
   PRIMARY KEY (id)
,CONSTRAINT ras_bua_res_fk
   FOREIGN KEY (business_association_id)
     REFERENCES ras_party.ras_business_associations(id)
,CONSTRAINT valid_status
   CHECK (status IN ('PENDING'
                    ,'ENABLED'
                    ,'DISABLED'
                    ,'SUSPENDED'))
);

--
-- Index: ras_enr_bua_fk_idx - FK Index
--
CREATE INDEX ras_enr_bua_fk_idx ON ras_party.ras_enrolments(business_association_id);

--
-- Index: ras_enr_survey_id_idx
--
CREATE INDEX ras_enr_survey_id_idx ON ras_party.ras_enrolments(survey_id);

--
-- Table: ras_enrolment_codes [ENC]
--
DROP TABLE IF EXISTS ras_party.ras_enrolment_codes CASCADE;

CREATE TABLE ras_party.ras_enrolment_codes
(id                       BIGSERIAL                 NOT NULL
,respondent_id            BIGINT
,business_id              BIGINT                    NOT NULL
,survey_id                CHARACTER VARYING (255)   NOT NULL
,iac                      TEXT
,status                   CHARACTER VARYING (30)    NOT NULL
,created_on               TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
,CONSTRAINT ras_enc_pk
   PRIMARY KEY (id)
,CONSTRAINT ras_enc_res_fk
   FOREIGN KEY (respondent_id)
     REFERENCES ras_party.ras_respondents(id)
,CONSTRAINT ras_enc_bus_fk
   FOREIGN KEY (business_id)
     REFERENCES ras_party.ras_businesses(id)
,CONSTRAINT valid_status
   CHECK (status IN ('ACTIVE'
                    ,'REDEEMED'
                    ,'REVOKED'))
);

--
-- Index: ras_enc_res_fk_idx - FK Index
--
CREATE INDEX ras_enc_res_fk_idx ON ras_party.ras_enrolment_codes(respondent_id);

--
-- Index: ras_enc_bus_fk_idx - FK Index
--
CREATE INDEX ras_enc_bus_fk_idx ON ras_party.ras_enrolment_codes(business_id);

--
-- Index: ras_enc_iac_idx
--
CREATE INDEX ras_enc_iac_idx ON ras_party.ras_enrolment_codes(iac);


--
-- Table: ras_enrolment_invitations [ENI]
--
DROP TABLE IF EXISTS ras_party.ras_enrolment_invitations CASCADE;

CREATE TABLE ras_party.ras_enrolment_invitations
(id                       BIGSERIAL                 NOT NULL
,respondent_id            BIGINT                    NOT NULL
,target_email             CHARACTER VARYING (255)   NOT NULL
,verification_token       UUID                      NOT NULL
,sms_verification_token   INTEGER                   NOT NULL
,status                   CHARACTER VARYING (30)    NOT NULL
,effective_from           TIMESTAMP WITH TIME ZONE  NOT NULL
,effective_to             TIMESTAMP WITH TIME ZONE
,created_on               TIMESTAMP WITH TIME ZONE  NOT NULL DEFAULT NOW()
,CONSTRAINT ras_eni_pk
   PRIMARY KEY (id)
,CONSTRAINT ras_eni_res_fk
   FOREIGN KEY (respondent_id)
     REFERENCES ras_party.ras_respondents(id)
,CONSTRAINT valid_status
   CHECK (status IN ('ACTIVE'
                    ,'REDEEMED'
                    ,'REVOKED'))
);

--
-- Index: ras_eni_res_fk_idx - FK Index
--
CREATE INDEX ras_eni_res_fk_idx ON ras_party.ras_enrolment_invitations(respondent_id);

--
-- Index: ras_enc_ver_tok_idx
--
CREATE INDEX ras_enc_ver_tok_idx ON ras_party.ras_enrolment_invitations(verification_token);

--
-- Index: ras_enc_sms_tok_idx
--
CREATE INDEX ras_enc_sms_tok_idx ON ras_party.ras_enrolment_invitations(sms_verification_token);


--
-- some initial data
--
INSERT INTO ras_party.ras_businesses
  (business_ref,name,address_line_1,city,postcode,telephone
  ,employee_count,fulltime_count,legal_status,sic_2003,sic_2007,turnover)
VALUES
  ('11111111111','AAA Ltd','1 New St','Newtown','AA1 1AA','+44 1111 111111'
  ,100,100,'PRIVATE_LIMITED_COMPANY','1111','1111',100000)
 ,
  ('22222222222','BBB Ltd','2 New St','Newtown','BB1 2BB','+44 2222 222222'
  ,200,200,'PRIVATE_LIMITED_COMPANY','2222','2222',200000);

INSERT INTO ras_party.ras_respondents
  (party_id,status,email_address,first_name,last_name,telephone)
VALUES
  ('urn:uk.gov.ons:id:respondent:1111','ACTIVE'
  ,'a.adams@nowhere.com','Adam','Adams','+44 1111 111111')
 ,
  ('urn:uk.gov.ons:id:respondent:2222','ACTIVE'
  ,'b.brown@nowhere.com','Bill','Brown','+44 2222 222222');

INSERT INTO ras_party.ras_business_associations
  (business_id,respondent_id,status,effective_from)
VALUES
  ((SELECT id
    FROM   ras_party.ras_businesses
    WHERE  business_ref = '11111111111')
  ,(SELECT id
    FROM   ras_party.ras_respondents
    WHERE  party_id = 'urn:uk.gov.ons:id:respondent:1111')
  ,'ACTIVE',NOW()
  )
 ,((SELECT id
    FROM   ras_party.ras_businesses
    WHERE  business_ref = '22222222222')
  ,(SELECT id
    FROM   ras_party.ras_respondents
    WHERE  party_id = 'urn:uk.gov.ons:id:respondent:2222')
 ,'ACTIVE',NOW()
  );

INSERT INTO ras_party.ras_enrolments
  (business_association_id,survey_id,status)
VALUES
  ((SELECT bua.id
    FROM   ras_party.ras_business_associations bua
           JOIN ras_party.ras_businesses bus
           ON   bus.id = bua.business_id
    WHERE  bus.business_ref = '11111111111')
  ,'urn:uk.gov.ons:id:survey:BRES'
  ,'ENABLED'
  )
 ,((SELECT bua.id
    FROM   ras_party.ras_business_associations bua
           JOIN ras_party.ras_businesses bus
           ON   bus.id = bua.business_id
    WHERE  bus.business_ref = '22222222222')
  ,'urn:uk.gov.ons:id:survey:BRES'
  ,'ENABLED'
  );

INSERT INTO ras_party.ras_enrolment_codes
  (respondent_id, business_id, survey_id, iac, status)
VALUES
  (NULL
  ,(SELECT id
    FROM   ras_party.ras_businesses
    WHERE  business_ref = '11111111111')
  ,'urn:uk.gov.ons:id:survey:BRES'
  ,'1111-1111-1111-1111'
  ,'ACTIVE')
 ,(NULL
  ,(SELECT id
    FROM   ras_party.ras_businesses
    WHERE  business_ref = '22222222222')
  ,'urn:uk.gov.ons:id:survey:BRES'
  ,'2222-2222-2222-2222'
  ,'ACTIVE');

COMMIT;
