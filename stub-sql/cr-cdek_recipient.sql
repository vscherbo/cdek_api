CREATE OR REPLACE FUNCTION shp.cdek_recipient(shp_id integer,
OUT company varchar(255), -- фирма-получатель
OUT contact varchar(255), -- (M) контактное лицо
OUT passport_series varchar(255),
OUT passport_number varchar(255),
OUT passport_date_of_issue date,
OUT passport_organization  varchar(255), -- кто выдал
OUT email varchar(255),
inn varchar(255)
)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
begin
if shp_id = 111 then
    company := 'ООО "Первое"';
    contact := 'Пётр Первый';
    email := 'petr1@ya.ru';
else
    company := 'ООО "Второе"';
    contact := 'Екатерина Вторая';
    email := 'cat2@mail.ru';
end if;

end;
$function$
;
