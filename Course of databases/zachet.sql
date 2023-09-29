create database chess_tournament;
use chess_tournament;

create table person 
(
	person_id int primary key auto_increment,
    person_name varchar(50) not null
);

alter table person
add column person_winner bool default false;

create table game
(
	game_id int primary key auto_increment,
	person1 int not null,
    person2 int not null,
    winner_id int default(if(rand() > 0.5, person1, person2)),
    foreign key (person1) references person(person_id),
    foreign key (person2) references person(person_id),
    foreign key (winner_id) references person(person_id)
);


delimiter //
create function check_pow(n int)
returns bool
begin
	declare lg double default log2(n);
    declare a double default pow(2, round(lg));
    return a = n;
end//
delimiter ;

delimiter //
create procedure iteration()
begin
	create or replace view winners
    ()
    as 
    select winner_id, row_number() over(partition by winner_id) as id from game);
    delete from game;
end//
delimiter ;


delimiter //
create procedure tournament()
begin
	declare n int default((select count(game_id) from game));
    start transaction;
	if check_pow(n) = 0 then rollback;
    end if;
    while n != 1
    do
		call iteration();
        set n = n div 2;
        create or replace view temp as
        select id as n1, (select winner_id from winners where id = n1*2 - 1) as first1, (select winner_id from winners where id = n1*2) as second1 from winners limit n;
        insert into game(person1, person2)
        select first1, second1 from temp;
	end while;
    update person
    set person_win = true
    where person_id = (select winner_id from game);
end//
delimiter ;

insert into person(person_name)
values
("Roma"),
("Nikita"),
("Diana"),
("Kirill");

insert into game(person1, person2)
values
(1, 2),
(3, 4);
delete from game;
drop procedure tournament;
call tournament();

select * from game;

delimiter //
create procedure make_pair()
begin
	declare id1, id2 int;
    select winner_id into id1 from game limit 0,1;
    select winner_id into id2 from game limit 1,1;
    insert into game(person1, person2)
    values
    (id1, id2);
    delete from game limit 2;
end//
delimiter ;

drop procedure make_pair;
select winner_id  from game limit 1,1;
select * from game;
call make_pair();
