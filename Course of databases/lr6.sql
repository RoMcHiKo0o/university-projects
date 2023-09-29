/*Сборник лучших цитат русских рэперов*/

create database mydb;
use mydb;


create table rapper
(
	rapper_id int primary key auto_increment,
    rapper_nick varchar(50) not null
);

insert into rapper(rapper_nick)
values
("Slava KPSS");

create table album
(
	album_id int primary key auto_increment,
    album_name varchar(50) not null
);

insert into album(album_name)
values
("ANTIHYPETRAIN");

create table song
(
	song_id int primary key auto_increment,
    song_name varchar(50) not null,
    ref_album int, 
    foreign key (ref_album) references rapper(rapper_id)
);


call  add_song("Дискотека Овсянкин", 1, 1);

create table songs_rappers
(
	song_id int not null,
    rapper_id int not null,
    primary key(song_id, rapper_id),
    foreign key (song_id) references song(song_id),
    foreign key (rapper_id) references rapper(rapper_id)
);

create table albums_rappers
(
	album_id int not null,
    rapper_id int not null,
    primary key(album_id, rapper_id),
    foreign key (album_id) references album(album_id),
    foreign key (rapper_id) references rapper(rapper_id)
);

create table quotes 
(
	quote_id int auto_increment primary key,
    quote_text text not null,
    rapper_id int not null,
    song_id int not null,
    foreign key (rapper_id) references rapper(rapper_id),
    foreign key (song_id) references song(song_id)
);

create table users
(
	user_id int primary key,
    user_name varchar(50),
    user_quotes int default 0
);

insert into users(user_id, user_name)
values
(1, "Roman");

create table user_quote
(
	quote_id int not null,
    user_id int not null,
    primary key(user_id, quote_id),
    foreign key (user_id) references users(user_id),
    foreign key (quote_id) references quotes(quote_id)
);

create table selection
(
	selection_id int primary key auto_increment, 
    selection_name varchar(50) not null
);

create table selection_quote
(
	selection_id int,
    quote_id int,
    primary key(selection_id, quote_id),
    foreign key (selection_id) references selection(selection_id),
    foreign key (quote_id) references quotes(quote_id)
);

create table user_selection
(
	selection_id int,
    user_id int,
    primary key(selection_id, user_id),
    foreign key (selection_id) references selection(selection_id),
    foreign key (user_id) references users(user_id)
);

create table rating
(
	rating_id int primary key auto_increment,
    rating_name varchar(50) not null,
    rating_type enum("song", "album", "quote")
);

create table rating_song
(
	rating_id int,
    song_id int, 
    primary key(rating_id, song_id),
    place int,
    foreign key (rating_id) references rating(rating_id),
    foreign key (song_id) references song(song_id)
);

create table rating_album
(
	rating_id int,
    album_id int, 
    primary key(rating_id, album_id),
    place int,
    foreign key (rating_id) references rating(rating_id),
    foreign key (album_id) references album(album_id)
);

create table rating_quote
(
	rating_id int,
    quote_id int, 
    primary key(rating_id, quote_id),
    place int,
    foreign key (rating_id) references rating(rating_id),
    foreign key (quote_id) references quotes(quote_id)
);

/*2*/

delimiter //
create procedure make_selection(in us_id int, in sel_name varchar(50))
begin
	insert into selection(selection_name)
    values
    (sel_name);
    insert into user_selection
    values
    ((select selection_id from selection where selection_name = sel_name), us_name);
end//
delimiter ;

delimiter //
create function get_mention(quo_id int)
returns int
begin
	declare ans int default 0;
    select count(selection_id) into ans from selection_quote where quote_id = quo_id;
    return ans;
end //
delimiter ;

delimiter //
create procedure create_quote(q_text varchar(50), rap_id int, so_id int)
begin
	start transaction;
    insert into quotes(quote_text, rapper_id, song_id)
    values
    (q_text, rap_id, so_id);
    if (select count(song_id) from song where so_id = song_id) = 0 then rollback;
    end if;
    if (select count(rapper_id) from rapper where rap_id = rapper_id) = 0 then rollback;
    end if;
end//
delimiter ;

call create_quote("Trust me, это не фотошоп, он реально огромный", 1, 2);

delimiter //
create trigger test_quote
before insert on quotes
for each row
begin
	if check_all_digit(new.quote_text) = 1 then
    SIGNAL SQLSTATE '45000'   
       SET MESSAGE_TEXT = '!!!!!!';
	end if;
end//
delimiter ;



delimiter //
create function check_all_digit(str varchar(50))
returns bool
begin
	return str REGEXP '^[[:digit:]]+$';
end//
delimiter ;

delimiter //
create procedure add_song(so_name int, ref_rapper int, ref_album int)
begin
	insert into song(song_name, ref_album)
    values
    (so_name, ref_album);
    insert into songs_rappers
    values
    ((select song_id from song where song_name = so_name), ref_rapper);
end//
delimiter ;

drop procedure add_quote;
delimiter //
create procedure add_quote(us_id int, quo_id int)
begin
	insert into user_quote
    values
    (quo_id, us_id);
    update users
    set user_quotes = user_quotes + 1
    where user_id = us_id;
end//
delimiter ;

create user base_user2 identified by '12345678';
create user rapper identified by 'antihype';

grant execute on procedure add_quote to base_user2;
grant execute on procedure add_song to rapper;

call add_quote(1,1);
create or replace view my_quotes
as select (select quote_text from quotes where quote_id = user_quote.quote_id) as `text` from user_quote where user_id = 1;

select * from my_quotes;

SET GLOBAL event_scheduler = ON;

create event `release`
on schedule at current_timestamp + interval 1 minute 
do 
	call add_song("Поставьте зачет пожалуйста!");
    