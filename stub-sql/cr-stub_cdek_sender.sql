DROP FUNCTION shp.stub_cdek_sender(shp_id integer);

CREATE OR REPLACE FUNCTION shp.stub_cdek_sender(shp_id integer,
    OUT company varchar(255), -- фирма-отправитель
    OUT "name" varchar(255), -- (M) контактное лицо
    OUT email varchar(255)
)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
res_sender varchar;
begin
if shp_id = -111 then
    company := 'ЭТК';
    "name" := 'Петрушенко Марина';
    email := 'buh@kipspb.ru';
else
    company := 'АРКОМ';
    "name" := 'Петрушенко Марина';
    email := 'buh@kipspb.ru';
end if;

end;
$function$
;
