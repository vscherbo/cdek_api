CREATE OR REPLACE FUNCTION shp.cdek_sender(shp_id integer,
    OUT company varchar(255), -- фирма-отправитель
    OUT contact varchar(255), -- (M) контактное лицо
    OUT email varchar(255)
)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
res_sender varchar;
begin
if shp_id = 111 then
    company := 'ЭТК';
    contact := 'Петрушенко Марина';
    email := 'buh@kipspb.ru';
else
    company := 'АРКОМ';
    contact := 'Петрушенко Марина';
    email := 'buh@kipspb.ru';
end if;

end;
$function$
;
