
use demohour;
DROP TABLE IF EXISTS demohour_project ;
DROP TABLE IF EXISTS demohour_supporter;
DROP TABLE IF EXISTS demohour_project_owner;
DROP TABLE IF EXISTS demohour_project_topic;
DROP TABLE IF EXISTS demohour_proj_incentive_options;

CREATE TABLE demohour_project
(
 -- proj_status	proj_id	proj_funding_target	proj_url	proj_current_funding_percentage	proj_surfer_count	proj_topic_count	proj_leftover_time	proj_current_funding_amount	
 -- proj_left_over_time_unit	proj_supporter_count	proj_owner_name	proj_name
  proj_id integer NOT NULL,
  proj_funding_target numeric(10,2) NOT NULL,
  proj_url text NOT NULL,
  proj_name text NOT NULL,
  
  proj_current_funding_amount numeric(10,2),
  proj_current_funding_percentage numeric(10,2),
  proj_status text,
  proj_leftover_time text,
  proj_left_over_time_unit text,
  proj_surfer_count integer,
  proj_topic_count integer,
  proj_supporter_count integer,
  proj_owner_name text
);

CREATE TABLE demohour_supporter
(
-- supporter_name,supporter_icon,supporter_support_time,supporter_total_support_proj,supporter_id,supporter_support_amount,supporter_proj_id
  supporter_name text NOT NULL,
  supporter_support_time Date NOT NULL,
  supporter_support_amount integer NOT NULL,
  supporter_proj_id integer NOT NULL,
  
  supporter_icon integer,
  supporter_total_support_proj integer,
  supporter_id integer
);

CREATE TABLE demohour_project_owner
(
-- proj_owner_owner_name,proj_owner_owner_id,proj_owner_last_log_in_time,proj_owner_own_proj_count,proj_owner_support_proj_count,proj_owner_proj_id,proj_owner_star_level

  proj_owner_owner_name text NOT NULL,
  proj_owner_owner_id integer NOT NULL,

  proj_owner_last_log_in_time Date,
  proj_owner_own_proj_count integer,
  proj_owner_support_proj_count integer,
  proj_owner_proj_id integer,
  proj_owner_star_level integer
);

CREATE TABLE demohour_project_topic
(
-- topic_proj_owner_name,topic_question_count,topic_proj_category,topic_proj_id,topic_down_count,topic_proj_location,topic_total_buzz_count,topic_announcement_count,topic_up_count
  topic_proj_owner_name text NOT NULL,
  topic_proj_category text NOT NULL,
  topic_proj_id integer NOT NULL,

  topic_down_count integer,
  topic_proj_location text,
  topic_total_buzz_count integer,
  topic_announcement_count integer,
  topic_question_count integer,
  topic_up_count integer
);

CREATE TABLE demohour_proj_incentive_options
(
-- incentive_reward_shipping_time	incentive_total_allowable_supporter_count	incentive_id	incentive_reward_shipping_method	incentive_description	
-- incentive_expect_support_amount	incentive_proj_id	incentive_current_supporter_count
  incentive_expect_support_amount integer NOT NULL,
  incentive_proj_id integer NOT NULL,
  
  incentive_reward_shipping_time integer,
  incentive_total_allowable_supporter_count integer,
  incentive_reward_shipping_method text,
  incentive_description text,
  incentive_current_supporter_count integer
);

-- set pk
ALTER TABLE demohour_project
      ADD CONSTRAINT pk_demohour_project PRIMARY KEY(proj_id);

-- ALTER TABLE demohour_supporter
   --   ADD CONSTRAINT pk_demohour_supporter PRIMARY KEY(_resourceid(32));

ALTER TABLE demohour_project_owner
      ADD CONSTRAINT pk_demohour_project_owner PRIMARY KEY(proj_owner_owner_id, proj_owner_proj_id);

ALTER TABLE demohour_project_topic
      ADD CONSTRAINT pk_demohour_project_topic PRIMARY KEY(topic_proj_id);


-- ALTER TABLE demohour_proj_incentive_options
 --     ADD CONSTRAINT pk_demohour_proj_incentive_options PRIMARY KEY(_giftcardid(32));


-- index all tables for perf
CREATE INDEX donorschoose_projects_teacher_acctid
  Using btree
  ON donorschoose_projects  (_teacher_acctid(32));


CREATE INDEX donorschoose_projects_schoolid
  USING btree
  ON donorschoose_projects(_schoolid(32));



CREATE INDEX donorschoose_resources_projectid
  USING btree
  ON donorschoose_resources
  (_projectid(32));

-- ALTER TABLE `donor`.`donorschoose_resources` 
--   ADD CONSTRAINT `FK_donorschoose_resources_projects`
--   FOREIGN KEY (_projectid(32))
--   REFERENCES `donor`.`donorschoose_projects` (`_projectid` )
--   ON DELETE CASCADE
--   ON UPDATE CASCADE
-- ;


CREATE INDEX donorschoose_essays_teacher_acctid
  USING btree
  ON donorschoose_essays
  (_teacher_acctid(32));


-- ALTER TABLE donorschoose_essays ADD CONSTRAINT FK_donorschoose_essays_projects
--   FOREIGN KEY (_projectid(32)) REFERENCES donorschoose_projects (_projectid);


CREATE INDEX donorschoose_donations_donor_acctid
  USING btree
  ON donorschoose_donations
  (_donor_acctid(32));

CREATE INDEX donorschoose_donations_projectid
  USING btree
  ON donorschoose_donations
  (_projectid(32));


CREATE INDEX donorschoose_donations_cartid
  USING btree
  ON donorschoose_donations
  (_cartid(32));


-- ALTER TABLE donorschoose_donations ADD CONSTRAINT FK_donorschoose_donations_projects
--   FOREIGN KEY (_projectid(32)) REFERENCES donorschoose_projects (_projectid);


CREATE INDEX donorschoose_giftcards_buyer_acctid
  USING btree
  ON donorschoose_giftcards
  (_buyer_acctid(32));

CREATE INDEX donorschoose_giftcards_recipient_acctid
  USING btree
  ON donorschoose_giftcards
  (_recipient_acctid(32));

CREATE INDEX donorschoose_giftcards_buyer_cartid
  USING btree
  ON donorschoose_giftcards
  (_buyer_cartid(32));

CREATE INDEX donorschoose_giftcards_redeemed_cartid
  USING btree
  ON donorschoose_giftcards
  (_redeemed_cartid(32));
