
drop table admin;
create table admin (
    version text primary key
);
insert into admin (version) values ("0.1.0");

drop table channels;
create table channels (
    id unicode primary key,
    call_sign unicode not null,
    tuner_id unicode not null
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
    channel_id unicode not null,
    title unicode not null,
    subtitle unicode,
    description unicode,
    episode unicode,
    start int not null,
    stop int not null,
    rating int,
    original_airdate int,
    stars int
);
create unique index programs_channel_start on programs (channel_id, start);

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
