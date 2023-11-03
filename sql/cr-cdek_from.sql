DROP FUNCTION shp.cdek_from(shp_id integer);

CREATE OR REPLACE FUNCTION shp.cdek_from(shp_id integer)
 RETURNS varchar
 LANGUAGE plpgsql
AS $function$
DECLARE
res_from varchar;
begin
    res_from = 'Мурино, ул. Ясная, д. 11';

return res_from;
end;
$function$
;
