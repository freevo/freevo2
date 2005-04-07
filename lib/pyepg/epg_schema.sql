
drop table versioning;
create table versioning (
    thing text primary key,
    version text
);
insert into versioning (thing, version) values ("sql", "0.1.1");

drop table channels;
create table channels (
    id unicode primary key,
    display_name unicode not null,
    access_id unicode not null
);

drop table channel_types;
create table channel_types (
    id integer primary key,
    name text not null
);
insert into channel_types (id, name) values (0, "undefined");
insert into channel_types (id, name) values (1, "tv");
insert into channel_types (id, name) values (2, "camera");
insert into channel_types (id, name) values (3, "radio");

drop table programs;
create table programs (
    id integer primary key,
    channel_id unicode(16) not null,
    start int not null,
    stop int not null,
    title unicode(256) not null,
    episode unicode(256),
    subtitle unicode(256),
    description unicode(4096),
    rating int,
    original_airdate int
);

create index programs_channel on programs (channel_id);
create unique index programs_channel_start on programs (channel_id, start);
create unique index programs_channel_start_stop on programs (channel_id, start, stop);
create index programs_start_stop on programs (start, stop);
create index programs_start on programs (start);
create index programs_stop on programs (stop);
create index programs_title on programs (title);

drop table categories;
create table categories (
    id integer primary key,
    name unicode not null
);
insert into categories (id, name) values (0, "undefined");
insert into categories (id, name) values (1, "series");
insert into categories (id, name) values (2, "news");
insert into categories (id, name) values (3, "movie");
insert into categories (id, name) values (4, "special");
insert into categories (id, name) values (5, "audio");
insert into categories (id, name) values (6, "feed");
insert into categories (id, name) values (7, "drama");

drop table program_category;
create table program_category (
    program_id integer not null,
    category_id integer not null
);

drop table advisories;
create table advisories (
    id integer primary key,
    name unicode not null
);
insert into advisories (id, name) values (0, "undefined");

drop table program_advisory;
create table program_advisory (
    program_id integer not null,
    advisory_id integer not null
);

drop table ratings;
create table ratings (
    id integer primary key,
    name unicode not null
);
insert into ratings (id, name) values (0, "undefined");
insert into ratings (id, name) values (1, "NR");
insert into ratings (id, name) values (2, "G");
insert into ratings (id, name) values (3, "PG");
insert into ratings (id, name) values (4, "PG-13");
insert into ratings (id, name) values (5, "PG-14");
insert into ratings (id, name) values (6, "A");
insert into ratings (id, name) values (7, "R");
insert into ratings (id, name) values (8, "X");

drop table record_programs;
create table record_programs (
    program_id integer primary key
);

drop table recorded_programs;
create table recorded_programs (
    program_id integer primary key
);
